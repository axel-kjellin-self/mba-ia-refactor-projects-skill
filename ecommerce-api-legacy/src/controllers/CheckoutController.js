const CheckoutService = require('../services/CheckoutService');

/**
 * Checkout Controller
 * Handles HTTP requests for checkout operations
 */
class CheckoutController {
    /**
     * POST /api/checkout
     * Process course checkout
     */
    async processCheckout(req, res, next) {
        try {
            const { usr: name, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

            // Validate required fields (basic validation)
            if (!name || !email || !courseId || !cardNumber) {
                return res.status(400).json({
                    error: 'Missing required fields: name, email, courseId, cardNumber'
                });
            }

            // Delegate to service
            const result = await CheckoutService.processCheckout({
                name,
                email,
                password,
                courseId: parseInt(courseId),
                cardNumber
            });

            return res.status(201).json(result);

        } catch (error) {
            // Business logic errors (validation, payment denied, etc.)
            if (error.message.includes('not found') ||
                error.message.includes('not available') ||
                error.message.includes('already enrolled')) {
                return res.status(400).json({ error: error.message });
            }

            if (error.message.includes('Payment denied')) {
                return res.status(400).json({ error: 'Payment was denied' });
            }

            // Unexpected errors
            next(error);
        }
    }

    /**
     * GET /api/users/:userId/enrollments
     * Get user enrollments
     */
    async getUserEnrollments(req, res, next) {
        try {
            const userId = parseInt(req.params.userId);

            const enrollments = await CheckoutService.getUserEnrollments(userId);

            return res.status(200).json({ enrollments });

        } catch (error) {
            next(error);
        }
    }
}

module.exports = new CheckoutController();
