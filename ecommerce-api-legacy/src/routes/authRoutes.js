const { Router } = require('express');

const validate = require('../middlewares/validate');
const { loginSchema } = require('../validators/schemas');

/** Rotas de autenticação. Apenas mapeiam URL → middleware → controller. */
module.exports = ({ authController }) => {
    const router = Router();

    router.post('/login', validate(loginSchema), authController.login);

    return router;
};
