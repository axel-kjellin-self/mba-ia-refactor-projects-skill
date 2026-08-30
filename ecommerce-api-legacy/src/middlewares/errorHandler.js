const { config } = require('../config');
const { AppError, NotFoundError } = require('../utils/errors');
const logger = require('../utils/logger');

/**
 * Tratamento de erro centralizado.
 *
 * No código legado cada callback tratava (ou ignorava) erros por conta própria:
 * o insert em `audit_logs` descartava o erro, o relatório nem verificava, e o
 * DELETE respondia 200 mesmo em falha.
 */

/** 404 para rotas não mapeadas. */
function notFoundHandler(req, res, next) {
    next(new NotFoundError(`Rota não encontrada: ${req.method} ${req.originalUrl}`));
}

/* eslint-disable-next-line no-unused-vars -- Express identifica o error handler pela aridade 4 */
function errorHandler(err, req, res, next) {
    const isOperational = err instanceof AppError;
    const statusCode = isOperational ? err.statusCode : 500;

    if (isOperational) {
        logger.warn(err.message, {
            code: err.code,
            statusCode,
            path: req.originalUrl,
            requestId: req.id,
        });
    } else {
        logger.error('Erro não tratado', {
            message: err.message,
            stack: err.stack,
            path: req.originalUrl,
            requestId: req.id,
        });
    }

    const body = {
        error: {
            code: isOperational ? err.code : 'INTERNAL_ERROR',
            // Detalhes de erros inesperados nunca vazam para o cliente.
            message: isOperational ? err.message : 'Erro interno do servidor',
        },
    };

    if (isOperational && err.details) body.error.details = err.details;
    if (!isOperational && !config.isProduction) body.error.debug = err.message;

    res.status(statusCode).json(body);
}

module.exports = { notFoundHandler, errorHandler };
