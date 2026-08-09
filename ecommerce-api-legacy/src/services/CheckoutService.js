const UserRepository = require('../repositories/UserRepository');
const CourseRepository = require('../repositories/CourseRepository');
const EnrollmentRepository = require('../repositories/EnrollmentRepository');
const PaymentRepository = require('../repositories/PaymentRepository');
const AuditLogRepository = require('../repositories/AuditLogRepository');
const User = require('../models/User');
const config = require('../config/index');
const { CARD_PREFIXES, PAYMENT_STATUS } = require('../config/constants');

/**
 * Checkout Service
 * Handles business logic for course checkout and enrollment
 */
class CheckoutService {
    /**
     * Process checkout: create/find user, validate course, process payment, enroll
     * @param {Object} checkoutData - { name, email, password, courseId, cardNumber }
     * @returns {Promise<Object>} { enrollmentId, message }
     * @throws {Error} If validation or business rules fail
     */
    async processCheckout(checkoutData) {
        const { name, email, password, courseId, cardNumber } = checkoutData;

        // 1. Validate course exists and is active
        const course = await CourseRepository.findActiveById(courseId);
        if (!course) {
            throw new Error('Course not found or not available');
        }

        // 2. Find or create user
        let user = await UserRepository.findByEmail(email);

        if (!user) {
            // Create new user with hashed password
            const hashedPassword = await User.hashPassword(password || 'TempPassword123!');
            user = await UserRepository.create({
                name,
                email,
                password: hashedPassword,
                role: 'user'
            });
        }

        // 3. Check if already enrolled
        const alreadyEnrolled = await EnrollmentRepository.exists(user.id, courseId);
        if (alreadyEnrolled) {
            throw new Error('User is already enrolled in this course');
        }

        // 4. Simulate payment processing
        const paymentStatus = this.processPaymentGateway(cardNumber, course.price);

        if (paymentStatus === PAYMENT_STATUS.DENIED) {
            // Log failed attempt but don't create enrollment
            await AuditLogRepository.log(
                `Failed checkout attempt for course ${course.id} by user ${user.id}`,
                user.id
            );
            throw new Error('Payment denied');
        }

        // 5. Create enrollment
        const enrollment = await EnrollmentRepository.create(user.id, courseId);

        // 6. Record payment
        await PaymentRepository.create({
            enrollment_id: enrollment.id,
            amount: course.price,
            status: paymentStatus
        });

        // 7. Log successful checkout
        await AuditLogRepository.log(
            `Checkout: course ${course.id} (${course.title}) by user ${user.id}`,
            user.id
        );

        return {
            enrollmentId: enrollment.id,
            message: 'Checkout successful',
            course: course.toJSON(),
            user: user.toJSON()
        };
    }

    /**
     * Simulate payment gateway processing
     * @param {string} cardNumber - Credit card number
     * @param {number} amount - Payment amount
     * @returns {string} Payment status (PAID or DENIED)
     * @private
     */
    processPaymentGateway(cardNumber, amount) {
        // Simple simulation: Visa cards (starting with 4) are approved
        console.log(`[Payment Gateway] Processing card ${cardNumber.substring(0, 4)}**** for $${amount} using key ${config.paymentGatewayKey}`);

        if (cardNumber.startsWith(CARD_PREFIXES.VISA)) {
            return PAYMENT_STATUS.PAID;
        }

        return PAYMENT_STATUS.DENIED;
    }

    /**
     * Get user enrollments with course details
     * @param {number} userId
     * @returns {Promise<Array>}
     */
    async getUserEnrollments(userId) {
        const enrollments = await EnrollmentRepository.findByUserId(userId);

        const result = [];
        for (const enrollment of enrollments) {
            const course = await CourseRepository.findById(enrollment.course_id);
            const payment = await PaymentRepository.findByEnrollmentId(enrollment.id);

            result.push({
                enrollment: enrollment.toJSON(),
                course: course ? course.toJSON() : null,
                payment: payment ? payment.toJSON() : null
            });
        }

        return result;
    }
}

module.exports = new CheckoutService();
