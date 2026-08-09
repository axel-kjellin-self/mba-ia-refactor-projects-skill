const database = require('../config/database');
const Enrollment = require('../models/Enrollment');

/**
 * Enrollment Repository
 * Handles database operations for enrollments
 */
class EnrollmentRepository {
    /**
     * Find enrollment by ID
     * @param {number} enrollmentId
     * @returns {Promise<Enrollment|null>}
     */
    async findById(enrollmentId) {
        const row = await database.get('SELECT * FROM enrollments WHERE id = ?', [enrollmentId]);
        return row ? new Enrollment(row) : null;
    }

    /**
     * Find enrollments by user ID
     * @param {number} userId
     * @returns {Promise<Enrollment[]>}
     */
    async findByUserId(userId) {
        const rows = await database.all(
            'SELECT * FROM enrollments WHERE user_id = ?',
            [userId]
        );
        return rows.map(row => new Enrollment(row));
    }

    /**
     * Find enrollments by course ID
     * @param {number} courseId
     * @returns {Promise<Enrollment[]>}
     */
    async findByCourseId(courseId) {
        const rows = await database.all(
            'SELECT * FROM enrollments WHERE course_id = ?',
            [courseId]
        );
        return rows.map(row => new Enrollment(row));
    }

    /**
     * Check if enrollment exists
     * @param {number} userId
     * @param {number} courseId
     * @returns {Promise<boolean>}
     */
    async exists(userId, courseId) {
        const row = await database.get(
            'SELECT id FROM enrollments WHERE user_id = ? AND course_id = ?',
            [userId, courseId]
        );
        return !!row;
    }

    /**
     * Create a new enrollment
     * @param {number} userId
     * @param {number} courseId
     * @returns {Promise<Enrollment>}
     */
    async create(userId, courseId) {
        const result = await database.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId]
        );

        return this.findById(result.lastID);
    }

    /**
     * Get financial report data with JOINs (optimized - no N+1)
     * @returns {Promise<Array>}
     */
    async getFinancialReportData() {
        const query = `
            SELECT
                c.id as course_id,
                c.title as course_title,
                u.name as student_name,
                u.email as student_email,
                p.amount as payment_amount,
                p.status as payment_status
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.course_id
            LEFT JOIN users u ON e.user_id = u.id
            LEFT JOIN payments p ON e.id = p.enrollment_id
            ORDER BY c.id
        `;

        return await database.all(query);
    }
}

module.exports = new EnrollmentRepository();
