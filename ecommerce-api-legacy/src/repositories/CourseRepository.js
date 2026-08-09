const database = require('../config/database');
const Course = require('../models/Course');

/**
 * Course Repository
 * Handles database operations for courses
 */
class CourseRepository {
    /**
     * Find course by ID
     * @param {number} courseId
     * @returns {Promise<Course|null>}
     */
    async findById(courseId) {
        const row = await database.get('SELECT * FROM courses WHERE id = ?', [courseId]);
        return row ? new Course(row) : null;
    }

    /**
     * Find active course by ID
     * @param {number} courseId
     * @returns {Promise<Course|null>}
     */
    async findActiveById(courseId) {
        const row = await database.get(
            'SELECT * FROM courses WHERE id = ? AND active = 1',
            [courseId]
        );
        return row ? new Course(row) : null;
    }

    /**
     * Find all courses
     * @param {boolean} activeOnly - Filter only active courses
     * @returns {Promise<Course[]>}
     */
    async findAll(activeOnly = false) {
        const query = activeOnly
            ? 'SELECT * FROM courses WHERE active = 1'
            : 'SELECT * FROM courses';

        const rows = await database.all(query);
        return rows.map(row => new Course(row));
    }

    /**
     * Create a new course
     * @param {Object} courseData - { title, price, active }
     * @returns {Promise<Course>}
     */
    async create(courseData) {
        const result = await database.run(
            'INSERT INTO courses (title, price, active) VALUES (?, ?, ?)',
            [courseData.title, courseData.price, courseData.active ?? 1]
        );

        return this.findById(result.lastID);
    }
}

module.exports = new CourseRepository();
