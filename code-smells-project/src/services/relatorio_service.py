"""Regras de negócio de relatórios."""

from typing import Any

from src.config.constants import FaixaDesconto
from src.repositories.relatorio_repository import RelatorioRepository


class RelatorioService:
    def __init__(self, repositorio: RelatorioRepository | None = None) -> None:
        self.repositorio = repositorio or RelatorioRepository()

    @staticmethod
    def calcular_desconto(faturamento: float) -> float:
        """Aplica a faixa de desconto correspondente ao faturamento.

        Função pura: testável sem banco e sem HTTP, ao contrário da versão
        anterior embutida na query do relatório.
        """
        for limite, taxa in FaixaDesconto.FAIXAS:
            if faturamento > limite:
                return round(faturamento * taxa, 2)
        return 0.0

    def vendas(self) -> dict[str, Any]:
        agregado = self.repositorio.agregado_vendas()
        desconto = self.calcular_desconto(agregado.faturamento_bruto)

        ticket_medio = (
            round(agregado.faturamento_bruto / agregado.total_pedidos, 2)
            if agregado.total_pedidos
            else 0.0
        )

        return {
            "total_pedidos": agregado.total_pedidos,
            "faturamento_bruto": round(agregado.faturamento_bruto, 2),
            "desconto_aplicavel": desconto,
            "faturamento_liquido": round(agregado.faturamento_bruto - desconto, 2),
            "pedidos_pendentes": agregado.pendentes,
            "pedidos_aprovados": agregado.aprovados,
            "pedidos_cancelados": agregado.cancelados,
            "ticket_medio": ticket_medio,
        }

    def health(self) -> dict[str, Any]:
        """Status mínimo do serviço.

        Deliberadamente não expõe SECRET_KEY, caminho do banco, flag de debug
        nem contagens de registros, como fazia o ``/health`` original.
        """
        conectado = self.repositorio.verificar_conexao()
        return {
            "status": "ok" if conectado else "degradado",
            "database": "connected" if conectado else "down",
        }
