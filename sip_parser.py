#!/usr/bin/env python3
"""
sip_parser.py

Módulo profissional de parsing SIP, Multipart SIPREC e SDP.
Suporta:
- SIP messages (start-line + headers + body)
- Via params reordering
- Multipart/mixed SIPREC (SDP + XML)
- SDP com múltiplas mídias (SIPREC dual stream)

Autor: Maicon Roger
"""

import re

CRLF = "\r\n"


# ============================================================
# 1) PARSER SIP BÁSICO
# ============================================================
def parse_sip_message(raw: str):
    """
    Faz parsing básico de uma mensagem SIP.
    Retorna:
    {
        "start_line": "INVITE ...",
        "headers": { "To": "...", "From": "...", ... },
        "body": "..."
    }
    """
    header_sep = CRLF + CRLF

    if header_sep in raw:
        head, body = raw.split(header_sep, 1)
    else:
        head, body = raw, ""

    lines = head.split(CRLF)
    start_line = lines[0]
    headers = {}

    for line in lines[1:]:
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        # Se header se repete, vira lista
        if key in headers:
            if not isinstance(headers[key], list):
                headers[key] = [headers[key]]
            headers[key].append(value)
        else:
            headers[key] = value

    return {
        "start_line": start_line,
        "headers": headers,
        "body": body,
    }


# ============================================================
# 2) REORDER VIA PARAMETERS
# ============================================================
def reorder_via_params(via_line: str) -> str:
    """
    Reordena parâmetros do cabeçalho Via para manter:
    rport ; received ; branch
    Exemplo:
      Via: SIP/2.0/UDP 1.1.1.1;branch=abc;rport;received=1.1.1.2
    """
    try:
        base, params_raw = via_line.split(";", 1)
    except ValueError:
        return via_line

    params = params_raw.split(";")
    parsed = {}
    others = []

    for p in params:
        if "=" in p:
            k, v = p.split("=", 1)
            parsed[k.strip()] = v.strip()
        else:
            others.append(p.strip())

    order = ["rport", "received", "branch"]

    reordered = []

    # coloca na ordem desejada
    for key in order:
        if key in parsed:
            reordered.append(f"{key}={parsed[key]}")

    # coloca os restantes
    for p in params:
        key = p.split("=")[0].strip() if "=" in p else p.strip()
        if key not in order:
            reordered.append(p.strip())

    return f"{base};" + ";".join(reordered)


# ============================================================
# 3) PARSER MULTIPART SIPREC
# ============================================================
def parse_multipart(body: str, content_type: str):
    """
    Faz parsing de multipart/mixed SIPREC.
    Retorna:
    {
        "application/sdp": "...",
        "application/rs-metadata+xml": "..."
    }
    """

    # Extrai boundary
    m = re.search(r'boundary="?([^";]+)"?', content_type, re.IGNORECASE)
    if not m:
        raise ValueError("Boundary não encontrado no Content-Type")

    boundary = m.group(1)
    delim = "--" + boundary

    parts_raw = body.split(delim)
    parsed_parts = {}

    for part in parts_raw:
        part = part.strip()

        if not part or part == "--":
            continue

        headers_raw, _, part_body = part.partition(CRLF + CRLF)
        if not part_body:
            continue

        # parse dos headers internos do multipart
        headers = {}
        for line in headers_raw.split(CRLF):
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()

        ctype = headers.get("Content-Type", "").lower()

        if "application/sdp" in ctype:
            parsed_parts["application/sdp"] = part_body.strip()
        elif "application/rs-metadata+xml" in ctype:
            parsed_parts["application/rs-metadata+xml"] = part_body.strip()

    return parsed_parts


# ============================================================
# 4) PARSER SDP COMPLETO (SUPORTA MÚLTIPLAS MÍDIAS)
# ============================================================
def parse_sdp(raw_sdp: str):
    """
    Parser SDP completo, multi-mídia (m=)
    Retorna:
    {
        "session": {...},
        "media": [ {...}, {...} ]
    }
    """
    lines = [l.strip() for l in raw_sdp.replace("\r", "").split("\n") if l.strip()]
    session = {"version": None, "origin": None, "session_name": None, "connection": None}
    medias = []
    current_media = None

    for line in lines:
        if "=" not in line:
            continue

        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip()

        # Sessão
        if k == "v":
            session["version"] = v
        elif k == "o":
            session["origin"] = v
        elif k == "s":
            session["session_name"] = v
        elif k == "c" and current_media is None:
            session["connection"] = v

        # Mídia
        elif k == "m":
            parts = v.split()
            current_media = {
                "type": parts[0],
                "port": int(parts[1]),
                "protocol": parts[2],
                "codecs": parts[3:],
                "connection": None,
                "attributes": {},
                "label": None
            }
            medias.append(current_media)

        # Connection dentro da mídia
        elif k == "c" and current_media:
            current_media["connection"] = v

        # Atributos
        elif k == "a" and current_media:
            if ":" in v:
                name, data = v.split(":", 1)
                name = name.strip()
                data = data.strip()

                if name == "rtpmap":
                    pt, codec = data.split(" ", 1)
                    current_media["attributes"].setdefault("rtpmap", {})[pt] = codec
                elif name == "fmtp":
                    pt, params = data.split(" ", 1)
                    current_media["attributes"].setdefault("fmtp", {})[pt] = params
                elif name == "label":
                    current_media["label"] = data
                else:
                    current_media["attributes"].setdefault(name, []).append(data)
            else:
                current_media["attributes"].setdefault("flags", []).append(v)

    return {
        "session": session,
        "media": medias
    }


# ============================================================
# 5) TESTE LOCAL
# ============================================================
if __name__ == "__main__":
    print("✔ Módulo sip_parser carregado corretamente.")
