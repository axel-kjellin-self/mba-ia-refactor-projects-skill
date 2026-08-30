const { Router } = require('express');

const authRoutes = require('./authRoutes');
const checkoutRoutes = require('./checkoutRoutes');
const reportRoutes = require('./reportRoutes');
const userRoutes = require('./userRoutes');

/** Agrega todas as rotas da aplicação sob o prefixo `/api`. */
function buildRouter(container) {
    const router = Router();

    router.get('/health', (req, res) => res.json({ status: 'ok' }));

    router.use('/auth', authRoutes(container));
    router.use('/checkout', checkoutRoutes(container));
    router.use('/admin', reportRoutes(container));
    router.use('/users', userRoutes(container));

    return router;
}

module.exports = buildRouter;
