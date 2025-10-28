from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import time
import random

app = Flask(__name__)
CORS(app)  # Permite frontend se conectar

# Usuários autorizados para o beta
AUTHORIZED_USERS = [
    'amigo1@gmail.com',
    'amigo2@gmail.com', 
    'amigo3@gmail.com'
]

# Simula processamento de vídeo (depois substituímos pelo seu código real)
def simular_processamento_video(url, email):
    """Simula o processamento do vídeo - DEPOIS SUBSTITUÍMOS PELO SEU CÓDIGO REAL"""
    
    # Gera um ID único para o vídeo
    video_id = f"video_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Simula tempo de processamento (2-5 segundos)
    tempo_processamento = random.randint(2, 5)
    time.sleep(tempo_processamento)
    
    # Simula resultado (DEPOIS SERÁ O VÍDEO REAL)
    return {
        'status': 'sucesso',
        'video_id': video_id,
        'url_download': f'https://exemplo.com/download/{video_id}.mp4',
        'mensagem': 'Vídeo processado com sucesso! Em breve teremos processamento real.',
        'tempo_processamento': tempo_processamento
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
        
        # Simula processamento (DEPOIS SUBSTITUÍMOS PELO SEU CÓDIGO)
        resultado = simular_processamento_video(video_url, email)
        
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

# Rota para servir o frontend
@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
