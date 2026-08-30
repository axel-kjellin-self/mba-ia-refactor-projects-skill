const { Roles } = require('../config/constants');
const { UnauthorizedError, ForbiddenError } = require('../utils/errors');

/**
 * Middlewares de autenticação e autorização.
 *
 * O código legado não tinha nenhum: o relatório financeiro e o DELETE de
 * usuários eram acessíveis por qualquer anônimo.
 */

/** Exige um JWT válido no header `Authorization: Bearer <token>`. */
function requireAuth(authService) {
    return (req, res, next) => {
        try {
            const header = req.headers.authorization || '';
            const [scheme, token] = header.split(' ');

            if (scheme !== 'Bearer' || !token) {
                throw new UnauthorizedError('Token de autenticação ausente');
            }

            const payload = authService.verifyToken(token);
            req.user = { id: payload.sub, role: payload.role };
            next();
        } catch (err) {
            next(err);
        }
    };
}

/** Exige papel de administrador. Deve ser aplicado depois de `requireAuth`. */
function requireAdmin(req, res, next) {
    if (!req.user) return next(new UnauthorizedError());
    if (req.user.role !== Roles.ADMIN) {
        return next(new ForbiddenError('Requer privilégios de administrador'));
    }
    return next();
}

/**
 * Permite a ação ao administrador ou ao próprio dono do recurso.
 * Previne IDOR: sem isso, um usuário autenticado poderia deletar outro.
 */
function requireSelfOrAdmin(getResourceUserId) {
    return (req, res, next) => {
        if (!req.user) return next(new UnauthorizedError());

        const targetId = getResourceUserId(req);
        if (req.user.role === Roles.ADMIN || req.user.id === targetId) {
            return next();
        }
        return next(new ForbiddenError('Você só pode alterar a própria conta'));
    };
}

module.exports = { requireAuth, requireAdmin, requireSelfOrAdmin };
