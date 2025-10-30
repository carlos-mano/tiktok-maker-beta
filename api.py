from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import time
import random
import uuid
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  # Permite frontend se conectar

# ==================== PROCESSAMENTO SIMULADO MELHORADO ====================
def processar_video_real(url, email):
    """Versão SIMULADA que mostra o progresso real"""
    
    try:
        # Gera um ID único para o vídeo
        video_id = f"video_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
        
        print(f"🎬 Simulando processamento para {email}")
        print(f"📹 URL: {url}")
        
        # Simula as etapas do processamento REAL
        etapas = [
            "📥 Conectando com YouTube...",
            "🔍 Analisando vídeo...", 
            "🎬 Baixando conteúdo...",
            "✂️ Cortando trechos...",
            "📐 Convertendo para vertical...",
            "🎪 Adicionando legendas...",
            "✅ Finalizando TikTok..."
        ]
        
        # Simula tempo de processamento (mais realista)
        for etapa in etapas:
            print(etapa)
            time.sleep(2)  # 2 segundos por etapa
        
        # Gera dados realistas baseados na URL
        titulos_possiveis = [
            "🎯 Dica importante que aprendi!",
            "💡 Isso vai mudar sua perspectiva!",
            "🚀 O segredo que ninguém conta!",
            "📚 Aula rápida e prática!",
            "🔍 Revelando os detalhes!",
            "✨ Momento de insight!",
            "🎓 Aprenda isso agora!",
            "📖 Lição valiosa!"
        ]
        
        tamanho_mb = random.uniform(8.5, 15.2)
        
        return {
            'status': 'sucesso',
            'video_id': video_id,
            'url_download': f'/api/download/{video_id}',
            'mensagem': f'✅ TikTok criado com sucesso! 🎬',
            'tamanho_arquivo': f'{tamanho_mb:.1f}MB',
            'duracao': '60 segundos',
            'formato': 'Vertical 9:16',
            'titulo': random.choice(titulos_possiveis),
            'observacoes': 'Este é um processamento SIMULADO. Em breve versão real!'
        }
            
    except Exception as e:
        print(f"❌ Erro na simulação: {str(e)}")
        return {
            'status': 'erro',
            'video_id': video_id if 'video_id' in locals() else 'unknown',
            'mensagem': f'Erro na simulação: {str(e)}'
        }

# Rota de saúde da API
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'online', 'message': 'API TikTok Maker funcionando!'})

# Rota para verificar se usuário está autorizado - ACEITA TODOS!
@app.route('/api/check-auth', methods=['POST'])
def check_auth():
    data = request.json
    email = data.get('email', '').lower().strip()
    
    # ACEITA QUALQUER EMAIL VÁLIDO!
    if email and '@' in email:
        return jsonify({'authorized': True, 'message': 'Usuário autorizado'})
    else:
        return jsonify({'authorized': False, 'message': 'Email inválido'}), 401

# Rota principal para processar vídeos
@app.route('/api/process-video', methods=['POST'])
def process_video():
    try:
        data = request.json
        email = data.get('email', '').lower().strip()
        video_url = data.get('video_url', '').strip()
        observacoes = data.get('observations', '')
        
        # VERIFICAÇÃO SIMPLIFICADA - ACEITA QUALQUER EMAIL VÁLIDO
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 401
        
        # Valida URL do YouTube
        if not video_url or ('youtube.com' not in video_url and 'youtu.be' not in video_url):
            return jsonify({'error': 'URL do YouTube inválida'}), 400
        
        print(f"📥 Processando vídeo para {email}: {video_url}")
        
        # Processamento SIMULADO (por enquanto)
        resultado = processar_video_real(video_url, email)
        
        return jsonify(resultado)
        
    except Exception as e:
        print(f"❌ Erro no processamento: {str(e)}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

# Rota para listar vídeos processados
@app.route('/api/videos/<email>', methods=['GET'])
def listar_videos(email):
    # Aceita qualquer email válido
    if not email or '@' not in email:
        return jsonify({'error': 'Email inválido'}), 401
    
    # Lista de vídeos simulados
    videos_simulados = [
        {
            'id': 'video_123456',
            'titulo': '🎯 Meu primeiro TikTok!',
            'data': '2024-12-01',
            'status': 'concluido'
        }
    ]
    
    return jsonify({'videos': videos_simulados, 'message': 'Histórico de vídeos'})

# Rota para download (simulada)
@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    return jsonify({
        'status': 'simulado',
        'message': 'Download simulado - em breve versão real!',
        'video_id': video_id,
        'url': '#'
    })

# Rota para servir o frontend
@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
