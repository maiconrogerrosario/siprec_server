# Use imagem oficial do Python
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia o código do servidor para dentro do container
COPY sip_udp_answer.py /app/sip_udp_answer.py

# Exponha a porta SIP UDP (5060)
EXPOSE 5060/udp

# Comando de inicialização
CMD ["python3", "sip_udp_answer.py"]
