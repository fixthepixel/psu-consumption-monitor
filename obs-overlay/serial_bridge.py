#!/usr/bin/env python3
"""
RP2040 JSON Serial → HTTP bridge for OBS Browser Source

Usage:
  Linux/Mac:  python serial_bridge.py --port /dev/ttyACM0
  Windows:    python serial_bridge.py --port COM3

Install dependency first:
  pip install pyserial
"""

import argparse
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

import serial

# ── Shared state ──────────────────────────────────────────────────────────────
latest = {}
lock = threading.Lock()

# ── Serial reader thread ──────────────────────────────────────────────────────
def serial_reader(port: str, baud: int):
    while True:
        try:
            print(f"[serial] Connecting to {port} @ {baud}...")
            with serial.Serial(port, baud, timeout=2) as ser:
                print(f"[serial] Connected.")
                while True:
                    raw = ser.readline().decode("utf-8", errors="ignore").strip()
                    if not raw:
                        continue
                    try:
                        parsed = json.loads(raw)
                        with lock:
                            latest.clear()
                            latest.update(parsed)
                    except json.JSONDecodeError:
                        print(f"[serial] Bad JSON: {raw!r}")
        except serial.SerialException as e:
            print(f"[serial] Error: {e}  — retrying in 3s")
            time.sleep(3)

# ── HTTP server ───────────────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            with lock:
                body = json.dumps(latest).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *_):  # silence request logs
        pass

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description="RP2040 serial → HTTP bridge for OBS")
    ap.add_argument("--port",      default="/dev/ttyACM0", help="Serial port (e.g. COM3 or /dev/ttyACM0)")
    ap.add_argument("--baud",      type=int, default=115200, help="Baud rate (default: 115200)")
    ap.add_argument("--http-port", type=int, default=5757,   help="Local HTTP port (default: 5757)")
    args = ap.parse_args()

    t = threading.Thread(target=serial_reader, args=(args.port, args.baud), daemon=True)
    t.start()

    server = HTTPServer(("127.0.0.1", args.http_port), Handler)
    print(f"[http]  Serving at http://127.0.0.1:{args.http_port}/data")
    print(f"[http]  Press Ctrl+C to stop.")
    server.serve_forever()

if __name__ == "__main__":
    main()
