const jwt = require('jsonwebtoken');
const UserRepository = require('../repositories/UserRepository');
const User = require('../models/User');
const config = require('../config/index');

/**
 * Authentication Service
 * Handles user authentication and JWT token generation
 */
class AuthService {
    /**
     * Authenticate user and generate JWT token
     * @param {string} email - User email
     * @param {string} password - User password (plaintext)
     * @returns {Promise<Object>} { user, token }
     * @throws {Error} If authentication fails
     */
    async login(email, password) {
        // Find user by email
        const user = await UserRepository.findByEmail(email);

        if (!user) {
            throw new Error('Invalid credentials');
        }

        // Verify password
        const isPasswordValid = await User.comparePassword(password, user.password);

        if (!isPasswordValid) {
            throw new Error('Invalid credentials');
        }

        // Generate JWT token
        const token = this.generateToken(user);

        return {
            user: user.toJSON(),
            token
        };
    }

    /**
     * Generate JWT token for user
     * @param {User} user
     * @returns {string} JWT token
     */
    generateToken(user) {
        const payload = {
            userId: user.id,
            email: user.email,
            role: user.role
        };

        return jwt.sign(payload, config.jwt.secret, {
            expiresIn: config.jwt.expiresIn
        });
    }

    /**
     * Verify and decode JWT token
     * @param {string} token
     * @returns {Object} Decoded token payload
     * @throws {Error} If token is invalid
     */
    verifyToken(token) {
        try {
            return jwt.verify(token, config.jwt.secret);
        } catch (error) {
            throw new Error('Invalid or expired token');
        }
    }

    /**
     * Register a new user
     * @param {Object} userData - { name, email, password }
     * @returns {Promise<Object>} { user, token }
     */
    async register(userData) {
        // Check if user already exists
        const existingUser = await UserRepository.findByEmail(userData.email);

        if (existingUser) {
            throw new Error('User with this email already exists');
        }

        // Hash password
        const hashedPassword = await User.hashPassword(userData.password);

        // Create user
        const user = await UserRepository.create({
            name: userData.name,
            email: userData.email,
            password: hashedPassword,
            role: userData.role || 'user'
        });

        // Generate token
        const token = this.generateToken(user);

        return {
            user: user.toJSON(),
            token
        };
    }
}

module.exports = new AuthService();
