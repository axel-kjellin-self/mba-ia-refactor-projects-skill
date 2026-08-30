/** Acesso a dados da entidade `payments`. */
class PaymentRepository {
    constructor(db) {
        this.db = db;
    }

    async create({ enrollmentId, amount, status }, executor = this.db) {
        const { lastID } = await executor.run(
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status]
        );
        return lastID;
    }

    findByEnrollmentId(enrollmentId, executor = this.db) {
        return executor.get('SELECT * FROM payments WHERE enrollment_id = ?', [enrollmentId]);
    }
}

module.exports = PaymentRepository;
