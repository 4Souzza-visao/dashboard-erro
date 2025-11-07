# 🚨 Error Dashboard - Sistema de Monitoramento de Erros

Dashboard profissional para monitoramento e gestão de logs de erros em aplicações web. Sistema completo com backend FastAPI, frontend React e banco de dados PostgreSQL, pronto para rodar no Docker Compose.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![React](https://img.shields.io/badge/react-18.2-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)

## 📋 Índice

- [Características](#-características)
- [Tipos de Erros Monitorados](#-tipos-de-erros-monitorados)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [API Documentation](#-api-documentation)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Exemplos de Integração](#-exemplos-de-integração)

## ✨ Características

### Dashboard Completo
- 📊 **Visualização em tempo real** de erros e métricas
- 📈 **Gráficos interativos** (timeline, distribuição por tipo e severidade)
- 🔍 **Filtros avançados** por tipo, severidade, origem, status e período
- 📱 **Interface responsiva** e moderna
- 🎨 **Design profissional** com UX otimizada

### Sistema de Gerenciamento
- ✅ **Categorização automática** de erros
- 🏷️ **Sistema de status** (Aberto, Em Progresso, Resolvido, Ignorado)
- 📝 **Notas e atribuições** para cada erro
- 🔎 **Busca textual** em mensagens e stack traces
- 📊 **Estatísticas detalhadas** e relatórios

### 🔗 Agrupamento de Erros (Fingerprinting) - NOVO!
- 🎯 **Agrupamento automático** de erros similares
- 🔍 **Algoritmo inteligente** que normaliza mensagens e stack traces
- 📈 **Rastreamento de ocorrências** ao longo do tempo
- 🎛️ **Gerenciamento em massa** de erros relacionados
- 📊 **Redução de ruído** - visualize apenas grupos únicos

### 🔔 Sistema de Alertas e Notificações - NOVO!
- 📢 **Notificações em tempo real** via múltiplos canais
- 🎚️ **5 tipos de condições**: Contagem, Taxa, Crítico, Novo Tipo, Pico
- 📱 **Canais suportados**: Slack, Discord, Webhook, Email, SMS
- ⏱️ **Cooldown inteligente** para evitar spam
- 🎯 **Filtros avançados** por tipo, severidade e origem
- 📝 **Logs de notificações** para auditoria

### API REST Completa
- 🚀 **FastAPI** com documentação automática (Swagger/OpenAPI)
- 🔐 **Pronta para autenticação** (estrutura preparada)
- 📦 **Endpoints RESTful** bem definidos
- 🎯 **Validação de dados** com Pydantic
- 📖 **Documentação interativa** em `/docs`

## 🎯 Tipos de Erros Monitorados

O sistema monitora 8 categorias principais de erros:

### 1. **HTTP** (Erros de Requisições HTTP)
- Códigos 4xx (Cliente)
  - 400 Bad Request
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found
- Códigos 5xx (Servidor)
  - 500 Internal Server Error
  - 502 Bad Gateway
  - 503 Service Unavailable
  - 504 Gateway Timeout

**Casos de uso:**
- Endpoints não encontrados
- Erros de servidor inesperados
- Problemas de roteamento
- Falhas em APIs REST

### 2. **DATABASE** (Erros de Banco de Dados)
- Erros de conexão
- Timeouts de query
- Violações de constraint (unique, foreign key)
- Pool de conexões esgotado
- Deadlocks
- Erros de transação

**Casos de uso:**
- Falhas de conexão com PostgreSQL/MySQL
- Queries lentas ou com timeout
- Problemas de integridade de dados
- Erros de migração

### 3. **AUTH** (Autenticação/Autorização)
- Token inválido ou expirado
- Sessão expirada
- Credenciais inválidas
- Permissões insuficientes
- Falhas de OAuth/JWT

**Casos de uso:**
- Tentativas de login falhadas
- Tokens JWT expirados
- Acesso não autorizado a recursos
- Problemas com refresh tokens

### 4. **VALIDATION** (Erros de Validação)
- Dados inválidos em formulários
- Campos obrigatórios ausentes
- Formato incorreto (email, telefone, etc.)
- Violações de regras de negócio
- Validação de schema

**Casos de uso:**
- Formulários com dados inválidos
- APIs recebendo payloads incorretos
- Validação de entrada de usuário
- Verificação de regras de negócio

### 5. **PERFORMANCE** (Problemas de Performance)
- Timeouts de requisição
- Uso excessivo de memória
- CPU alta
- Queries lentas
- Limites de recursos excedidos

**Casos de uso:**
- Requisições que excedem tempo limite
- Memory leaks
- Processos consumindo muita CPU
- Problemas de escalabilidade

### 6. **INTEGRATION** (Erros de Integração)
- APIs externas indisponíveis
- Timeouts em chamadas externas
- Respostas inválidas de serviços externos
- Falhas em webhooks
- Problemas com serviços de terceiros

**Casos de uso:**
- Gateway de pagamento offline
- Serviço de email falhando
- APIs de terceiros com timeout
- Webhooks não processados

### 7. **APPLICATION** (Erros de Aplicação)
- Exceptions não tratadas
- NullPointerException
- Erros de lógica de negócio
- Falhas em processamento assíncrono
- Erros de configuração

**Casos de uso:**
- Bugs no código
- Erros em workers/background jobs
- Problemas de configuração
- Exceptions não capturadas

### 8. **FRONTEND** (Erros de Frontend)
- Erros JavaScript/TypeScript
- Falhas de renderização React/Vue/Angular
- Network errors
- Falhas ao carregar recursos
- Erros de estado/props

**Casos de uso:**
- TypeError no JavaScript
- Componentes React com erro
- Falhas ao buscar dados da API
- Problemas de bundle/chunk loading

## 🎚️ Níveis de Severidade

Cada erro é classificado em um dos 4 níveis:

- **🟢 LOW** (Baixa): Erros que não afetam funcionalidade crítica
- **🟡 MEDIUM** (Média): Erros que afetam funcionalidade mas têm workaround
- **🟠 HIGH** (Alta): Erros que afetam funcionalidade importante
- **🔴 CRITICAL** (Crítica): Erros que impedem funcionamento ou afetam segurança

## 🛠️ Tecnologias

### Backend
- **FastAPI** 0.104.1 - Framework web moderno e rápido
- **SQLAlchemy** 2.0.23 - ORM para Python
- **PostgreSQL** 15 - Banco de dados relacional
- **Pydantic** 2.5.0 - Validação de dados
- **Uvicorn** - ASGI server de alta performance

### Frontend
- **React** 18.2 - Biblioteca UI
- **React Router** 6.20 - Roteamento
- **Chart.js** 4.4 - Gráficos interativos
- **Axios** - Cliente HTTP
- **React Icons** - Ícones
- **date-fns** - Manipulação de datas

### DevOps
- **Docker** & **Docker Compose** - Containerização
- **Nginx** - Servidor web para frontend
- **PostgreSQL** - Banco de dados containerizado

## 📦 Instalação

### Pré-requisitos
- Docker & Docker Compose instalados
- Git (opcional, para clonar o repositório)

### Passo a Passo

1. **Clone ou baixe o projeto**
```bash
git clone <repository-url>
cd dashboard-de-erro
```

2. **Inicie os containers**
```bash
docker-compose up -d
```

Isso irá:
- Criar o banco de dados PostgreSQL
- Iniciar o backend na porta 8000
- Iniciar o frontend na porta 3000
- Configurar a rede entre os serviços

3. **Aguarde os serviços iniciarem** (aproximadamente 30 segundos)

4. **Popule o banco com dados de exemplo** (opcional)
```bash
# Dentro do container do backend
docker-compose exec backend python init_db.py
```

Ou use o script Python externo:
```bash
# Certifique-se de ter requests instalado: pip install requests
python scripts/generate_sample_errors.py
```

## 🚀 Uso

### Acessar o Dashboard
```
http://localhost:3000
```

### Acessar a API
```
http://localhost:8000
```

### Documentação Interativa da API (Swagger)
```
http://localhost:8000/docs
```

### Documentação Alternativa (ReDoc)
```
http://localhost:8000/redoc
```

### Parar os serviços
```bash
docker-compose down
```

### Remover volumes (limpar dados)
```bash
docker-compose down -v
```

### Ver logs
```bash
# Todos os serviços
docker-compose logs -f

# Apenas backend
docker-compose logs -f backend

# Apenas frontend
docker-compose logs -f frontend
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints Principais

#### 1. Criar um Erro
```http
POST /api/errors
Content-Type: application/json

{
  "message": "Database connection timeout",
  "error_type": "DATABASE",
  "severity": "CRITICAL",
  "source": "backend",
  "stack_trace": "Traceback...",
  "endpoint": "/api/users",
  "method": "GET",
  "status_code": 500,
  "user_id": "user_123",
  "ip_address": "192.168.1.100",
  "metadata": {
    "server": "prod-01",
    "region": "us-east-1"
  }
}
```

**Resposta:**
```json
{
  "id": 1,
  "message": "Database connection timeout",
  "error_type": "DATABASE",
  "severity": "CRITICAL",
  "source": "backend",
  "status": "OPEN",
  "timestamp": "2024-11-06T10:30:00Z",
  "occurrences": 1
}
```

#### 2. Listar Erros com Filtros
```http
GET /api/errors?error_type=HTTP&severity=CRITICAL&limit=50&skip=0
```

**Parâmetros de Query:**
- `skip` (int): Paginação - número de registros para pular
- `limit` (int): Limite de registros (máx: 1000)
- `error_type` (string): Filtrar por tipo
- `severity` (string): Filtrar por severidade
- `source` (string): Filtrar por origem
- `status` (string): Filtrar por status
- `start_date` (datetime): Data inicial
- `end_date` (datetime): Data final
- `search` (string): Busca textual

**Resposta:**
```json
{
  "total": 150,
  "skip": 0,
  "limit": 50,
  "errors": [...]
}
```

#### 3. Obter Detalhes de um Erro
```http
GET /api/errors/{error_id}
```

#### 4. Atualizar Status de um Erro
```http
PATCH /api/errors/{error_id}
Content-Type: application/json

{
  "status": "RESOLVED",
  "assigned_to": "dev_team",
  "notes": "Fixed by deploying patch v1.2.3"
}
```

#### 5. Deletar um Erro
```http
DELETE /api/errors/{error_id}
```

#### 6. Obter Estatísticas
```http
GET /api/stats/summary?days=7
```

**Resposta:**
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
    ...
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

#### 7. Timeline de Erros
```http
GET /api/stats/timeline?days=30
```

#### 8. Top Erros Mais Frequentes
```http
GET /api/stats/top-errors?limit=10&days=7
```

### Enums Válidos

**ErrorType:**
- `HTTP`
- `DATABASE`
- `AUTH`
- `VALIDATION`
- `PERFORMANCE`
- `INTEGRATION`
- `APPLICATION`
- `FRONTEND`

**Severity:**
- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

**ErrorStatus:**
- `OPEN`
- `IN_PROGRESS`
- `RESOLVED`
- `IGNORED`

**Source (exemplos):**
- `frontend`
- `backend`
- `database`
- `api`
- `external_service`

## 📁 Estrutura do Projeto

```
dashboard-de-erro/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                    # API principal
│   ├── models.py                  # Modelos SQLAlchemy (com Fingerprinting)
│   ├── schemas.py                 # Schemas Pydantic
│   ├── database.py                # Configuração do banco
│   ├── notification_service.py    # Serviço de notificações
│   ├── alert_service.py           # Serviço de alertas
│   └── init_db.py                 # Script de inicialização
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── services/
│       │   └── api.js             # Cliente API
│       ├── components/
│       │   ├── Layout.js
│       │   ├── StatCard.js
│       │   └── ErrorTable.js
│       └── pages/
│           ├── Dashboard.js
│           ├── ErrorList.js
│           ├── ErrorDetail.js
│           ├── ErrorGroups.js     # Página de grupos (NOVO)
│           ├── GroupDetail.js     # Detalhes do grupo (NOVO)
│           └── Alerts.js          # Configuração de alertas (NOVO)
├── scripts/
│   └── generate_sample_errors.py
├── docker-compose.yml
├── README.md
└── FINGERPRINTING_E_ALERTAS.md    # Documentação completa (NOVO)
```

## 🔌 Exemplos de Integração

### Python / Flask
```python
import requests
import traceback

API_URL = "http://localhost:8000"

def log_error(error, error_type="APPLICATION", severity="HIGH"):
    """Envia erro para o dashboard"""
    try:
        payload = {
            "message": str(error),
            "error_type": error_type,
            "severity": severity,
            "source": "backend",
            "stack_trace": traceback.format_exc()
        }
        requests.post(f"{API_URL}/api/errors", json=payload)
    except Exception as e:
        print(f"Failed to log error: {e}")

# Uso
try:
    # seu código aqui
    result = some_function()
except Exception as e:
    log_error(e, error_type="APPLICATION", severity="CRITICAL")
```

### JavaScript / Node.js
```javascript
const axios = require('axios');

const API_URL = 'http://localhost:8000';

async function logError(error, errorType = 'APPLICATION', severity = 'HIGH') {
  try {
    await axios.post(`${API_URL}/api/errors`, {
      message: error.message,
      error_type: errorType,
      severity: severity,
      source: 'backend',
      stack_trace: error.stack,
      metadata: {
        name: error.name,
        code: error.code
      }
    });
  } catch (err) {
    console.error('Failed to log error:', err);
  }
}

// Uso
try {
  // seu código aqui
  await someAsyncFunction();
} catch (error) {
  await logError(error, 'DATABASE', 'CRITICAL');
}
```

### React / Frontend
```javascript
import axios from 'axios';

const API_URL = 'http://localhost:8000';

class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    // Enviar erro para o dashboard
    axios.post(`${API_URL}/api/errors`, {
      message: error.toString(),
      error_type: 'FRONTEND',
      severity: 'HIGH',
      source: 'frontend',
      stack_trace: errorInfo.componentStack,
      user_agent: navigator.userAgent,
      metadata: {
        url: window.location.href,
        component: errorInfo.componentStack.split('\n')[1]
      }
    }).catch(err => console.error('Failed to log error:', err));
  }

  render() {
    return this.props.children;
  }
}

// Capturar erros globais
window.addEventListener('error', (event) => {
  axios.post(`${API_URL}/api/errors`, {
    message: event.message,
    error_type: 'FRONTEND',
    severity: 'MEDIUM',
    source: 'frontend',
    stack_trace: event.error?.stack,
    endpoint: event.filename,
    metadata: {
      line: event.lineno,
      column: event.colno
    }
  });
});
```

### Curl (para testes manuais)
```bash
curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test error from curl",
    "error_type": "APPLICATION",
    "severity": "LOW",
    "source": "test"
  }'
