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

### Firmware
- **MicroPython**
- Supported MCUs depend on firmware implementation
  (RP2040 / ESP32 recommended)

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
