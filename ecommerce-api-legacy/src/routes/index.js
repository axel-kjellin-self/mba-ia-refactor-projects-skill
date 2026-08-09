const express = require('express');
const authRoutes = require('./authRoutes');
const checkoutRoutes = require('./checkoutRoutes');
const adminRoutes = require('./adminRoutes');
const userRoutes = require('./userRoutes');

/**
 * Register all application routes
 * @param {Express} app - Express application instance
 */
function registerRoutes(app) {
    // Health check endpoint
    app.get('/health', (req, res) => {
        res.status(200).json({
            status: 'healthy',
            timestamp: new Date().toISOString()
        });
    });

    // API routes
    app.use('/api/auth', authRoutes);
    app.use('/api/checkout', checkoutRoutes);
    app.use('/api/admin', adminRoutes);
    app.use('/api/users', userRoutes);
}

module.exports = { registerRoutes };
