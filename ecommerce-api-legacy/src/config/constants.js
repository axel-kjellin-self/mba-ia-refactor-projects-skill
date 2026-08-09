/**
 * Application constants
 * Extract magic numbers and strings to named constants
 */

const CARD_PREFIXES = {
    VISA: '4',
    MASTERCARD: '5',
    AMEX: '3'
};

const PAYMENT_STATUS = {
    PAID: 'PAID',
    DENIED: 'DENIED',
    PENDING: 'PENDING'
};

const COURSE_STATUS = {
    ACTIVE: 1,
    INACTIVE: 0
};

const VALIDATION_RULES = {
    MIN_PASSWORD_LENGTH: 12,
    MAX_NAME_LENGTH: 100,
    MAX_TITLE_LENGTH: 200
};

module.exports = {
    CARD_PREFIXES,
    PAYMENT_STATUS,
    COURSE_STATUS,
    VALIDATION_RULES
};
