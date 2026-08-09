const EnrollmentRepository = require('../repositories/EnrollmentRepository');
const { PAYMENT_STATUS } = require('../config/constants');

/**
 * Report Service
 * Handles business logic for generating reports
 */
class ReportService {
    /**
     * Generate financial report with optimized query (no N+1 problem)
     * @returns {Promise<Array>} Report grouped by course
     */
    async generateFinancialReport() {
        // Use optimized JOIN query from repository
        const data = await EnrollmentRepository.getFinancialReportData();

        // Group by course
        const coursesMap = new Map();

        for (const row of data) {
            const courseId = row.course_id;

            if (!coursesMap.has(courseId)) {
                coursesMap.set(courseId, {
                    course: row.course_title,
                    revenue: 0,
                    students: []
                });
            }

            const courseData = coursesMap.get(courseId);

            // Add revenue if payment was successful
            if (row.payment_status === PAYMENT_STATUS.PAID) {
                courseData.revenue += row.payment_amount || 0;
            }

            // Add student if exists (might be null for courses with no enrollments)
            if (row.student_name) {
                courseData.students.push({
                    student: row.student_name,
                    email: row.student_email,
                    paid: row.payment_amount || 0,
                    status: row.payment_status || 'N/A'
                });
            }
        }

        // Convert map to array
        return Array.from(coursesMap.values());
    }

    /**
     * Get revenue summary
     * @returns {Promise<Object>} Total revenue and course count
     */
    async getRevenueSummary() {
        const report = await this.generateFinancialReport();

        const totalRevenue = report.reduce((sum, course) => sum + course.revenue, 0);
        const totalCourses = report.length;
        const totalStudents = report.reduce((sum, course) => sum + course.students.length, 0);

        return {
            totalRevenue,
            totalCourses,
            totalStudents,
            averageRevenuePerCourse: totalCourses > 0 ? totalRevenue / totalCourses : 0
        };
    }
}

module.exports = new ReportService();
