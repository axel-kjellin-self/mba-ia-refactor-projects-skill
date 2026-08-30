const { PaymentStatus } = require('../config/constants');
const logger = require('../utils/logger');

/**
 * Fronteira com o provedor de pagamento.
 *
 * O código legado decidia a aprovação com `card.startsWith("4")` e logava o
 * número completo do cartão junto com a chave do gateway. Isolar isso atrás de
 * uma interface permite: (a) nunca vazar o PAN, (b) trocar a implementação fake
 * por uma real sem tocar na regra de negócio, (c) testar o checkout com um
 * gateway dublê.
 */
class PaymentGateway {
    /**
     * @param {string} cardNumber
     * @param {number} amount
     * @returns {Promise<{status: string, transactionId: string}>}
     */
    // eslint-disable-next-line no-unused-vars
    async charge(cardNumber, amount) {
        throw new Error('PaymentGateway.charge() não implementado');
    }
}

/**
 * Implementação de desenvolvimento/testes. Mantém a heurística do código legado
 * (cartões iniciados em "4" são aprovados) para preservar o comportamento dos
 * exemplos em `api.http`, mas agora explicitamente marcada como fake.
 */
class FakePaymentGateway extends PaymentGateway {
    async charge(cardNumber, amount) {
        const approved = cardNumber.startsWith('4');

        // Apenas os 4 últimos dígitos vão para o log; a chave do gateway nunca.
        logger.info('Cobrança processada pelo gateway fake', {
            card: logger.maskCard(cardNumber),
            amount,
            approved,
        });

        return {
            status: approved ? PaymentStatus.PAID : PaymentStatus.DENIED,
            transactionId: `fake_${Date.now()}`,
        };
    }
}

module.exports = { PaymentGateway, FakePaymentGateway };
