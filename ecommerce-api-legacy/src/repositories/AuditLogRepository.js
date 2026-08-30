/** Acesso a dados da entidade `audit_logs`. */
class AuditLogRepository {
    constructor(db) {
        this.db = db;
    }

    async create({ action, actorId = null }, executor = this.db) {
        const { lastID } = await executor.run(
            'INSERT INTO audit_logs (action, actor_id) VALUES (?, ?)',
            [action, actorId]
        );
        return lastID;
    }
}

module.exports = AuditLogRepository;
