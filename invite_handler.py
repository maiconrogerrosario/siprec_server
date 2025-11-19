import threading
from sip_session import SipSession
from sip_responses import sip_response_100_trying, sip_response_200_ok_invite_siprec

class InviteHandler:

    @staticmethod
    def handle_invite(server, sip, addr):
        server_ip = server.get_external_ip()

        # Envia 100 Trying
        trying = sip_response_100_trying(sip, server_ip)
        server.sock.sendto(trying.encode(), addr)

        # Envia 200 OK SIPREC
        ok = sip_response_200_ok_invite_siprec(
            sip,
            server_ip,
            addr=addr
        )
        server.sock.sendto(ok.encode(), addr)

        # Cria sessão SIP (AGORA CORRETO)
        session = SipSession(server, sip, addr)

        # Armazena sessão no servidor
        call_id = session.call_id
        server.calls[call_id] = session

        print(f"📌 Sessão criada para Call-ID: {call_id}")

        # Espera ACK em thread
        threading.Thread(
            target=session.wait_for_ack,
            daemon=True
        ).start()
