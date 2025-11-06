# 📖 API Documentation - Error Dashboard

## Visão Geral

API REST completa para gerenciamento de logs de erros, construída com FastAPI. Oferece endpoints para criação, leitura, atualização e exclusão de erros, além de estatísticas e análises.

**Base URL:** `http://localhost:8000`  
**Documentação Interativa:** `http://localhost:8000/docs`  
**Versão:** 1.0.0

## 🔐 Autenticação

> **Nota:** A versão atual não possui autenticação implementada. Para produção, recomenda-se adicionar JWT ou OAuth2.

## 📊 Endpoints

### Health Check

#### GET `/health`
Verifica se a API está funcionando.

**Response 200:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-06T10:30:00.123456"
}
```

---

## 🚨 Error Logs

### Criar Erro

#### POST `/api/errors`

Cria um novo registro de erro no sistema.

**Request Body:**
```json
{
  "message": "Database connection timeout",
  "error_type": "DATABASE",
  "severity": "CRITICAL",
  "source": "backend",
  "stack_trace": "Traceback (most recent call last):\n  File \"db.py\", line 23...",
  "endpoint": "/api/users",
  "method": "GET",
  "status_code": 500,
  "user_id": "user_123",
  "session_id": "sess_456",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "metadata": {
    "server": "prod-01",
    "database": "main",
    "retry_count": 3
  }
}
```

**Campos Obrigatórios:**
- `message` (string): Mensagem descritiva do erro
- `error_type` (ErrorType): Tipo do erro
- `severity` (Severity): Nível de severidade
- `source` (string): Origem do erro

**Campos Opcionais:**
- `stack_trace` (string): Stack trace completo
- `endpoint` (string): URL/endpoint onde ocorreu
- `method` (string): Método HTTP (GET, POST, etc.)
- `status_code` (integer): Código de status HTTP
- `user_id` (string): ID do usuário afetado
- `session_id` (string): ID da sessão
- `ip_address` (string): Endereço IP
- `user_agent` (string): User agent do navegador
- `metadata` (object): Dados adicionais em formato JSON

**Response 201:**
```json
{
  "id": 1,
  "message": "Database connection timeout",
  "error_type": "DATABASE",
  "severity": "CRITICAL",
  "source": "backend",
  "stack_trace": "Traceback...",
  "endpoint": "/api/users",
  "method": "GET",
  "status_code": 500,
  "user_id": "user_123",
  "session_id": "sess_456",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "metadata": {...},
  "status": "OPEN",
  "assigned_to": null,
  "notes": null,
  "timestamp": "2024-11-06T10:30:00.123456",
  "resolved_at": null,
  "occurrences": 1
}
```

---

### Listar Erros

#### GET `/api/errors`

Retorna lista de erros com filtros e paginação.

**Query Parameters:**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `skip` | integer | 0 | Número de registros para pular (paginação) |
| `limit` | integer | 100 | Limite de registros (1-1000) |
| `error_type` | string | - | Filtrar por tipo de erro |
| `severity` | string | - | Filtrar por severidade |
| `source` | string | - | Filtrar por origem |
| `status` | string | - | Filtrar por status |
| `start_date` | datetime | - | Data inicial (ISO 8601) |
| `end_date` | datetime | - | Data final (ISO 8601) |
| `search` | string | - | Busca textual em message e stack_trace |

**Exemplos:**

```bash
# Todos os erros críticos
GET /api/errors?severity=CRITICAL

# Erros HTTP dos últimos 7 dias
GET /api/errors?error_type=HTTP&start_date=2024-10-30T00:00:00

# Erros abertos de banco de dados
GET /api/errors?error_type=DATABASE&status=OPEN

# Busca por texto
GET /api/errors?search=connection%20timeout

