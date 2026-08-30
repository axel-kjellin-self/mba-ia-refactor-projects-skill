"""Constantes de domínio — substituem os magic numbers espalhados pelo código legado."""

CATEGORIAS_VALIDAS = (
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
)
CATEGORIA_PADRAO = "geral"

STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_ENVIADO = "enviado"
STATUS_ENTREGUE = "entregue"
STATUS_CANCELADO = "cancelado"
STATUS_PEDIDO_VALIDOS = (
    STATUS_PENDENTE,
    STATUS_APROVADO,
    STATUS_ENVIADO,
    STATUS_ENTREGUE,
    STATUS_CANCELADO,
)

TIPO_CLIENTE = "cliente"
TIPO_ADMIN = "admin"
TIPOS_USUARIO_VALIDOS = (TIPO_CLIENTE, TIPO_ADMIN)

# Faixas de desconto sobre o faturamento: (valor mínimo exclusivo, percentual).
# Avaliadas da maior para a menor; a primeira que se aplica vence.
FAIXAS_DESCONTO_FATURAMENTO = (
    (10_000.0, 0.10),
    (5_000.0, 0.05),
    (1_000.0, 0.02),
)

NOME_PRODUTO_TAMANHO_MINIMO = 2
NOME_PRODUTO_TAMANHO_MAXIMO = 200
NOME_USUARIO_TAMANHO_MINIMO = 2
NOME_USUARIO_TAMANHO_MAXIMO = 120
SENHA_TAMANHO_MINIMO = 12
SENHA_TAMANHO_MAXIMO = 128
QUANTIDADE_MAXIMA_POR_ITEM = 1_000
ITENS_MAXIMOS_POR_PEDIDO = 100

PAGINA_PADRAO = 1
ITENS_POR_PAGINA_PADRAO = 50
ITENS_POR_PAGINA_MAXIMO = 200

CASAS_DECIMAIS_MONETARIAS = 2
