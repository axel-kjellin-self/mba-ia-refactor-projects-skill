/**
 * Orquestração HTTP do checkout. Sem regra de negócio e sem acesso a banco:
 * extrai os dados já validados, delega ao service e formata a resposta.
 */
class CheckoutController {
    constructor(checkoutService) {
        this.checkoutService = checkoutService;
        this.create = this.create.bind(this);
    }

    /** POST /api/checkout */
    async create(req, res, next) {
        try {
            const result = await this.checkoutService.execute(req.validated.body);

            res.status(201).json({
                message: 'Matrícula realizada com sucesso',
                enrollmentId: result.enrollmentId,
                course: result.courseTitle,
                amount: result.amount,
            });
        } catch (err) {
            next(err);
        }
    }
}

module.exports = CheckoutController;
