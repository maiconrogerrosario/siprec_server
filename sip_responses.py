#!/usr/bin/env python3
"""
sip_responses.py

Funções profissionais para montar respostas SIP para SIPREC UAS.
Padrão:
- sip_response_XXX()  → respostas SIP enviadas pelo servidor
"""

import time
from sip_parser import CRLF, reorder_via_params , parse_multipart, parse_sdp
import random


def make_tag():
    return str(random.randint(10000, 99999))


# ============================================================
# 100 TRYING (resposta ao INVITE)
# ============================================================
def sip_response_100_trying(sip, server_ip):
    """
    Gera SIP/2.0 100 Trying (UAS responding to INVITE).
    """
    hdr = sip["headers"]
    via = hdr.get("Via", "")
    from_hdr = hdr.get("From", "")
    to_hdr = hdr.get("To", "")
    call_id = hdr.get("Call-ID", "")
    cseq = hdr.get("CSeq", "")

    # Ajuste do rport
    if "rport" in via:
        via = via.replace("rport", f"rport=5060;received={server_ip}")

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


# ============================================================
# 200 OK (SIPREC / resposta ao INVITE)
# ============================================================
def sip_response_200_ok_invite_siprec(invite, server_ip, addr=None,
                                      media_port1=10000, media_port2=10002):
    """
    Gera SIP/2.0 200 OK para INVITE SIPREC.
    Inclui SDP SIPREC (dual stream).
    """
    hdr = invite["headers"]
    via = hdr.get("Via", "")
    from_hdr = hdr.get("From", "")
    to_hdr = hdr.get("To", "")
    call_id = hdr.get("Call-ID", "")
    cseq = hdr.get("CSeq", "")
    contact = f"<sip:{server_ip}:5060>;sip.srs"

    # 🧩 rport/received
    if "rport" in via:
        ip, port = addr if addr else ("127.0.0.1", 5060)
        via = via.replace("rport", f"rport={port};received={ip}")

    via = reorder_via_params(via)

    # SDP recebido (para extrair labels)
    parts = parse_multipart(invite["body"], hdr.get("Content-Type", ""))
    raw_sdp = parts.get("application/sdp", "")
    sdp_info = parse_sdp(raw_sdp)

    session_block = [
        "v=0",
        f"o=- 0 0 IN IP4 {server_ip}",
        "s=SIPREC Server",
        f"c=IN IP4 {server_ip}",
        "t=0 0",
    ]
    sdp1 = [
        f"m=audio {media_port1} RTP/AVP 0 8",
        "a=rtpmap:0 PCMU/8000",
        "a=rtpmap:8 PCMA/8000",
        f"a=label:{sdp_info['media'][0]['label']}",
        "a=recvonly",
    ]
    sdp2 = [
        f"m=audio {media_port2} RTP/AVP 0 8",
        "a=rtpmap:0 PCMU/8000",
        "a=rtpmap:8 PCMA/8000",
        f"a=label:{sdp_info['media'][1]['label']}",
        "a=recvonly",
    ]

    body = CRLF.join(session_block + sdp1 + sdp2)

    resp = [
        "SIP/2.0 200 OK",
        f"Via: {via}",
        f"From: {from_hdr}",
        f"To: {to_hdr};tag={make_tag()}",
        f"Call-ID: {call_id}",
        f"CSeq: {cseq}",
        "Supported: siprec,timer",
        f"Contact: {contact}",
        "Session-Expires: 1800;refresher=uas",
        "Content-Type: application/sdp",
        f"Content-Length: {len(body.encode())}",
        "",
        body
    ]

    return CRLF.join(resp) + CRLF


# ============================================================
# 200 OK (resposta ao OPTIONS)
# ============================================================
def sip_response_200_ok_options(options, server_ip, addr=None):
    """
    Gera SIP/2.0 200 OK em resposta a OPTIONS.
    """
    hdr = options["headers"]
    via = hdr.get("Via", "")
    from_hdr = hdr.get("From", "")
    to_hdr = hdr.get("To", "")
    call_id = hdr.get("Call-ID", "")
    cseq = hdr.get("CSeq", "")

    if "rport" in via:
        ip, port = addr if addr else ("127.0.0.1", 5060)
        via = via.replace("rport", f"rport={port};received={ip}")

    via = reorder_via_params(via)

    resp = [
        "SIP/2.0 200 OK",
        f"Via: {via}",
        f"From: {from_hdr}",
        f"To: {to_hdr};tag={make_tag()}",
        f"Call-ID: {call_id}",
        f"CSeq: {cseq}",
        f"Contact: <sip:{server_ip}>",
        "Allow: INVITE, ACK, CANCEL, OPTIONS, BYE, REFER, NOTIFY, MESSAGE, SUBSCRIBE, INFO",
        "Accept: application/sdp",
        "Accept-Encoding: gzip",
        "Accept-Language: en, pt-BR",
        "Supported: replaces, timer, 100rel, norefersub",
        "Server: Python-SIP-Responder/1.0",
        "Content-Length: 0",
        ""
    ]

    return CRLF.join(resp) + CRLF


# ============================================================
# 200 OK (resposta ao BYE)
# ============================================================
def sip_response_200_ok_bye(sip):
    """
    Gera SIP/2.0 200 OK para BYE recebido (encerra diálogo).
    RFC 3261: Resposta minimalista.
    """
    hdr = sip["headers"]

    via = reorder_via_params(hdr.get("Via", ""))
    from_hdr = hdr.get("From", "")
    to_hdr = hdr.get("To", "")
    call_id = hdr.get("Call-ID", "")
    cseq = hdr.get("CSeq", "")

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

    return CRLF.join(resp) + CRLF
