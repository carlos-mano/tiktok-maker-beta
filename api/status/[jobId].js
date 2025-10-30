// api/status/[jobId].js - Consulta status do processamento
import redis from '../../lib/redis.js';

export default async function handler(req, res) {
  const { jobId } = req.query;

  try {
    const jobData = await redis.get(`job:${jobId}`);
    
    if (!jobData) {
      return res.status(404).json({ error: 'Job não encontrado' });
    }

    const job = JSON.parse(jobData);
    res.status(200).json(job);

  } catch (error) {
    console.error('❌ Erro ao buscar status:', error);
    res.status(500).json({ error: 'Erro interno do servidor' });
  }
}
