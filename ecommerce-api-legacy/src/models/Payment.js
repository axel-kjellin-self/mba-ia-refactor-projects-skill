const { PAYMENT_STATUS } = require('../config/constants');

/**
 * Payment Model
 * Represents a payment transaction
 */
class Payment {
    constructor(data) {
        this.id = data.id;
        this.enrollment_id = data.enrollment_id;
        this.amount = parseFloat(data.amount);
        this.status = data.status;
        this.created_at = data.created_at;
    }

    /**
     * Convert payment to JSON
     * @returns {Object}
     */
    toJSON() {
        return {
            id: this.id,
            enrollment_id: this.enrollment_id,
            amount: this.amount,
            status: this.status,
            created_at: this.created_at
        };
    }

    /**
     * Check if payment was successful
     * @returns {boolean}
     */
    isPaid() {
        return this.status === PAYMENT_STATUS.PAID;
    }

    /**
     * Check if payment was denied
     * @returns {boolean}
     */
    isDenied() {
        return this.status === PAYMENT_STATUS.DENIED;
    }
}

module.exports = Payment;
