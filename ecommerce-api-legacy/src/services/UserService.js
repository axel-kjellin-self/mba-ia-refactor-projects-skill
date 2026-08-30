const { NotFoundError } = require('../utils/errors');
const logger = require('../utils/logger');

/** Regras de negócio da entidade usuário. */
class UserService {
    constructor({ db, userRepository, auditLogRepository }) {
        this.db = db;
        this.userRepository = userRepository;
        this.auditLogRepository = auditLogRepository;
    }

    async getById(id) {
        const user = await this.userRepository.findById(id);
        if (!user) throw new NotFoundError('Usuário não encontrado');
        return user;
    }

    /**
     * Remove o usuário e, por `ON DELETE CASCADE`, suas matrículas e pagamentos.
     * O código legado deixava esses registros órfãos — o relatório financeiro
     * passava a exibir alunos `'Unknown'`.
     */
    async deleteById(id, actorId) {
        return this.db.transaction(async (tx) => {
            const user = await this.userRepository.findById(id, tx);
            if (!user) throw new NotFoundError('Usuário não encontrado');

            // Auditoria antes do DELETE: se o ator remover a própria conta, o
            // `ON DELETE SET NULL` da FK zera `actor_id` sem violar a constraint.
            await this.auditLogRepository.create(
                { action: `user:deleted=${id}`, actorId },
                tx
            );
            await this.userRepository.deleteById(id, tx);

            logger.info('Usuário removido', { userId: id, actorId });
            return true;
        });
    }
}

module.exports = UserService;
