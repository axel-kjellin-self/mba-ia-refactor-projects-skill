# Refactoring Playbook

Este playbook contém padrões concretos de transformação para cada anti-pattern, com exemplos de código antes/depois.

---

## Transformação 1: Extrair Configuração de Secrets Hardcoded

### Anti-Pattern
Secrets e credenciais hardcoded no código.

### Antes (Python)
```python
# app.py
app.config['SECRET_KEY'] = 'minha-chave-super-secreta-123'
app.config['DATABASE_URL'] = 'sqlite:///app.db'

# utils.py
SMTP_PASSWORD = 'senha123'
API_KEY = 'pk_live_1234567890'
```

### Depois (Python)
```python
# .env (NÃO commitar no git!)
SECRET_KEY=generated-random-key-here-min-32-bytes
DATABASE_URL=sqlite:///app.db
SMTP_PASSWORD=actual-password-here
API_KEY=pk_live_actual_key_here

# .env.example (commitar no git)
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
SMTP_PASSWORD=your-smtp-password
API_KEY=your-api-key

# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    API_KEY = os.getenv('API_KEY')

    @staticmethod
    def validate():
        """Validate all required config is present"""
        required = ['SECRET_KEY', 'SMTP_PASSWORD', 'API_KEY']
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            raise ValueError(f"Missing required config: {', '.join(missing)}")

# app.py
from config.settings import Config

Config.validate()
app.config.from_object(Config)
```

### Antes (JavaScript/Node.js)
```javascript
// utils.js
const config = {
  dbPass: "senha_super_secreta_prod_123",
  paymentGatewayKey: "pk_live_1234567890abcdef",
  smtpUser: "no-reply@company.com"
};
```

### Depois (JavaScript/Node.js)
```javascript
// .env (NÃO commitar!)
DB_PASSWORD=actual-password-here
PAYMENT_GATEWAY_KEY=pk_live_actual_key
SMTP_USER=no-reply@company.com

// .env.example (commitar)
DB_PASSWORD=your-db-password
PAYMENT_GATEWAY_KEY=your-payment-key
SMTP_USER=your-smtp-user

// config/index.js
require('dotenv').config();

const config = {
  dbPass: process.env.DB_PASSWORD,
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY,
  smtpUser: process.env.SMTP_USER,

  validate() {
    const required = ['DB_PASSWORD', 'PAYMENT_GATEWAY_KEY'];
    const missing = required.filter(key => !process.env[key]);
    if (missing.length > 0) {
      throw new Error(`Missing required env vars: ${missing.join(', ')}`);
    }
  }
};

config.validate();
module.exports = config;
```

---

## Transformação 2: Parametrizar Queries SQL (SQL Injection → Seguro)

### Antes (Python)
```python
# VULNERÁVEL - SQL Injection
def get_user_by_email(email):
    cursor.execute("SELECT * FROM users WHERE email = '" + email + "'")
    return cursor.fetchone()

def create_product(name, price):
    cursor.execute(
        "INSERT INTO products (name, price) VALUES ('" +
        name + "', " + str(price) + ")"
    )
```

### Depois (Python com sqlite3)
```python
# SEGURO - Queries parametrizadas
def get_user_by_email(email):
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    return cursor.fetchone()

def create_product(name, price):
    cursor.execute(
        "INSERT INTO products (name, price) VALUES (?, ?)",
        (name, price)
    )
```

### Depois (Python com SQLAlchemy ORM - Recomendado)
```python
# SEGURO - ORM previne SQL injection por padrão
from models import User, Product
from database import db

def get_user_by_email(email):
    return User.query.filter_by(email=email).first()

def create_product(name, price):
    product = Product(name=name, price=price)
    db.session.add(product)
    db.session.commit()
    return product
```

### Antes (JavaScript/Node.js)
```javascript
// VULNERÁVEL
function getUserByEmail(email, callback) {
  db.query("SELECT * FROM users WHERE email = '" + email + "'", callback);
}
```

### Depois (JavaScript/Node.js)
```javascript
// SEGURO - Queries parametrizadas
function getUserByEmail(email, callback) {
  db.query("SELECT * FROM users WHERE email = ?", [email], callback);
}

// OU com Promises/async-await
async function getUserByEmail(email) {
  const [rows] = await db.query(
    "SELECT * FROM users WHERE email = ?",
    [email]
  );
  return rows[0];
}
```

---