# Paginação
GET /api/errors?skip=50&limit=50
```

**Response 200:**
```json
{
  "total": 245,
  "skip": 0,
  "limit": 100,
  "errors": [
    {
      "id": 1,
      "message": "Database connection timeout",
      "error_type": "DATABASE",
      "severity": "CRITICAL",
      "source": "backend",
      "status": "OPEN",
      "timestamp": "2024-11-06T10:30:00.123456",
      ...
    },
    ...
  ]
}
```

---

### Obter Erro por ID

#### GET `/api/errors/{error_id}`

Retorna detalhes completos de um erro específico.

**Path Parameters:**
- `error_id` (integer): ID do erro

**Response 200:**
```json
{
  "id": 1,
  "message": "Database connection timeout",
  "error_type": "DATABASE",
  "severity": "CRITICAL",
  "source": "backend",
  "stack_trace": "Traceback...",
  "endpoint": "/api/users",
  "method": "GET",
  "status_code": 500,
  "user_id": "user_123",
  "session_id": "sess_456",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "metadata": {...},
  "status": "OPEN",
  "assigned_to": null,
  "notes": null,
  "timestamp": "2024-11-06T10:30:00.123456",
  "resolved_at": null,
  "occurrences": 1
}
```

**Response 404:**
```json
{
  "detail": "Error log not found"
}
```

---

### Atualizar Erro

#### PATCH `/api/errors/{error_id}`

Atualiza o status, responsável ou notas de um erro.

**Path Parameters:**
- `error_id` (integer): ID do erro

**Request Body:**
```json
{
  "status": "RESOLVED",
  "assigned_to": "dev_team",
  "notes": "Fixed in version 1.2.3 - database pool size increased"
}
```

**Campos Atualizáveis:**
- `status` (ErrorStatus): Novo status
- `assigned_to` (string): Responsável
- `notes` (string): Notas sobre o erro

**Response 200:**
```json
{
  "id": 1,
  "message": "Database connection timeout",
  "status": "RESOLVED",
  "assigned_to": "dev_team",
  "notes": "Fixed in version 1.2.3...",
  "resolved_at": "2024-11-06T12:00:00.123456",
  ...
}
```

> **Nota:** Quando o status é alterado para `RESOLVED`, o campo `resolved_at` é automaticamente preenchido.

---

### Deletar Erro

#### DELETE `/api/errors/{error_id}`

Remove um erro do sistema.

**Path Parameters:**
- `error_id` (integer): ID do erro

**Response 204:** No Content

**Response 404:**
```json
{
  "detail": "Error log not found"
}
```

---

## 📈 Estatísticas

### Resumo Estatístico

#### GET `/api/stats/summary`

Retorna estatísticas agregadas de erros.

**Query Parameters:**
- `days` (integer, padrão: 7): Período em dias (1-365)

**Response 200:**
```json
{
  "total_errors": 245,
  "by_severity": {
    "LOW": 50,
    "MEDIUM": 100,
    "HIGH": 70,
    "CRITICAL": 25
  },
  "by_type": {
    "HTTP": 80,
    "DATABASE": 45,
    "AUTH": 30,
    "VALIDATION": 20,
    "PERFORMANCE": 15,
    "INTEGRATION": 25,
    "APPLICATION": 20,
    "FRONTEND": 10
  },
  "by_source": {
    "frontend": 60,
    "backend": 150,
    "database": 35
  },
  "by_status": {
    "OPEN": 100,
    "IN_PROGRESS": 50,
    "RESOLVED": 90,
    "IGNORED": 5
  },
  "error_rate": 35.0,
  "period_days": 7
}
```

**Campos:**
- `total_errors`: Total de erros no período
- `by_severity`: Distribuição por severidade
- `by_type`: Distribuição por tipo
- `by_source`: Distribuição por origem
- `by_status`: Distribuição por status
- `error_rate`: Taxa média de erros por dia
- `period_days`: Período analisado

---

### Timeline de Erros

#### GET `/api/stats/timeline`

Retorna contagem de erros por dia.

**Query Parameters:**
- `days` (integer, padrão: 7): Período em dias (1-365)

**Response 200:**
```json
{
  "timeline": [
    {
      "date": "2024-11-01",
      "count": 35
    },
    {
      "date": "2024-11-02",
      "count": 42
    },
    {
      "date": "2024-11-03",
      "count": 28
    },
    ...
  ]
}
```

Útil para criar gráficos de linha mostrando tendências de erros.

---

### Top Erros Mais Frequentes

#### GET `/api/stats/top-errors`

Retorna os erros mais recorrentes.

**Query Parameters:**
- `limit` (integer, padrão: 10): Número de erros (1-50)
- `days` (integer, padrão: 7): Período em dias (1-365)

**Response 200:**
```json
{
  "top_errors": [
    {
      "message": "Database connection timeout",
      "error_type": "DATABASE",
      "count": 45
    },
    {
      "message": "404 Not Found - User not found",
      "error_type": "HTTP",
      "count": 38
    },
    {
      "message": "Invalid authentication token",
      "error_type": "AUTH",
      "count": 32
    },
    ...
  ]
}
```

---

## 📋 Enumerações

### ErrorType

Tipos de erro suportados:

| Valor | Descrição |
|-------|-----------|
| `HTTP` | Erros de requisições HTTP (4xx, 5xx) |
| `DATABASE` | Erros relacionados ao banco de dados |
| `AUTH` | Erros de autenticação/autorização |
| `VALIDATION` | Erros de validação de dados |
| `PERFORMANCE` | Problemas de performance |
| `INTEGRATION` | Erros em integrações externas |
| `APPLICATION` | Erros gerais de aplicação |
| `FRONTEND` | Erros no frontend (JavaScript, etc.) |

### Severity

Níveis de severidade:

| Valor | Descrição | Cor Sugerida |
|-------|-----------|--------------|
| `LOW` | Baixa - não afeta funcionalidade crítica | 🟢 Verde |
| `MEDIUM` | Média - afeta funcionalidade mas tem workaround | 🟡 Amarelo |
| `HIGH` | Alta - afeta funcionalidade importante | 🟠 Laranja |
| `CRITICAL` | Crítica - impede funcionamento ou afeta segurança | 🔴 Vermelho |

### ErrorStatus

Status do erro:

| Valor | Descrição |
|-------|-----------|
| `OPEN` | Aberto - erro não tratado |
| `IN_PROGRESS` | Em progresso - sendo investigado/corrigido |
| `RESOLVED` | Resolvido - correção implementada |
| `IGNORED` | Ignorado - erro conhecido e aceito |

---

## 🔍 Exemplos de Uso

### Exemplo 1: Logging de Erro HTTP 500

```python
import requests

