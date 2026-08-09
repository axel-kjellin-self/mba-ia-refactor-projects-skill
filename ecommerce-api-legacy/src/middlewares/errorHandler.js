const config = require('../config/index');

/**
 * Custom Error Classes
 */

class AppError extends Error {
    constructor(message, statusCode = 400) {
        super(message);
        this.statusCode = statusCode;
        this.name = this.constructor.name;
        Error.captureStackTrace(this, this.constructor);
    }
}

class NotFoundError extends AppError {
    constructor(message = 'Resource not found') {
        super(message, 404);
    }
}

class ValidationError extends AppError {
    constructor(message) {
        super(message, 400);
    }
}

class UnauthorizedError extends AppError {
    constructor(message = 'Unauthorized') {
        super(message, 401);
    }
}

class ForbiddenError extends AppError {
    constructor(message = 'Forbidden') {
        super(message, 403);
    }
}

/**
 * Global error handler middleware
 * Catches all errors and formats consistent responses
 */
function errorHandler(err, req, res, next) {
    // Log error (in production, use proper logger like Winston)
    console.error('[Error]', {
        message: err.message,
        stack: config.nodeEnv === 'development' ? err.stack : undefined,
        path: req.path,
        method: req.method
    });

    // Determine status code
    const statusCode = err.statusCode || 500;

    // Build error response
    const errorResponse = {
        error: err.message || 'Internal server error'
    };

    // Include stack trace in development
    if (config.nodeEnv === 'development') {
        errorResponse.stack = err.stack;
    }

    // Send response
    res.status(statusCode).json(errorResponse);
}

/**
 * 404 handler for undefined routes
 */
function notFoundHandler(req, res) {
    res.status(404).json({
        error: `Route ${req.method} ${req.path} not found`
    });
}

/**
 * Async handler wrapper
 * Wraps async route handlers to catch promise rejections
 */
function asyncHandler(fn) {
    return (req, res, next) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
}

module.exports = {
    AppError,
    NotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    errorHandler,
    notFoundHandler,
    asyncHandler
};
