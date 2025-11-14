#!/usr/bin/env python3
"""
sip_udp_siprec.py

Servidor SIP mínimo (UDP) para SIPREC:
 - Escuta em 0.0.0.0:5060
 - Responde INVITE com 200 OK multipart/mixed (dois SDP)
 - Responde OPTIONS com 200 OK (com rport/received reordenados)
 - Aguarda ACK
 - Após 10s envia BYE
 - Trata Require: SIPREC
"""

import socket
import threading
import time
import random

LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 5060
CRLF = "\r\n"

# -----------------------------------------------------------
# 📦 Funções auxiliares
# -----------------------------------------------------------

def parse_sip(msg):
    """Converte texto SIP em dicionário estruturado."""
    lines = msg.split(CRLF)
    start = lines[0]
    headers = {}
    body = ""
    i = 1
    while i < len(lines):
        line = lines[i]
        if line == "":
            body = CRLF.join(lines[i+1:]) if i+1 < len(lines) else ""
            break
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()
        i += 1
    return {"start": start, "headers": headers, "body": body, "raw": msg}


def make_tag():
    """Gera um tag aleatório para To: ou Call-ID."""
    return str(random.randint(10000, 99999))


# -----------------------------------------------------------
# 🧩 Função para reordenar parâmetros do cabeçalho Via
# -----------------------------------------------------------
def reorder_via_params(via_line):
    """
    Reordena parâmetros do cabeçalho Via para deixar em ordem:
    rport, received, branch.
    """
    try:
        parts = via_line.split(";", 1)
        base = parts[0]
        if len(parts) == 1:
            return via_line

        params = parts[1].split(";")
        parsed = {}
        others = []
        for p in params:
            if "=" in p:
                k, v = p.split("=", 1)
                parsed[k.strip()] = v.strip()
            else:
                others.append(p.strip())

        # Define a ordem desejada
        order = ["rport", "received", "branch"]

        reordered = []
        for key in order:
            if key in parsed:
                reordered.append(f"{key}={parsed[key]}")

        # Adiciona os parâmetros que sobraram
        for p in params:
            k = p.split("=")[0].strip() if "=" in p else p.strip()
            if k not in order:
                reordered.append(p.strip())

        via_reordered = f"{base};" + ";".join(reordered)
        return via_reordered
    except Exception:
        return via_line


# -----------------------------------------------------------
# 🧠 Construtores de respostas SIP
# -----------------------------------------------------------


def build_100_trying(sip, server_ip):
    hdr = sip["headers"]
    via = hdr.get("Via", "")
    from_hdr = hdr.get("From", "")
    to_hdr = hdr.get("To", "")
    call_id = hdr.get("Call-ID", "")
    cseq = hdr.get("CSeq", "")

    # Ajustar rport
    if "rport" in via:
        via = via.replace("rport", f"rport={5060};received={server_ip}")

    resp = [
        "SIP/2.0 100 Trying",
        f"Via: {via}",
        f"From: {from_hdr}",
        f"To: {to_hdr}",
        f"Call-ID: {call_id}",
        f"CSeq: {cseq}",
        "Content-Length: 0",
        ""
    ]

    return CRLF.join(resp) + CRLF



