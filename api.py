from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import requests
import time
import random
import uuid
from datetime import datetime, timedelta
import json
import base64
import threading

app = Flask(__name__)
CORS(app)  # Permite frontend se conectar

# Armazenamento com expiração automática
videos_processados = {}

# ==================== SISTEMA DE EXPIRAÇÃO AUTOMÁTICA ====================
def limpar_videos_expirados():
    """Remove vídeos com mais de 24 horas automaticamente"""
    agora = datetime.now()
    videos_para_remover = []
    
    for video_id, video_info in videos_processados.items():
        data_criacao = datetime.fromisoformat(video_info['data_criacao'])
        if agora - data_criacao > timedelta(hours=24):
            videos_para_remover.append(video_id)
    
    for video_id in videos_para_remover:
        del videos_processados[video_id]
        print(f"🗑️ Vídeo expirado removido: {video_id}")
    
    print(f"🧹 Limpeza concluída. {len(videos_para_remover)} vídeos removidos.")

def agendar_limpeza():
    """Agenda limpeza automática a cada hora"""
    while True:
        time.sleep(3600)  # Espera 1 hora
        limpar_videos_expirados()

# Inicia a limpeza automática em thread separada
threading.Thread(target=agendar_limpeza, daemon=True).start()

# ==================== SISTEMA DE DOWNLOAD ====================
def gerar_video_simulado():
    """Gera um vídeo simulado para download"""
    video_id = f"video_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}"
    
    # Salva o "vídeo" simulado com timestamp
    videos_processados[video_id] = {
        'id': video_id,
        'status': 'pronto',
        'titulo': '🎬 TikTok Criado!',
        'data_criacao': datetime.now().isoformat(),
        'data_expiracao': (datetime.now() + timedelta(hours=24)).isoformat(),
        'conteudo': "VIDEO_SIMULADO_PARA_TESTE",
        'tamanho': f"{random.uniform(5.2, 12.8):.1f}MB",
        'duracao': '60 segundos',
        'downloads': 0
    }
    
    return video_id

def verificar_expiracao(video_id):
    """Verifica se o vídeo já expirou"""
    if video_id not in videos_processados:
        return True
    
    video_info = videos_processados[video_id]
    data_expiracao = datetime.fromisoformat(video_info['data_expiracao'])
    
    if datetime.now() > data_expiracao:
        del videos_processados[video_id]
        return True
    
    return False

# ==================== PROCESSAMENTO SIMULADO MELHORADO ====================
def processar_video_real(url, email):
    """Versão SIMULADA que prepara para download com expiração"""
    
    try:
        # Gera um ID único para o vídeo
        video_id = gerar_video_simulado()
        
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
            "📤 Preparando download...",
            "⏰ Configurando expiração (24h)...",
            "✅ Vídeo pronto para baixar!"
        ]
        
        # Simula tempo de processamento
        for etapa in etapas:
            print(etapa)
            time.sleep(1.2)
        
        # Gera dados realistas
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
        
        # Atualiza o vídeo com mais informações
        videos_processados[video_id].update({
            'titulo': random.choice(titulos_possiveis),
            'url_original': url,
            'email_usuario': email
        })
        
        # Calcula tempo restante
        tempo_restante = "24 horas"
        
        return {
            'status': 'sucesso',
            'video_id': video_id,
            'url_download': f'/api/download/{video_id}',
            'mensagem': f'✅ TikTok criado com sucesso! 🎬',
            'tamanho_arquivo': videos_processados[video_id]['tamanho'],
            'duracao': '60 segundos',
            'formato': 'Vertical 9:16',
            'titulo': videos_processados[video_id]['titulo'],
            'expiracao': tempo_restante,
            'observacoes': f'⚠️ Download disponível por 24 horas apenas!'
        }
            
    except Exception as e:
        print(f"❌ Erro na simulação: {str(e)}")
        return {
            'status': 'erro',
            'video_id': video_id if 'video_id' in locals() else 'unknown',
            'mensagem': f'Erro na simulação: {str(e)}'
        }

# ==================== ROTAS DA API ====================
# Rota de saúde da API
@app.route('/api/health', methods=['GET'])
def health_check():
    # Limpa vídeos expirados a cada health check também
    limpar_videos_expirados()
    return jsonify({
        'status': 'online', 
        'message': 'API TikTok Maker funcionando!',
        'videos_ativos': len(videos_processados)
    })

