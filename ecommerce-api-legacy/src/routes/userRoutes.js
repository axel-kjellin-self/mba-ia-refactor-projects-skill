const { Router } = require('express');

const { requireAuth, requireSelfOrAdmin } = require('../middlewares/auth');
const validate = require('../middlewares/validate');
const { userIdParamSchema } = require('../validators/schemas');

/**
 * Rotas de usuário. Toda operação exige autenticação e, além disso, que o
 * solicitante seja o dono do recurso ou um admin (proteção contra IDOR).
 */
module.exports = ({ userController, authService }) => {
    const router = Router();

    const ownership = requireSelfOrAdmin((req) => req.validated.params.id);

    router.get(
        '/:id',
        validate(userIdParamSchema, 'params'),
        requireAuth(authService),
        ownership,
        userController.getById
    );

    router.delete(
        '/:id',
        validate(userIdParamSchema, 'params'),
        requireAuth(authService),
        ownership,
        userController.remove
    );

    return router;
};
