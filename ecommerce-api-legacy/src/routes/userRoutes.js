const express = require('express');
const UserController = require('../controllers/UserController');
const CheckoutController = require('../controllers/CheckoutController');
const { requireAuth } = require('../middlewares/auth');
const { asyncHandler } = require('../middlewares/errorHandler');

const router = express.Router();

/**
 * GET /api/users/:id
 * Get user by ID (requires authentication)
 */
router.get(
    '/:id',
    requireAuth,
    asyncHandler(UserController.getUser.bind(UserController))
);

/**
 * DELETE /api/users/:id
 * Delete user (requires authentication + authorization)
 */
router.delete(
    '/:id',
    requireAuth,
    asyncHandler(UserController.deleteUser.bind(UserController))
);

/**
 * GET /api/users/:userId/enrollments
 * Get user's enrollments (requires authentication)
 */
router.get(
    '/:userId/enrollments',
    requireAuth,
    asyncHandler(CheckoutController.getUserEnrollments.bind(CheckoutController))
);

module.exports = router;