```

## 🔒 Segurança e Produção

⚠️ **Atenção:** Este projeto é uma base para desenvolvimento. Para uso em produção, considere:

1. **Autenticação e Autorização**
   - Implementar JWT ou OAuth2
   - Proteger endpoints sensíveis
   - Validar permissões de usuário

2. **CORS**
   - Configurar origins específicos (não usar `*`)
   - Definir headers permitidos

3. **HTTPS**
   - Usar certificados SSL/TLS
   - Redirecionar HTTP para HTTPS

4. **Variáveis de Ambiente**
   - Nunca commitar senhas
   - Usar secrets management (Vault, AWS Secrets Manager)

5. **Rate Limiting**
   - Implementar limites de requisições
   - Proteger contra DDoS

6. **Backup**
   - Configurar backup automático do PostgreSQL
   - Testar restauração de backups

7. **Monitoramento**
   - Configurar alertas para erros críticos
   - Monitorar recursos (CPU, memória, disco)

## 📊 Recursos do Dashboard

### Página Principal (Dashboard)
- Cards com métricas principais
- Gráfico de timeline de erros
- Gráfico de distribuição por severidade (Doughnut)
- Gráfico de distribuição por tipo (Bar)
- Lista dos erros mais frequentes
- Tabela de erros recentes

### Página de Logs
- Tabela completa de erros
- Filtros avançados
- Busca textual
- Paginação
- Ordenação

### Página de Detalhes
- Informações completas do erro
- Stack trace formatado
- Metadados JSON
- Histórico de status
- Ações (atualizar status, deletar)

### 🔗 Página de Grupos de Erros (NOVO)
- Visualização de erros agrupados por fingerprint
- Filtros por tipo, severidade, origem e status
- Estatísticas de ocorrências por grupo
- Indicadores visuais de severidade
- Informações de primeira e última ocorrência

### 📋 Página de Detalhes do Grupo (NOVO)
- Informações completas do grupo
- Fingerprint único do grupo
- Lista de erros recentes do grupo (últimos 10)
- Edição de status, atribuição e notas
- Deleção do grupo e erros associados

### 🔔 Página de Alertas (NOVO)
- Listagem de todas as regras de alerta
- Criação de novas regras com formulário intuitivo
- Edição de regras existentes
- Ativação/desativação rápida de regras
- Configuração de múltiplos canais de notificação
- Visualização de último disparo e histórico

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abrir um Pull Request

## 🆕 Novos Recursos (v2.0)

### Agrupamento de Erros (Fingerprinting)

O sistema agora agrupa automaticamente erros similares usando um algoritmo inteligente de fingerprinting. Isso reduz significativamente o ruído e permite que você foque nos problemas reais.

**Acesse**: `http://localhost:3000/groups`

