from flask import request, jsonify
from src.services.usuario_service import UsuarioService
from src.middlewares.auth import gerar_token
import logging

logger = logging.getLogger(__name__)

usuario_service = UsuarioService()


class UsuarioController:
    """Controller for user-related operations"""

    @staticmethod
    def listar_usuarios():
        """GET /usuarios - List all users (without passwords!)"""
        try:
            usuarios = usuario_service.listar_todos()
            return jsonify({
                'dados': [u.to_dict() for u in usuarios],
                'sucesso': True
            }), 200

        except Exception as e:
            logger.error(f"Erro ao listar usuários: {e}")
            raise

    @staticmethod
    def buscar_usuario(usuario_id):
        """GET /usuarios/<id> - Get user by ID"""
        try:
            usuario = usuario_service.buscar_por_id(usuario_id)

            if not usuario:
                return jsonify({
                    'erro': 'Usuário não encontrado',
                    'sucesso': False
                }), 404

            return jsonify({
                'dados': usuario.to_dict(),
                'sucesso': True
            }), 200

        except Exception as e:
            logger.error(f"Erro ao buscar usuário: {e}")
            raise

    @staticmethod
    def criar_usuario():
        """POST /usuarios - Create new user"""
        try:
            dados = request.get_json()

            if not dados:
                return jsonify({'erro': 'Dados inválidos'}), 400

            nome = dados.get('nome')
            email = dados.get('email')
            senha = dados.get('senha')
            tipo = dados.get('tipo', 'cliente')

            # Delegate to service (includes validation)
            usuario = usuario_service.criar_usuario(nome, email, senha, tipo)

            logger.info(f"Usuário criado: {email}")

            return jsonify({
                'dados': usuario.to_dict(),
                'sucesso': True,
                'mensagem': 'Usuário criado com sucesso'
            }), 201

        except ValueError as e:
            # Business logic error
            return jsonify({'erro': str(e)}), 400

        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            raise

    @staticmethod
    def login():
        """POST /login - Authenticate user and return JWT token"""
        try:
            dados = request.get_json()

            if not dados:
                return jsonify({'erro': 'Dados inválidos'}), 400

            email = dados.get('email')
            senha = dados.get('senha')

            if not email or not senha:
                return jsonify({'erro': 'Email e senha são obrigatórios'}), 400

            # Authenticate
            usuario = usuario_service.autenticar(email, senha)

            if not usuario:
                logger.warning(f"Login falhou: {email}")
                return jsonify({
                    'erro': 'Email ou senha inválidos',
                    'sucesso': False
                }), 401

            # Generate JWT token
            token = gerar_token(usuario)

            logger.info(f"Login bem-sucedido: {email}")

            return jsonify({
                'token': token,
                'usuario': usuario.to_dict(),
                'sucesso': True,
                'mensagem': 'Login realizado com sucesso'
            }), 200

        except Exception as e:
            logger.error(f"Erro no login: {e}")
            raise
