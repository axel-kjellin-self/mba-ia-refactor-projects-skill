"""Regras de negócio de produtos."""

from src.config.database import transacao
from src.models.produto import Produto
from src.repositories.produto_repository import ProdutoRepository
from src.schemas.produto_schema import BuscaProdutoInput, ProdutoInput
from src.utils.errors import NotFoundError, ValidationError


class ProdutoService:
    def __init__(self, repositorio: ProdutoRepository | None = None) -> None:
        self.repositorio = repositorio or ProdutoRepository()

    def listar(self, limite: int, offset: int = 0) -> list[Produto]:
        return self.repositorio.listar(limite, offset)

    def buscar(self, produto_id: int) -> Produto:
        produto = self.repositorio.buscar_por_id(produto_id)
        if produto is None:
            raise NotFoundError(f"Produto {produto_id} não encontrado.")
        return produto

    def pesquisar(self, filtros: BuscaProdutoInput) -> list[Produto]:
        if (
            filtros.preco_min is not None
            and filtros.preco_max is not None
            and filtros.preco_min > filtros.preco_max
        ):
            raise ValidationError("'preco_min' não pode ser maior que 'preco_max'.")

        return self.repositorio.pesquisar(
            termo=filtros.termo,
            categoria=filtros.categoria,
            preco_min=filtros.preco_min,
            preco_max=filtros.preco_max,
            limite=filtros.limite,
            offset=filtros.offset,
        )

    def criar(self, entrada: ProdutoInput) -> Produto:
        with transacao():
            produto_id = self.repositorio.criar(
                entrada.nome,
                entrada.descricao,
                entrada.preco,
                entrada.estoque,
                entrada.categoria,
            )
        return self.buscar(produto_id)

    def atualizar(self, produto_id: int, entrada: ProdutoInput) -> Produto:
        self.buscar(produto_id)  # garante existência antes de escrever

        with transacao():
            self.repositorio.atualizar(
                produto_id,
                entrada.nome,
                entrada.descricao,
                entrada.preco,
                entrada.estoque,
                entrada.categoria,
            )
        return self.buscar(produto_id)

    def deletar(self, produto_id: int) -> None:
        self.buscar(produto_id)
        with transacao():
            self.repositorio.deletar(produto_id)
