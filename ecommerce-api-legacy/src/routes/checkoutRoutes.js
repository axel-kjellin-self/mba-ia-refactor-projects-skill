const { Router } = require('express');

const validate = require('../middlewares/validate');
const { checkoutSchema } = require('../validators/schemas');

/**
 * Rota de checkout. Permanece pública por ser o fluxo de cadastro + compra,
 * mas agora exige senha válida e valida todos os campos.
 */
module.exports = ({ checkoutController }) => {
    const router = Router();

    router.post('/', validate(checkoutSchema), checkoutController.create);

    return router;
};
