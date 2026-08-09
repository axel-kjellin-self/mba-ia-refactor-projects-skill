/**
 * Course Model
 * Represents a course entity
 */
class Course {
    constructor(data) {
        this.id = data.id;
        this.title = data.title;
        this.price = parseFloat(data.price);
        this.active = Boolean(data.active);
        this.created_at = data.created_at;
    }

    /**
     * Convert course to JSON
     * @returns {Object}
     */
    toJSON() {
        return {
            id: this.id,
            title: this.title,
            price: this.price,
            active: this.active,
            created_at: this.created_at
        };
    }

    /**
     * Check if course is available for enrollment
     * @returns {boolean}
     */
    isAvailable() {
        return this.active === true;
    }
}

module.exports = Course;
