# main.py
from machine import Pin, I2C, SPI
import utime
from ina3221 import INA3221
from ili934xnew import ILI9341, color565
import tt14, tt24

# Main loop delay in ms
_loop_delay = 500

# Parasitic resistances (vias and traces) in ohms
rp_shunt_12V     = 0.0035
rp_shunt_12V_CPU = 0.0000
rp_shunt_5V      = 0.0031
rp_shunt_3V      = 0.0017

# Cache for storing text values based on coordinates and inversed flag
_text_cache = {}

# Function to show text on display
def show_text(disp, x, y, text, inversed = False):
    key = (x, y, inversed)
    
    # if text is identical → skip redraw
    if _text_cache.get(key) == text:
        return
    
    if inversed:
        disp.set_color(color565(0,0,0), color565(255,255,255))
    disp.set_pos(x,y)
    disp.print(text)
    if inversed:
        disp.set_color(color565(255,255,255), color565(0,0,0))
    
    # store rendered text
    _text_cache[key] = text

print("ATX Current Monitor - Initializing...")

bl = Pin(22, Pin.OUT); bl.value(1)

# Dsplay
spi = SPI(0, baudrate=40_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
print("ATX Current Monitor - SPI bus initialized")

disp = ILI9341(spi, dc=Pin(20), cs=Pin(17), rst=Pin(21), r=3, w=320, h=240)
print("ATX Current Monitor - Display initialized")

# Clear display
disp.erase()

# Static labels
disp.set_font(tt24)
disp.set_color(color565(255,255,255), color565(0,0,0))
show_text(disp, 2, 2,   "5V")
disp.set_font(tt14)
show_text(disp, 42, 10, "VSB")
disp.set_font(tt24)
show_text(disp, 2, 32,  "12V ")
show_text(disp, 2, 52,  "5V")
show_text(disp, 2, 72,  "3.3V")
show_text(disp, 2, 102, "12V")
disp.set_font(tt14)
show_text(disp, 42, 110, "CPU")
disp.set_font(tt24)
show_text(disp, 2, 132, "TOTAL", True)
disp.set_font(tt14)
disp.set_color(color565(255,255,200), color565(0,0,0))
show_text(disp, 2,  220, "PSU CONSUMPTION MONITOR")
disp.set_font(tt24)

# I2C setup
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400_000)
print("ATX Current Monitor - I2C bus initialized")

# Init INA3221 sensors
sensor1 = INA3221(i2c, 0x40, [0.005 + rp_shunt_12V, 0.005 + rp_shunt_12V_CPU, 0.005 + rp_shunt_5V])
sensor2 = INA3221(i2c, 0x41, [0.1,   0.005 + rp_shunt_3V, 0.005])

print("ATX Current Monitor - INA3221 sensors initialized")
print("ATX Current Monitor - Initialized")

while True:
    stamp = utime.ticks_ms()
    
    data1 = sensor1.read_all()
    data2 = sensor2.read_all()
    
    # Calculate time spent to read sensors
    sensor_read_ms = utime.ticks_diff(utime.ticks_ms(), stamp)
    stamp = utime.ticks_ms()
    
    disp.set_font(tt24)
    
    # Show current
    disp.set_color(color565(252,215,3), color565(0,0,0))
    show_text(disp, 100, 2,   f"{data2[0]['current']:5.2f}A") # 5VSB
    show_text(disp, 100, 32,  f"{data1[0]['current']:5.2f}A") # 12V
    show_text(disp, 100, 52,  f"{data1[2]['current']:5.2f}A") # 5V
    show_text(disp, 100, 72,  f"{data2[1]['current']:5.2f}A") # 3.3V
    show_text(disp, 100, 102, f"{data1[1]['current']:5.2f}A") # 12V CPU
    
    # Show bus voltages
    disp.set_color(color565(252,61,3), color565(0,0,0))
    show_text(disp, 175, 2,   f"{data2[0]['bus_voltage']:04.1f}V") # 5VSB
    show_text(disp, 175, 32,  f"{data1[0]['bus_voltage']:04.1f}V") # 12V
    show_text(disp, 175, 52,  f"{data1[2]['bus_voltage']:04.1f}V") # 5V
    show_text(disp, 175, 72,  f"{data2[1]['bus_voltage']:04.1f}V") # 3.3V
    show_text(disp, 175, 102, f"{data1[1]['bus_voltage']:04.1f}V") # 12V CPU

    # Show power consumption
    disp.set_color(color565(3,161,252), color565(0,0,0))
    show_text(disp, 250, 2,   f"{data2[0]['power']:5.1f}W") # 5VSB
    show_text(disp, 250, 32,  f"{data1[0]['power']:5.1f}W") # 12V
    show_text(disp, 250, 52,  f"{data1[2]['power']:5.1f}W") # 5V
    show_text(disp, 250, 72,  f"{data2[1]['power']:5.1f}W") # 3.3V
    show_text(disp, 250, 102, f"{data1[1]['power']:5.1f}W") # 12V CPU

    # Show totals
    total_current = data1[0]['current'] + data1[1]['current'] + data1[2]['current'] + data2[0]['current'] + data2[1]['current']
    total_power = data1[0]['power'] + data1[1]['power'] + data1[2]['power'] + data2[0]['power'] + data2[1]['power']
    show_text(disp, 100, 132, f"{total_current:5.2f}A", True)
    show_text(disp, 250, 132, f"{total_power:5.1f}W", True)

    # Calculate time spent to refresh display values in ms
    display_show_ms = utime.ticks_diff(utime.ticks_ms(), stamp)

    # Display stat data
    disp.set_font(tt14)
    disp.set_color(color565(255,255,200), color565(0,0,0))
    show_text(disp, 2,  200, f"S: {sensor_read_ms:0004d}")
    show_text(disp, 70, 200, f"D: {display_show_ms:0004d}")
    
    loop_delay = _loop_delay - display_show_ms - sensor_read_ms
    if (loop_delay < 50):
        loop_delay = 50
        
    utime.sleep_ms(loop_delay)

