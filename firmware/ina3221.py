# ina3221.py
from machine import I2C

class INA3221:
    REG_CONFIG = 0x00
    
    BUS_REGS = {
        1: 0x02,
        2: 0x04,
        3: 0x06,
    }

    SHUNT_REGS = {
        1: 0x01,
        2: 0x03,
        3: 0x05,
    }

    def __init__(self, i2c: I2C, address: int, shunt_resistor_ohms = [0.005, 0.005, 0.005]):
        self.i2c = i2c
        self.address = address
        self.shunt_resistor = shunt_resistor_ohms
        self.configure()

    def configure(self):
        """Initialize INA3221 in continuous mode with default averaging."""
        config = 0b0111010100100111  # continuous, averaging, etc.
        buf = bytearray([self.REG_CONFIG, (config >> 8) & 0xFF, config & 0xFF])
        self.i2c.writeto(self.address, buf)


    def calibrate_zero(self, samples=50):
        offset = [0, 0, 0]
        for _ in range(samples):
            for ch in range(3):
                offset[ch] += self.read_shunt_voltage(ch+1)
            time.sleep_ms(5)
        self.zero_offset = [o / samples for o in offset]

    def _read_register(self, reg):
        self.i2c.writeto(self.address, bytes([reg]))
        data = self.i2c.readfrom(self.address, 2)
        return (data[0] << 8) | data[1]

    def read_shunt_voltage(self, channel: int) -> float:
        raw = self._read_register(self.SHUNT_REGS[channel])
        if raw >32767:
            raw -= 65536
        return raw * 0.005 /1000

    def read_bus_voltage(self, channel: int) -> float:
        raw = self._read_register(self.BUS_REGS[channel])
        return (raw >> 3) * 8e-3  # Each LSB = 8 mV

    def read_all(self):
        """Return dict with voltages and currents for all 3 channels."""
        readings = []
        for ch in range(1, 4):
            bus = self.read_bus_voltage(ch)
            shunt = self.read_shunt_voltage(ch)
            current = shunt / self.shunt_resistor[ch-1]
            power = current * bus
            
            readings.append({
                "channel": ch,
                "bus_voltage": bus,
                "shunt_voltage": shunt,
                "current": current,
                "power": power,
            })
        
        return readings
