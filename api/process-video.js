// api/process-video.js - Recebe URLs para processar
import redis from '../lib/redis.js';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Método não permitido' });
  }

  try {
    const { videoUrl, email } = req.body;
    
    // Gera ID único para o job
    const jobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Cria job no Redis
    const jobData = {
      id: jobId,
      videoUrl,
      email,
      status: 'pending',
      createdAt: new Date().toISOString(),
      progress: 0
    };

    await redis.set(`job:${jobId}`, JSON.stringify(jobData));
    await redis.lpush('video_queue', jobId);

    console.log(`🎬 Novo job criado: ${jobId}`);

    res.status(202).json({
      jobId,
      status: 'processing',
      message: 'Vídeo em processamento. Aguarde...'
    });

  } catch (error) {
    console.error('❌ Erro na API:', error);
    res.status(500).json({ error: 'Erro interno do servidor' });
  }
}
