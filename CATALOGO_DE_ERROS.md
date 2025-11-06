# 📚 Catálogo de Erros - Error Dashboard

Guia completo dos principais tipos de erros que podem ser monitorados através do dashboard.

---

## 🌐 1. HTTP Errors

Erros relacionados a requisições HTTP e APIs REST.

### Erros 4xx - Cliente

#### 400 Bad Request
**Severidade:** MEDIUM  
**Descrição:** Requisição malformada ou com dados inválidos  
**Exemplo:**
```json
{
  "message": "400 Bad Request - Invalid JSON payload",
  "error_type": "HTTP",
  "severity": "MEDIUM",
  "source": "backend",
  "endpoint": "/api/users",
  "method": "POST",
  "status_code": 400
}
```

#### 401 Unauthorized
**Severidade:** HIGH  
**Descrição:** Falta de autenticação ou credenciais inválidas  
**Exemplo:**
```json
{
  "message": "401 Unauthorized - Missing authentication token",
  "error_type": "HTTP",
  "severity": "HIGH",
  "source": "backend",
  "endpoint": "/api/protected/resource",
  "method": "GET",
  "status_code": 401
}
```

#### 403 Forbidden
**Severidade:** HIGH  
**Descrição:** Usuário autenticado mas sem permissão  
**Exemplo:**
```json
{
  "message": "403 Forbidden - Insufficient permissions",
  "error_type": "HTTP",
  "severity": "HIGH",
  "source": "backend",
  "endpoint": "/api/admin/users",
  "method": "DELETE",
  "status_code": 403
}
```

#### 404 Not Found
**Severidade:** MEDIUM  
**Descrição:** Recurso não encontrado  
**Exemplo:**
```json
{
  "message": "404 Not Found - User profile not found",
  "error_type": "HTTP",
  "severity": "MEDIUM",
  "source": "backend",
  "endpoint": "/api/users/99999",
  "method": "GET",
  "status_code": 404
}
```

### Erros 5xx - Servidor

#### 500 Internal Server Error
**Severidade:** CRITICAL  
**Descrição:** Erro inesperado no servidor  
**Exemplo:**
```json
{
  "message": "500 Internal Server Error - Unhandled exception",
  "error_type": "HTTP",
  "severity": "CRITICAL",
  "source": "backend",
  "endpoint": "/api/orders",
  "method": "POST",
  "status_code": 500,
  "stack_trace": "Traceback (most recent call last):\n  File 'app.py', line 145..."
}
```

#### 502 Bad Gateway
**Severidade:** CRITICAL  
**Descrição:** Gateway recebeu resposta inválida  
**Exemplo:**
```json
{
  "message": "502 Bad Gateway - Upstream server not responding",
  "error_type": "HTTP",
  "severity": "CRITICAL",
  "source": "api",
  "status_code": 502
}
```

#### 503 Service Unavailable
**Severidade:** CRITICAL  
**Descrição:** Serviço temporariamente indisponível  
**Exemplo:**
```json
{
  "message": "503 Service Unavailable - Server overloaded",
  "error_type": "HTTP",
  "severity": "CRITICAL",
  "source": "backend",
  "status_code": 503,
  "metadata": {
    "load": "95%",
    "active_connections": 1500
  }
}
```

---

## 🗄️ 2. DATABASE Errors

Erros relacionados ao banco de dados.

### Connection Errors

#### Connection Timeout
**Severidade:** CRITICAL  
**Descrição:** Timeout ao conectar no banco  
**Exemplo:**
```json
{
  "message": "Database connection timeout after 30 seconds",
  "error_type": "DATABASE",
  "severity": "CRITICAL",
  "source": "database",
  "stack_trace": "psycopg2.OperationalError: could not connect to server\nConnection timeout"
}
```

#### Connection Pool Exhausted
**Severidade:** CRITICAL  
**Descrição:** Pool de conexões esgotado  
**Exemplo:**
```json
{
  "message": "Connection pool exhausted - max 50 connections",
  "error_type": "DATABASE",
  "severity": "CRITICAL",
  "source": "database",
  "metadata": {
    "max_connections": 50,
    "active_connections": 50,
    "pool_size": 50
  }
}
```

### Query Errors

