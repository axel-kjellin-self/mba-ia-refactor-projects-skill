const UserRepository = require('./repositories/UserRepository');
const CourseRepository = require('./repositories/CourseRepository');
const EnrollmentRepository = require('./repositories/EnrollmentRepository');
const PaymentRepository = require('./repositories/PaymentRepository');
const AuditLogRepository = require('./repositories/AuditLogRepository');
const ReportRepository = require('./repositories/ReportRepository');

const AuthService = require('./services/AuthService');
const CheckoutService = require('./services/CheckoutService');
const ReportService = require('./services/ReportService');
const UserService = require('./services/UserService');
const { FakePaymentGateway } = require('./services/PaymentGateway');

const AuthController = require('./controllers/AuthController');
const CheckoutController = require('./controllers/CheckoutController');
const ReportController = require('./controllers/ReportController');
const UserController = require('./controllers/UserController');

/**
 * Composition root: monta o grafo de dependências em um único lugar.
 *
 * Cada camada recebe suas dependências por construtor, então qualquer uma pode
 * ser substituída por um dublê em testes — o que era impossível quando tudo
 * vivia dentro de `AppManager`.
 */
function buildContainer({ db, paymentGateway = new FakePaymentGateway() }) {
    const userRepository = new UserRepository(db);
    const courseRepository = new CourseRepository(db);
    const enrollmentRepository = new EnrollmentRepository(db);
    const paymentRepository = new PaymentRepository(db);
    const auditLogRepository = new AuditLogRepository(db);
    const reportRepository = new ReportRepository(db);

    const authService = new AuthService(userRepository);
    const checkoutService = new CheckoutService({
        db,
        userRepository,
        courseRepository,
        enrollmentRepository,
        paymentRepository,
        auditLogRepository,
        authService,
        paymentGateway,
    });
    const reportService = new ReportService(reportRepository);
    const userService = new UserService({ db, userRepository, auditLogRepository });

    return {
        db,
        authService,
        checkoutService,
        reportService,
        userService,
        authController: new AuthController(authService),
        checkoutController: new CheckoutController(checkoutService),
        reportController: new ReportController(reportService),
        userController: new UserController(userService),
    };
}

module.exports = buildContainer;
