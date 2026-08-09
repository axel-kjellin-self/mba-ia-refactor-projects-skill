const express = require('express');
const AuthController = require('../controllers/AuthController');
const { asyncHandler } = require('../middlewares/errorHandler');

const router = express.Router();

/**
 * POST /api/auth/login
 * User login with email and password
 */
router.post('/login', asyncHandler(AuthController.login.bind(AuthController)));

/**
 * POST /api/auth/register
 * User registration
 */
router.post('/register', asyncHandler(AuthController.register.bind(AuthController)));

module.exports = router;
