# PSU Consumption Monitor

High-side current and power monitoring board for **ATX power supplies**.  
This project allows measuring real-time **current, voltage, and power consumption**
on major ATX rails for diagnostics, testing, and educational purposes.

Created and documented by **FixThePixel**.

---

## ✨ Features

- High-side current sensing using precision shunt resistors
- Multi-rail monitoring:
  - +12 V
  - +5 V
  - +3.3 V
  - +5 VSB
- Bus voltage and current measurement via **INA3221**
- Inline ATX connector design
- MicroPython-based firmware
- Project-local KiCad symbols and footprints
- Clean, GitHub-friendly project structure

---

## 📐 Measurements

Per-rail power is calculated as:

```
Power (W) = Voltage (V) × Current (A)
```

Total system power can be derived by summing all monitored rails.

---

## 🧰 Tools & Requirements

### Hardware / CAD

- **KiCad 9.x** (tested)
- Standard KiCad libraries (symbols, footprints, 3D models)

---

## 🧩 3D Models

This repository **does not include third-party 3D models**.

- Standard KiCad 3D models are referenced via `${KICAD*_3DMODEL_DIR}`
- Third-party 3D models shown in videos are **not bundled**
- Optional model links may be provided separately

---

## 🧪 Fabrication (Gerbers)

Generated Gerber files are included for **non-commercial manufacturing only**.

See `gerber/README.md` for fabrication-specific notes and licensing.

---

## 🔌 Firmware

The `/firmware` directory contains MicroPython firmware for the monitor.

### Firmware Installation Guide

1.  **Board**
   
    MicroPython firmware must be installed on the target board (RP2040).

2.  **Installation**
   
    Copy all `*.py` files from `/firmware` directory into the root directory of the MicroPython device.

3.  **Third-party dependencies**
   
    The firmware depends on the ILI9341 display driver and font files from:

    - `https://github.com/jeffmer/micropython-ili9341`

    Required files:
      - ili934xnew.py
      - glcdfont.py
      - tt14.py
      - tt24.py

    These files are used unmodified and retain their original MIT license.
    They must also be copied to the root directory of the MicroPython device.

---

## 📜 License

This project is licensed under:

**Creative Commons Attribution–NonCommercial 4.0 International (CC BY-NC 4.0)**

Commercial use, manufacturing, or sale is **not permitted** without explicit permission.

https://creativecommons.org/licenses/by-nc/4.0/

---

## ⚠️ Disclaimer

This project is intended for **development, diagnostics, and educational use**.

Working with ATX power supplies involves **high current and potentially hazardous voltages**.
Use at your own risk.

---

## 👤 Author

**FixThePixel**  
YouTube: https://www.youtube.com/@FixThePixel
