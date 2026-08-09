const AuthService = require('../services/AuthService');

/**
 * Authentication Middleware
 * Verifies JWT token and attaches user info to request
 */
function requireAuth(req, res, next) {
    try {
        // Get token from Authorization header
        const authHeader = req.headers.authorization;

        if (!authHeader) {
            return res.status(401).json({ error: 'No token provided' });
        }

        // Extract token (format: "Bearer <token>")
        const token = authHeader.replace('Bearer ', '');

        if (!token) {
            return res.status(401).json({ error: 'No token provided' });
        }

        // Verify token
        const decoded = AuthService.verifyToken(token);

        // Attach user info to request
        req.user = {
            userId: decoded.userId,
            email: decoded.email,
            role: decoded.role
        };

        next();

    } catch (error) {
        if (error.message.includes('Invalid') || error.message.includes('expired')) {
            return res.status(401).json({ error: 'Invalid or expired token' });
        }

        next(error);
    }
}

/**
 * Role-based authorization middleware
 * Requires user to have specific role
 */
function requireRole(...roles) {
    return (req, res, next) => {
        if (!req.user) {
            return res.status(401).json({ error: 'Authentication required' });
        }

        if (!roles.includes(req.user.role)) {
            return res.status(403).json({
                error: `Forbidden: Requires role ${roles.join(' or ')}`
            });
        }

        next();
    };
}

/**
 * Optional authentication
 * Attaches user if token is valid, but doesn't reject if missing
 */
function optionalAuth(req, res, next) {
    try {
        const authHeader = req.headers.authorization;

        if (!authHeader) {
            return next();
        }

        const token = authHeader.replace('Bearer ', '');
        const decoded = AuthService.verifyToken(token);

        req.user = {
            userId: decoded.userId,
            email: decoded.email,
            role: decoded.role
        };

        next();

    } catch (error) {
        // Token invalid, but continue without user
        next();
    }
}

module.exports = {
    requireAuth,
    requireRole,
    optionalAuth
};