response = requests.post('http://localhost:8000/api/errors', json={
    "message": "Internal Server Error in user creation",
    "error_type": "HTTP",
    "severity": "CRITICAL",
    "source": "backend",
    "endpoint": "/api/users",
    "method": "POST",
    "status_code": 500,
    "stack_trace": "Traceback...",
    "user_id": "user_789",
    "metadata": {
        "input_data": {"email": "test@example.com"},
        "environment": "production"
    }
})

print(response.json())
```

### Exemplo 2: Buscar Erros Críticos Abertos

```python
import requests

response = requests.get('http://localhost:8000/api/errors', params={
    'severity': 'CRITICAL',
    'status': 'OPEN',
    'limit': 20
})

data = response.json()
print(f"Total de erros críticos abertos: {data['total']}")

for error in data['errors']:
    print(f"#{error['id']}: {error['message']}")
```

### Exemplo 3: Resolver um Erro

```python
import requests

error_id = 15

response = requests.patch(
    f'http://localhost:8000/api/errors/{error_id}',
    json={
        "status": "RESOLVED",
        "assigned_to": "backend_team",
        "notes": "Root cause: connection pool exhausted. Solution: increased pool size from 10 to 50"
    }
)

print(response.json())
```

### Exemplo 4: Obter Estatísticas dos Últimos 30 Dias

```python
import requests

response = requests.get('http://localhost:8000/api/stats/summary', params={
    'days': 30
})

stats = response.json()

print(f"Total de erros: {stats['total_errors']}")
print(f"Taxa diária: {stats['error_rate']} erros/dia")
print(f"Erros críticos: {stats['by_severity']['CRITICAL']}")
print(f"Erros de banco: {stats['by_type']['DATABASE']}")
```

### Exemplo 5: Integração com Try/Catch (Node.js)

```javascript
const axios = require('axios');

async function logErrorToDashboard(error, context = {}) {
  try {
    await axios.post('http://localhost:8000/api/errors', {
      message: error.message,
      error_type: context.errorType || 'APPLICATION',
      severity: context.severity || 'HIGH',
      source: 'backend',
      stack_trace: error.stack,
      endpoint: context.endpoint,
      method: context.method,
      user_id: context.userId,
      metadata: {
        ...context.metadata,
        node_version: process.version,
        timestamp: new Date().toISOString()
      }
    });
  } catch (logError) {
    console.error('Failed to log error to dashboard:', logError);
  }
}

// Uso
try {
  await someRiskyOperation();
} catch (error) {
  await logErrorToDashboard(error, {
    errorType: 'DATABASE',
    severity: 'CRITICAL',
    endpoint: '/api/orders',
    method: 'POST',
    userId: req.user.id,
    metadata: {
      orderId: req.params.orderId
    }
  });
  throw error; // Re-throw se necessário
}
```

---

## 🧪 Testando a API

### Com cURL

```bash
# Health Check
curl http://localhost:8000/health

# Criar erro
curl -X POST http://localhost:8000/api/errors \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test error",
    "error_type": "APPLICATION",
    "severity": "LOW",
    "source": "test"
  }'

# Listar erros
curl "http://localhost:8000/api/errors?limit=10"

# Obter estatísticas
curl "http://localhost:8000/api/stats/summary?days=7"
```

### Com HTTPie

```bash
# Criar erro
http POST localhost:8000/api/errors \
  message="Test error" \
  error_type=APPLICATION \
  severity=LOW \
  source=test

# Atualizar erro
http PATCH localhost:8000/api/errors/1 \
  status=RESOLVED \
  notes="Fixed"
```

### Com Postman

Importe a URL da documentação Swagger:
```
http://localhost:8000/openapi.json
```

---

## ⚠️ Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 200 | OK - Requisição bem-sucedida |
| 201 | Created - Recurso criado com sucesso |
| 204 | No Content - Recurso deletado com sucesso |
| 400 | Bad Request - Dados inválidos |
| 404 | Not Found - Recurso não encontrado |
| 422 | Unprocessable Entity - Validação falhou |
| 500 | Internal Server Error - Erro no servidor |

---

## 🚀 Limites e Performance

- **Taxa de requisições:** Sem limite (recomenda-se implementar rate limiting em produção)
- **Tamanho máximo do body:** 16MB
- **Timeout de requisição:** 30 segundos
- **Limite de paginação:** 1000 registros por requisição
- **Período máximo de estatísticas:** 365 dias

---

## 📚 Recursos Adicionais

- **Documentação Interativa (Swagger):** `http://localhost:8000/docs`
- **Documentação Alternativa (ReDoc):** `http://localhost:8000/redoc`
- **Schema OpenAPI:** `http://localhost:8000/openapi.json`

---

**Última atualização:** 06/11/2024  
**Versão da API:** 1.0.0

