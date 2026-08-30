"""Regras de negócio de relatórios.

O cálculo de desconto vive aqui (e não dentro da camada de dados, como no
legado), podendo ser testado sem banco através de ``calcular_desconto``.
"""

from src.config.constants import CASAS_DECIMAIS_MONETARIAS, FAIXAS_DESCONTO_FATURAMENTO
from src.repositories import relatorio_repository


def calcular_desconto(faturamento: float) -> float:
    """Aplica a primeira faixa de desconto cujo piso o faturamento ultrapassa."""
    for piso, percentual in FAIXAS_DESCONTO_FATURAMENTO:
        if faturamento > piso:
            return faturamento * percentual
    return 0.0


def _arredondar(valor: float) -> float:
    return round(valor, CASAS_DECIMAIS_MONETARIAS)


def gerar_relatorio_de_vendas() -> dict:
    resumo = relatorio_repository.resumo_vendas()
    total_pedidos = resumo["total_pedidos"]
    faturamento = resumo["faturamento"]
    desconto = calcular_desconto(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": _arredondar(faturamento),
        "desconto_aplicavel": _arredondar(desconto),
        "faturamento_liquido": _arredondar(faturamento - desconto),
        "ticket_medio": _arredondar(faturamento / total_pedidos) if total_pedidos else 0,
        "pedidos_por_status": resumo["por_status"],
    }


def status_da_aplicacao() -> dict:
    """Health check sem dados sensíveis — o legado devolvia a SECRET_KEY aqui."""
    return {
        "status": "ok",
        "database": "connected",
        "counts": relatorio_repository.contagens_health(),
    }
