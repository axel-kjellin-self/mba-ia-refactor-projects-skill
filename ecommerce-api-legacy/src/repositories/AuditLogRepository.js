const database = require('../config/database');

/**
 * Audit Log Repository
 * Handles database operations for audit logs
 */
class AuditLogRepository {
    /**
     * Create an audit log entry
     * @param {string} action - Description of the action
     * @param {number|null} userId - ID of user who performed action
     * @returns {Promise<Object>}
     */
    async log(action, userId = null) {
        await database.run(
            'INSERT INTO audit_logs (action, user_id) VALUES (?, ?)',
            [action, userId]
        );

        return { action, userId, created_at: new Date() };
    }

    /**
     * Find all audit logs
     * @param {number} limit - Maximum number of logs to return
     * @returns {Promise<Array>}
     */
    async findAll(limit = 100) {
        return await database.all(
            'SELECT * FROM audit_logs ORDER BY created_at DESC LIMIT ?',
            [limit]
        );
    }

    /**
     * Find audit logs by user ID
     * @param {number} userId
     * @param {number} limit
     * @returns {Promise<Array>}
     */
    async findByUserId(userId, limit = 50) {
        return await database.all(
            'SELECT * FROM audit_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
            [userId, limit]
        );
    }
}

module.exports = new AuditLogRepository();