## Transformação 3: Implementar Hash Seguro de Senhas

### Antes (Python - MD5/Plaintext)
```python
import hashlib

class User:
    def set_password(self, pwd):
        # INSEGURO - MD5 é quebrado
        self.password = hashlib.md5(pwd.encode()).hexdigest()

    def check_password(self, pwd):
        return self.password == hashlib.md5(pwd.encode()).hexdigest()
```

### Depois (Python - bcrypt)
```python
from werkzeug.security import generate_password_hash, check_password_hash
# OU: import bcrypt

class User:
    def set_password(self, pwd):
        # SEGURO - bcrypt com salt automático
        self.password = generate_password_hash(pwd, method='pbkdf2:sha256')

    def check_password(self, pwd):
        return check_password_hash(self.password, pwd)

# OU usando bcrypt diretamente:
# def set_password(self, pwd):
#     self.password = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
#
# def check_password(self, pwd):
#     return bcrypt.checkpw(pwd.encode(), self.password.encode())
```

### Antes (JavaScript/Node.js - Custom/Weak)
```javascript
// INSEGURO - Base64 não é hash
function badCrypto(pwd) {
  let hash = "";
  for(let i = 0; i < 10000; i++) {
    hash += Buffer.from(pwd).toString('base64').substring(0, 2);
  }
  return hash.substring(0, 10);
}
```

### Depois (JavaScript/Node.js - bcrypt)
```javascript
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12;

async function hashPassword(pwd) {
  // SEGURO - bcrypt com salt
  return await bcrypt.hash(pwd, SALT_ROUNDS);
}

async function checkPassword(pwd, hash) {
  return await bcrypt.compare(pwd, hash);
}

// Uso:
// const hashedPassword = await hashPassword('user-password');
// const isValid = await checkPassword('user-password', hashedPassword);
```

---

## Transformação 4: Separar God Class em Camadas MVC

### Antes (Monolítico)
```python
# models.py - God Class com 300+ linhas
import sqlite3

def get_all_products():
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()

def create_order(user_id, items):
    # Validação + lógica de negócio + acesso a dados tudo junto
    total = 0
    for item in items:
        cursor.execute("SELECT * FROM products WHERE id = " + str(item['id']))
        product = cursor.fetchone()
        if not product:
            return {"error": "Product not found"}
        if product['stock'] < item['quantity']:
            return {"error": "Insufficient stock"}
        total += product['price'] * item['quantity']

    cursor.execute("INSERT INTO orders (user_id, total) VALUES (?, ?)", (user_id, total))
    order_id = cursor.lastrowid

    for item in items:
        cursor.execute("INSERT INTO order_items ...")
        cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?", ...)

    return {"order_id": order_id, "total": total}
```

### Depois (Separado em Camadas)

```python
# models/product.py - APENAS definição de entidade
from database import db

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'stock': self.stock
        }

# models/order.py
class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# repositories/product_repository.py - Acesso a dados
class ProductRepository:
    @staticmethod
    def find_by_id(product_id):
        return Product.query.get(product_id)

    @staticmethod
    def find_all():
        return Product.query.all()

    @staticmethod
    def decrease_stock(product_id, quantity):
        product = Product.query.get(product_id)
        if product:
            product.stock -= quantity
            db.session.commit()

# services/order_service.py - Lógica de negócio
from repositories.product_repository import ProductRepository

class OrderService:
    def __init__(self):
        self.product_repo = ProductRepository()

    def create_order(self, user_id, items):
        # Validação
        for item in items:
            product = self.product_repo.find_by_id(item['product_id'])
            if not product:
                raise ValueError(f"Product {item['product_id']} not found")
            if product.stock < item['quantity']:
                raise ValueError(f"Insufficient stock for {product.name}")

        # Cálculo do total
        total = sum(
            self.product_repo.find_by_id(item['product_id']).price * item['quantity']
            for item in items
        )

        # Criar pedido (em transação)
        order = Order(user_id=user_id, total=total)
        db.session.add(order)

        # Criar itens do pedido e atualizar estoque
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity']
            )
            db.session.add(order_item)
            self.product_repo.decrease_stock(item['product_id'], item['quantity'])

        db.session.commit()
        return order

# controllers/order_controller.py - Orquestração HTTP
from flask import request, jsonify
from services.order_service import OrderService

class OrderController:
    def __init__(self):
        self.order_service = OrderService()

    def create(self):
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            items = data.get('items', [])

            order = self.order_service.create_order(user_id, items)
            return jsonify(order.to_dict()), 201

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Internal server error'}), 500
```

