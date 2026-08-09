const bcrypt = require('bcrypt');

const SALT_ROUNDS = 12;

/**
 * User Model
 * Represents a user entity with password hashing capabilities
 */
class User {
    constructor(data) {
        this.id = data.id;
        this.name = data.name;
        this.email = data.email;
        this.password = data.password; // Already hashed
        this.role = data.role || 'user';
        this.created_at = data.created_at;
    }

    /**
     * Hash a plaintext password using bcrypt
     * @param {string} plainPassword - Plaintext password
     * @returns {Promise<string>} Hashed password
     */
    static async hashPassword(plainPassword) {
        return await bcrypt.hash(plainPassword, SALT_ROUNDS);
    }

    /**
     * Compare plaintext password with hashed password
     * @param {string} plainPassword - Plaintext password to check
     * @param {string} hashedPassword - Hashed password from database
     * @returns {Promise<boolean>} True if passwords match
     */
    static async comparePassword(plainPassword, hashedPassword) {
        return await bcrypt.compare(plainPassword, hashedPassword);
    }

    /**
     * Convert user to safe JSON (excludes password)
     * @returns {Object} User data without password
     */
    toJSON() {
        return {
            id: this.id,
            name: this.name,
            email: this.email,
            role: this.role,
            created_at: this.created_at
        };
    }

    /**
     * Check if user is admin
     * @returns {boolean}
     */
    isAdmin() {
        return this.role === 'admin';
    }
}

module.exports = User;
