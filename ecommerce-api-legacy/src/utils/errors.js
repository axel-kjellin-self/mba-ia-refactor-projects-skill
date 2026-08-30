/**
 * Hierarquia de erros da aplicação. Services lançam estes erros sem saber nada
 * de HTTP; o middleware de error handling faz a tradução para status code.
 */

class AppError extends Error {
    constructor(message, statusCode = 400, code = 'APP_ERROR', details = undefined) {
        super(message);
        this.name = this.constructor.name;
        this.statusCode = statusCode;
        this.code = code;
        this.details = details;
        this.isOperational = true;
    }
}

class ValidationError extends AppError {
    constructor(message = 'Dados inválidos', details) {
        super(message, 400, 'VALIDATION_ERROR', details);
    }
}

class UnauthorizedError extends AppError {
    constructor(message = 'Não autenticado') {
        super(message, 401, 'UNAUTHORIZED');
    }
}

class ForbiddenError extends AppError {
    constructor(message = 'Acesso negado') {
        super(message, 403, 'FORBIDDEN');
    }
}

class NotFoundError extends AppError {
    constructor(message = 'Recurso não encontrado') {
        super(message, 404, 'NOT_FOUND');
    }
}

class ConflictError extends AppError {
    constructor(message = 'Conflito de estado') {
        super(message, 409, 'CONFLICT');
    }
}

/** 402 Payment Required — recusa do gateway, não é erro do cliente. */
class PaymentDeclinedError extends AppError {
    constructor(message = 'Pagamento recusado') {
        super(message, 402, 'PAYMENT_DECLINED');
    }
}

module.exports = {
    AppError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    PaymentDeclinedError,
};