#### Query Timeout
**Severidade:** HIGH  
**Descrição:** Query excedeu tempo limite  
**Exemplo:**
```json
{
  "message": "Query execution timeout after 10 seconds",
  "error_type": "DATABASE",
  "severity": "HIGH",
  "source": "database",
  "metadata": {
    "query": "SELECT * FROM large_table WHERE...",
    "execution_time": 10.5
  }
}
```

#### Deadlock Detected
**Severidade:** HIGH  
**Descrição:** Deadlock entre transações  
**Exemplo:**
```json
{
  "message": "Deadlock detected between transactions",
  "error_type": "DATABASE",
  "severity": "HIGH",
  "source": "database",
  "stack_trace": "psycopg2.errors.DeadlockDetected: deadlock detected"
}
```

### Constraint Violations

#### Unique Constraint
**Severidade:** MEDIUM  
**Descrição:** Violação de constraint unique  
**Exemplo:**
```json
{
  "message": "Duplicate key violation: user_email_unique",
  "error_type": "DATABASE",
  "severity": "MEDIUM",
  "source": "database",
  "stack_trace": "sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint"
}
```

#### Foreign Key Constraint
**Severidade:** MEDIUM  
**Descrição:** Violação de foreign key  
**Exemplo:**
```json
{
  "message": "Foreign key constraint violation: order_user_id_fkey",
  "error_type": "DATABASE",
  "severity": "MEDIUM",
  "source": "database"
}
```

---

## 🔐 3. AUTH Errors

Erros de autenticação e autorização.

#### Invalid Token
**Severidade:** HIGH  
**Descrição:** Token JWT inválido ou corrompido  
**Exemplo:**
```json
{
  "message": "Invalid authentication token - signature verification failed",
  "error_type": "AUTH",
  "severity": "HIGH",
  "source": "backend",
  "endpoint": "/api/protected/data",
  "method": "GET"
}
```

#### Expired Token
**Severidade:** MEDIUM  
**Descrição:** Token expirado  
**Exemplo:**
```json
{
  "message": "Authentication token expired",
  "error_type": "AUTH",
  "severity": "MEDIUM",
  "source": "backend",
  "metadata": {
    "expired_at": "2024-11-06T10:00:00Z",
    "current_time": "2024-11-06T12:00:00Z"
  }
}
```

#### Invalid Credentials
**Severidade:** LOW  
**Descrição:** Credenciais incorretas  
**Exemplo:**
```json
{
  "message": "Invalid username or password",
  "error_type": "AUTH",
  "severity": "LOW",
  "source": "backend",
  "endpoint": "/api/login",
  "method": "POST",
  "user_id": "user_123"
}
```

#### Session Expired
**Severidade:** MEDIUM  
**Descrição:** Sessão do usuário expirada  
**Exemplo:**
```json
{
  "message": "Session expired - please login again",
  "error_type": "AUTH",
  "severity": "MEDIUM",
  "source": "backend",
  "session_id": "sess_12345"
}
```

---

## ✅ 4. VALIDATION Errors

Erros de validação de dados.

#### Invalid Email Format
**Severidade:** LOW  
**Descrição:** Formato de email inválido  
**Exemplo:**
```json
{
  "message": "Invalid email format: 'user@invalid'",
  "error_type": "VALIDATION",
  "severity": "LOW",
  "source": "backend",
  "endpoint": "/api/users/register",
  "method": "POST"
}
```

#### Missing Required Field
**Severidade:** MEDIUM  
**Descrição:** Campo obrigatório ausente  
**Exemplo:**
```json
{
  "message": "Required field 'password' is missing",
  "error_type": "VALIDATION",
  "severity": "MEDIUM",
  "source": "backend",
  "metadata": {
    "required_fields": ["email", "password", "name"],
    "provided_fields": ["email", "name"]
  }
}
```

#### Value Out of Range
**Severidade:** LOW  
**Descrição:** Valor fora do intervalo permitido  
**Exemplo:**
```json
{
  "message": "Age must be between 18 and 120, got 150",
  "error_type": "VALIDATION",
  "severity": "LOW",
  "source": "backend"
}
```

#### Invalid Format
**Severidade:** LOW  
**Descrição:** Formato de dado incorreto  
**Exemplo:**
```json
{
  "message": "Phone number format is invalid",
  "error_type": "VALIDATION",
  "severity": "LOW",
  "source": "backend",
  "metadata": {
    "expected_format": "+55 (XX) XXXXX-XXXX",
    "received": "123456"
  }
}
```

