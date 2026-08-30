const { randomUUID } = require('crypto');

const logger = require('../utils/logger');

/**
 * Loga método, rota, status e duração de cada request, com um id de correlação
 * que também aparece nos logs de erro.
 */
function requestLogger(req, res, next) {
    req.id = randomUUID();
    const startedAt = process.hrtime.bigint();

    res.on('finish', () => {
        const durationMs = Number(process.hrtime.bigint() - startedAt) / 1e6;
        logger.info('request', {
            requestId: req.id,
            method: req.method,
            path: req.originalUrl,
            status: res.statusCode,
            durationMs: Number(durationMs.toFixed(2)),
        });
    });

    next();
}

module.exports = requestLogger;
