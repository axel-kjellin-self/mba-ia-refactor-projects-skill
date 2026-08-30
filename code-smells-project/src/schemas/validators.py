"""Primitivas de validação de entrada.

Cada função valida tipo *antes* de faixa — o código original comparava
``preco < 0`` sem checar o tipo, o que transformava ``{"preco": "abc"}`` num
TypeError capturado como erro 500.
"""

import re
from typing import Any

from src.utils.errors import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+(\.[^@\s.]+)+$")


def exigir_objeto(dados: Any) -> dict[str, Any]:
    """Garante que o corpo do request é um objeto JSON."""
    if not isinstance(dados, dict):
        raise ValidationError("Corpo da requisição deve ser um objeto JSON.")
    return dados


def texto(
    dados: dict[str, Any],
    campo: str,
    *,
    obrigatorio: bool = True,
    minimo: int = 0,
    maximo: int = 255,
    padrao: str | None = None,
) -> str:
    valor = dados.get(campo, padrao)

    if valor is None or (isinstance(valor, str) and not valor.strip()):
        if obrigatorio:
            raise ValidationError(f"'{campo}' é obrigatório.", {campo: "obrigatório"})
        return padrao if padrao is not None else ""

    if not isinstance(valor, str):
        raise ValidationError(f"'{campo}' deve ser texto.", {campo: "tipo inválido"})

    valor = valor.strip()
    if len(valor) < minimo:
        raise ValidationError(
            f"'{campo}' deve ter no mínimo {minimo} caracteres.", {campo: "muito curto"}
        )
    if len(valor) > maximo:
        raise ValidationError(
            f"'{campo}' deve ter no máximo {maximo} caracteres.", {campo: "muito longo"}
        )
    return valor


def numero(
    dados: dict[str, Any],
    campo: str,
    *,
    obrigatorio: bool = True,
    minimo: float | None = None,
    maximo: float | None = None,
    padrao: float | None = None,
) -> float:
    valor = dados.get(campo, padrao)

    if valor is None:
        if obrigatorio:
            raise ValidationError(f"'{campo}' é obrigatório.", {campo: "obrigatório"})
        return padrao

    # bool é subclasse de int em Python; aceitar True como número seria um bug.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidationError(f"'{campo}' deve ser numérico.", {campo: "tipo inválido"})

    return _checar_faixa(float(valor), campo, minimo, maximo)


def inteiro(
    dados: dict[str, Any],
    campo: str,
    *,
    obrigatorio: bool = True,
    minimo: int | None = None,
    maximo: int | None = None,
    padrao: int | None = None,
) -> int:
    valor = dados.get(campo, padrao)

    if valor is None:
        if obrigatorio:
            raise ValidationError(f"'{campo}' é obrigatório.", {campo: "obrigatório"})
        return padrao

    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValidationError(f"'{campo}' deve ser um inteiro.", {campo: "tipo inválido"})

    return int(_checar_faixa(valor, campo, minimo, maximo))


def escolha(
    dados: dict[str, Any],
    campo: str,
    opcoes: tuple[str, ...],
    *,
    obrigatorio: bool = True,
    padrao: str | None = None,
) -> str:
    valor = dados.get(campo, padrao)

    if valor is None:
        if obrigatorio:
            raise ValidationError(f"'{campo}' é obrigatório.", {campo: "obrigatório"})
        return padrao

    if valor not in opcoes:
        raise ValidationError(
            f"'{campo}' inválido. Valores aceitos: {', '.join(opcoes)}.",
            {campo: "valor não permitido"},
        )
    return valor


def email(dados: dict[str, Any], campo: str, *, maximo: int = 254) -> str:
    valor = texto(dados, campo, minimo=3, maximo=maximo).lower()
    if not _EMAIL_RE.match(valor):
        raise ValidationError("Formato de e-mail inválido.", {campo: "formato inválido"})
    return valor


def lista(
    dados: dict[str, Any], campo: str, *, minimo: int = 1, maximo: int = 100
) -> list[Any]:
    valor = dados.get(campo)

    if not isinstance(valor, list):
        raise ValidationError(f"'{campo}' deve ser uma lista.", {campo: "tipo inválido"})
    if len(valor) < minimo:
        raise ValidationError(
            f"'{campo}' deve conter ao menos {minimo} item(ns).", {campo: "muito curta"}
        )
    if len(valor) > maximo:
        raise ValidationError(
            f"'{campo}' deve conter no máximo {maximo} itens.", {campo: "muito longa"}
        )
    return valor


def numero_query(valor: str | None, campo: str, *, minimo: float | None = None) -> float | None:
    """Converte um parâmetro de query string, sinalizando 400 em vez de 500."""
    if valor is None or valor == "":
        return None
    try:
        convertido = float(valor)
    except ValueError:
        raise ValidationError(
            f"'{campo}' deve ser numérico.", {campo: "tipo inválido"}
        ) from None
    return _checar_faixa(convertido, campo, minimo, None)


def inteiro_query(
    valor: str | None, campo: str, *, padrao: int, minimo: int, maximo: int
) -> int:
    if valor is None or valor == "":
        return padrao
    try:
        convertido = int(valor)
    except ValueError:
        raise ValidationError(
            f"'{campo}' deve ser um inteiro.", {campo: "tipo inválido"}
        ) from None
    return int(_checar_faixa(convertido, campo, minimo, maximo))


def _checar_faixa(
    valor: float, campo: str, minimo: float | None, maximo: float | None
) -> float:
    if minimo is not None and valor < minimo:
        raise ValidationError(
            f"'{campo}' deve ser maior ou igual a {minimo}.", {campo: "abaixo do mínimo"}
        )
    if maximo is not None and valor > maximo:
        raise ValidationError(
            f"'{campo}' deve ser menor ou igual a {maximo}.", {campo: "acima do máximo"}
        )
    return valor
