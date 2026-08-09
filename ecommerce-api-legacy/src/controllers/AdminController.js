const ReportService = require('../services/ReportService');

/**
 * Admin Controller
 * Handles HTTP requests for admin operations
 */
class AdminController {
    /**
     * GET /api/admin/financial-report
     * Generate financial report (requires admin authentication)
     */
    async getFinancialReport(req, res, next) {
        try {
            const report = await ReportService.generateFinancialReport();

            return res.status(200).json({ report });

        } catch (error) {
            next(error);
        }
    }

    /**
     * GET /api/admin/revenue-summary
     * Get revenue summary statistics
     */
    async getRevenueSummary(req, res, next) {
        try {
            const summary = await ReportService.getRevenueSummary();

            return res.status(200).json({ summary });

        } catch (error) {
            next(error);
        }
    }
}

module.exports = new AdminController();