---

## Transformação 5: Adicionar Middleware de Autenticação

### Antes (Sem Autenticação)
```python
# routes/user_routes.py
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Qualquer pessoa pode acessar qualquer usuário!
    user = User.query.get(user_id)
    return jsonify(user.to_dict())

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Qualquer pessoa pode deletar qualquer usuário!
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204
```

### Depois (Com Autenticação JWT)
```python
# middlewares/auth.py
from functools import wraps
from flask import request, jsonify
import jwt
from config.settings import Config

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'No token provided'}), 401

        try:
            # Remove "Bearer " prefix
            token = token.replace('Bearer ', '')
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            request.current_user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated

def require_owner_or_admin(f):
    @wraps(f)
    @require_auth
    def decorated(*args, **kwargs):
        user_id = kwargs.get('user_id')
        current_user = User.query.get(request.current_user_id)

        # Verifica se é o próprio usuário ou admin
        if request.current_user_id != user_id and current_user.role != 'admin':
            return jsonify({'error': 'Forbidden'}), 403

        return f(*args, **kwargs)

    return decorated

# routes/user_routes.py
from middlewares.auth import require_auth, require_owner_or_admin

@app.route('/users/<int:user_id>', methods=['GET'])
@require_auth
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@app.route('/users/<int:user_id>', methods=['DELETE'])
@require_owner_or_admin
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# controllers/auth_controller.py - Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        },
        Config.SECRET_KEY,
        algorithm='HS256'
    )

    return jsonify({'token': token, 'user': user.to_dict()})
```

---

## Transformação 6: Otimizar N+1 Queries com JOINs

### Antes (N+1 Problem)
```python
# Busca todos os pedidos com itens - LENTO!
def get_orders_with_items():
    orders = Order.query.all()  # 1 query
    result = []

    for order in orders:  # Para cada pedido
        order_data = order.to_dict()
        order_data['items'] = []

        # N queries adicionais!
        items = OrderItem.query.filter_by(order_id=order.id).all()

        for item in items:  # Para cada item
            # Mais N queries!
            product = Product.query.get(item.product_id)
            order_data['items'].append({
                'product_name': product.name,
                'quantity': item.quantity
            })

        result.append(order_data)

    return result

# Total: 1 + N + (N * M) queries
```

### Depois (Eager Loading - RÁPIDO)
```python
# models/order.py - Adicionar relationships
class Order(db.Model):
    # ...
    items = db.relationship('OrderItem', backref='order', lazy='joined')

class OrderItem(db.Model):
    # ...
    product = db.relationship('Product', backref='order_items', lazy='joined')

# Busca com eager loading - 1 query com JOINs!
def get_orders_with_items():
    orders = Order.query.options(
        db.joinedload(Order.items).joinedload(OrderItem.product)
    ).all()

    result = []
    for order in orders:
        order_data = order.to_dict()
        order_data['items'] = [
            {
                'product_name': item.product.name,
                'quantity': item.quantity
            }
            for item in order.items
        ]
        result.append(order_data)

    return result

# Total: 1 query (ou 2-3 com joined load)
```

### Alternativa: SQL Puro com JOINs
```python
def get_orders_with_items_sql():
    query = """
        SELECT
            o.id as order_id,
            o.total,
            o.created_at,
            p.name as product_name,
            oi.quantity
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        LEFT JOIN products p ON oi.product_id = p.id
        ORDER BY o.id
    """

    results = db.session.execute(query).fetchall()

    # Agrupar por order_id
    orders = {}
    for row in results:
        if row.order_id not in orders:
            orders[row.order_id] = {
                'id': row.order_id,
                'total': row.total,
                'created_at': row.created_at,
                'items': []
            }

        if row.product_name:
            orders[row.order_id]['items'].append({
                'product_name': row.product_name,
                'quantity': row.quantity
            })

    return list(orders.values())
```

---

## Transformação 7: Callback Hell → Async/Await (Node.js)

