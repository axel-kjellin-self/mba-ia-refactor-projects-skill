const UserRepository = require('../repositories/UserRepository');

/**
 * User Controller
 * Handles HTTP requests for user operations
 */
class UserController {
    /**
     * DELETE /api/users/:id
     * Delete a user (requires authentication and authorization)
     */
    async deleteUser(req, res, next) {
        try {
            const userId = parseInt(req.params.id);

            // Check authorization: user can only delete themselves, or must be admin
            if (req.user.userId !== userId && req.user.role !== 'admin') {
                return res.status(403).json({ error: 'Forbidden: You can only delete your own account' });
            }

            const deleted = await UserRepository.delete(userId);

            if (!deleted) {
                return res.status(404).json({ error: 'User not found' });
            }

            // Cascade deletes handled by database constraints
            return res.status(204).send();

        } catch (error) {
            next(error);
        }
    }

    /**
     * GET /api/users/:id
     * Get user by ID
     */
    async getUser(req, res, next) {
        try {
            const userId = parseInt(req.params.id);

            const user = await UserRepository.findById(userId);

            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }

            return res.status(200).json({ user: user.toJSON() });

        } catch (error) {
            next(error);
        }
    }
}

module.exports = new UserController();
