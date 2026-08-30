const { PaymentStatus, Roles } = require('../config/constants');
const {
    NotFoundError,
    ConflictError,
    PaymentDeclinedError,
} = require('../utils/errors');
const logger = require('../utils/logger');

/**
 * Regra de negócio do checkout: garante o usuário, cobra o cartão e matricula.
 *
 * Toda a persistência acontece dentro de uma transação — o código legado gravava
 * matrícula, pagamento e auditoria em callbacks encadeados sem transação, então
 * uma falha no meio deixava uma matrícula sem pagamento correspondente.
 *
 * Esta classe não conhece `req`/`res`: pode ser chamada por um controller HTTP,
 * um worker ou um teste unitário.
 */
class CheckoutService {
    constructor({
        db,
        userRepository,
        courseRepository,
        enrollmentRepository,
        paymentRepository,
        auditLogRepository,
        authService,
        paymentGateway,
    }) {
        this.db = db;
        this.userRepository = userRepository;
        this.courseRepository = courseRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.paymentRepository = paymentRepository;
        this.auditLogRepository = auditLogRepository;
        this.authService = authService;
        this.paymentGateway = paymentGateway;
    }

    /**
     * @param {{name: string, email: string, password: string, courseId: number, cardNumber: string}} input
     * @returns {Promise<{enrollmentId: number, courseTitle: string, amount: number, userId: number}>}
     */
    async execute({ name, email, password, courseId, cardNumber }) {
        const course = await this.courseRepository.findActiveById(courseId);
        if (!course) {
            throw new NotFoundError('Curso não encontrado ou inativo');
        }

        const user = await this.#findOrCreateUser({ name, email, password });

        const alreadyEnrolled = await this.enrollmentRepository.findByUserAndCourse(
            user.id,
            course.id
        );
        if (alreadyEnrolled) {
            throw new ConflictError('Usuário já está matriculado neste curso');
        }

        // A cobrança acontece fora da transação: chamadas de rede não devem
        // manter uma transação de banco aberta.
        const charge = await this.paymentGateway.charge(cardNumber, course.price);

        if (charge.status !== PaymentStatus.PAID) {
            logger.warn('Pagamento recusado', { userId: user.id, courseId: course.id });
            throw new PaymentDeclinedError();
        }

        const enrollmentId = await this.db.transaction(async (tx) => {
            const newEnrollmentId = await this.enrollmentRepository.create(
                { userId: user.id, courseId: course.id },
                tx
            );

            await this.paymentRepository.create(
                { enrollmentId: newEnrollmentId, amount: course.price, status: charge.status },
                tx
            );

            await this.auditLogRepository.create(
                { action: `checkout:course=${course.id}`, actorId: user.id },
                tx
            );

            return newEnrollmentId;
        });

        logger.info('Checkout concluído', {
            userId: user.id,
            courseId: course.id,
            enrollmentId,
        });

        return {
            enrollmentId,
            userId: user.id,
            courseTitle: course.title,
            amount: course.price,
        };
    }

    /**
     * Reaproveita a conta existente ou cria uma nova. A senha é obrigatória e
     * validada na borda — o código legado caía no fallback silencioso `"123456"`,
     * criando contas com senha padrão sem o usuário saber.
     */
    async #findOrCreateUser({ name, email, password }) {
        const existing = await this.userRepository.findByEmail(email);
        if (existing) return existing;

        const passwordHash = await this.authService.hashPassword(password);
        return this.userRepository.create({
            name,
            email,
            passwordHash,
            role: Roles.USER,
        });
    }
}

module.exports = CheckoutService;
