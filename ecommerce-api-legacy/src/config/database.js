const sqlite3 = require('sqlite3').verbose();
const { promisify } = require('util');

/**
 * Database connection manager
 * Provides promisified database methods for async/await
 */
class Database {
    constructor() {
        this.db = new sqlite3.Database(':memory:');

        // Promisify database methods
        this.run = promisify(this.db.run.bind(this.db));
        this.get = promisify(this.db.get.bind(this.db));
        this.all = promisify(this.db.all.bind(this.db));
    }

    /**
     * Initialize database schema
     */
    async initSchema() {
        await this.db.serialize(async () => {
            // Users table
            await this.run(`
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            `);

            // Courses table
            await this.run(`
                CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    price REAL NOT NULL CHECK(price >= 0),
                    active INTEGER DEFAULT 1 CHECK(active IN (0, 1)),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            `);

            // Enrollments table
            await this.run(`
                CREATE TABLE IF NOT EXISTS enrollments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (course_id) REFERENCES courses(id),
                    UNIQUE(user_id, course_id)
                )
            `);

            // Payments table
            await this.run(`
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    enrollment_id INTEGER NOT NULL,
                    amount REAL NOT NULL CHECK(amount >= 0),
                    status TEXT NOT NULL CHECK(status IN ('PAID', 'DENIED', 'PENDING')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE
                )
            `);

            // Audit logs table
            await this.run(`
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    user_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            `);
        });

        console.log('[Database] Schema initialized with proper constraints');
    }

    /**
     * Seed initial data
     */
    async seed(seedData) {
        await this.run(
            'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
            [seedData.user.name, seedData.user.email, seedData.user.password, seedData.user.role]
        );

        for (const course of seedData.courses) {
            await this.run(
                'INSERT INTO courses (title, price, active) VALUES (?, ?, ?)',
                [course.title, course.price, course.active]
            );
        }

        if (seedData.enrollment) {
            await this.run(
                'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
                [seedData.enrollment.userId, seedData.enrollment.courseId]
            );
        }

        if (seedData.payment) {
            await this.run(
                'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
                [seedData.payment.enrollmentId, seedData.payment.amount, seedData.payment.status]
            );
        }

        console.log('[Database] Seed data loaded');
    }

    /**
     * Close database connection
     */
    close() {
        return new Promise((resolve, reject) => {
            this.db.close((err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }
}

module.exports = new Database();
