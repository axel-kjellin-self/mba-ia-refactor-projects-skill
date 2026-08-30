"""Primitivas de validação reutilizáveis.

Substituem os blocos de ``if`` ad-hoc espalhados pelos controllers legados, que
divergiam entre endpoints e deixavam passar erros de tipo (transformados em 500).
"""

import re

from src.utils.errors import ValidationError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")


def exigir_dict(dados, nome: str = "corpo da requisição") -> dict:
    if not isinstance(dados, dict) or not dados:
        raise ValidationError(f"O {nome} deve ser um objeto JSON não vazio")
    return dados


def texto(
    dados: dict,
    campo: str,
    *,
    obrigatorio: bool = True,
    minimo: int = 0,
    maximo: int | None = None,
    padrao: str = "",
) -> str:
    if campo not in dados or dados[campo] is None:
        if obrigatorio:
            raise ValidationError(f"'{campo}' é obrigatório")
        return padrao

    valor = dados[campo]
    if not isinstance(valor, str):
        raise ValidationError(f"'{campo}' deve ser texto")

    valor = valor.strip()
    if obrigatorio and not valor:
        raise ValidationError(f"'{campo}' é obrigatório")
    if valor and len(valor) < minimo:
        raise ValidationError(f"'{campo}' deve ter ao menos {minimo} caracteres")
    if maximo is not None and len(valor) > maximo:
        raise ValidationError(f"'{campo}' deve ter no máximo {maximo} caracteres")
    return valor


def numero(
    dados: dict,
    campo: str,
    *,
    obrigatorio: bool = True,
    minimo: float | None = None,
    maximo: float | None = None,
    padrao: float | None = None,
) -> float | None:
    if campo not in dados or dados[campo] is None:
        if obrigatorio:
            raise ValidationError(f"'{campo}' é obrigatório")
        return padrao

    valor = dados[campo]
    # bool é subclasse de int em Python: True passaria como 1 sem esta checagem.
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidationError(f"'{campo}' deve ser numérico")
    return _checar_faixa(float(valor), campo, minimo, maximo)


def inteiro(
    dados: dict,
    campo: str,
    *,
    obrigatorio: bool = True,
    minimo: int | None = None,
    maximo: int | None = None,
    padrao: int | None = None,
) -> int | None:
    if campo not in dados or dados[campo] is None:
        if obrigatorio:
            raise ValidationError(f"'{campo}' é obrigatório")
        return padrao

    valor = dados[campo]
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValidationError(f"'{campo}' deve ser um número inteiro")
    return int(_checar_faixa(valor, campo, minimo, maximo))


def _checar_faixa(valor: float, campo: str, minimo, maximo) -> float:
    if minimo is not None and valor < minimo:
        raise ValidationError(f"'{campo}' deve ser maior ou igual a {minimo}")
    if maximo is not None and valor > maximo:
        raise ValidationError(f"'{campo}' deve ser menor ou igual a {maximo}")
    return valor


def opcao(valor: str, campo: str, opcoes) -> str:
    if valor not in opcoes:
        raise ValidationError(f"'{campo}' inválido. Valores aceitos: {', '.join(opcoes)}")
    return valor


def email(dados: dict, campo: str = "email") -> str:
    valor = texto(dados, campo, minimo=3, maximo=254).lower()
    if not _EMAIL_RE.match(valor):
        raise ValidationError("Email em formato inválido")
    return valor


def numero_de_query(valor: str | None, campo: str, minimo: float | None = None):
    """Converte um parâmetro de query string, devolvendo 400 (e não 500) se inválido."""
    if valor is None or valor.strip() == "":
        return None
    try:
        convertido = float(valor)
    except ValueError as exc:
        raise ValidationError(f"'{campo}' deve ser numérico") from exc
    return _checar_faixa(convertido, campo, minimo, None)


def inteiro_de_query(valor: str | None, campo: str, padrao: int, minimo: int, maximo: int) -> int:
    if valor is None or valor.strip() == "":
        return padrao
    try:
        convertido = int(valor)
    except ValueError as exc:
        raise ValidationError(f"'{campo}' deve ser um número inteiro") from exc
    return int(_checar_faixa(convertido, campo, minimo, maximo))
