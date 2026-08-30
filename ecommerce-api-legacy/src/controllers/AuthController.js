/** Orquestração HTTP da autenticação. */
class AuthController {
    constructor(authService) {
        this.authService = authService;
        this.login = this.login.bind(this);
    }

    /** POST /api/auth/login */
    async login(req, res, next) {
        try {
            const { email, password } = req.validated.body;
            const result = await this.authService.login(email, password);
            res.status(200).json(result);
        } catch (err) {
            next(err);
        }
    }
}

module.exports = AuthController;
