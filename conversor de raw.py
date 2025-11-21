# 🔹 Etapa 1: Upload do arquivo .raw
from google.colab import files
import os

print("📁 Faça upload do arquivo .raw (ex: audio.raw)")
uploaded = files.upload()

# Pega o nome do arquivo enviado
raw_file = list(uploaded.keys())[0]
print(f"✅ Arquivo recebido: {raw_file}")

# 🔹 Etapa 2: Converter com FFmpeg (μ-law → PCM16/WAV)
wav_file = os.path.splitext(raw_file)[0] + ".wav"

# Se o RAW veio do Asterisk como μ-law 8kHz mono:
!ffmpeg -f mulaw -ar 8000 -ac 1 -i "$raw_file" "$wav_file" -y

# 🔹 Etapa 3: Reproduzir no Colab (opcional)
from IPython.display import Audio
Audio(wav_file)

# 🔹 Etapa 4: Download do arquivo convertido
print("🎧 Conversão concluída! Baixe o arquivo WAV abaixo 👇")
files.download(wav_file)