### Antes (Callback Hell)
```javascript
// DIFÍCIL DE LER - Pyramid of doom
app.get('/api/report', (req, res) => {
  db.all("SELECT * FROM courses", [], (err, courses) => {
    if (err) return res.status(500).send("Error");

    courses.forEach(course => {
      db.all("SELECT * FROM enrollments WHERE course_id = ?", [course.id], (err, enrollments) => {
        if (err) return res.status(500).send("Error");

        enrollments.forEach(enrollment => {
          db.get("SELECT * FROM users WHERE id = ?", [enrollment.user_id], (err, user) => {
            if (err) return res.status(500).send("Error");

            db.get("SELECT * FROM payments WHERE enrollment_id = ?", [enrollment.id], (err, payment) => {
              if (err) return res.status(500).send("Error");
              // ... mais aninhamento
            });
          });
        });
      });
    });
  });
});
```

### Depois (Async/Await)
```javascript
// LEGÍVEL - Código linear
const { promisify } = require('util');

// Converter callbacks para promises
const dbAll = promisify(db.all.bind(db));
const dbGet = promisify(db.get.bind(db));

app.get('/api/report', async (req, res) => {
  try {
    const courses = await dbAll("SELECT * FROM courses");

    const report = await Promise.all(
      courses.map(async (course) => {
        const enrollments = await dbAll(
          "SELECT * FROM enrollments WHERE course_id = ?",
          [course.id]
        );

        const enrollmentDetails = await Promise.all(
          enrollments.map(async (enrollment) => {
            const user = await dbGet(
              "SELECT * FROM users WHERE id = ?",
              [enrollment.user_id]
            );

            const payment = await dbGet(
              "SELECT * FROM payments WHERE enrollment_id = ?",
              [enrollment.id]
            );

            return { enrollment, user, payment };
          })
        );

        return { course, enrollments: enrollmentDetails };
      })
    );

    res.json(report);

  } catch (err) {
    console.error(err);
    res.status(500).send("Internal server error");
  }
});
```

### Melhor Ainda: Usar ORM + Single Query
```javascript
// Usando Sequelize ORM
app.get('/api/report', async (req, res) => {
  try {
    const courses = await Course.findAll({
      include: [{
        model: Enrollment,
        include: [User, Payment]
      }]
    });

    res.json(courses);

  } catch (err) {
    console.error(err);
    res.status(500).send("Internal server error");
  }
});
```

---

## Transformação 8: Adicionar Validação Centralizada com Schemas

### Antes (Validação Espalhada)
```python
@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    # Validação manual repetida em cada endpoint
    if not data.get('title'):
        return jsonify({'error': 'Title required'}), 400

    if len(data['title']) > 100:
        return jsonify({'error': 'Title too long'}), 400

    priority = data.get('priority', 3)
    if priority < 1 or priority > 5:
        return jsonify({'error': 'Priority must be 1-5'}), 400

    # ... mais validação manual
```

### Depois (Schema Validation com Marshmallow)
```python
# schemas/task_schema.py
from marshmallow import Schema, fields, validate, ValidationError

class TaskSchema(Schema):
    title = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Title is required'}
    )
    description = fields.Str(
        validate=validate.Length(max=500),
        allow_none=True
    )
    priority = fields.Integer(
        validate=validate.Range(min=1, max=5),
        missing=3
    )
    status = fields.Str(
        validate=validate.OneOf(['pending', 'in_progress', 'done', 'cancelled']),
        missing='pending'
    )
    due_date = fields.DateTime(allow_none=True)
    user_id = fields.Integer(required=True)

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

# middlewares/validation.py
from functools import wraps
from flask import request, jsonify

def validate_schema(schema):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                validated_data = schema.load(request.get_json())
                request.validated_data = validated_data
            except ValidationError as err:
                return jsonify({'errors': err.messages}), 400

            return f(*args, **kwargs)

        return decorated
    return decorator

# routes/task_routes.py
from schemas.task_schema import task_schema
from middlewares.validation import validate_schema

@app.route('/tasks', methods=['POST'])
@validate_schema(task_schema)
def create_task():
    # Dados já validados e disponíveis em request.validated_data
    data = request.validated_data

    task = Task(**data)
    db.session.add(task)
    db.session.commit()

    return jsonify(task_schema.dump(task)), 201
```

---

## Transformação 9: Adicionar Error Handling Centralizado

### Antes (Error Handling Inconsistente)
```python
@app.route('/users/<int:id>')
def get_user(id):
    try:
        user = User.query.get(id)
        return jsonify(user.to_dict())
    except:  # Bare except - ruim!
        return jsonify({'error': 'Error'}), 500

@app.route('/tasks/<int:id>')
def get_task(id):
    user = Task.query.get(id)  # Sem tratamento de erro!
    return jsonify(user.to_dict())
```

