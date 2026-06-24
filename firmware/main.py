# main.py
from machine import Pin, I2C, SPI
import utime
import _thread
import ujson
from ina3221 import INA3221
from ili934xnew import ILI9341, color565
import tt14, tt24

# Parasitic resistances (vias and traces) in ohms
rp_shunt_12V     = 0.0035
rp_shunt_12V_CPU = 0.0000
rp_shunt_5V      = 0.0031
rp_shunt_3V      = 0.0017

# Shared sensor data protected by a lock
_data_lock = _thread.allocate_lock()
_shared = {
    "12v":     {"current": 0.0, "bus_voltage": 0.0, "power": 0.0},
    "12v_cpu": {"current": 0.0, "bus_voltage": 0.0, "power": 0.0},
    "5v":      {"current": 0.0, "bus_voltage": 0.0, "power": 0.0},
    "5vsb":    {"current": 0.0, "bus_voltage": 0.0, "power": 0.0},
    "3v3":     {"current": 0.0, "bus_voltage": 0.0, "power": 0.0},
    "total":   {"current": 0.0, "power": 0.0},
}

# Cache for storing text values based on coordinates and inversed flag
_text_cache = {}

# Graph ring buffers (320 samples, one per display column)
_GRAPH_Y     = 162
_GRAPH_H     = 35
_GRAPH_PMAX  = 300.0   # watts full scale
_GRAPH_IMAX  = 25.0    # amps full scale
_graph_power   = [0.0] * 320
_graph_current = [0.0] * 320
_graph_idx = 0

def _draw_graph_col(disp, col, power, current):
    disp.fill_rectangle(col, _GRAPH_Y, 1, _GRAPH_H, color565(0, 0, 0))
    ph = int(min(power / _GRAPH_PMAX, 1.0) * _GRAPH_H)
    if ph > 0:
        disp.fill_rectangle(col, _GRAPH_Y + _GRAPH_H - ph, 1, ph, color565(3, 161, 252))
    ch = int(min(current / _GRAPH_IMAX, 1.0) * (_GRAPH_H - 1))
    disp.pixel(col, _GRAPH_Y + _GRAPH_H - 1 - ch, color565(252, 215, 3))

def graph_update(disp, power, current):
    global _graph_idx
    _graph_power[_graph_idx] = power
    _graph_current[_graph_idx] = current
    _draw_graph_col(disp, _graph_idx, power, current)
    _graph_idx = (_graph_idx + 1) % 320
    disp.fill_rectangle(_graph_idx, _GRAPH_Y, 1, _GRAPH_H, color565(32, 32, 32))

def show_text(disp, x, y, text, inversed=False):
    key = (x, y, inversed)
    if _text_cache.get(key) == text:
        return
    if inversed:
        disp.set_color(color565(0, 0, 0), color565(255, 255, 255))
    disp.set_pos(x, y)
    disp.print(text)
    if inversed:
        disp.set_color(color565(255, 255, 255), color565(0, 0, 0))
    _text_cache[key] = text

# Core 1: poll sensors + send JSON every 200 ms
def serial_thread():
    while True:
        stamp = utime.ticks_ms()

        data1 = sensor1.read_all()
        data2 = sensor2.read_all()

        total_current = (data1[0]['current'] + data1[1]['current'] + data1[2]['current'] +
                         data2[0]['current'] + data2[1]['current'])
        total_power   = (data1[0]['power']   + data1[1]['power']   + data1[2]['power'] +
                         data2[0]['power']   + data2[1]['power'])

        _data_lock.acquire()
        try:
            _shared["12v"]     = dict(data1[0])
            _shared["12v_cpu"] = dict(data1[1])
            _shared["5v"]      = dict(data1[2])
            _shared["5vsb"]    = dict(data2[0])
            _shared["3v3"]     = dict(data2[1])
            _shared["total"]   = {"current": total_current, "power": total_power}
        finally:
            _data_lock.release()

        print(ujson.dumps({
            "12v":     dict(data1[0]),
            "12v_cpu": dict(data1[1]),
            "5v":      dict(data1[2]),
            "5vsb":    dict(data2[0]),
            "3v3":     dict(data2[1]),
            "total":   {"current": total_current, "power": total_power},
        }))

        elapsed = utime.ticks_diff(utime.ticks_ms(), stamp)
        delay = 200 - elapsed
        if delay > 0:
            utime.sleep_ms(delay)

print("ATX Current Monitor - Initializing...")

