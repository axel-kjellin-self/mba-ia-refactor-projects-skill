"""Application constants"""


class DiscountTiers:
    """Discount tiers based on total purchase amount"""
    TIER_1_THRESHOLD = 10000
    TIER_1_RATE = 0.10  # 10%

    TIER_2_THRESHOLD = 5000
    TIER_2_RATE = 0.05  # 5%

    TIER_3_THRESHOLD = 1000
    TIER_3_RATE = 0.02  # 2%


class ValidationRules:
    """Validation rules for inputs"""
    MIN_PASSWORD_LENGTH = 8

    MIN_PRODUCT_NAME_LENGTH = 2
    MAX_PRODUCT_NAME_LENGTH = 200

    MAX_DESCRIPTION_LENGTH = 1000

    MIN_PRIORITY = 1
    MAX_PRIORITY = 5


class PedidoStatus:
    """Valid order statuses"""
    PENDENTE = 'pendente'
    APROVADO = 'aprovado'
    ENVIADO = 'enviado'
    ENTREGUE = 'entregue'
    CANCELADO = 'cancelado'

    ALL = [PENDENTE, APROVADO, ENVIADO, ENTREGUE, CANCELADO]


class UsuarioTipo:
    """Valid user types"""
    ADMIN = 'admin'
    CLIENTE = 'cliente'

    ALL = [ADMIN, CLIENTE]


class CategoriaProduto:
    """Valid product categories"""
    INFORMATICA = 'informatica'
    MOVEIS = 'moveis'
    VESTUARIO = 'vestuario'
    ELETRONICOS = 'eletronicos'
    LIVROS = 'livros'
    GERAL = 'geral'

    ALL = [INFORMATICA, MOVEIS, VESTUARIO, ELETRONICOS, LIVROS, GERAL]
