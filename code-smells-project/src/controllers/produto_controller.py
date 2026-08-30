"""Controller HTTP de produtos."""

from flask import request

from src.controllers import http
from src.schemas.produto_schema import carregar_busca, carregar_produto
from src.services.produto_service import ProdutoService


class ProdutoController:
    def __init__(self, servico: ProdutoService | None = None) -> None:
        self.servico = servico or ProdutoService()

    def listar(self):
        """GET /produtos"""
        limite, offset = http.paginacao()
        produtos = self.servico.listar(limite, offset)
        return http.ok([p.to_dict() for p in produtos], total=len(produtos))

    def buscar(self, id: int):
        """GET /produtos/<id>"""
        return http.ok(self.servico.buscar(id).to_dict())

    def pesquisar(self):
        """GET /produtos/busca"""
        filtros = carregar_busca(request.args)
        resultados = self.servico.pesquisar(filtros)
        return http.ok([p.to_dict() for p in resultados], total=len(resultados))

    def criar(self):
        """POST /produtos — restrito a administradores."""
        entrada = carregar_produto(http.corpo_json())
        produto = self.servico.criar(entrada)
        return http.ok(produto.to_dict(), status=201, mensagem="Produto criado.")

    def atualizar(self, id: int):
        """PUT /produtos/<id> — restrito a administradores."""
        entrada = carregar_produto(http.corpo_json())
        produto = self.servico.atualizar(id, entrada)
        return http.ok(produto.to_dict(), mensagem="Produto atualizado.")

    def deletar(self, id: int):
        """DELETE /produtos/<id> — restrito a administradores."""
        self.servico.deletar(id)
        return http.mensagem("Produto deletado.")