def build_200_ok_siprec(invite, server_ip, addr=None, media_port1=10000, media_port2=10000):
    """Monta resposta 200 OK SIPREC com multipart SDP e headers corretos."""
    hdr = invite["headers"]
    via = hdr.get("Via", "")
    from_hdr = hdr.get("From", "")
    to_hdr = hdr.get("To", "")
    call_id = hdr.get("Call-ID", "")
    cseq = hdr.get("CSeq", "")
    contact = hdr.get("Contact", f"<sip:{server_ip}>")

    # 🧩 rport/received
    if "rport" in via:
        ip, port = addr if addr else ("127.0.0.1", 5060)
        via = via.replace("rport", f"rport={port};received={ip}")

    # Reordena parâmetros
    via = reorder_via_params(via)

    # Boundary para multipart
    boundary = "siprecboundary12345"

    # SDP 1
    sdp1 = [
        "v=0",
        f"o=- {int(time.time())} {int(time.time())} IN IP4 {server_ip}",
        "s=Stream 1",
        f"c=IN IP4 {server_ip}",
        "t=0 0",
        f"m=audio {media_port1} RTP/AVP 0 8",
        "a=rtpmap:0 PCMU/8000",
        "a=rtpmap:8 PCMA/8000",
        "a=recvonly"
    ]

    # SDP 2
    sdp2 = [
        f"m=audio {media_port2} RTP/AVP 0 8",
        "a=rtpmap:0 PCMU/8000",
        "a=rtpmap:8 PCMA/8000",
        "a=recvonly"
    ]

    # Multipart body
    multipart_body = CRLF.join([

        CRLF.join(sdp1),

        CRLF.join(sdp2),

    ])

    # Resposta SIP
    resp = [
        "SIP/2.0 200 OK",
        f"From: {from_hdr}",
        f"To: {to_hdr};tag={make_tag()}",
        f"Call-ID: {call_id}",
        f"CSeq: {cseq}",
        f"Via: {via}",
        f"Supported: timer,siprec",
        f"Contact: {contact}",
        "Session-Expires: 1800;refresher=uas",
        f"Content-Type: application/sdp",
        f"Content-Length: {len(multipart_body.encode('utf-8'))}",
        "",
        multipart_body
    ]

    response = CRLF.join(resp)
    return response + CRLF


def build_200_ok_options(options, server_ip, addr=None):
    """Monta resposta 200 OK para OPTIONS (com rport e received adicionados e ordenados)."""
    hdr = options["headers"]
    via = hdr.get("Via", "")
    from_hdr = hdr.get("From", "")
    to_hdr = hdr.get("To", "")
    call_id = hdr.get("Call-ID", "")
    cseq = hdr.get("CSeq", "")
    contact = hdr.get("Contact", f"<sip:{server_ip}>")

    # 🧩 Se o cliente enviou rport, adicionamos os valores reais
    if "rport" in via:
        ip, port = addr if addr else ("127.0.0.1", 5060)
        # Remove possíveis duplicados
        via = via.replace("rport", f"rport={port};received={ip}")

    # 🧠 Agora reordenamos para rport, received, branch
    via = reorder_via_params(via)

    # 🧱 Monta resposta SIP padrão
    resp = [
        "SIP/2.0 200 OK",
        f"Via: {via}",
        f"From: {from_hdr}",
        f"To: {to_hdr};tag={make_tag()}",
        f"Call-ID: {call_id}",
        f"CSeq: {cseq}",
        f"Contact: {contact}",
        "Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, NOTIFY, MESSAGE, SUBSCRIBE, INFO",
        "Accept: application/sdp",
        "Accept-Encoding: gzip",
        "Accept-Language: en, pt-BR",
        "Supported: replaces, timer, 100rel, norefersub",
        "Server: Python-SIP-Responder/1.0",
        "Content-Length: 0",
        ""
    ]
    response = CRLF.join(resp)
    return response + CRLF


def build_bye(invite, server_ip, addr=None):
    """Monta uma requisição BYE válida para o peer do INVITE."""
    hdr = invite["headers"]
    via = hdr.get("Via", "")
    from_hdr = hdr.get("From", "")
    to_hdr = hdr.get("To", "")
    call_id = hdr.get("Call-ID", "")
    cseq_num = int(hdr.get("CSeq", "1").split()[0])
    cseq = f"{cseq_num + 1} BYE"

    # Usa o endereço real do peer se disponível
    peer_uri = f"sip:{addr[0]}:{addr[1]}" if addr else "sip:callee@server"
    contact = hdr.get("Contact", f"<sip:{server_ip}>")

    resp = [
        f"BYE {peer_uri} SIP/2.0",
        f"Via: {via}",
        f"From: {from_hdr}",
        f"To: {to_hdr}",
        f"Call-ID: {call_id}",
        f"CSeq: {cseq}",
        f"Contact: {contact}",
        "Content-Length: 0",
        ""
    ]

    response = CRLF.join(resp)
    return response + CRLF


# -----------------------------------------------------------
# 🚀 Classe principal do servidor
# -----------------------------------------------------------

