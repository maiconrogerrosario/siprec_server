#!/usr/bin/env python3
"""
sip_session.py

Controla sessão criada por INVITE SIPREC.
"""

import time
import threading

from sip_responses import (
    sip_response_100_trying,
    sip_response_200_ok_invite_siprec,
    sip_response_200_ok_bye
)

from sip_parser import parse_multipart, parse_sdp
from utils import make_tag


class SipSession:

    def __init__(self, server, sip_invite, peer_addr):
        self.server = server
        self.invite = sip_invite
        self.peer = peer_addr
        self.server_ip = server.get_external_ip()

        hdr = sip_invite["headers"]
        self.call_id = hdr.get("Call-ID")
        self.to_tag = make_tag()          # ← tag da sessão
        self.state = "EARLY"
        self.ack_received = False

        # SDP do INVITE
        parts = parse_multipart(
            sip_invite["body"],
            hdr.get("Content-Type", "")
        )
        raw_sdp = parts.get("application/sdp", "")
        self.sdp_info = parse_sdp(raw_sdp)

    # ---------------------------------------------------------------
    def send_trying(self):
        msg = sip_response_100_trying(self.invite, self.server_ip)
        self.server.sock.sendto(msg.encode(), self.peer)

    # ---------------------------------------------------------------
    def send_200_ok(self):
        msg = sip_response_200_ok_invite_siprec(
            self.invite,
            self.server_ip,
            to_tag=self.to_tag,   # ← agora usa o mesmo tag da sessão
            addr=self.peer
        )
        self.server.sock.sendto(msg.encode(), self.peer)
        self.state = "AWAITING_ACK"

    # ---------------------------------------------------------------
    def receive_ack(self):
        self.ack_received = True
        self.state = "CONFIRMED"

    # ---------------------------------------------------------------
    def wait_for_ack(self, timeout=30):
        waited = 0
        while waited < timeout:
            if self.ack_received:
                print(f"✔ ACK confirmado ({self.call_id})")
                return
            time.sleep(0.5)
            waited += 0.5
        print(f"⚠ Timeout esperando ACK ({self.call_id})")

    # ---------------------------------------------------------------
    def receive_bye(self, sip):
        msg = sip_response_200_ok_bye(sip)
        self.server.sock.sendto(msg.encode(), self.peer)
        self.state = "TERMINATED"

    # ---------------------------------------------------------------


