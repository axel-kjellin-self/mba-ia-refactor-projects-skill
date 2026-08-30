"""Rotas de produtos.

Leitura é pública; escrita exige papel de administrador.
"""

from flask import Blueprint

from src.controllers.produto_controller import ProdutoController
from src.middlewares.auth import require_admin

produto_bp = Blueprint("produtos", __name__, url_prefix="/produtos")
_controller = ProdutoController()

produto_bp.get("")(_controller.listar)
produto_bp.get("/busca")(_controller.pesquisar)
produto_bp.get("/<int:id>")(_controller.buscar)

produto_bp.post("")(require_admin(_controller.criar))
produto_bp.put("/<int:id>")(require_admin(_controller.atualizar))
produto_bp.delete("/<int:id>")(require_admin(_controller.deletar))
