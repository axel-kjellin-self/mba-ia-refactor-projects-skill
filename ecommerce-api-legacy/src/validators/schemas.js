const { z } = require('zod');

const { ValidationRules } = require('../config/constants');

/**
 * Schemas de validação de input. O código legado só checava presença
 * (`if (!u || !e || !cid || !cc)`), sem validar formato, tipo ou range.
 */

const passwordSchema = z
    .string()
    .min(
        ValidationRules.MIN_PASSWORD_LENGTH,
        `A senha deve ter no mínimo ${ValidationRules.MIN_PASSWORD_LENGTH} caracteres`
    );

const checkoutSchema = z.object({
    name: z.string().trim().min(1).max(ValidationRules.MAX_NAME_LENGTH),
    email: z.string().trim().toLowerCase().email('Email inválido'),
    // Senha obrigatória: elimina o fallback silencioso para "123456" do legado.
    password: passwordSchema,
    courseId: z.coerce.number().int().positive(),
    cardNumber: z
        .string()
        .regex(
            new RegExp(
                `^\\d{${ValidationRules.MIN_CARD_DIGITS},${ValidationRules.MAX_CARD_DIGITS}}$`
            ),
            'Número de cartão inválido'
        ),
});

const loginSchema = z.object({
    email: z.string().trim().toLowerCase().email('Email inválido'),
    password: z.string().min(1, 'Senha obrigatória'),
});

const userIdParamSchema = z.object({
    id: z.coerce.number().int().positive('ID de usuário inválido'),
});

module.exports = { checkoutSchema, loginSchema, userIdParamSchema };
