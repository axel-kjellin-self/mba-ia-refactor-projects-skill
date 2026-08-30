const bcrypt = require('bcryptjs');

const { config } = require('../config');
const { Roles, PaymentStatus, Security } = require('../config/constants');
const logger = require('../utils/logger');

/**
 * Definição do schema e seeds.
 *
 * Diferenças em relação ao schema legado:
 *  - FOREIGN KEYs declaradas (integridade referencial era inexistente).
 *  - `ON DELETE CASCADE` em enrollments/payments — deletar um usuário não deixa
 *    mais matrículas e pagamentos órfãos no banco.
 *  - `NOT NULL` nos campos obrigatórios e `UNIQUE` em `users.email`, coluna que
 *    o código já tratava como única ao buscar usuário por email.
 *  - Coluna `role`, base para a autorização das rotas administrativas.
 *  - Índices nas FKs usadas pelo relatório financeiro.
 */
const DDL = `
CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    pass       TEXT    NOT NULL,
    role       TEXT    NOT NULL DEFAULT '${Roles.USER}',
    created_at DATETIME NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS courses (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    title  TEXT    NOT NULL,
    price  REAL    NOT NULL CHECK (price >= 0),
    active INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS enrollments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id)   ON DELETE CASCADE,
    course_id  INTEGER NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    UNIQUE (user_id, course_id)
);

CREATE TABLE IF NOT EXISTS payments (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    enrollment_id INTEGER NOT NULL REFERENCES enrollments(id) ON DELETE CASCADE,
    amount        REAL    NOT NULL CHECK (amount >= 0),
    status        TEXT    NOT NULL CHECK (status IN ('${PaymentStatus.PAID}', '${PaymentStatus.DENIED}')),
    created_at    DATETIME NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    action     TEXT    NOT NULL,
    actor_id   INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at DATETIME NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_user   ON enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_enrollment ON payments(enrollment_id);
`;

async function createTables(db) {
    await db.exec(DDL);
}

/**
 * Popula dados de demonstração. As senhas são hasheadas com bcrypt — o seed
 * legado gravava a senha `'123'` em texto plano.
 */
async function seed(db) {
    const existing = await db.get('SELECT COUNT(*) AS total FROM courses');
    if (existing.total > 0) return;

    await db.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, ?)',
        ['Clean Architecture', 997.0, 1]
    );
    await db.run(
        'INSERT INTO courses (title, price, active) VALUES (?, ?, ?)',
        ['Docker', 497.0, 1]
    );

    if (config.isProduction) {
        logger.info('Seed de usuários ignorado em produção');
        return;
    }

    const { adminEmail, adminPassword } = config.seed;
    if (!adminEmail || !adminPassword) {
        logger.warn(
            'SEED_ADMIN_EMAIL/SEED_ADMIN_PASSWORD não definidos: nenhum admin foi criado'
        );
        return;
    }

    const hash = await bcrypt.hash(adminPassword, Security.BCRYPT_SALT_ROUNDS);
    const { lastID: adminId } = await db.run(
        'INSERT INTO users (name, email, pass, role) VALUES (?, ?, ?, ?)',
        ['Admin', adminEmail, hash, Roles.ADMIN]
    );

    // Matrícula + pagamento de exemplo, para que o relatório financeiro tenha
    // dados logo após o boot (equivalente ao seed do código legado).
    const { lastID: enrollmentId } = await db.run(
        'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
        [adminId, 1]
    );
    await db.run(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, 997.0, PaymentStatus.PAID]
    );

    logger.info('Seed aplicado', { adminEmail });
}

module.exports = { createTables, seed };
