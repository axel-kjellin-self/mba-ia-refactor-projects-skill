/** Acesso a dados da entidade `enrollments`. */
class EnrollmentRepository {
    constructor(db) {
        this.db = db;
    }

    findById(id, executor = this.db) {
        return executor.get('SELECT * FROM enrollments WHERE id = ?', [id]);
    }

    findByUserAndCourse(userId, courseId, executor = this.db) {
        return executor.get(
            'SELECT * FROM enrollments WHERE user_id = ? AND course_id = ?',
            [userId, courseId]
        );
    }

    async create({ userId, courseId }, executor = this.db) {
        const { lastID } = await executor.run(
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId]
        );
        return lastID;
    }
}

module.exports = EnrollmentRepository;
