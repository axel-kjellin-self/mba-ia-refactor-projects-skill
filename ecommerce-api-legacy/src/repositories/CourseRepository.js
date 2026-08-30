/** Acesso a dados da entidade `courses`. */
class CourseRepository {
    constructor(db) {
        this.db = db;
    }

    findById(id, executor = this.db) {
        return executor.get('SELECT * FROM courses WHERE id = ?', [id]);
    }

    findActiveById(id, executor = this.db) {
        return executor.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
    }

    findAll(executor = this.db) {
        return executor.all('SELECT * FROM courses ORDER BY id');
    }
}

module.exports = CourseRepository;
