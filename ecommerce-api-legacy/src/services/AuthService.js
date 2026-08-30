const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const { config } = require('../config');
const { Security } = require('../config/constants');
const { UnauthorizedError } = require('../utils/errors');

/**
 * Autenticação e hashing de senhas.
 *
 * Substitui `badCrypto()`, que concatenava base64 e truncava em 10 caracteres —
 * sem salt e trivialmente reversível. Agora: bcrypt com salt automático.
 */
class AuthService {
    constructor(userRepository) {
        this.userRepository = userRepository;
    }

    hashPassword(plainPassword) {
        return bcrypt.hash(plainPassword, Security.BCRYPT_SALT_ROUNDS);
    }

    verifyPassword(plainPassword, hash) {
        return bcrypt.compare(plainPassword, hash);
    }

    /**
     * Valida credenciais e emite um JWT.
     * @throws {UnauthorizedError} credenciais inválidas
     */
    async login(email, password) {
        const user = await this.userRepository.findByEmailWithPassword(email);

        // Mensagem genérica em ambos os casos: distinguir "email não existe" de
        // "senha errada" permite enumeração de usuários.
        const isValid = user && (await this.verifyPassword(password, user.pass));
        if (!isValid) {
            throw new UnauthorizedError('Credenciais inválidas');
        }

        return {
            token: this.issueToken(user),
            user: { id: user.id, name: user.name, email: user.email, role: user.role },
        };
    }

    issueToken(user) {
        return jwt.sign(
            { sub: user.id, role: user.role },
            config.jwt.secret,
            { expiresIn: config.jwt.expiresIn, algorithm: Security.JWT_ALGORITHM }
        );
    }

    /** @throws {UnauthorizedError} token ausente, expirado ou adulterado */
    verifyToken(token) {
        try {
            return jwt.verify(token, config.jwt.secret, {
                algorithms: [Security.JWT_ALGORITHM],
            });
        } catch (err) {
            const message =
                err.name === 'TokenExpiredError' ? 'Token expirado' : 'Token inválido';
            throw new UnauthorizedError(message);
        }
    }
}

module.exports = AuthService;
