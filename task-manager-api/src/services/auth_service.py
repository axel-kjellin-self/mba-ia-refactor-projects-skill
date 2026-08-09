import jwt
from datetime import datetime, timedelta
from src.models.user import User
from src.config.settings import Config
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication business logic"""

    @staticmethod
    def login(email, password):
        """
        Authenticate user and generate JWT token

        Args:
            email: User email
            password: User password (plaintext)

        Returns:
            dict with token and user data

        Raises:
            ValueError: If credentials are invalid or user is inactive
        """
        user = User.query.filter_by(email=email).first()

        if not user:
            logger.warning(f"Login attempt with non-existent email: {email}")
            raise ValueError("Invalid credentials")

        if not user.check_password(password):
            logger.warning(f"Failed login attempt for user: {email}")
            raise ValueError("Invalid credentials")

        if not user.active:
            logger.warning(f"Login attempt for inactive user: {email}")
            raise ValueError("User account is inactive")

        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'email': user.email,
                'role': user.role,
                'exp': datetime.utcnow() + timedelta(seconds=Config.JWT_ACCESS_TOKEN_EXPIRES)
            },
            Config.JWT_SECRET_KEY,
            algorithm='HS256'
        )

        logger.info(f"User logged in successfully: {user.email}")

        return {
            'token': token,
            'user': user.to_dict()
        }

    @staticmethod
    def verify_token(token):
        """
        Verify JWT token and extract payload

        Args:
            token: JWT token string

        Returns:
            dict with user_id, email, role

        Raises:
            jwt.ExpiredSignatureError: If token is expired
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Expired token")
            raise

        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            raise