class SIPServer:
    def __init__(self, host=LISTEN_HOST, port=LISTEN_PORT):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.host, self.port))
        print(f"📡 SIP UDP listener started on {self.host}:{self.port}")
        self.calls = {}

    def start(self):
        while True:
            data, addr = self.sock.recvfrom(65535)
            text = data.decode("utf-8", errors="ignore")
            print(f"\n--- Received from {addr} ---\n{text}\n--- end ---\n")
            threading.Thread(target=self.handle_message, args=(text, addr), daemon=True).start()

    def handle_message(self, text, addr):
        sip = parse_sip(text)
        start = sip["start"]

        if start.startswith("INVITE"):
            print("➡ INVITE detected")
            server_ip = self.get_external_ip()

            # ✅ Envia 100 Trying primeiro
            trying = build_100_trying(sip,server_ip)
            self.sock.sendto(trying.encode("utf-8"), addr)
            print(f"\n--- Enviando 100 Trying ---\n{trying}\n--- end ---\n")


            require = sip["headers"].get("Require","")
            ok = build_200_ok_siprec(sip, server_ip)
            print(f"\n--- Enviando resposta OPTIONS ---\n{ok}\n--- end ---\n")
            self.sock.sendto(ok.encode("utf-8"), addr)
            call_id = sip["headers"].get("Call-ID")
            self.calls[call_id] = {"invite": sip, "peer": addr, "answered": True}
            threading.Thread(target=self.wait_for_ack, args=(call_id,), daemon=True).start()

        elif start.startswith("ACK"):
            call_id = sip["headers"].get("Call-ID")
            print(f"➡ ACK received for Call-ID {call_id}")
            if call_id in self.calls:
                self.calls[call_id]["ack"] = True
                threading.Thread(target=self.hangup_later, args=(call_id,10), daemon=True).start()

        elif start.startswith("BYE"):
            call_id = sip["headers"].get("Call-ID", "")
            cseq = sip["headers"].get("CSeq", "")
            via = sip["headers"].get("Via", "")
            from_hdr = sip["headers"].get("From", "")

            # O To deve ser o mesmo que o To usado no 200 OK do INVITE
            # Pegamos do registro da chamada
            entry = self.calls.get(call_id, {})
            if entry and "to_tag" in entry:
                to_hdr = f"{entry['invite']['headers'].get('To', '')};tag={entry['to_tag']}"
            else:
                # fallback: se não tiver registro, usa o que veio
                to_hdr = sip["headers"].get("To", "")

            resp = [
                "SIP/2.0 200 OK",
                f"Via: {via}",
                f"From: {from_hdr}",
                f"To: {to_hdr}",
                f"Call-ID: {call_id}",
                f"CSeq: {cseq}",
                "Content-Length: 0",
                ""
            ]

            self.sock.sendto(CRLF.join(resp).encode("utf-8"), addr)
            print(f"➡ 200 OK for BYE sent (Call-ID {call_id})")





        elif start.startswith("OPTIONS"):
            print("➡ OPTIONS detected, sending 200 OK...")
            server_ip = self.get_external_ip()
            ok = build_200_ok_options(sip, server_ip)
            print(f"\n--- Enviando resposta OPTIONS ---\n{ok}\n--- end ---\n")
            self.sock.sendto(ok.encode("utf-8"), addr)

        else:
            print("◻ Mensagem SIP não tratada (apenas log).")

    def wait_for_ack(self, call_id, timeout=30):
        waited = 0
        while waited < timeout:
            if call_id in self.calls and self.calls[call_id].get("ack"):
                print(f"✅ ACK confirmado para {call_id}")
                return True
            time.sleep(0.5)
            waited += 0.5
        print(f"⚠️ Timeout aguardando ACK para {call_id}")
        return False

    def hangup_later(self, call_id, seconds=10):
        time.sleep(seconds)
        entry = self.calls.get(call_id)
        if not entry:
            return
        peer = entry["peer"]
        invite = entry["invite"]
        server_ip = self.get_external_ip()
        bye = build_bye(invite, server_ip)
        self.sock.sendto(bye.encode("utf-8"), peer)
        print(f"➡ Enviado BYE para {peer} (Call-ID {call_id})")

    def get_external_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


if __name__ == "__main__":
    server = SIPServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Encerrando servidor SIP.")
