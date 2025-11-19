# handlers/bye_handler.py

from sip_responses import sip_response_200_ok_bye

def handle_bye(server, sip, addr):
    msg = sip_response_200_ok_bye(sip)
    server.sock.sendto(msg.encode(), addr)

    call_id = sip["headers"].get("Call-ID")
    if call_id in server.calls:
        del server.calls[call_id]

    print("➡ BYE recebido e sessão removida")
