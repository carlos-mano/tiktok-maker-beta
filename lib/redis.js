// lib/redis.js - Conexão com Redis
import Redis from 'ioredis';

const redis = new Redis(
  'rediss://default:AXlsAAIncDIyYzU2ZjFiMGViZTk0Y2MxOTRiYmYzMjM1OGI1MTNkNnAyMzEwODQ@wealthy-jay-31084.upstash.io:6379'
);

export default redis;
