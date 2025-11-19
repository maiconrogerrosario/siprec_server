#!/usr/bin/env python3
"""
utils.py

Funções utilitárias comuns usadas pelo servidor SIP.
"""

import random

def make_tag():
    """
    Gera um tag SIP aleatório usado em respostas (to-tag).
    """
    return str(random.randint(10000, 99999))
