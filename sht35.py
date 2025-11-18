import time
import json
import smbus2
from datetime import datetime
import mysql.connector
from mysql.connector import Error

# ========== SHT35 sensorinställningar ==========
I2C_BUS = 2                 # /dev/i2c-2
SHT3X_ADDRESS = 0x45        # Grove SHT35 address
CMD_SINGLE_SHOT_HIGH = (0x24, 0x00)

DATA_FILE = "/home/debian/sht35_log.jsonl"   # NDJSON-fil

# --- CRC-funktion ---
def _crc8_sht(data: bytes) -> int:
    poly = 0x31
    crc = 0xFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x80:
                crc = ((crc << 1) ^ poly) & 0xFF
            else:
                crc = (crc << 1) & 0xFF
    return crc

# --- Läs sensor ---
def read_sht35():
    with smbus2.SMBus(I2C_BUS) as bus:
        bus.write_i2c_block_data(SHT3X_ADDRESS, CMD_SINGLE_SHOT_HIGH[0], [CMD_SINGLE_SHOT_HIGH[1]])
        time.sleep(0.02)
        data = bus.read_i2c_block_data(SHT3X_ADDRESS, 0x00, 6)

        t_raw = bytes(data[0:2])
        t_crc = data[2]
        rh_raw = bytes(data[3:5])
        rh_crc = data[5]

        if _crc8_sht(t_raw) != t_crc or _crc8_sht(rh_raw) != rh_crc:
            raise ValueError("CRC check failed reading SHT35")

        t_ticks = (t_raw[0] << 8) | t_raw[1]
        rh_ticks = (rh_raw[0] << 8) | rh_raw[1]

        temperature_c = -45.0 + (175.0 * (t_ticks / 65535.0))
        humidity_rh = max(0.0, min(100.0, 100.0 * (rh_ticks / 65535.0)))

        return {
            "temperature": temperature_c,
            "humidity": humidity_rh
        }

# --- Logga till NDJSON-fil ---
def log_record(record):
    with open(DATA_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")

# --- Skriv data till MySQL-databas ---
def insert_to_db(record):
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='sht35user',
            password='By8Hq2Ze',
            database='sht35db'
        )
        if connection.is_connected():
            cursor = connection.cursor()
            sql = """
                INSERT INTO readings (timestamp, temperature, humidity)
                VALUES (%s, %s, %s)
            """
            data = (record["timestamp"], record["temperature"], record["humidity"])
            cursor.execute(sql, data)
            connection.commit()
            cursor.close()
    except Error as e:
        print(f"Error connecting/inserting to DB: {e}")
    finally:
        if connection.is_connected():
            connection.close()

# --- Huvudloop ---
print("Logging SHT35 data every minute...")

while True:
    try:
        reading = read_sht35()
        record = {
            "timestamp": datetime.now().isoformat(),
            "temperature": reading["temperature"],
            "humidity": reading["humidity"]
        }

        log_record(record)
        insert_to_db(record)
        print("Logged:", record)

    except Exception as e:
        print("Error:", e)

    time.sleep(5)  # vänta 5 sekunder


