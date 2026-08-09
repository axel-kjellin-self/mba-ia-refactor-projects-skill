from src.models.usuario import Usuario
from src.config.database import db
from src.config.constants import ValidationRules


class UsuarioService:
    """Business logic for user operations"""

    @staticmethod
    def criar_usuario(nome, email, senha, tipo='cliente'):
        """
        Create a new user with password validation

        Args:
            nome: User's name
            email: User's email
            senha: Plain text password (will be hashed)
            tipo: User type (admin or cliente)

        Returns:
            Created Usuario instance

        Raises:
            ValueError: If validation fails
        """
        # Validation
        if not nome or not email or not senha:
            raise ValueError("Nome, email e senha são obrigatórios")

        if len(senha) < ValidationRules.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Senha deve ter no mínimo {ValidationRules.MIN_PASSWORD_LENGTH} caracteres"
            )

        # Check if email already exists
        if Usuario.query.filter_by(email=email).first():
            raise ValueError(f"Email {email} já está cadastrado")

        # Create user
        usuario = Usuario(nome=nome, email=email, tipo=tipo)
        usuario.set_password(senha)

        db.session.add(usuario)
        db.session.commit()

        return usuario

    @staticmethod
    def autenticar(email, senha):
        """
        Authenticate user by email and password

        Args:
            email: User's email
            senha: Plain text password

        Returns:
            Usuario instance if authentication successful, None otherwise
        """
        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.check_password(senha):
            return usuario

        return None

    @staticmethod
    def buscar_por_id(usuario_id):
        """Find user by ID"""
        return Usuario.query.get(usuario_id)

    @staticmethod
    def buscar_por_email(email):
        """Find user by email"""
        return Usuario.query.filter_by(email=email).first()

    @staticmethod
    def listar_todos():
        """List all users"""
        return Usuario.query.all()
