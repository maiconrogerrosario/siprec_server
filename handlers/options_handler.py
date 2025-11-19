# handlers/options_handler.py

from sip_responses import sip_response_200_ok_options
from utils import make_tag

def handle_options(server, sip, addr):
    """
    Responde a requisições OPTIONS com 200 OK.
    """
    to_tag = make_tag()   # gera um tag válido

    msg = sip_response_200_ok_options(
        sip,
        server.get_external_ip(),
        to_tag=to_tag
    )

    server.sock.sendto(msg.encode(), addr)
    print(f"✔ Respondido OPTIONS 200 OK para {addr}")
