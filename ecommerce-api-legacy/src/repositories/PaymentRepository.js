const database = require('../config/database');
const Payment = require('../models/Payment');

/**
 * Payment Repository
 * Handles database operations for payments
 */
class PaymentRepository {
    /**
     * Find payment by ID
     * @param {number} paymentId
     * @returns {Promise<Payment|null>}
     */
    async findById(paymentId) {
        const row = await database.get('SELECT * FROM payments WHERE id = ?', [paymentId]);
        return row ? new Payment(row) : null;
    }

    /**
     * Find payment by enrollment ID
     * @param {number} enrollmentId
     * @returns {Promise<Payment|null>}
     */
    async findByEnrollmentId(enrollmentId) {
        const row = await database.get(
            'SELECT * FROM payments WHERE enrollment_id = ?',
            [enrollmentId]
        );
        return row ? new Payment(row) : null;
    }

    /**
     * Create a new payment
     * @param {Object} paymentData - { enrollment_id, amount, status }
     * @returns {Promise<Payment>}
     */
    async create(paymentData) {
        const result = await database.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [paymentData.enrollment_id, paymentData.amount, paymentData.status]
        );

        return this.findById(result.lastID);
    }

    /**
     * Find all payments for a user
     * @param {number} userId
     * @returns {Promise<Payment[]>}
     */
    async findByUserId(userId) {
        const query = `
            SELECT p.*
            FROM payments p
            JOIN enrollments e ON p.enrollment_id = e.id
            WHERE e.user_id = ?
        `;

        const rows = await database.all(query, [userId]);
        return rows.map(row => new Payment(row));
    }
}

module.exports = new PaymentRepository();
