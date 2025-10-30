from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
import uuid
import json
from datetime import datetime
import threading

app = Flask(__name__)
CORS(app)

# Armazenamento em memória (simples)
videos_processados = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'online', 'message': 'API TikTok Maker REAL'})

@app.route('/api/process-video', methods=['POST'])
def process_video():
    try:
        data = request.json
        video_url = data.get('video_url', '')
        email = data.get('email', '')
        
        if not video_url:
            return jsonify({'error': 'URL do YouTube é obrigatória'}), 400
        
        # Gerar ID único
        video_id = str(uuid.uuid4())
        
        # Iniciar processamento em thread separada
        thread = threading.Thread(
            target=processar_video_background,
            args=(video_url, video_id, email)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'processando',
            'video_id': video_id,
            'message': 'Vídeo está sendo processado... Isso pode levar alguns minutos.',
            'estimated_time': '8-10 minutos'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/status/<video_id>', methods=['GET'])
def check_status(video_id):
    if video_id in videos_processados:
        return jsonify(videos_processados[video_id])
    else:
        return jsonify({'error': 'Vídeo não encontrado'}), 404

@app.route('/api/download/<video_id>', methods=['GET'])
def download_video(video_id):
    if video_id in videos_processados:
        video_info = videos_processados[video_id]
        if video_info['status'] == 'pronto':
            # Aqui retornaria o arquivo real
            return jsonify({
                'status': 'pronto',
                'download_url': f'/api/real-file/{video_id}',
                'message': 'Download disponível'
            })
    return jsonify({'error': 'Vídeo não disponível'}), 404

def processar_video_background(video_url, video_id, email):
    """Processa o vídeo em background - VERSÃO SIMPLIFICADA DO COLAB"""
    try:
        videos_processados[video_id] = {
            'status': 'baixando',
            'progresso': 'Iniciando download...',
            'video_id': video_id
        }
        
        # PASSO 1: Baixar vídeo
        videos_processados[video_id]['progresso'] = 'Baixando vídeo do YouTube...'
        video_file = f"/tmp/{video_id}.mp4"
        
        cmd_download = [
            'yt-dlp',
            '-f', 'best[height<=720]',
            '-o', video_file,
            video_url
        ]
        
        result = subprocess.run(cmd_download, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            videos_processados[video_id] = {
                'status': 'erro',
                'error': 'Erro ao baixar vídeo'
            }
            return
        
        # PASSO 2: Processar vídeo (versão simplificada)
        videos_processados[video_id]['progresso'] = 'Processando vídeo...'
        output_file = f"/tmp/{video_id}_final.mp4"
        
        cmd_process = [
            'ffmpeg',
            '-i', video_file,
            '-t', '60',  # 60 segundos
            '-vf', 'scale=608:1080:force_original_aspect_ratio=decrease,pad=608:1080:(ow-iw)/2:(oh-ih)/2:black',
            '-c:a', 'copy',
            '-y',
            output_file
        ]
        
        result = subprocess.run(cmd_process, capture_output=True, text=True, timeout=300)
        if result.returncode != 0:
            videos_processados[video_id] = {
                'status': 'erro', 
                'error': 'Erro ao processar vídeo'
            }
            return
        
        # PASSO 3: Verificar se arquivo foi criado
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file) / (1024 * 1024)
            
            videos_processados[video_id] = {
                'status': 'pronto',
                'video_id': video_id,
                'tamanho': f'{file_size:.1f}MB',
                'duracao': '60 segundos',
                'formato': 'Vertical 9:16',
                'download_url': f'/api/download/{video_id}',
                'message': 'Vídeo processado com sucesso!'
            }
        else:
            videos_processados[video_id] = {
                'status': 'erro',
                'error': 'Arquivo final não criado'
            }
            
    except subprocess.TimeoutExpired:
        videos_processados[video_id] = {
            'status': 'erro',
            'error': 'Tempo esgotado no processamento'
        }
    except Exception as e:
        videos_processados[video_id] = {
            'status': 'erro',
            'error': f'Erro inesperado: {str(e)}'
        }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
