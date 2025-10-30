from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import time

app = Flask(__name__)
CORS(app)

# URL da sua API REAL no Render
RENDER_API_URL = "https://tiktok-maker-beta.onrender.com/api"

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'online', 'message': 'Frontend funcionando!'})

@app.route('/api/check-auth', methods=['POST'])
def check_auth():
    data = request.json
    email = data.get('email', '').lower().strip()
    
    if email and '@' in email:
        return jsonify({'authorized': True, 'message': 'Usuário autorizado'})
    else:
        return jsonify({'authorized': False, 'message': 'Email inválido'}), 401

@app.route('/api/process-video', methods=['POST'])
def process_video():
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        video_url = data.get('video_url', '').strip()
        
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 401
        
        if not video_url or ('youtube.com' not in video_url and 'youtu.be' not in video_url):
            return jsonify({'error': 'URL do YouTube inválida'}), 400
        
        # 🔥 CHAMA A API REAL NO RENDER!
        response = requests.post(
            f"{RENDER_API_URL}/process-video",
            json={
                'video_url': video_url,
                'email': email
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'error': 'Serviço temporariamente indisponível',
                'details': 'API de processamento está iniciando...'
            }), 503
            
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'Tempo esgotado',
            'message': 'A API de processamento está iniciando. Tente novamente em 2 minutos.'
        }), 408
    except Exception as e:
        return jsonify({
            'error': 'Erro de conexão',
            'message': 'Não foi possível conectar com o serviço de processamento.'
        }), 500

@app.route('/api/status/<video_id>', methods=['GET'])
def check_status(video_id):
    try:
        # 🔥 CHAMA A API REAL NO RENDER!
        response = requests.get(f"{RENDER_API_URL}/status/{video_id}", timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Status não disponível'}), 404
            
    except Exception as e:
        return jsonify({'error': 'Erro ao verificar status'}), 500

@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    try:
        # 🔥 CHAMA A API REAL NO RENDER!
        response = requests.get(f"{RENDER_API_URL}/download/{video_id}", timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Download não disponível'}), 404
            
    except Exception as e:
        return jsonify({'error': 'Erro ao preparar download'}), 500

@app.route('/api/videos/<email>', methods=['GET'])
def listar_videos(email):
    # Por enquanto retorna vazio - depois integra com Render
    return jsonify({'videos': [], 'message': 'Em breve integrado com API real'})

@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
