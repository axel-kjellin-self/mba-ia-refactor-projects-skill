/**
 * Acesso a dados da entidade `users`. Sem regra de negócio e sem HTTP.
 *
 * `pass` nunca é incluído nos SELECTs de leitura — apenas em `findByEmailWithPassword`,
 * usado exclusivamente pelo fluxo de login.
 */
class UserRepository {
    constructor(db) {
        this.db = db;
    }

    /** Colunas públicas — jamais expor o hash da senha em respostas de API. */
    static get PUBLIC_COLUMNS() {
        return 'id, name, email, role, created_at';
    }

    findById(id, executor = this.db) {
        return executor.get(
            `SELECT ${UserRepository.PUBLIC_COLUMNS} FROM users WHERE id = ?`,
            [id]
        );
    }

    findByEmail(email, executor = this.db) {
        return executor.get(
            `SELECT ${UserRepository.PUBLIC_COLUMNS} FROM users WHERE email = ?`,
            [email]
        );
    }

    /** Inclui o hash da senha. Use apenas na autenticação. */
    findByEmailWithPassword(email, executor = this.db) {
        return executor.get('SELECT * FROM users WHERE email = ?', [email]);
    }

    async create({ name, email, passwordHash, role }, executor = this.db) {
        const { lastID } = await executor.run(
            'INSERT INTO users (name, email, pass, role) VALUES (?, ?, ?, ?)',
            [name, email, passwordHash, role]
        );
        return this.findById(lastID, executor);
    }

    async deleteById(id, executor = this.db) {
        const { changes } = await executor.run('DELETE FROM users WHERE id = ?', [id]);
        return changes > 0;
    }
}

module.exports = UserRepository;
