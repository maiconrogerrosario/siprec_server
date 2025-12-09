import socket

import socket

def decode_rtp_packet(packet):
    """Decodifica um pacote RTP a partir de bytes"""
    header = {}

    # ----- BYTE 0 -----
    b0 = packet[0]
    header["version"]       = (b0 >> 6) & 0b11
    header["padding"]       = (b0 >> 5) & 0b1
    header["extension"]     = (b0 >> 4) & 0b1
    header["csrc_count"]    = b0 & 0b1111

    # ----- BYTE 1 -----
    b1 = packet[1]
    header["marker"]        = (b1 >> 7) & 0b1
    header["payload_type"]  = b1 & 0b01111111

    # ----- SEQUENCE NUMBER (2 bytes) -----
    header["sequence_number"] = int.from_bytes(packet[2:4], "big")

    # ----- TIMESTAMP (4 bytes) -----
    header["timestamp"] = int.from_bytes(packet[4:8], "big")

    # ----- SSRC (4 bytes) -----
    header["ssrc"] = int.from_bytes(packet[8:12], "big")

    # ----- PAYLOAD -----
    header["payload"] = packet[12:]  # bytes do áudio

    return header


# ===================== SERVIDOR RTP =======================
IP = "127.0.0.1"
PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

print(f"📡 Servidor UDP ouvindo em {IP}:{PORT}...")

while True:
    data, addr = sock.recvfrom(4096)

    print("\n==============================================")
    print(f"📩 Pacote recebido de {addr}")
    print(f"📦 Tamanho total: {len(data)} bytes")
    print(f"🔢 Primeiro 32 bytes (hex): {data[:32].hex()}")

    rtp = decode_rtp_packet(data)

    # ----- IMPRIME TODOS OS CAMPOS DO RTP -----
    print("\n🧩 **DECODE COMPLETO DO RTP**")
    print(f"• Version.............: {rtp['version']}")
    print(f"• Padding.............: {rtp['padding']}")
    print(f"• Extension...........: {rtp['extension']}")
    print(f"• CSRC Count..........: {rtp['csrc_count']}")
    print(f"• Marker..............: {rtp['marker']}")
    print(f"• Payload Type........: {rtp['payload_type']}")
    print(f"• Sequence Number.....: {rtp['sequence_number']}")
    print(f"• Timestamp...........: {rtp['timestamp']}")
    print(f"• SSRC................: {hex(rtp['ssrc'])} ({rtp['ssrc']})")
    print(f"• Payload bytes.......: {len(rtp['payload'])} bytes")
    print("==============================================\n")


IP = "127.0.0.1"
PORT = 10000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))

print(f"📡 Servidor UDP ouvindo em {IP}:{PORT}...")

while True:
    data, addr = sock.recvfrom(2048)
    print(f"\n📩 Pacote recebido de {addr}")
    print(f"📦 Tamanho: {len(data)} bytes")
    print(f"🔢 Hex: {data[:40].hex()}...")  # primeiros bytes

    packet = decode_rtp_packet(data.hex())
    audio = bytes.fromhex(packet['payload'])

    print(f"{packet['ssrc']}")
