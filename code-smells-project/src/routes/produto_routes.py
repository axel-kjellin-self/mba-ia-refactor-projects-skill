"""Rotas de produto. A camada de rota só mapeia URL → controller + guarda de acesso."""

from flask import Blueprint

from src.controllers import produto_controller
from src.middlewares.auth import admin_required

produto_bp = Blueprint("produtos", __name__, url_prefix="/produtos")

# Leitura é pública (catálogo); escrita exige administrador.
produto_bp.get("")(produto_controller.listar_produtos)
produto_bp.get("/busca")(produto_controller.buscar_produtos)
produto_bp.get("/<int:produto_id>")(produto_controller.buscar_produto)
produto_bp.post("")(admin_required(produto_controller.criar_produto))
produto_bp.put("/<int:produto_id>")(admin_required(produto_controller.atualizar_produto))
produto_bp.delete("/<int:produto_id>")(admin_required(produto_controller.deletar_produto))
