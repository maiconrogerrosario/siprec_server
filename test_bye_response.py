#!/usr/bin/env python3
"""
Arquivo de testes para validar todas as respostas SIP no sip_responses.py.
Inclui parsing das mensagens brutas e impressão das respostas.
"""

# ============================================================
# IMPORTS
# ============================================================

from sip_parser import (
    parse_sip_message,
    CRLF
)

from sip_responses import (
    sip_response_200_ok_invite_siprec,
    sip_response_200_ok_options,
    sip_response_200_ok_bye
)


# ============================================================
# MOCK SIPREC INVITE REAL (Cisco SBC)
# ============================================================

sip_invite_raw_cisco = (
    "INVITE sip:AAAA@10.0.0.10:5060 SIP/2.0\r\n"
    "Via: SIP/2.0/UDP y.y.y.y:5060;branch=z9hG4bK11BD2CA;rport\r\n"
    "From: <sip:y.y.y.y>;tag=F75AD7F-2065\r\n"
    "To: <sip:AAAA@10.0.0.10>\r\n"
    "Date: Mon, 13 May 2019 15:32:45 GMT\r\n"
    "Call-ID: 3089C795-74CB11E9-961DA422-D6FC9BE1@y.y.y.y\r\n"
    "Supported: 100rel,timer,resource-priority,replaces,sdp-anat\r\n"
    "Require: siprec\r\n"
    "Min-SE: 1800\r\n"
    "Cisco-Guid: 0802710458-1959465449-2686421522-1015028268\r\n"
    "User-Agent: Cisco-SIPGateway/IOS-16.10.2\r\n"
    "Allow: INVITE, OPTIONS, BYE, CANCEL, ACK, PRACK, UPDATE, REFER, SUBSCRIBE, NOTIFY, INFO, REGISTER\r\n"
    "CSeq: 101 INVITE\r\n"
    "Max-Forwards: 70\r\n"
    "Timestamp: 1557761565\r\n"
    "Contact: <sip:y.y.y.y:5060>;+sip.src\r\n"
    "Expires: 180\r\n"
    "Allow-Events: telephone-event\r\n"
    "Session-ID: a62dd6d8be0059c38d142bae9b46880b;remote=00000000000000000000000000000000\r\n"
    "Session-Expires: 1800\r\n"
    "Content-Type: multipart/mixed;boundary=uniqueBoundary\r\n"
    "Mime-Version: 1.0\r\n"
    "Content-Length: 2470\r\n"
    "\r\n"
    "--uniqueBoundary\r\n"
    "Content-Type: application/sdp\r\n"
    "Content-Disposition: session;handling=required\r\n"
    "\r\n"
    "v=0\r\n"
    "o=CiscoSystemsSIP-GW-UserAgent 5511 2889 IN IP4 y.y.y.y\r\n"
    "s=SIP Call\r\n"
    "c=IN IP4 y.y.y.y\r\n"
    "t=0 0\r\n"
    "m=audio 8086 RTP/AVP 0 101 19\r\n"
    "c=IN IP4 y.y.y.y\r\n"
    "a=rtpmap:0 PCMU/8000\r\n"
    "a=rtpmap:101 telephone-event/8000\r\n"
    "a=fmtp:101 0-16\r\n"
    "a=rtpmap:19 CN/8000\r\n"
    "a=ptime:20\r\n"
    "a=sendonly\r\n"
    "a=label:1\r\n"
    "\r\n"
    "m=audio 8088 RTP/AVP 0 101 19\r\n"
    "c=IN IP4 y.y.y.y\r\n"
    "a=rtpmap:0 PCMU/8000\r\n"
    "a=rtpmap:101 telephone-event/8000\r\n"
    "a=fmtp:101 0-16\r\n"
    "a=rtpmap:19 CN/8000\r\n"
    "a=ptime:20\r\n"
    "a=sendonly\r\n"
    "a=label:2\r\n"
    "\r\n"
    "--uniqueBoundary\r\n"
    "Content-Type: application/rs-metadata+xml\r\n"
    "Content-Disposition: recording-session\r\n"
    "\r\n"
    "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\r\n"
    "<recording xmlns=\"urn:ietf:params:xml:ns:recording:1\">\r\n"
    "  <datamode>complete</datamode>\r\n"
    "  <session session_id=\"MIgZ2nTLEemWFaQi1vyb4Q==\">\r\n"
    "    <sipSessionID>a0b9b2a1e4db51f082e777c0df9015e5;remote=6bea155500105000a0002c31246a214b</sipSessionID>\r\n"
    "    <start-time>2019-05-13T15:32:45.293Z</start-time>\r\n"
    "  </session>\r\n"
    "</recording>\r\n"
    "\r\n"
    "--uniqueBoundary--\r\n"
)


# ============================================================
# MOCK OPTIONS
# ============================================================

sip_options_mock = {
    "headers": {
        "Via": "SIP/2.0/UDP 10.0.0.5:5060;branch=z9hG4bKopt;rport",
        "From": "<sip:check@10.0.0.5>;tag=1234",
        "To": "<sip:siprec@10.0.0.100>",
        "Call-ID": "check999@10.0.0.5",
        "CSeq": "77 OPTIONS"
    }
}


# ============================================================
# MOCK BYE
# ============================================================

sip_bye_mock = {
    "headers": {
        "Via": "SIP/2.0/UDP 10.0.0.9:5060;branch=z9hG4bKbye;rport",
        "From": "<sip:user@10.0.0.9>;tag=777",
        "To": "<sip:siprec@10.0.0.100>;tag=999",
        "Call-ID": "callbye@10.0.0.9",
        "CSeq": "6 BYE"
    }
}


# ============================================================
# TESTE 200 OK SIPREC
# ============================================================

def test_200_ok_invite():
    print("\n===== TESTE: 200 OK INVITE SIPREC =====")

    sip_obj = parse_sip_message(sip_invite_raw_cisco)

    resp = sip_response_200_ok_invite_siprec(
        sip_obj,
        "10.0.0.100",
        addr=("y.y.y.y", 5060)
    )

    print(resp)
    print("===============================")


# ============================================================
# TESTE 200 OK OPTIONS
# ============================================================

def test_200_ok_options():
    print("\n===== TESTE: 200 OK OPTIONS =====")

    resp = sip_response_200_ok_options(
        sip_options_mock,
        "10.0.0.100",
        addr=("10.0.0.5", 5060)
    )

    print(resp)
    print("===============================")


# ============================================================
# TESTE 200 OK BYE
# ============================================================

def test_200_ok_bye():
    print("\n===== TESTE: 200 OK BYE =====")

    resp = sip_response_200_ok_bye(sip_bye_mock)

    print(resp)
    print("===============================")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    test_200_ok_invite()
    test_200_ok_options()
    test_200_ok_bye()