# Rota para verificar se usuário está autorizado
@app.route('/api/check-auth', methods=['POST'])
def check_auth():
    data = request.json
    email = data.get('email', '').lower().strip()
    
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
        
        if not email or '@' not in email:
            return jsonify({'error': 'Email inválido'}), 401
        
        if not video_url or ('youtube.com' not in video_url and 'youtu.be' not in video_url):
            return jsonify({'error': 'URL do YouTube inválida'}), 400
        
        print(f"📥 Processando vídeo para {email}: {video_url}")
        
        resultado = processar_video_real(video_url, email)
        return jsonify(resultado)
        
    except Exception as e:
        print(f"❌ Erro no processamento: {str(e)}")
        return jsonify({'error': 'Erro interno no servidor'}), 500

# Rota para DOWNLOAD REAL do vídeo
@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    try:
        # Verifica se o vídeo expirou
        if verificar_expiracao(video_id):
            return jsonify({
                'error': 'Vídeo expirado',
                'message': 'Este vídeo expirou (24 horas). Processe um novo vídeo.'
            }), 410  # 410 Gone
        
        video_info = videos_processados[video_id]
        
        # Incrementa contador de downloads
        video_info['downloads'] = video_info.get('downloads', 0) + 1
        
        # Simula um arquivo de vídeo
        tempo_restante = datetime.fromisoformat(video_info['data_expiracao']) - datetime.now()
        horas_restantes = int(tempo_restante.total_seconds() // 3600)
        minutos_restantes = int((tempo_restante.total_seconds() % 3600) // 60)
        
        video_content = f"""
TikTok Maker - {video_info['titulo']}
ID: {video_id}
Criado em: {video_info['data_criacao']}
Tamanho: {video_info['tamanho']}
Duração: {video_info['duracao']}
Downloads: {video_info['downloads']}
⏰ EXPIRA EM: {horas_restantes}h {minutos_restantes}m

Este é um arquivo simulado.
Em breve: vídeos reais processados automaticamente!

tiktok-maker-beta.vercel.app
        """.strip()
        
        # Cria arquivo temporário
        temp_filename = f"/tmp/{video_id}.txt"
        with open(temp_filename, 'w', encoding='utf-8') as f:
            f.write(video_content)
        
        return send_file(
            temp_filename,
            as_attachment=True,
            download_name=f"tiktok_{video_id}.mp4",
            mimetype='video/mp4'
        )
        
    except Exception as e:
        print(f"❌ Erro no download: {str(e)}")
        return jsonify({'error': 'Erro ao fazer download'}), 500

# Rota para ver informações do vídeo
@app.route('/api/video-info/<video_id>', methods=['GET'])
def video_info(video_id):
    if verificar_expiracao(video_id):
        return jsonify({'error': 'Vídeo expirado'}), 410
    
    return jsonify(videos_processados[video_id])

# Rota para listar vídeos do usuário
@app.route('/api/videos/<email>', methods=['GET'])
def listar_videos(email):
    # Limpa expirados primeiro
    limpar_videos_expirados()
    
    # Filtra vídeos por email do usuário
    videos_usuario = [
        video for video in videos_processados.values() 
        if video.get('email_usuario') == email
    ]
    
    # Adiciona tempo restante para cada vídeo
    for video in videos_usuario:
        tempo_restante = datetime.fromisoformat(video['data_expiracao']) - datetime.now()
        horas = int(tempo_restante.total_seconds() // 3600)
        minutos = int((tempo_restante.total_seconds() % 3600) // 60)
        video['tempo_restante'] = f"{horas}h {minutos}m"
    
    return jsonify({
        'videos': videos_usuario,
        'total': len(videos_usuario),
        'message': f'Seus vídeos ativos ({len(videos_usuario)} disponíveis)'
    })

# Rota para status do sistema
@app.route('/api/status', methods=['GET'])
def system_status():
    limpar_videos_expirados()
    
    # Estatísticas
    total_videos = len(videos_processados)
    downloads_totais = sum(video.get('downloads', 0) for video in videos_processados.values())
    
    # Próximas expirações
    expiracoes_proximas = []
    for video_id, video_info in videos_processados.items():
        tempo_restante = datetime.fromisoformat(video_info['data_expiracao']) - datetime.now()
        if tempo_restante.total_seconds() < 3600:  # Menos de 1 hora
            expiracoes_proximas.append({
                'video_id': video_id,
                'expira_em': f"{int(tempo_restante.total_seconds() // 60)} minutos"
            })
    
    return jsonify({
        'status': 'online',
        'videos_ativos': total_videos,
        'downloads_totais': downloads_totais,
        'expiracoes_proximas': expiracoes_proximas,
        'proxima_limpeza': '1 hora'
    })

# Rota para servir o frontend
@app.route('/')
def serve_frontend():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
