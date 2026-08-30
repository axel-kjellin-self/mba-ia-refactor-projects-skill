/** Orquestração HTTP da entidade usuário. */
class UserController {
    constructor(userService) {
        this.userService = userService;
        this.getById = this.getById.bind(this);
        this.remove = this.remove.bind(this);
    }

    /** GET /api/users/:id */
    async getById(req, res, next) {
        try {
            const user = await this.userService.getById(req.validated.params.id);
            res.status(200).json(user);
        } catch (err) {
            next(err);
        }
    }

    /** DELETE /api/users/:id */
    async remove(req, res, next) {
        try {
            await this.userService.deleteById(req.validated.params.id, req.user.id);
            res.status(204).send();
        } catch (err) {
            next(err);
        }
    }
}

module.exports = UserController;
