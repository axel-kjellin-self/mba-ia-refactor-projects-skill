const { PaymentStatus } = require('../config/constants');

/**
 * Monta o relatório financeiro a partir de uma única query com JOINs,
 * agrupando as linhas em memória.
 *
 * O código legado fazia queries aninhadas dentro de dois `forEach` e controlava
 * a conclusão com contadores manuais (`coursesPending`/`enrPending`) — além do
 * N+1, isso quebrava quando um curso não tinha matrículas.
 */
class ReportService {
    constructor(reportRepository) {
        this.reportRepository = reportRepository;
    }

    /**
     * @returns {Promise<Array<{course: string, revenue: number, students: Array}>>}
     */
    async buildFinancialReport() {
        const rows = await this.reportRepository.findFinancialRows();

        const byCourse = new Map();

        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, {
                    course: row.course_title,
                    revenue: 0,
                    students: [],
                });
            }

            const entry = byCourse.get(row.course_id);

            // LEFT JOIN: cursos sem matrícula geram uma linha com enrollment nulo.
            if (row.enrollment_id === null) continue;

            if (row.payment_status === PaymentStatus.PAID) {
                entry.revenue += row.payment_amount;
            }

            entry.students.push({
                student: row.student_name,
                paid: row.payment_amount ?? 0,
                status: row.payment_status ?? null,
            });
        }

        return Array.from(byCourse.values()).map((entry) => ({
            ...entry,
            // Evita ruído de ponto flutuante ao somar valores monetários.
            revenue: Number(entry.revenue.toFixed(2)),
        }));
    }
}

module.exports = ReportService;