---

## ⚡ 5. PERFORMANCE Errors

Problemas de performance e recursos.

#### Request Timeout
**Severidade:** HIGH  
**Descrição:** Requisição excedeu tempo limite  
**Exemplo:**
```json
{
  "message": "Request timeout after 60 seconds",
  "error_type": "PERFORMANCE",
  "severity": "HIGH",
  "source": "backend",
  "endpoint": "/api/reports/generate",
  "method": "POST",
  "metadata": {
    "timeout": 60,
    "elapsed": 60.5
  }
}
```

#### Memory Limit Exceeded
**Severidade:** CRITICAL  
**Descrição:** Limite de memória excedido  
**Exemplo:**
```json
{
  "message": "Memory limit exceeded: heap out of memory",
  "error_type": "PERFORMANCE",
  "severity": "CRITICAL",
  "source": "backend",
  "stack_trace": "MemoryError: Cannot allocate memory",
  "metadata": {
    "memory_used": "4GB",
    "memory_limit": "4GB"
  }
}
```

#### Slow Query
**Severidade:** MEDIUM  
**Descrição:** Query lenta detectada  
**Exemplo:**
```json
{
  "message": "Slow query detected - execution time 8.5 seconds",
  "error_type": "PERFORMANCE",
  "severity": "MEDIUM",
  "source": "database",
  "metadata": {
    "query": "SELECT * FROM users JOIN orders...",
    "execution_time": 8.5,
    "threshold": 5.0
  }
}
```

#### CPU Threshold Exceeded
**Severidade:** HIGH  
**Descrição:** CPU acima do limite  
**Exemplo:**
```json
{
  "message": "CPU usage exceeded 90% threshold",
  "error_type": "PERFORMANCE",
  "severity": "HIGH",
  "source": "backend",
  "metadata": {
    "cpu_usage": "95%",
    "threshold": "90%",
    "duration": "5 minutes"
  }
}
```

---

## 🔌 6. INTEGRATION Errors

Erros em integrações com serviços externos.

#### External API Timeout
**Severidade:** CRITICAL  
**Descrição:** Timeout em API externa  
**Exemplo:**
```json
{
  "message": "Payment gateway API timeout after 30 seconds",
  "error_type": "INTEGRATION",
  "severity": "CRITICAL",
  "source": "external_service",
  "stack_trace": "requests.exceptions.Timeout: HTTPSConnectionPool timeout",
  "metadata": {
    "service": "stripe",
    "endpoint": "https://api.stripe.com/v1/charges",
    "timeout": 30
  }
}
```

#### Service Unavailable
**Severidade:** HIGH  
**Descrição:** Serviço externo indisponível  
**Exemplo:**
```json
{
  "message": "Email service unavailable (503)",
  "error_type": "INTEGRATION",
  "severity": "HIGH",
  "source": "external_service",
  "status_code": 503,
  "metadata": {
    "service": "sendgrid",
    "retry_count": 3
  }
}
```

#### Invalid API Response
**Severidade:** MEDIUM  
**Descrição:** Resposta inválida de API externa  
**Exemplo:**
```json
{
  "message": "Invalid JSON response from external API",
  "error_type": "INTEGRATION",
  "severity": "MEDIUM",
  "source": "external_service",
  "metadata": {
    "service": "geocoding_api",
    "expected": "application/json",
    "received": "text/html"
  }
}
```

---

## 💻 7. APPLICATION Errors

Erros gerais de aplicação.

#### Null Pointer Exception
**Severidade:** CRITICAL  
**Descrição:** Tentativa de acessar objeto nulo  
**Exemplo:**
```json
{
  "message": "NullPointerException in user service",
  "error_type": "APPLICATION",
  "severity": "CRITICAL",
  "source": "backend",
  "stack_trace": "NullPointerException: Cannot invoke method on null object\nat UserService.processUser(UserService.java:45)"
}
```

#### Unhandled Exception
**Severidade:** HIGH  
**Descrição:** Exception não capturada  
**Exemplo:**
```json
{
  "message": "Unhandled exception in data processing pipeline",
  "error_type": "APPLICATION",
  "severity": "HIGH",
  "source": "backend",
  "stack_trace": "Exception: Unexpected error in job processor\nat process_job(worker.py:123)"
}
```

