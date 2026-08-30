const { config } = require('../config');

/**
 * Logger estruturado (JSON) substituindo os `console.log` espalhados pelo código.
 *
 * Regra de ouro: NUNCA passe secrets, senhas ou dados de cartão para o logger.
 * Use `maskCard` para qualquer identificador de pagamento.
 */

const LEVELS = { error: 0, warn: 1, info: 2, debug: 3 };
const currentLevel = config.isProduction ? LEVELS.info : LEVELS.debug;

function emit(level, message, meta = {}) {
    if (LEVELS[level] > currentLevel) return;

    const entry = JSON.stringify({
        timestamp: new Date().toISOString(),
        level,
        message,
        ...meta,
    });

    if (level === 'error') process.stderr.write(`${entry}\n`);
    else process.stdout.write(`${entry}\n`);
}

/** Retorna apenas os 4 últimos dígitos — exigência de PCI-DSS 3.4. */
function maskCard(cardNumber) {
    if (typeof cardNumber !== 'string' || cardNumber.length < 4) return '****';
    return `**** **** **** ${cardNumber.slice(-4)}`;
}

module.exports = {
    error: (message, meta) => emit('error', message, meta),
    warn: (message, meta) => emit('warn', message, meta),
    info: (message, meta) => emit('info', message, meta),
    debug: (message, meta) => emit('debug', message, meta),
    maskCard,
};
