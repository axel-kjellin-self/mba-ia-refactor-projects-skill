# LMS API - Refactored

Learning Management System API with checkout flow, refactored to follow MVC architecture pattern with proper separation of concerns.

## What Changed?

This project has been refactored from a legacy monolith into a clean MVC architecture:

### Before (Legacy)
- ❌ All logic in one 142-line `AppManager.js` God Class
- ❌ Hardcoded credentials in source code
- ❌ Weak custom cryptography (Base64 encoding)
- ❌ No authentication/authorization
- ❌ Callback hell (5+ levels deep)
- ❌ N+1 query problem
- ❌ No separation of concerns

### After (Refactored) ✅
- ✅ **MVC Architecture**: Models, Services, Controllers, Routes
- ✅ **Security**: bcrypt password hashing, JWT authentication
- ✅ **Configuration**: Environment variables via `.env`
- ✅ **Database**: Proper constraints (FK, UNIQUE, CHECK)
- ✅ **Performance**: Optimized queries with JOINs (no N+1)
- ✅ **Error Handling**: Centralized error middleware
- ✅ **Code Quality**: Proper separation of concerns

## Architecture

```
src/
├── config/
│   ├── index.js          # Configuration loader (reads .env)
│   ├── database.js       # Database connection with promisified methods
│   └── constants.js      # Application constants
├── models/               # Data entities
│   ├── User.js
│   ├── Course.js
│   ├── Enrollment.js
│   └── Payment.js
├── repositories/         # Data Access Layer
│   ├── UserRepository.js
│   ├── CourseRepository.js
│   ├── EnrollmentRepository.js
│   ├── PaymentRepository.js
│   └── AuditLogRepository.js
├── services/             # Business Logic
│   ├── AuthService.js    # JWT authentication
│   ├── CheckoutService.js # Checkout workflow
│   └── ReportService.js  # Financial reports
├── controllers/          # HTTP Orchestration
│   ├── AuthController.js
│   ├── CheckoutController.js
│   ├── AdminController.js
│   └── UserController.js
├── routes/               # Route definitions
│   ├── authRoutes.js
│   ├── checkoutRoutes.js
│   ├── adminRoutes.js
│   ├── userRoutes.js
│   └── index.js
├── middlewares/          # Cross-cutting concerns
│   ├── auth.js           # JWT authentication middleware
│   ├── errorHandler.js   # Global error handling
│   └── logger.js         # Request logging
└── app.js                # Application entry point
```

## Installation

```bash
# Install dependencies
npm install

# The .env file is already created for development
# For production, copy .env.example and fill in real values
```

## Running

```bash
npm start
```

The API will start on `http://localhost:3000`.

## Environment Variables

Required variables (already set in `.env` for development):

```bash
PORT=3000
NODE_ENV=development
JWT_SECRET=your-super-secret-jwt-key-min-32-characters-long-please
JWT_EXPIRES_IN=24h
PAYMENT_GATEWAY_KEY=pk_test_demo_key_for_development
```

## API Endpoints

### Authentication

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "leonan@fullcycle.com.br",
  "password": "SecurePassword123!"
}
```

Response:
```json
{
  "user": {
    "id": 1,
    "name": "Leonan",
    "email": "leonan@fullcycle.com.br",
    "role": "admin"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

### Checkout

#### Process Checkout
```http
POST /api/checkout
Content-Type: application/json

{
  "usr": "John Doe",
  "eml": "john@example.com",
  "pwd": "password123",
  "c_id": 1,
  "card": "4111111111111111"
}
```

**Note**: Card numbers starting with `4` (Visa) are approved, others are denied.

### Admin (Requires JWT + Admin Role)

#### Financial Report
```http
GET /api/admin/financial-report
Authorization: Bearer <your-jwt-token>
```

Response:
```json
{
  "report": [
    {
      "course": "Clean Architecture",
      "revenue": 997.00,
      "students": [
        {
          "student": "Leonan",
          "email": "leonan@fullcycle.com.br",
          "paid": 997.00,
          "status": "PAID"
        }
      ]
    }
  ]
}
```

#### Revenue Summary
```http
GET /api/admin/revenue-summary
Authorization: Bearer <your-jwt-token>
```

### Users (Requires JWT)

#### Get User
```http
GET /api/users/:id
Authorization: Bearer <your-jwt-token>
```

#### Delete User
```http
DELETE /api/users/:id
Authorization: Bearer <your-jwt-token>
```

**Note**: Users can only delete their own account unless they have admin role.

#### Get User Enrollments
```http
GET /api/users/:userId/enrollments
Authorization: Bearer <your-jwt-token>
```

## Security Improvements

1. **Password Hashing**: bcrypt with 12 salt rounds (replaces weak Base64 encoding)
2. **JWT Authentication**: Protected admin and user endpoints
3. **Environment Variables**: No hardcoded secrets
4. **Database Constraints**: Foreign keys, unique constraints, cascading deletes
5. **Input Validation**: Proper error messages and status codes
6. **Authorization**: Role-based access control (RBAC)

## Performance Improvements

1. **Optimized Queries**: Financial report uses single JOIN query instead of N+1
2. **Async/Await**: No callback hell, linear code flow
3. **Proper Indexing**: Database constraints provide automatic indexing

## Code Quality Improvements

1. **Separation of Concerns**: MVC layers with clear responsibilities
2. **Error Handling**: Centralized error middleware
3. **Logging**: Structured request/response logging
4. **Constants**: Magic numbers extracted to named constants
5. **Documentation**: JSDoc comments on all public methods

## Testing the Refactoring

Compare with the legacy version in git history:

```bash
# View the legacy code
git show HEAD~1:src/AppManager.js

# See the transformation
git diff HEAD~1 HEAD
```

## Default Credentials

The application seeds one admin user:

- **Email**: `leonan@fullcycle.com.br`
- **Password**: `SecurePassword123!`

Use these credentials to login and get a JWT token for testing admin endpoints.

## Database Schema

The application uses SQLite in-memory database with the following schema:

- `users` (id, name, email, password, role, created_at)
- `courses` (id, title, price, active, created_at)
- `enrollments` (id, user_id, course_id, created_at) + FK constraints
- `payments` (id, enrollment_id, amount, status, created_at) + FK constraints
- `audit_logs` (id, action, user_id, created_at)

All tables have proper constraints (NOT NULL, UNIQUE, CHECK, FOREIGN KEY).

## License

MIT