**Documentação completa**: [FINGERPRINTING_E_ALERTAS.md](FINGERPRINTING_E_ALERTAS.md)

**Exemplo de uso**:
```bash
# Listar grupos de erros
curl "http://localhost:8000/api/groups?severity=CRITICAL"

# Obter detalhes de um grupo
curl "http://localhost:8000/api/groups/1"

# Atualizar status do grupo
curl -X PATCH "http://localhost:8000/api/groups/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "RESOLVED", "notes": "Fixed in v1.2.3"}'
```

### Sistema de Alertas e Notificações

Configure regras de alerta para ser notificado automaticamente sobre erros críticos via Slack, Discord, Email, SMS ou Webhook.

**Acesse**: `http://localhost:3000/alerts`

**Canais suportados**:
- 🟦 **Slack** - Webhooks
- 🟪 **Discord** - Webhooks
- 🌐 **Webhook** - HTTP POST genérico
- 📧 **Email** - SMTP
- 📱 **SMS** - Twilio

**Tipos de condições**:
1. **ERROR_COUNT**: X erros em Y minutos
2. **ERROR_RATE**: Taxa de erro excede X%
3. **CRITICAL_ERROR**: Qualquer erro crítico
4. **NEW_ERROR_TYPE**: Novo tipo de erro detectado
5. **ERROR_SPIKE**: Aumento súbito de erros

**Exemplo de configuração**:
```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Critical Errors Alert",
    "condition": "CRITICAL_ERROR",
    "notification_channels": ["SLACK"],
    "notification_config": {
      "SLACK": {
        "recipient": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
      }
    },
    "cooldown_minutes": 15
  }'
```

**Para mais detalhes**, consulte: [FINGERPRINTING_E_ALERTAS.md](FINGERPRINTING_E_ALERTAS.md)

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

Desenvolvido para demonstração de um sistema completo de monitoramento de erros com fingerprinting e alertas inteligentes.

## 🆘 Suporte

Se você encontrar problemas:

1. Verifique se o Docker está rodando: `docker ps`
2. Veja os logs: `docker-compose logs -f`
3. Recrie os containers: `docker-compose down && docker-compose up -d`
4. Verifique as portas 3000 e 8000 estão livres

**Problemas com notificações?**
- Verifique logs de notificação: `GET /api/notifications?success_only=false`
- Confirme credenciais (SMTP, Twilio, etc.)
- Teste webhooks manualmente

---

**Feito com ❤️ usando FastAPI, React e Docker**

**v2.0** - Agora com Fingerprinting e Alertas Inteligentes! 🚀

