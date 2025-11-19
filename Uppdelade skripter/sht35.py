import time                            # Importera modulen time för fördröjningar
import json                            # Importera modulen json för att skriva data i JSON-format
import smbus2                         # Importera smbus2 för I2C-kommunikation
from datetime import datetime          # Importera datetime för tidsstämpling
import mysql.connector                 # Importera MySQL-connector för databasanslutning
from mysql.connector import Error      # Importera felhantering från mysql.connector

# ========== SHT35 sensorinställningar ==========
I2C_BUS = 2                 # I2C bussnummer, här används /dev/i2c-2
SHT3X_ADDRESS = 0x45        # I2C-adress för SHT35 sensorn
CMD_SINGLE_SHOT_HIGH = (0x24, 0x00)  # Kommando för enkel mätning i hög precision

DATA_FILE = "/home/debian/sht35_log.jsonl"   # Filväg för att spara data i NDJSON-format

# --- CRC-funktion ---
def _crc8_sht(data: bytes) -> int:
    poly = 0x31                    # Polynom för CRC-beräkning
    crc = 0xFF                    # Startvärde för CRC
    for b in data:                # Gå igenom varje byte i datan
        crc ^= b                 # XOR med aktuell byte
        for _ in range(8):        # Loopa 8 bitar
            if crc & 0x80:       # Om högsta biten är satt
                crc = ((crc << 1) ^ poly) & 0xFF  # Skifta vänster, XOR med poly
            else:
                crc = (crc << 1) & 0xFF           # Annars bara skifta vänster
    return crc                   # Returnera beräknad CRC

# --- Läs sensor ---
def read_sht35():
    with smbus2.SMBus(I2C_BUS) as bus:         # Öppna I2C-bussen
        bus.write_i2c_block_data(SHT3X_ADDRESS, CMD_SINGLE_SHOT_HIGH[0], [CMD_SINGLE_SHOT_HIGH[1]])  # Skicka mätkommando
        time.sleep(0.02)                        # Vänta 20 ms för mätning
        data = bus.read_i2c_block_data(SHT3X_ADDRESS, 0x00, 6)  # Läs 6 bytes från sensorn

        t_raw = bytes(data[0:2])                # Temperaturdata råa bytes
        t_crc = data[2]                         # Temperatur CRC-byte
        rh_raw = bytes(data[3:5])               # Luftfuktighetsdata råa bytes
        rh_crc = data[5]                        # Luftfuktighets CRC-byte

        # Kontrollera CRC för temperatur och luftfuktighet
        if _crc8_sht(t_raw) != t_crc or _crc8_sht(rh_raw) != rh_crc:
            raise ValueError("CRC check failed reading SHT35")  # Om CRC misslyckas, kasta fel

        t_ticks = (t_raw[0] << 8) | t_raw[1]    # Konvertera temperatur till ticks
        rh_ticks = (rh_raw[0] << 8) | rh_raw[1] # Konvertera luftfuktighet till ticks

        # Omvandla ticks till grader Celsius och relativ luftfuktighet %
        temperature_c = -45.0 + (175.0 * (t_ticks / 65535.0))
        humidity_rh = max(0.0, min(100.0, 100.0 * (rh_ticks / 65535.0)))

        return {
            "temperature": temperature_c,        # Returnera temperatur i Celsius
            "humidity": humidity_rh              # Returnera luftfuktighet i procent
        }

# --- Logga till NDJSON-fil ---
def log_record(record):
    with open(DATA_FILE, "a") as f:             # Öppna filen i append-läge
        f.write(json.dumps(record) + "\n")      # Skriv JSON-objekt + ny rad

# --- Skriv data till MySQL-databas ---
def insert_to_db(record):
    try:
        connection = mysql.connector.connect(   # Skapa databasanslutning
            host='localhost',
            user='sht35user',
            password='By8Hq2Ze',
            database='sht35db'
        )
        if connection.is_connected():
            cursor = connection.cursor()        # Skapa cursor för SQL-kommandon
            sql = """
                INSERT INTO readings (timestamp, temperature, humidity)
                VALUES (%s, %s, %s)
            """
            data = (record["timestamp"], record["temperature"], record["humidity"])  # Data att infoga
            cursor.execute(sql, data)           # Kör SQL-frågan
            connection.commit()                 # Spara ändringar i databasen
            cursor.close()                     # Stäng cursor
    except Error as e:
        print(f"Error connecting/inserting to DB: {e}")  # Skriv ut eventuella fel
    finally:
        if connection.is_connected():
            connection.close()                 # Stäng anslutning

# --- Huvudloop ---
print("Logging SHT35 data every minute...")     # Startmeddelande

while True:
    try:
        reading = read_sht35()                    # Läs sensorvärden
        record = {
            "timestamp": datetime.now().isoformat(),  # Skapa tidsstämpel i ISO-format
            "temperature": reading["temperature"],    # Temperatur
            "humidity": reading["humidity"]           # Luftfuktighet
        }

        log_record(record)                         # Logga till fil
        insert_to_db(record)                       # Skriv till databas
        print("Logged:", record)                   # Skriv ut loggmeddelande

    except Exception as e:
        print("Error:", e)                         # Hantera eventuella fel

    time.sleep(5)                                 # Vänta 5 sekunder innan nästa mätning

