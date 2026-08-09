const database = require('../config/database');
const User = require('../models/User');

/**
 * User Repository
 * Handles database operations for users
 */
class UserRepository {
    /**
     * Find user by ID
     * @param {number} userId
     * @returns {Promise<User|null>}
     */
    async findById(userId) {
        const row = await database.get('SELECT * FROM users WHERE id = ?', [userId]);
        return row ? new User(row) : null;
    }

    /**
     * Find user by email
     * @param {string} email
     * @returns {Promise<User|null>}
     */
    async findByEmail(email) {
        const row = await database.get('SELECT * FROM users WHERE email = ?', [email]);
        return row ? new User(row) : null;
    }

    /**
     * Create a new user
     * @param {Object} userData - { name, email, password (hashed), role }
     * @returns {Promise<User>}
     */
    async create(userData) {
        const result = await database.run(
            'INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)',
            [userData.name, userData.email, userData.password, userData.role || 'user']
        );

        return this.findById(result.lastID);
    }

    /**
     * Delete user by ID
     * @param {number} userId
     * @returns {Promise<boolean>}
     */
    async delete(userId) {
        const result = await database.run('DELETE FROM users WHERE id = ?', [userId]);
        return result.changes > 0;
    }

    /**
     * Find all users
     * @returns {Promise<User[]>}
     */
    async findAll() {
        const rows = await database.all('SELECT * FROM users');
        return rows.map(row => new User(row));
    }
}

module.exports = new UserRepository();
