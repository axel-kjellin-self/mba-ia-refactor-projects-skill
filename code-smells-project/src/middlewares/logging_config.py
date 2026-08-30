"""Configuração de logging — substitui os ``print()`` espalhados pelo legado."""

import logging
import sys

_FORMATO = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"


def configurar_logging(nivel: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, nivel, logging.INFO),
        format=_FORMATO,
        stream=sys.stdout,
        force=True,
    )
