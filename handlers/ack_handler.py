# handlers/ack_handler.py

def handle_ack(server, sip, addr):
    """
    Processa ACK recebido do SIPp após envio do 200 OK (INVITE).
    """

    call_id = sip["headers"].get("Call-ID")

    # 1) ACK sem Call-ID → lixo de rede
    if not call_id:
        print("⚠ ACK sem Call-ID — ignorado.")
        return

    # 2) Localiza sessão criada no INVITE handler
    session = server.calls.get(call_id)
    if not session:
        print(f"⚠ ACK recebido, mas sessão {call_id} não existe.")
        return

    # 3) Atualiza estado interno da sessão
    session.receive_ack()

    # 4) Log bonitinho
    print(f"✔ ACK recebido e confirmado para Call-ID {call_id}")
