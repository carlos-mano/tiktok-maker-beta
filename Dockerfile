FROM python:3.9-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar yt-dlp
RUN pip install yt-dlp

# Instalar dependências Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Criar diretório de trabalho
WORKDIR /app
COPY . .

# Baixar modelo do Whisper (base - menor)
RUN python -c "import whisper; whisper.load_model('base')"

# Expor porta
EXPOSE 10000

# Comando para rodar a aplicação
CMD ["python", "api.py"]
