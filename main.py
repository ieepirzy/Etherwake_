"""
Etherwake HTTP trigger.
Listens for POST /wake → sends a WoL magic packet over LAN.
"""

import os
import socket
import struct
from http.server import HTTPServer, BaseHTTPRequestHandler

TARGET_MAC = os.getenv("TARGET_MAC")  # format: AA:BB:CC:DD:EE:FF
LISTEN_HOST = os.getenv("LISTEN_HOST")
LISTEN_PORT = int(os.getenv("LISTEN_PORT"))

if not TARGET_MAC:
    raise RuntimeError("TARGET_MAC must be set (e.g. AA:BB:CC:DD:EE:FF)")


def send_magic_packet(mac: str):
    """Send a Wake-on-LAN magic packet: 6x 0xFF + 16x MAC address."""
    mac_bytes = bytes.fromhex(mac.replace(":", "").replace("-", ""))
    payload = b"\xff" * 6 + mac_bytes * 16

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(payload, ("255.255.255.255", 9))


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/wake":
            try:
                send_magic_packet(TARGET_MAC)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "ok", "message": "Magic packet sent"}')
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(f'{{"status": "error", "message": "{e}"}}'.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "ok"}')
        else:
            self.send_response(404)
            self.end_headers()

    # Suppress request logging noise
    def log_message(self, format, *args):
        print(f"[etherwake] {args[0]}")


if __name__ == "__main__":
    server = HTTPServer((LISTEN_HOST, LISTEN_PORT), Handler)
    print(f"[etherwake] Listening on {LISTEN_HOST}:{LISTEN_PORT}")
    print(f"[etherwake] Target MAC: {TARGET_MAC}")
    server.serve_forever()