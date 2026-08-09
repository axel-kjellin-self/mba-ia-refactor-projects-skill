require('dotenv').config();

const config = {
    port: process.env.PORT || 3000,
    nodeEnv: process.env.NODE_ENV || 'development',

    // Database
    db: {
        user: process.env.DB_USER || 'admin_master',
        password: process.env.DB_PASSWORD
    },

    // Payment Gateway
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,

    // SMTP
    smtp: {
        user: process.env.SMTP_USER
    },

    // JWT
    jwt: {
        secret: process.env.JWT_SECRET,
        expiresIn: process.env.JWT_EXPIRES_IN || '24h'
    },

    // Validate required environment variables
    validate() {
        const required = ['JWT_SECRET', 'PAYMENT_GATEWAY_KEY'];
        const missing = required.filter(key => !process.env[key]);

        if (missing.length > 0) {
            throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
        }
    }
};

// Validate on load
config.validate();

module.exports = config;
