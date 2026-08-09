const express = require('express');
const CheckoutController = require('../controllers/CheckoutController');
const { asyncHandler } = require('../middlewares/errorHandler');

const router = express.Router();

/**
 * POST /api/checkout
 * Process course checkout (create/find user, enroll, process payment)
 */
router.post('/', asyncHandler(CheckoutController.processCheckout.bind(CheckoutController)));

module.exports = router;
