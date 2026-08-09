# MVC Architecture Guidelines

Este documento define o padrão MVC alvo para refatoração, incluindo responsabilidades de cada camada e estrutura de diretórios.

---

## Visão Geral do Padrão MVC

**MVC (Model-View-Controller)** separa a aplicação em três camadas principais:

- **Model**: Dados e lógica de acesso a dados
- **View**: Apresentação (em APIs REST, são as rotas/endpoints)
- **Controller**: Orquestração entre Model e View, delegando para Services

### Variação MVCS (MVC + Service Layer)

Para aplicações de maior complexidade, adicionamos uma camada de **Service**:

- **Model**: Apenas definição de entidades e repositories
- **View/Routes**: Apenas definição de rotas e mapeamento HTTP
- **Controller**: Orquestração HTTP (request/response)
- **Service**: Lógica de negócio pura

---

## Estrutura de Diretórios

### Python/Flask Projects

```
project/
├── .env.example              # Template de variáveis de ambiente
├── .gitignore               # Incluir .env
├── requirements.txt         # Dependências
├── app.py                   # Entry point (composition root)
│
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py      # Carrega .env, define Config class
│   │   ├── database.py      # Configuração de conexão com BD
│   │   └── constants.py     # Constantes globais
│   │
│   ├── models/              # Camada de Dados
│   │   ├── __init__.py
│   │   ├── user.py          # Model User
│   │   ├── product.py       # Model Product
│   │   └── order.py         # Model Order
│   │
│   ├── repositories/        # Data Access Layer (opcional, se não usar ORM)
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   └── product_repository.py
│   │
│   ├── services/            # Camada de Negócio
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── order_service.py
│   │   └── auth_service.py
│   │
│   ├── controllers/         # Camada de Orquestração HTTP
│   │   ├── __init__.py
│   │   ├── user_controller.py
│   │   ├── product_controller.py
│   │   └── order_controller.py
│   │
│   ├── routes/              # Camada de Apresentação (Views)
│   │   ├── __init__.py
│   │   ├── user_routes.py
│   │   ├── product_routes.py
│   │   └── order_routes.py
│   │
│   ├── middlewares/         # Middlewares
│   │   ├── __init__.py
│   │   ├── auth.py          # Autenticação JWT
│   │   ├── error_handler.py # Tratamento de erros
│   │   ├── validation.py    # Validação de schemas
│   │   └── logging.py       # Logging estruturado
│   │
│   ├── schemas/             # Validação de input/output
│   │   ├── __init__.py
│   │   ├── user_schema.py
│   │   └── product_schema.py
│   │
│   └── utils/               # Utilitários
│       ├── __init__.py
│       └── helpers.py
│
└── tests/                   # Testes
    ├── unit/
    ├── integration/
    └── conftest.py
```

### Node.js/Express Projects

```
project/
├── .env.example
├── .gitignore
├── package.json
├── package-lock.json
├── server.js                # Entry point
│
├── src/
│   ├── config/
│   │   ├── index.js         # Carrega .env, exporta config
│   │   ├── database.js      # Configuração de BD
│   │   └── constants.js     # Constantes
│   │
│   ├── models/              # Camada de Dados
│   │   ├── User.js
│   │   ├── Product.js
│   │   └── Order.js
│   │
│   ├── repositories/        # Data Access (se não usar ORM)
│   │   ├── UserRepository.js
│   │   └── ProductRepository.js
│   │
│   ├── services/            # Lógica de Negócio
│   │   ├── UserService.js
│   │   ├── OrderService.js
│   │   └── AuthService.js
│   │
│   ├── controllers/         # Orquestração HTTP
│   │   ├── UserController.js
│   │   ├── ProductController.js
│   │   └── OrderController.js
│   │
│   ├── routes/              # Definição de rotas
│   │   ├── index.js         # Agrega todas as rotas
│   │   ├── userRoutes.js
│   │   ├── productRoutes.js
│   │   └── orderRoutes.js
│   │
│   ├── middlewares/
│   │   ├── auth.js
│   │   ├── errorHandler.js
│   │   ├── validation.js
│   │   └── logger.js
│   │
│   ├── validators/          # Schemas de validação
│   │   ├── userValidator.js
│   │   └── productValidator.js
│   │
│   └── utils/
│       └── helpers.js
│
└── tests/
    ├── unit/
    └── integration/
```

