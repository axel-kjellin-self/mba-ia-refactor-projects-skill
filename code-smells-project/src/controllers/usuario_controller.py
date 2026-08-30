"""Controllers de usuário e autenticação."""

from flask import current_app, request

from src.controllers.http import parametros_de_paginacao, sucesso
from src.middlewares.auth import carregar_usuario_autenticado
from src.schemas.usuario_schema import validar_login, validar_novo_usuario
from src.services import auth_service, usuario_service
from src.utils.errors import ForbiddenError


def listar_usuarios():
    pagina, por_pagina = parametros_de_paginacao()
    return sucesso(usuario_service.listar(pagina, por_pagina))


def buscar_usuario(usuario_id: int):
    solicitante = carregar_usuario_autenticado()
    if not solicitante.is_admin and solicitante.id != usuario_id:
        raise ForbiddenError("Você só pode consultar o seu próprio cadastro")
    return sucesso(usuario_service.buscar(usuario_id))


def criar_usuario():
    dados = validar_novo_usuario(request.get_json(silent=True))
    return sucesso(auth_service.registrar(dados), status=201, mensagem="Usuário criado")


def login():
    dados = validar_login(request.get_json(silent=True))
    resultado = auth_service.autenticar(dados, current_app.config["SETTINGS"])
    return sucesso(resultado, mensagem="Login realizado")


def perfil():
    return sucesso(carregar_usuario_autenticado().to_dict())
