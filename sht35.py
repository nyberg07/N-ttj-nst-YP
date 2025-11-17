import time
import smbus2

I2C_BUS = 2                 # /dev/i2c-2
SHT3X_ADDRESS = 0x45        # Grove SHT35 address
CMD_SINGLE_SHOT_HIGH = (0x24, 0x00)

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

if __name__ == "__main__":
    with open("/home/debian/sht35.log", "a") as logfile:
        while True:
            try:
                data = read_sht35()
                log_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} Temperature: {data['temperature']:.2f} °C, Humidity: {data['humidity']:.2f} %\n"
                print(log_line, end="")
                logfile.write(log_line)
                logfile.flush()
            except Exception as e:
                error_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} Error reading sensor: {e}\n"
                print(error_line, end="")
                logfile.write(error_line)
                logfile.flush()
            time.sleep(5)  # Vänta 5 sekunder innan nästa läsning