---

## Responsabilidades de Cada Camada

### 1. Models (Camada de Dados)

**Responsabilidade**: Definição de entidades e estrutura de dados.

**O que DEVE conter**:
- Definição de schemas/classes de entidades
- Campos e seus tipos
- Relações entre entidades
- Métodos de serialização simples (`to_dict()`, `toJSON()`)
- Validações básicas de tipo/formato

**O que NÃO deve conter**:
- Lógica de negócio
- Queries complexas (usar Repositories)
- Dependências HTTP
- Cálculos ou transformações complexas

**Exemplo (Python/SQLAlchemy)**:
```python
# models/user.py
from database import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self, include_password=False):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': self.created_at.isoformat()
        }
        # Nunca incluir senha por padrão
        return data
```

---

### 2. Repositories (Camada de Acesso a Dados) - Opcional

**Responsabilidade**: Abstrair acesso ao banco de dados.

**O que DEVE conter**:
- Métodos de CRUD (Create, Read, Update, Delete)
- Queries específicas de domínio
- Agregações e relatórios de dados

**O que NÃO deve conter**:
- Lógica de negócio
- Validações de regras de negócio
- Dependências HTTP

**Exemplo**:
```python
# repositories/user_repository.py
from models.user import User
from database import db

class UserRepository:
    @staticmethod
    def find_by_id(user_id):
        return User.query.get(user_id)

    @staticmethod
    def find_by_email(email):
        return User.query.filter_by(email=email).first()

    @staticmethod
    def find_all(active_only=True):
        query = User.query
        if active_only:
            query = query.filter_by(active=True)
        return query.all()

    @staticmethod
    def create(user_data):
        user = User(**user_data)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(user_id, user_data):
        user = User.query.get(user_id)
        if user:
            for key, value in user_data.items():
                setattr(user, key, value)
            db.session.commit()
        return user

    @staticmethod
    def delete(user_id):
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
        return user
```

---

### 3. Services (Camada de Negócio)

**Responsabilidade**: Implementar regras de negócio e orquestrar repositórios.

**O que DEVE conter**:
- Lógica de negócio pura
- Validações de regras de domínio
- Orquestração de múltiplos repositories
- Transações
- Cálculos complexos

**O que NÃO deve conter**:
- Dependências de HTTP (request, response)
- Acesso direto ao banco (usar Repositories)
- Lógica de apresentação

**Exemplo**:
```python
# services/order_service.py
from repositories.product_repository import ProductRepository
from repositories.order_repository import OrderRepository
from models.order import Order
from database import db

class OrderService:
    def __init__(self):
        self.product_repo = ProductRepository()
        self.order_repo = OrderRepository()

    def create_order(self, user_id, items):
        """
        Cria um pedido validando estoque e calculando total.

        Args:
            user_id: ID do usuário
            items: Lista de dicts com product_id e quantity

        Returns:
            Order criado

        Raises:
            ValueError: Se validação falhar
        """
        # Validação de negócio: verificar estoque
        for item in items:
            product = self.product_repo.find_by_id(item['product_id'])
            if not product:
                raise ValueError(f"Product {item['product_id']} not found")

            if product.stock < item['quantity']:
                raise ValueError(f"Insufficient stock for {product.name}")

        # Cálculo de negócio: total
        total = sum(
            self.product_repo.find_by_id(item['product_id']).price * item['quantity']
            for item in items
        )

        # Transação: criar pedido e atualizar estoque
        try:
            order = Order(user_id=user_id, total=total)
            db.session.add(order)

            for item in items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=item['product_id'],
                    quantity=item['quantity']
                )
                db.session.add(order_item)

                # Atualizar estoque
                product = self.product_repo.find_by_id(item['product_id'])
                product.stock -= item['quantity']

            db.session.commit()
            return order

        except Exception as e:
            db.session.rollback()
            raise

    def get_user_orders(self, user_id):
        """Busca todos os pedidos de um usuário"""
        return self.order_repo.find_by_user(user_id)

    def calculate_discount(self, total):
        """Aplica regras de desconto baseadas no total"""
        # Regra de negócio centralizada
        from config.constants import DiscountTiers

        if total >= DiscountTiers.TIER_1_THRESHOLD:
            return total * DiscountTiers.TIER_1_RATE
        elif total >= DiscountTiers.TIER_2_THRESHOLD:
            return total * DiscountTiers.TIER_2_RATE
        elif total >= DiscountTiers.TIER_3_THRESHOLD:
            return total * DiscountTiers.TIER_3_RATE

        return 0
```

