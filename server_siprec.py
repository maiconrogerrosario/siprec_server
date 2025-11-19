#!/usr/bin/env python3
"""
sip_udp_siprec.py
Servidor SIPREC mínimo – recebe pacotes e encaminha para handlers.
"""

import socket
import threading
from sip_parser import parse_sip_message
from handlers.invite_handler import handle_invite
from handlers.ack_handler import handle_ack
from handlers.bye_handler import handle_bye
from handlers.options_handler import handle_options


class SIPServer:

    def __init__(self, host="0.0.0.0", port=5060):
        self.host = host
        self.port = port
        self.calls = {}    # Call-ID → SipSession
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))

    def get_external_ip(self):
        """
        Obtém o IP da interface de saída real do servidor.
        Funciona tanto em servidores locais quanto em EC2, DO, GCP, etc.
        """
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # não envia nada, só escolhe a rota
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def start(self):
        print(f"📡 SIP server listening on {self.host}:{self.port}")
        while True:
            data, addr = self.sock.recvfrom(65535)
            text = data.decode("utf-8", errors="ignore")

            sip = parse_sip_message(text)
            start = sip["start_line"]



            if start.startswith("INVITE"):
                threading.Thread(
                    target=handle_invite,
                    args=(self, sip, addr),
                    daemon=True
                ).start()

            elif start.startswith("ACK"):
                handle_ack(self, sip, addr)

            elif start.startswith("BYE"):
                handle_bye(self, sip, addr)

            elif start.startswith("OPTIONS"):
                handle_options(self, sip, addr)

            else:
                print("◻ Ignorado:", start)


if __name__ == "__main__":
    s = SIPServer()
    s.start()
