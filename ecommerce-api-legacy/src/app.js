const express = require('express');
const config = require('./config/index');
const database = require('./config/database');
const { registerRoutes } = require('./routes');
const { errorHandler, notFoundHandler } = require('./middlewares/errorHandler');
const { requestLogger } = require('./middlewares/logger');
const User = require('./models/User');

/**
 * Application factory
 * Creates and configures Express application
 */
async function createApp() {
    const app = express();

    // Middleware
    app.use(express.json());
    app.use(requestLogger);

    // Initialize database
    console.log('[App] Initializing database...');
    await database.initSchema();

    // Seed initial data with hashed password
    const hashedPassword = await User.hashPassword('SecurePassword123!');
    await database.seed({
        user: {
            name: 'Leonan',
            email: 'leonan@fullcycle.com.br',
            password: hashedPassword,
            role: 'admin'
        },
        courses: [
            { title: 'Clean Architecture', price: 997.00, active: 1 },
            { title: 'Docker', price: 497.00, active: 1 }
        ],
        enrollment: {
            userId: 1,
            courseId: 1
        },
        payment: {
            enrollmentId: 1,
            amount: 997.00,
            status: 'PAID'
        }
    });

    // Register routes
    registerRoutes(app);

    // 404 handler (must be after routes)
    app.use(notFoundHandler);

    // Global error handler (must be last)
    app.use(errorHandler);

    return app;
}

/**
 * Start server
 */
async function startServer() {
    try {
        const app = await createApp();

        app.listen(config.port, () => {
            console.log('========================================');
            console.log(`🚀 LMS API running on port ${config.port}`);
            console.log(`📚 Environment: ${config.nodeEnv}`);
            console.log(`🔐 JWT authentication enabled`);
            console.log('========================================');
            console.log('');
            console.log('Default admin user:');
            console.log('  Email: leonan@fullcycle.com.br');
            console.log('  Password: SecurePassword123!');
            console.log('');
            console.log('Available endpoints:');
            console.log('  POST   /api/auth/login');
            console.log('  POST   /api/auth/register');
            console.log('  POST   /api/checkout');
            console.log('  GET    /api/admin/financial-report (admin only)');
            console.log('  GET    /api/users/:id (authenticated)');
            console.log('  DELETE /api/users/:id (authenticated)');
            console.log('========================================');
        });

    } catch (error) {
        console.error('[App] Failed to start:', error);
        process.exit(1);
    }
}

// Start server if run directly
if (require.main === module) {
    startServer();
}

module.exports = { createApp, startServer };
