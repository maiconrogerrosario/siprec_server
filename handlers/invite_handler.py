# handlers/invite_handler.py

from sip_session import SipSession

def handle_invite(server, sip, addr):
    print("➡ INVITE recebido de", addr)

    session = SipSession(server, sip, addr)
    server.calls[session.call_id] = session

    session.send_trying()
    session.send_200_ok()
