const AuthService = require('../services/AuthService');

/**
 * Auth Controller
 * Handles HTTP requests for authentication
 */
class AuthController {
    /**
     * POST /api/auth/login
     * User login
     */
    async login(req, res, next) {
        try {
            const { email, password } = req.body;

            if (!email || !password) {
                return res.status(400).json({ error: 'Email and password are required' });
            }

            const result = await AuthService.login(email, password);

            return res.status(200).json(result);

        } catch (error) {
            if (error.message === 'Invalid credentials') {
                return res.status(401).json({ error: 'Invalid email or password' });
            }

            next(error);
        }
    }

    /**
     * POST /api/auth/register
     * User registration
     */
    async register(req, res, next) {
        try {
            const { name, email, password } = req.body;

            if (!name || !email || !password) {
                return res.status(400).json({ error: 'Name, email, and password are required' });
            }

            const result = await AuthService.register({ name, email, password });

            return res.status(201).json(result);

        } catch (error) {
            if (error.message.includes('already exists')) {
                return res.status(409).json({ error: error.message });
            }

            next(error);
        }
    }
}

module.exports = new AuthController();