bl = Pin(22, Pin.OUT); bl.value(1)

spi = SPI(0, baudrate=40_000_000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(19), miso=Pin(16))
print("ATX Current Monitor - SPI bus initialized")

disp = ILI9341(spi, dc=Pin(20), cs=Pin(17), rst=Pin(21), r=3, w=320, h=240)
print("ATX Current Monitor - Display initialized")

disp.erase()

# Static labels
disp.set_font(tt24)
disp.set_color(color565(255, 255, 255), color565(0, 0, 0))
show_text(disp, 2, 2,    "5V")
disp.set_font(tt14)
show_text(disp, 42, 10,  "VSB")
disp.set_font(tt24)
show_text(disp, 2, 32,   "12V ")
show_text(disp, 2, 52,   "5V")
show_text(disp, 2, 72,   "3.3V")
show_text(disp, 2, 102,  "12V")
disp.set_font(tt14)
show_text(disp, 42, 110, "CPU")
disp.set_font(tt24)
show_text(disp, 2, 132,  "TOTAL", True)
disp.set_font(tt14)
disp.set_color(color565(255, 255, 200), color565(0, 0, 0))
show_text(disp, 2, 220,  "PSU CONSUMPTION MONITOR")
disp.fill_rectangle(0, _GRAPH_Y - 1, 320, 1, color565(48, 48, 48))
disp.set_font(tt24)

i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400_000)
print("ATX Current Monitor - I2C bus initialized")

sensor1 = INA3221(i2c, 0x40, [0.005 + rp_shunt_12V, 0.005 + rp_shunt_12V_CPU, 0.005 + rp_shunt_5V])
sensor2 = INA3221(i2c, 0x41, [0.1, 0.005 + rp_shunt_3V, 0.005])

print("ATX Current Monitor - INA3221 sensors initialized")

_thread.start_new_thread(serial_thread, ())

print("ATX Current Monitor - Initialized")

# Main loop (core 0): read shared data + update display
while True:
    stamp = utime.ticks_ms()

    _data_lock.acquire()
    try:
        d = {k: dict(v) for k, v in _shared.items()}
    finally:
        _data_lock.release()

    disp.set_font(tt24)

    disp.set_color(color565(252, 215, 3), color565(0, 0, 0))
    show_text(disp, 100, 2,   f"{d['5vsb']['current']:5.2f}A")
    show_text(disp, 100, 32,  f"{d['12v']['current']:5.2f}A")
    show_text(disp, 100, 52,  f"{d['5v']['current']:5.2f}A")
    show_text(disp, 100, 72,  f"{d['3v3']['current']:5.2f}A")
    show_text(disp, 100, 102, f"{d['12v_cpu']['current']:5.2f}A")

    disp.set_color(color565(252, 61, 3), color565(0, 0, 0))
    show_text(disp, 175, 2,   f"{d['5vsb']['bus_voltage']:04.1f}V")
    show_text(disp, 175, 32,  f"{d['12v']['bus_voltage']:04.1f}V")
    show_text(disp, 175, 52,  f"{d['5v']['bus_voltage']:04.1f}V")
    show_text(disp, 175, 72,  f"{d['3v3']['bus_voltage']:04.1f}V")
    show_text(disp, 175, 102, f"{d['12v_cpu']['bus_voltage']:04.1f}V")

    disp.set_color(color565(3, 161, 252), color565(0, 0, 0))
    show_text(disp, 250, 2,   f"{d['5vsb']['power']:5.1f}W")
    show_text(disp, 250, 32,  f"{d['12v']['power']:5.1f}W")
    show_text(disp, 250, 52,  f"{d['5v']['power']:5.1f}W")
    show_text(disp, 250, 72,  f"{d['3v3']['power']:5.1f}W")
    show_text(disp, 250, 102, f"{d['12v_cpu']['power']:5.1f}W")

    show_text(disp, 100, 132, f"{d['total']['current']:5.2f}A", True)
    show_text(disp, 250, 132, f"{d['total']['power']:5.1f}W",   True)

    graph_update(disp, d['total']['power'], d['total']['current'])

    display_show_ms = utime.ticks_diff(utime.ticks_ms(), stamp)

    disp.set_font(tt14)
    disp.set_color(color565(255, 255, 200), color565(0, 0, 0))
    show_text(disp, 2, 200, f"D: {display_show_ms:04d}")

    loop_delay = 500 - display_show_ms
    if loop_delay < 50:
        loop_delay = 50
    utime.sleep_ms(loop_delay)
