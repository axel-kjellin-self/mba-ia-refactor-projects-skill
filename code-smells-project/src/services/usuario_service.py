"""Regras de negócio de usuário (consulta; cadastro fica em auth_service)."""

from src.config.constants import ITENS_POR_PAGINA_PADRAO, PAGINA_PADRAO
from src.repositories import usuario_repository
from src.utils.errors import NotFoundError


def listar(pagina: int = PAGINA_PADRAO, por_pagina: int = ITENS_POR_PAGINA_PADRAO) -> dict:
    usuarios = usuario_repository.listar(por_pagina, (pagina - 1) * por_pagina)
    return {
        "itens": [usuario.to_dict() for usuario in usuarios],
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": usuario_repository.contar(),
    }


def buscar(usuario_id: int) -> dict:
    usuario = usuario_repository.buscar_por_id(usuario_id)
    if usuario is None:
        raise NotFoundError("Usuário não encontrado")
    return usuario.to_dict()
