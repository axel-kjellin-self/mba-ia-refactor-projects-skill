/**
 * Enrollment Model
 * Represents a student enrollment in a course
 */
class Enrollment {
    constructor(data) {
        this.id = data.id;
        this.user_id = data.user_id;
        this.course_id = data.course_id;
        this.created_at = data.created_at;
    }

    /**
     * Convert enrollment to JSON
     * @returns {Object}
     */
    toJSON() {
        return {
            id: this.id,
            user_id: this.user_id,
            course_id: this.course_id,
            created_at: this.created_at
        };
    }
}

module.exports = Enrollment;
