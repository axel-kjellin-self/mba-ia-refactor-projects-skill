const { Router } = require('express');

const { requireAuth, requireAdmin } = require('../middlewares/auth');

/**
 * Relatórios administrativos: expõem receita e dados pessoais de alunos,
 * portanto exigem autenticação e papel de admin.
 */
module.exports = ({ reportController, authService }) => {
    const router = Router();

    router.get(
        '/financial-report',
        requireAuth(authService),
        requireAdmin,
        reportController.financial
    );

    return router;
};
