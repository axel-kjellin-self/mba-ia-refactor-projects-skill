/**
 * Queries agregadas para relatórios.
 *
 * Substitui o N+1 do código legado: o relatório financeiro fazia
 * 1 + N + (2 × M) queries (para 50 cursos × 100 matrículas: ~10.000 queries).
 * Aqui é uma única query com LEFT JOINs.
 */
class ReportRepository {
    constructor(db) {
        this.db = db;
    }

    /**
     * Uma linha por (curso, matrícula). Cursos sem matrícula aparecem com as
     * colunas de aluno/pagamento nulas, graças aos LEFT JOINs.
     */
    findFinancialRows(executor = this.db) {
        return executor.all(`
            SELECT
                c.id            AS course_id,
                c.title         AS course_title,
                e.id            AS enrollment_id,
                u.name          AS student_name,
                p.amount        AS payment_amount,
                p.status        AS payment_status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u       ON u.id = e.user_id
            LEFT JOIN payments p    ON p.enrollment_id = e.id
            ORDER BY c.id, e.id
        `);
    }
}

module.exports = ReportRepository;