#### Configuration Error
**Severidade:** CRITICAL  
**Descrição:** Erro de configuração  
**Exemplo:**
```json
{
  "message": "Failed to load configuration file: config.yaml",
  "error_type": "APPLICATION",
  "severity": "CRITICAL",
  "source": "backend",
  "stack_trace": "yaml.scanner.ScannerError: mapping values are not allowed here"
}
```

---

## 🌐 8. FRONTEND Errors

Erros no lado do cliente (JavaScript/TypeScript).

#### TypeError
**Severidade:** MEDIUM  
**Descrição:** Erro de tipo no JavaScript  
**Exemplo:**
```json
{
  "message": "TypeError: Cannot read property 'map' of undefined",
  "error_type": "FRONTEND",
  "severity": "MEDIUM",
  "source": "frontend",
  "stack_trace": "TypeError: Cannot read property 'map' of undefined\nat Dashboard.render (Dashboard.jsx:23)",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
  "metadata": {
    "component": "Dashboard",
    "url": "http://example.com/dashboard"
  }
}
```

#### Network Error
**Severidade:** HIGH  
**Descrição:** Falha na requisição de rede  
**Exemplo:**
```json
{
  "message": "Network request failed: Failed to fetch",
  "error_type": "FRONTEND",
  "severity": "HIGH",
  "source": "frontend",
  "endpoint": "/api/users",
  "metadata": {
    "error_type": "NetworkError",
    "url": "http://api.example.com/users"
  }
}
```

#### React Component Error
**Severidade:** MEDIUM  
**Descrição:** Erro em componente React  
**Exemplo:**
```json
{
  "message": "React component rendering error",
  "error_type": "FRONTEND",
  "severity": "MEDIUM",
  "source": "frontend",
  "stack_trace": "Error: Cannot render undefined value\nat UserList.render",
  "metadata": {
    "component": "UserList",
    "props": {"users": null}
  }
}
```

#### Chunk Load Error
**Severidade:** MEDIUM  
**Descrição:** Falha ao carregar chunk do webpack  
**Exemplo:**
```json
{
  "message": "ChunkLoadError: Loading chunk 5 failed",
  "error_type": "FRONTEND",
  "severity": "MEDIUM",
  "source": "frontend",
  "metadata": {
    "chunk_id": 5,
    "chunk_name": "settings-page"
  }
}
```

---

## 📊 Resumo de Severidades

| Severidade | Quando Usar | Tempo de Resposta Sugerido |
|------------|-------------|----------------------------|
| **CRITICAL** | Sistema inoperante, dados em risco, serviço offline | Imediato (< 1 hora) |
| **HIGH** | Funcionalidade importante afetada, performance degradada | Urgente (< 4 horas) |
| **MEDIUM** | Funcionalidade afetada mas com workaround disponível | Normal (< 24 horas) |
| **LOW** | Inconveniência menor, não afeta operação crítica | Planejado (< 1 semana) |

---

## 🎯 Melhores Práticas

### Ao Reportar Erros:

1. **Seja Específico**: Mensagem clara e descritiva
2. **Inclua Context**: Stack trace, metadata, user_id quando relevante
3. **Classifique Corretamente**: Tipo e severidade apropriados
4. **Dados Sensíveis**: Nunca inclua senhas ou tokens nos logs
5. **Timestamps**: Sempre use UTC
6. **IDs Únicos**: Inclua request_id, session_id quando disponível

### Exemplo Completo:

```json
{
  "message": "Payment processing failed - card declined",
  "error_type": "INTEGRATION",
  "severity": "HIGH",
  "source": "backend",
  "endpoint": "/api/payments/process",
  "method": "POST",
  "status_code": 402,
  "user_id": "user_12345",
  "session_id": "sess_67890",
  "ip_address": "203.0.113.45",
  "stack_trace": "stripe.error.CardError: Your card was declined",
  "metadata": {
    "payment_method": "credit_card",
    "amount": 99.99,
    "currency": "BRL",
    "stripe_error_code": "card_declined",
    "request_id": "req_abc123"
  }
}
```

---

**Este catálogo serve como referência para os tipos de erros que podem ser monitorados através do Error Dashboard.**

