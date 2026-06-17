#!/usr/bin/env python3
"""Servidor com navegação rápida entre HTMLs."""

import http.server
import socketserver
import os
import sys
from pathlib import Path

# ─── Configuração ───────────────────────────────────────────
PORT = 8000
TEMPLATES_DIR = Path(__file__).parent / "templates"

# Páginas disponíveis (atalho → arquivo)
PAGES = {
    "1": "dashbord1.html",
    "2": "dashbord2.html",
    "3": "dashbord3.html",
    "4": "dashbord4.html",
    "electro": "electro.html",
    "e": "electro.html",
}

current_page = PAGES["1"]


class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global current_page

        if self.path == "/" or self.path == "/current":
            self.path = f"/templates/{current_page}"
        elif self.path.startswith("/goto/"):
            page_key = self.path[6:]  # Remove "/goto/"
            if page_key in PAGES:
                current_page = PAGES[page_key]
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
                return
            else:
                self.send_error(404, f"Página não encontrada: {page_key}")
                return
        elif self.path == "/list":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            page_list = "<br>".join(
                f'<a href="/goto/{k}">{v}</a>' for k, v in PAGES.items()
            )
            self.wfile.write(
                f"<html><body><h2>Todas as páginas:</h2>{page_list}</body></html>".encode()
            )
            return
        elif self.path == "/pages":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            import json

            self.wfile.write(json.dumps(list(PAGES.keys())).encode())
            return

        return super().do_GET()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")


def print_banner():
    print("⚡ ELECTRO SERVER")
    print("─" * 20)


def main():
    global current_page

    os.chdir(TEMPLATES_DIR.parent)

    # Verificar argumentos
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in PAGES:
            current_page = PAGES[arg]
        elif arg in ["list", "ls"]:
            print_banner()
            print("📄 Páginas disponíveis:\n")
            for k, v in PAGES.items():
                print(f"   → /goto/{k:<10} {v}")
            print()
            return
        elif arg in ["q", "quit", "exit"]:
            return

    print_banner()
    print(f"🌐 http://localhost:{PORT} | {current_page}")
    print()

    socketserver.TCPServer.allow_reuse_address = True
    with ReuseAddrTCPServer(("", PORT), CustomHandler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
