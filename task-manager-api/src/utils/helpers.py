"""Utilitários genéricos.

As demais funções deste módulo (`process_task_data`, `generate_id`,
`sanitize_string`, `validate_email`, `log_action`, `is_valid_color`,
`format_date`) foram removidas: nenhuma era chamada, e as regras que
duplicavam agora vivem em `schemas/` e `config/constants.py`.
"""
from datetime import datetime

from src.config.constants import DATE_FORMAT

ALTERNATE_DATE_FORMATS = (DATE_FORMAT, '%d/%m/%Y')


def parse_date(date_string: str) -> datetime | None:
    """Converte string de data nos formatos aceitos. Devolve None se inválida."""
    for fmt in ALTERNATE_DATE_FORMATS:
        try:
            return datetime.strptime(date_string, fmt)
        except (ValueError, TypeError):
            continue
    return None
