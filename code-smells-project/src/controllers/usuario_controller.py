"""Controller HTTP de usuários e autenticação."""

from src.config.settings import Config
from src.controllers import http
from src.schemas.usuario_schema import carregar_login, carregar_usuario
from src.services.auth_service import AuthService
from src.services.usuario_service import UsuarioService


class UsuarioController:
    def __init__(
        self,
        servico: UsuarioService | None = None,
        auth: AuthService | None = None,
    ) -> None:
        self.servico = servico or UsuarioService()
        self.auth = auth or AuthService()

    def listar(self):
        """GET /usuarios — restrito a administradores."""
        limite, offset = http.paginacao()
        usuarios = self.servico.listar(limite, offset)
        return http.ok([u.to_dict() for u in usuarios], total=len(usuarios))

    def buscar(self, usuario_id: int):
        """GET /usuarios/<usuario_id> — próprio usuário ou administrador."""
        return http.ok(self.servico.buscar(usuario_id).to_dict())

    def criar(self):
        """POST /usuarios — cadastro público, sempre como cliente."""
        entrada = carregar_usuario(http.corpo_json())
        usuario = self.servico.criar(entrada)
        return http.ok(usuario.to_dict(), status=201, mensagem="Usuário criado.")

    def login(self):
        """POST /login — emite o token de acesso."""
        entrada = carregar_login(http.corpo_json())
        token, usuario = self.auth.autenticar(entrada)

        return http.ok(
            {
                "token": token,
                "token_type": "Bearer",
                "expira_em": Config.JWT_EXPIRES_SECONDS,
                "usuario": usuario.to_dict(),
            },
            mensagem="Login realizado com sucesso.",
        )
