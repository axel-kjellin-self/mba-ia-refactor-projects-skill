const express = require('express');
const AdminController = require('../controllers/AdminController');
const { requireAuth, requireRole } = require('../middlewares/auth');
const { asyncHandler } = require('../middlewares/errorHandler');

const router = express.Router();

/**
 * All admin routes require authentication and admin role
 */
router.use(requireAuth);
router.use(requireRole('admin'));

/**
 * GET /api/admin/financial-report
 * Generate financial report with course revenue and student details
 */
router.get(
    '/financial-report',
    asyncHandler(AdminController.getFinancialReport.bind(AdminController))
);

/**
 * GET /api/admin/revenue-summary
 * Get revenue summary statistics
 */
router.get(
    '/revenue-summary',
    asyncHandler(AdminController.getRevenueSummary.bind(AdminController))
);

module.exports = router;
