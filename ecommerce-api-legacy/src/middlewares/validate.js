const { ValidationError } = require('../utils/errors');

/**
 * Valida uma parte do request contra um schema Zod e substitui o conteúdo pelos
 * dados já parseados/coeridos. Controllers passam a receber dados confiáveis.
 *
 * @param {import('zod').ZodSchema} schema
 * @param {'body'|'params'|'query'} source
 */
function validate(schema, source = 'body') {
    return (req, res, next) => {
        const result = schema.safeParse(req[source]);

        if (!result.success) {
            const details = result.error.issues.map((issue) => ({
                field: issue.path.join('.'),
                message: issue.message,
            }));
            return next(new ValidationError('Dados inválidos', details));
        }

        // `req.query` é getter-only no Express 5; guardamos em `validated`.
        req.validated = { ...(req.validated || {}), [source]: result.data };
        return next();
    };
}

module.exports = validate;
