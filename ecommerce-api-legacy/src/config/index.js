require('dotenv').config();

const { Security } = require('./constants');

/**
 * Configuração da aplicação, carregada exclusivamente de variáveis de ambiente.
 * Nenhum secret é hardcoded — ver `.env.example` para o contrato esperado.
 */
const config = {
    env: process.env.NODE_ENV || 'development',
    port: Number(process.env.PORT) || 3000,

    database: {
        file: process.env.DATABASE_FILE || ':memory:',
    },

    jwt: {
        secret: process.env.JWT_SECRET,
        expiresIn: process.env.JWT_EXPIRES_IN || '1h',
    },

    payment: {
        gatewayKey: process.env.PAYMENT_GATEWAY_KEY,
    },

    smtp: {
        user: process.env.SMTP_USER,
    },

    seed: {
        adminEmail: process.env.SEED_ADMIN_EMAIL,
        adminPassword: process.env.SEED_ADMIN_PASSWORD,
    },
};

config.isProduction = config.env === 'production';

/**
 * Falha rápido no boot se a configuração obrigatória estiver ausente ou fraca,
 * em vez de descobrir o problema no primeiro request.
 */
function validate() {
    const required = ['JWT_SECRET', 'PAYMENT_GATEWAY_KEY'];
    const missing = required.filter((key) => !process.env[key]);

    if (missing.length > 0) {
        throw new Error(
            `Variáveis de ambiente obrigatórias ausentes: ${missing.join(', ')}. ` +
            'Copie .env.example para .env e preencha os valores.'
        );
    }

    if (config.jwt.secret.length < Security.MIN_JWT_SECRET_LENGTH) {
        throw new Error(
            `JWT_SECRET deve ter no mínimo ${Security.MIN_JWT_SECRET_LENGTH} caracteres.`
        );
    }
}

module.exports = { config, validate };
