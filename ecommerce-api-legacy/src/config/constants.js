/**
 * Constantes de domínio. Centralizadas para eliminar magic numbers/strings
 * espalhados pelo código.
 */

const PaymentStatus = Object.freeze({
    PAID: 'PAID',
    DENIED: 'DENIED',
});

const Roles = Object.freeze({
    ADMIN: 'admin',
    USER: 'user',
});

const ValidationRules = Object.freeze({
    MIN_PASSWORD_LENGTH: 12,
    MAX_NAME_LENGTH: 100,
    MIN_CARD_DIGITS: 13,
    MAX_CARD_DIGITS: 19,
});

const Security = Object.freeze({
    BCRYPT_SALT_ROUNDS: 12,
    JWT_ALGORITHM: 'HS256',
    MIN_JWT_SECRET_LENGTH: 32,
});

module.exports = { PaymentStatus, Roles, ValidationRules, Security };