### Depois (Error Handling Centralizado)
```python
# middlewares/error_handler.py
from flask import jsonify
from sqlalchemy.exc import IntegrityError, DataError
import logging

logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception for application errors"""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class NotFoundError(AppError):
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)

class ValidationError(AppError):
    def __init__(self, message):
        super().__init__(message, 400)

class UnauthorizedError(AppError):
    def __init__(self, message="Unauthorized"):
        super().__init__(message, 401)

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return jsonify({'error': error.message}), error.status_code

    @app.errorhandler(NotFoundError)
    def handle_not_found(error):
        return jsonify({'error': error.message}), 404

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        logger.error(f"Database integrity error: {error}")
        db.session.rollback()
        return jsonify({'error': 'Database constraint violation'}), 400

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.error(f"Unexpected error: {error}", exc_info=True)
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

# app.py
from middlewares.error_handler import register_error_handlers

register_error_handlers(app)

# routes/user_routes.py
from middlewares.error_handler import NotFoundError

@app.route('/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        raise NotFoundError(f"User {id} not found")

    return jsonify(user.to_dict())
```

---

## Transformação 10: Extrair Constantes de Magic Numbers

### Antes (Magic Numbers)
```python
def calculate_discount(total):
    discount = 0
    if total > 10000:
        discount = total * 0.1
    elif total > 5000:
        discount = total * 0.05
    elif total > 1000:
        discount = total * 0.02
    return discount

def validate_priority(priority):
    if priority < 1 or priority > 5:
        raise ValueError("Invalid priority")

def validate_password(password):
    if len(password) < 4:
        raise ValueError("Password too short")
```

### Depois (Constantes Nomeadas)
```python
# config/constants.py
class DiscountTiers:
    TIER_1_THRESHOLD = 10000
    TIER_1_RATE = 0.10  # 10%

    TIER_2_THRESHOLD = 5000
    TIER_2_RATE = 0.05  # 5%

    TIER_3_THRESHOLD = 1000
    TIER_3_RATE = 0.02  # 2%

class ValidationRules:
    MIN_PRIORITY = 1
    MAX_PRIORITY = 5

    MIN_PASSWORD_LENGTH = 12  # Atualizado de 4 para 12

    VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
    VALID_ROLES = ['admin', 'user', 'guest']

class DateFormats:
    ISO_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

# services/discount_service.py
from config.constants import DiscountTiers

def calculate_discount(total):
    """Calculate discount based on total purchase amount"""
    if total >= DiscountTiers.TIER_1_THRESHOLD:
        return total * DiscountTiers.TIER_1_RATE
    elif total >= DiscountTiers.TIER_2_THRESHOLD:
        return total * DiscountTiers.TIER_2_RATE
    elif total >= DiscountTiers.TIER_3_THRESHOLD:
        return total * DiscountTiers.TIER_3_RATE

    return 0

# validators/task_validator.py
from config.constants import ValidationRules

def validate_priority(priority):
    if not (ValidationRules.MIN_PRIORITY <= priority <= ValidationRules.MAX_PRIORITY):
        raise ValueError(
            f"Priority must be between {ValidationRules.MIN_PRIORITY} "
            f"and {ValidationRules.MAX_PRIORITY}"
        )

def validate_password(password):
    if len(password) < ValidationRules.MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {ValidationRules.MIN_PASSWORD_LENGTH} characters"
        )
```

---

## Resumo das Transformações

| # | Transformação | Anti-Pattern | Solução |
|---|---------------|--------------|---------|
| 1 | Extrair Configuração | Hardcoded Secrets | `.env` + config module |
| 2 | Parametrizar Queries | SQL Injection | Parameterized queries / ORM |
| 3 | Hash Seguro | Weak Crypto | bcrypt / argon2 |
| 4 | Separar Camadas | God Class | Models + Services + Controllers |
| 5 | Adicionar Auth | Missing Auth | JWT middleware + decorators |
| 6 | Otimizar Queries | N+1 Queries | JOINs / Eager loading |
| 7 | Async/Await | Callback Hell | Promises / async-await |
| 8 | Schema Validation | Missing Validation | Marshmallow / Joi schemas |
| 9 | Error Handling | Improper Errors | Centralized error handlers |
| 10 | Extrair Constantes | Magic Numbers | Constants module |

**Total**: 10 padrões de transformação com exemplos completos