---

### 4. Controllers (Camada de Orquestração HTTP)

**Responsabilidade**: Receber requests, validar, delegar para services, retornar responses.

**O que DEVE conter**:
- Extração de dados do request
- Validação de input (pode delegar para schemas)
- Delegação para services
- Formatação de response
- Tratamento de erros HTTP
- Códigos de status HTTP apropriados

**O que NÃO deve conter**:
- Lógica de negócio
- Queries de banco
- Cálculos complexos

**Exemplo**:
```python
# controllers/order_controller.py
from flask import request, jsonify
from services.order_service import OrderService
from middlewares.auth import require_auth
from schemas.order_schema import order_schema, order_create_schema
from marshmallow import ValidationError

class OrderController:
    def __init__(self):
        self.order_service = OrderService()

    @require_auth
    def create(self):
        """POST /orders - Criar novo pedido"""
        try:
            # Validar input
            data = order_create_schema.load(request.get_json())

            # Delegar para service
            order = self.order_service.create_order(
                user_id=request.current_user_id,
                items=data['items']
            )

            # Formatar response
            return jsonify(order_schema.dump(order)), 201

        except ValidationError as e:
            return jsonify({'errors': e.messages}), 400

        except ValueError as e:
            # Erro de lógica de negócio
            return jsonify({'error': str(e)}), 400

        except Exception as e:
            # Erro inesperado
            logger.error(f"Error creating order: {e}", exc_info=True)
            return jsonify({'error': 'Internal server error'}), 500

    @require_auth
    def get_user_orders(self, user_id):
        """GET /users/<user_id>/orders"""
        # Verificar autorização: só pode ver próprios pedidos ou se admin
        if request.current_user_id != user_id and not request.is_admin:
            return jsonify({'error': 'Forbidden'}), 403

        orders = self.order_service.get_user_orders(user_id)
        return jsonify(order_schema.dump(orders, many=True)), 200
```

---

### 5. Routes (Camada de Apresentação / Views)

**Responsabilidade**: Mapear URLs para controllers.

**O que DEVE conter**:
- Definição de rotas (URL + método HTTP)
- Mapeamento para métodos de controllers
- Aplicação de middlewares de rota
- Agrupamento de rotas por domínio

**O que NÃO deve conter**:
- Lógica de negócio
- Lógica de controller (apenas chamar controller)

**Exemplo**:
```python
# routes/order_routes.py
from flask import Blueprint
from controllers.order_controller import OrderController

order_bp = Blueprint('orders', __name__, url_prefix='/orders')
order_controller = OrderController()

# POST /orders - Criar pedido
order_bp.route('/', methods=['POST'])(order_controller.create)

# GET /users/<user_id>/orders - Listar pedidos do usuário
order_bp.route('/users/<int:user_id>/orders', methods=['GET'])(
    order_controller.get_user_orders
)

# GET /orders/<order_id> - Detalhes do pedido
order_bp.route('/<int:order_id>', methods=['GET'])(order_controller.get)
```

**Agregação de Rotas**:
```python
# routes/__init__.py
from flask import Flask
from routes.user_routes import user_bp
from routes.product_routes import product_bp
from routes.order_routes import order_bp

def register_routes(app: Flask):
    """Registra todos os blueprints"""
    app.register_blueprint(user_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)
```

---

### 6. Middlewares

