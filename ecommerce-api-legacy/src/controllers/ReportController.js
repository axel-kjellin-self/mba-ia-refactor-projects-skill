/** Orquestração HTTP dos relatórios administrativos. */
class ReportController {
    constructor(reportService) {
        this.reportService = reportService;
        this.financial = this.financial.bind(this);
    }

    /** GET /api/admin/financial-report — restrito a administradores. */
    async financial(req, res, next) {
        try {
            const report = await this.reportService.buildFinancialReport();
            res.status(200).json(report);
        } catch (err) {
            next(err);
        }
    }
}

module.exports = ReportController;
