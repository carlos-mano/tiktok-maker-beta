from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import time
import random
import subprocess
import uuid
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Permite frontend se conectar

# Usuários autorizados para o beta
AUTHORIZED_USERS = [
    'amigo1@gmail.com',
    'amigo2@gmail.com', 
    'amigo3@gmail.com'
]

# ==================== PROCESSAMENTO REAL DE VÍDEO ====================
def processar_video_real(url, email):
    """Processa vídeos do YouTube DE VERDADE - versão simplificada"""
    
    try:
        # Gera um ID único para o vídeo
        video_id = f"video_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        print(f"🎬 Iniciando processamento para {email}")
        print(f"📹 URL: {url}")
        
        # Cria pasta temporária (no Vercel é /tmp)
        temp_dir = "/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Nome dos arquivos
        video_file = os.path.join(temp_dir, f"{video_id}_original.mp4")
        output_file = os.path.join(temp_dir, f"{video_id}_final.mp4")
        
        # PASSO 1: Baixar vídeo do YouTube (versão simplificada)
        print("📥 Baixando vídeo do YouTube...")
        
        # Comando para baixar (versão básica)
        cmd_download = [
            'yt-dlp',
            '-f', 'best[height<=720]',  # Qualidade limitada para ser mais rápido
            '-o', video_file,
            url
        ]
        
        try:
            result = subprocess.run(cmd_download, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                return {
                    'status': 'erro',
                    'video_id': video_id,
                    'mensagem': 'Erro ao baixar vídeo do YouTube',
                    'debug': result.stderr[:200]  # Mostra só os primeiros 200 caracteres do erro
                }
        except subprocess.TimeoutExpired:
            return {
                'status': 'erro', 
                'video_id': video_id,
                'mensagem': 'Tempo esgotado ao baixar vídeo (2 minutos)'
            }
        
        # Verifica se o arquivo foi baixado
        if not os.path.exists(video_file):
            return {
                'status': 'erro',
                'video_id': video_id,
                'mensagem': 'Vídeo não foi baixado corretamente'
            }
        
        # PASSO 2: Processar vídeo (versão ultra-simplificada)
        print("🎪 Processando vídeo...")
        
        # Comando básico de processamento - vertical 9:16
        cmd_process = [
            'ffmpeg',
            '-i', video_file,
            '-t', '60',  # Limita para 60 segundos
            '-vf', 'scale=608:1080:force_original_aspect_ratio=decrease,pad=608:1080:(ow-iw)/2:(oh-ih)/2:black',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-y',  # Sobrescrever se existir
            output_file
        ]
        
        try:
            result = subprocess.run(cmd_process, capture_output=True, text=True, timeout=180)
            if result.returncode != 0:
                return {
                    'status': 'erro',
                    'video_id': video_id, 
                    'mensagem': 'Erro ao processar vídeo',
                    'debug': result.stderr[:200]
                }
        except subprocess.TimeoutExpired:
            return {
                'status': 'erro',
                'video_id': video_id,
                'mensagem': 'Tempo esgotado ao processar vídeo (3 minutos)'
            }
        
        # Verifica se o arquivo foi criado
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)  # Tamanho em MB
            
            return {
                'status': 'sucesso',
                'video_id': video_id,
                'url_download': f'/api/download/{video_id}',
                'mensagem': f'✅ TikTok criado com sucesso! Tamanho: {file_size:.1f}MB',
                'tamanho_arquivo': f'{file_size:.1f}MB',
                'duracao': '60 segundos',
                'formato': 'Vertical 9:16'
            }
        else:
            return {
                'status': 'erro',
                'video_id': video_id,
                'mensagem': 'Arquivo final não foi criado'
            }
            
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return {
            'status': 'erro',
            'video_id': video_id if 'video_id' in locals() else 'unknown',
            'mensagem': f'Erro inesperado: {str(e)}'
        }

# Rota de saúde da API
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'online', 'message': 'API TikTok Maker funcionando!'})

# Rota para verificar se usuário está autorizado
@app.route('/api/check-auth', methods=['POST'])
def check_auth():
    data = request.json
    email = data.get('email', '').lower().strip()
    
    if email in AUTHORIZED_USERS:
        return jsonify({'authorized': True, 'message': 'Usuário autorizado'})
    else:
        return jsonify({'authorized': False, 'message': 'Acesso não autorizado'}), 401

# Rota principal para processar vídeos
@app.route('/api/process-video', methods=['POST'])
def process_video():
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        video_url = data.get('video_url', '').strip()
        observacoes = data.get('observations', '')
        
        # Verifica se usuário está autorizado
        if email not in AUTHORIZED_USERS:
            return jsonify({'error': 'Acesso não autorizado'}), 401
        
        # Valida URL do YouTube
        if not video_url or 'youtube.com' not in video_url and 'youtu.be' not in video_url:
            return jsonify({'error': 'URL do YouTube inválida'}), 400
        
        print(f"📥 Processando vídeo para {email}: {video_url}")
        
        # Processamento REAL do vídeo
        resultado = processar_video_real(video_url, email)
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"❌ Erro no processamento: {str(e)}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

# Rota para listar vídeos processados (futuramente)
@app.route('/api/videos/<email>', methods=['GET'])
def listar_videos(email):
    if email not in AUTHORIZED_USERS:
        return jsonify({'error': 'Acesso não autorizado'}), 401
    
    # Por enquanto retorna lista vazia (depois puxa do banco)
    return jsonify({'videos': [], 'message': 'Em breve: histórico de vídeos'})

# Rota para download (simulada por enquanto)
@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    return jsonify({
        'status': 'em_desenvolvimento',
        'message': 'Download em desenvolvimento',
        'video_id': video_id
    })

# Rota para servir o frontend
@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