**Responsabilidade**: Interceptar requests/responses para cross-cutting concerns.

**Tipos Comuns**:

#### 6.1 Authentication Middleware
```python
# middlewares/auth.py
from functools import wraps
from flask import request, jsonify
import jwt
from config.settings import Config

def require_auth(f):
    """Decorator para exigir autenticação JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')

        if not token:
            return jsonify({'error': 'No token provided'}), 401

        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            request.current_user_id = payload['user_id']
            request.is_admin = payload.get('role') == 'admin'

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated
```

#### 6.2 Error Handler Middleware
```python
# middlewares/error_handler.py
from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal error: {error}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
```

#### 6.3 Logging Middleware
```python
# middlewares/logging.py
from flask import request
import logging
import time

logger = logging.getLogger(__name__)

def log_requests(app):
    @app.before_request
    def before_request():
        request.start_time = time.time()

    @app.after_request
    def after_request(response):
        duration = time.time() - request.start_time
        logger.info(
            f"{request.method} {request.path} "
            f"{response.status_code} {duration:.2f}s"
        )
        return response
```

---

### 7. Config (Camada de Configuração)

**Responsabilidade**: Centralizar configurações e carregar variáveis de ambiente.

```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_EXPIRES', 3600))

    # Email
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

    @staticmethod
    def validate():
        required = ['SECRET_KEY', 'DATABASE_URL']
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            raise ValueError(f"Missing config: {', '.join(missing)}")

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

# Selecionar config baseado em ENV
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

---

## Fluxo de Request Completo

```
1. REQUEST chega no servidor
   ↓
2. MIDDLEWARES (before_request)
   - Logging
   - CORS
   ↓
3. ROUTE mapeia URL → Controller
   ↓
4. MIDDLEWARE de Autenticação
   - Valida JWT
   - Injeta user info no request
   ↓
5. CONTROLLER
   - Extrai dados do request
   - Valida schema
   - Delega para SERVICE
   ↓
6. SERVICE
   - Executa lógica de negócio
   - Chama REPOSITORIES
   ↓
7. REPOSITORY
   - Acessa banco via MODEL/ORM
   ↓
8. SERVICE retorna resultado
   ↓
9. CONTROLLER formata response
   ↓
10. MIDDLEWARES (after_request)
    - Logging de response
    ↓
11. RESPONSE enviada ao cliente
```

---

## Entry Point (app.py / server.js)

**Responsabilidade**: Inicializar aplicação, registrar componentes, iniciar servidor.

```python
# app.py
from flask import Flask
from flask_cors import CORS
from config.settings import config
from config.database import init_db
from routes import register_routes
from middlewares.error_handler import register_error_handlers
from middlewares.logging import log_requests

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)

    # Carregar configuração
    app.config.from_object(config[config_name])
    config[config_name].validate()

    # Inicializar extensões
    CORS(app)
    init_db(app)

    # Registrar middlewares
    register_error_handlers(app)
    log_requests(app)

    # Registrar rotas
    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app(os.getenv('FLASK_ENV', 'development'))
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )
```

---

## Princípios SOLID Aplicados

1. **Single Responsibility**: Cada camada tem uma responsabilidade única
2. **Open/Closed**: Fácil adicionar novos endpoints sem modificar existentes
3. **Liskov Substitution**: Repositories/Services podem ser substituídos
4. **Interface Segregation**: Controllers dependem de interfaces, não implementações
5. **Dependency Inversion**: Camadas superiores dependem de abstrações

---

## Checklist de Refatoração MVC

- [ ] Config extraída para módulo separado (.env + settings)
- [ ] Models contêm apenas definição de entidades
- [ ] Services implementam lógica de negócio
- [ ] Controllers orquestram HTTP (não contêm lógica de negócio)
- [ ] Routes apenas mapeiam URLs → Controllers
- [ ] Middlewares de autenticação implementados
- [ ] Error handling centralizado
- [ ] Validação de input com schemas
- [ ] Logging estruturado (não print/console.log)
- [ ] Transações de banco apropriadas
- [ ] Entry point limpo (app.py / server.js)
