# 🔗 Fingerprinting e Alertas - Documentação Completa

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Agrupamento de Erros (Fingerprinting)](#agrupamento-de-erros-fingerprinting)
- [Sistema de Alertas e Notificações](#sistema-de-alertas-e-notificações)
- [API Endpoints](#api-endpoints)
- [Exemplos de Uso](#exemplos-de-uso)
- [Configuração de Canais](#configuração-de-canais)

---

## 🎯 Visão Geral

O Error Dashboard agora inclui dois recursos avançados para melhorar o gerenciamento de erros:

### 1. **Fingerprinting (Agrupamento de Erros)**
- Agrupa automaticamente erros similares
- Reduz ruído e facilita identificação de problemas
- Rastreia ocorrências ao longo do tempo
- Permite gerenciamento em massa de erros relacionados

### 2. **Sistema de Alertas e Notificações**
- Notificações em tempo real via múltiplos canais
- Regras de alerta configuráveis
- Suporte para Slack, Discord, Webhook, Email e SMS
- Cooldown inteligente para evitar spam

---

## 🔗 Agrupamento de Erros (Fingerprinting)

### Como Funciona

O sistema de fingerprinting agrupa automaticamente erros similares usando um algoritmo que analisa:

1. **Tipo do erro** (HTTP, DATABASE, AUTH, etc.)
2. **Mensagem normalizada** (remove IDs, números, timestamps)
3. **Endpoint** (se disponível)
4. **Stack trace** (primeiras linhas)

### Normalização de Mensagens

O algoritmo remove informações variáveis para agrupar erros similares:

```
Original: "User 12345 not found"
Normalizado: "User N not found"

Original: "Connection timeout after 5000ms"
Normalizado: "Connection timeout after Nms"

Original: "Invalid UUID: 550e8400-e29b-41d4-a716-446655440000"
Normalizado: "Invalid UUID: UUID"
```

### Estrutura de um Grupo

```json
{
  "id": 1,
  "fingerprint": "a3f5c8b2...",
  "message_pattern": "Database connection timeout",
  "error_type": "DATABASE",
  "severity": "CRITICAL",
  "source": "backend",
  "total_occurrences": 45,
  "first_seen": "2024-11-01T10:00:00Z",
  "last_seen": "2024-11-07T15:30:00Z",
  "status": "OPEN",
  "assigned_to": "dev_team",
  "notes": "Investigating connection pool issues"
}
```

### Benefícios

✅ **Redução de Ruído**: 1000 erros similares = 1 grupo  
✅ **Visão Consolidada**: Veja tendências e padrões  
✅ **Gerenciamento Eficiente**: Resolva múltiplos erros de uma vez  
✅ **Priorização**: Foque nos grupos com mais ocorrências  

---

## 🔔 Sistema de Alertas e Notificações

### Tipos de Condições de Alerta

#### 1. **ERROR_COUNT** - Contagem de Erros
Dispara quando X erros ocorrem em Y minutos.

```json
{
  "condition": "ERROR_COUNT",
  "condition_params": {
    "threshold": 10,
    "time_window_minutes": 5
  }
}
```

**Exemplo**: Alerta se houver mais de 10 erros em 5 minutos.

#### 2. **ERROR_RATE** - Taxa de Erro
Dispara quando a taxa de erro excede uma porcentagem.

```json
{
  "condition": "ERROR_RATE",
  "condition_params": {
    "threshold_percent": 50,
    "time_window_minutes": 15,
    "min_requests": 100
  }
}
```

**Exemplo**: Alerta se a taxa de erro exceder 50% em 15 minutos.

#### 3. **CRITICAL_ERROR** - Erro Crítico
Dispara imediatamente para qualquer erro com severidade CRITICAL.

```json
{
  "condition": "CRITICAL_ERROR"
}
```

**Exemplo**: Notificação instantânea para erros críticos.

#### 4. **NEW_ERROR_TYPE** - Novo Tipo de Erro
Dispara quando um novo tipo de erro é detectado.

```json
{
  "condition": "NEW_ERROR_TYPE"
}
```

**Exemplo**: Alerta quando um erro nunca visto antes ocorre.

#### 5. **ERROR_SPIKE** - Pico de Erros
Dispara quando há aumento súbito de erros comparado ao baseline.

```json
{
  "condition": "ERROR_SPIKE",
  "condition_params": {
    "spike_multiplier": 3,
    "time_window_minutes": 10,
    "comparison_window_minutes": 60
  }
}
```

**Exemplo**: Alerta se erros triplicarem nos últimos 10 minutos comparado à última hora.

### Canais de Notificação

#### 🟦 Slack

```json
{
  "notification_channels": ["SLACK"],
  "notification_config": {
    "SLACK": {
      "recipient": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    }
  }
}
```

**Configuração do Webhook Slack**:
1. Acesse https://api.slack.com/apps
2. Crie um novo app ou selecione existente
3. Ative "Incoming Webhooks"
4. Adicione novo webhook ao workspace
5. Copie a URL do webhook

#### 🟪 Discord

```json
{
  "notification_channels": ["DISCORD"],
  "notification_config": {
    "DISCORD": {
      "recipient": "https://discord.com/api/webhooks/YOUR/WEBHOOK/URL"
    }
  }
}
```

**Configuração do Webhook Discord**:
1. Vá para Configurações do Servidor → Integrações
2. Crie um webhook
3. Escolha o canal de destino
4. Copie a URL do webhook

#### 🌐 Webhook Genérico

```json
{
  "notification_channels": ["WEBHOOK"],
  "notification_config": {
    "WEBHOOK": {
      "recipient": "https://your-api.com/webhook",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN"
      },
      "custom_fields": {
        "environment": "production"
      }
    }
  }
}
```

**Payload enviado**:
```json
{
  "subject": "🔴 [CRITICAL] DATABASE Error",
  "message": "Error Type: DATABASE\nSeverity: CRITICAL\n...",
  "timestamp": "2024-11-07T15:30:00Z",
  "source": "error-dashboard",
  "environment": "production"
}
```

#### 📧 Email

```json
{
  "notification_channels": ["EMAIL"],
  "notification_config": {
    "EMAIL": {
      "recipient": "admin@example.com",
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "smtp_user": "your-email@gmail.com",
      "smtp_password": "your-app-password",
      "from_email": "alerts@yourdomain.com"
    }
  }
}
```

**Gmail App Password**:
1. Ative autenticação de 2 fatores
2. Vá para https://myaccount.google.com/apppasswords
3. Gere uma senha de app
4. Use essa senha no campo `smtp_password`

#### 📱 SMS (Twilio)

```json
{
  "notification_channels": ["SMS"],
  "notification_config": {
    "SMS": {
      "recipient": "+5511999999999",
      "twilio_account_sid": "ACxxxxxxxxxxxxx",
      "twilio_auth_token": "your_auth_token",
      "twilio_phone_number": "+15555555555"
    }
  }
}
```

**Configuração Twilio**:
1. Crie conta em https://www.twilio.com
2. Obtenha Account SID e Auth Token
3. Compre um número de telefone
4. Configure as credenciais

### Cooldown

O cooldown evita spam de notificações. Se uma regra for disparada, ela só poderá disparar novamente após o período de cooldown.

```json
{
  "cooldown_minutes": 15
}
```

**Exemplo**: Se alertar às 10:00, só alertará novamente após 10:15.

---

## 📡 API Endpoints

### Grupos de Erros

#### Listar Grupos
```http
GET /api/groups?error_type=DATABASE&severity=CRITICAL&limit=50
```

**Resposta**:
```json
{
  "total": 25,
  "skip": 0,
  "limit": 50,
  "groups": [...]
}
```

#### Detalhes do Grupo
```http
GET /api/groups/{group_id}
```

**Resposta**:
```json
{
  "id": 1,
  "fingerprint": "a3f5c8b2...",
  "message_pattern": "Database connection timeout",
  "total_occurrences": 45,
  "recent_errors": [...]
}
```

#### Atualizar Grupo
```http
PATCH /api/groups/{group_id}
Content-Type: application/json

{
  "status": "RESOLVED",
  "assigned_to": "dev_team",
  "notes": "Fixed by increasing connection pool size"
}
```

#### Deletar Grupo
```http
DELETE /api/groups/{group_id}
```

### Regras de Alerta

#### Listar Regras
```http
GET /api/alerts
```

#### Criar Regra
```http
POST /api/alerts
Content-Type: application/json

{
  "name": "High Error Rate Alert",
  "description": "Alert when error rate is high",
  "condition": "ERROR_COUNT",
  "error_type": "DATABASE",
  "severity": "CRITICAL",
  "condition_params": {
    "threshold": 10,
    "time_window_minutes": 5
  },
  "notification_channels": ["SLACK", "EMAIL"],
  "notification_config": {
    "SLACK": {
      "recipient": "https://hooks.slack.com/..."
    },
    "EMAIL": {
      "recipient": "admin@example.com",
      "smtp_host": "smtp.gmail.com",
      "smtp_port": 587,
      "smtp_user": "alerts@example.com",
      "smtp_password": "password"
    }
  },
  "cooldown_minutes": 15,
  "is_active": true
}
```

#### Atualizar Regra
```http
PATCH /api/alerts/{rule_id}
Content-Type: application/json

{
  "is_active": false
}
```

#### Ativar/Desativar Regra
```http
POST /api/alerts/{rule_id}/toggle
```

#### Deletar Regra
```http
DELETE /api/alerts/{rule_id}
```

### Logs de Notificações

#### Listar Notificações
```http
GET /api/notifications?alert_rule_id=1&success_only=true&limit=50
```

**Resposta**:
```json
{
  "total": 15,
  "skip": 0,
  "limit": 50,
  "notifications": [
    {
      "id": 1,
      "alert_rule_id": 1,
      "channel": "SLACK",
      "recipient": "https://hooks.slack.com/...",
      "subject": "🔴 [CRITICAL] DATABASE Error",
      "message": "Error Type: DATABASE...",
      "sent_successfully": true,
      "sent_at": "2024-11-07T15:30:00Z"
    }
  ]
}
```

---

## 💡 Exemplos de Uso

### Exemplo 1: Alerta de Erros Críticos no Slack

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Critical Errors - Slack",
    "description": "Immediate notification for critical errors",
    "condition": "CRITICAL_ERROR",
    "notification_channels": ["SLACK"],
    "notification_config": {
      "SLACK": {
        "recipient": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
      }
    },
    "cooldown_minutes": 5,
    "is_active": true
  }'
```

### Exemplo 2: Alerta de Pico de Erros no Discord

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Error Spike Detection",
    "description": "Alert when errors spike suddenly",
    "condition": "ERROR_SPIKE",
    "condition_params": {
      "spike_multiplier": 3,
      "time_window_minutes": 10,
      "comparison_window_minutes": 60
    },
    "notification_channels": ["DISCORD"],
    "notification_config": {
      "DISCORD": {
        "recipient": "https://discord.com/api/webhooks/YOUR/WEBHOOK"
      }
    },
    "cooldown_minutes": 30,
    "is_active": true
  }'
```

### Exemplo 3: Alerta Multi-Canal para Erros de Database

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Database Errors - Multi-Channel",
    "description": "Alert via Slack and Email for database errors",
    "condition": "ERROR_COUNT",
    "error_type": "DATABASE",
    "severity": "HIGH",
    "condition_params": {
      "threshold": 5,
      "time_window_minutes": 10
    },
    "notification_channels": ["SLACK", "EMAIL"],
    "notification_config": {
      "SLACK": {
        "recipient": "https://hooks.slack.com/services/YOUR/WEBHOOK"
      },
      "EMAIL": {
        "recipient": "dba@example.com",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "alerts@example.com",
        "smtp_password": "your-app-password"
      }
    },
    "cooldown_minutes": 15,
    "is_active": true
  }'
```

### Exemplo 4: Consultar Grupos de Erros

```bash
# Listar todos os grupos
curl "http://localhost:8000/api/groups"

# Filtrar por tipo e severidade
curl "http://localhost:8000/api/groups?error_type=DATABASE&severity=CRITICAL"

# Obter detalhes de um grupo específico
curl "http://localhost:8000/api/groups/1"

# Atualizar status de um grupo
curl -X PATCH "http://localhost:8000/api/groups/1" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "RESOLVED",
    "notes": "Fixed by optimizing database queries"
  }'
```

---

## 🎨 Interface Web

### Página de Grupos de Erros

Acesse: `http://localhost:3000/groups`

**Recursos**:
- ✅ Visualização de todos os grupos de erros
- ✅ Filtros por tipo, severidade, origem e status
- ✅ Estatísticas de ocorrências
- ✅ Indicadores visuais de severidade
- ✅ Informações de primeira e última ocorrência

### Página de Detalhes do Grupo

Acesse: `http://localhost:3000/groups/{id}`

**Recursos**:
- ✅ Informações completas do grupo
- ✅ Fingerprint único
- ✅ Lista de erros recentes do grupo
- ✅ Edição de status, atribuição e notas
- ✅ Deleção do grupo e erros associados

### Página de Alertas

Acesse: `http://localhost:3000/alerts`

**Recursos**:
- ✅ Listagem de todas as regras de alerta
- ✅ Criação de novas regras com formulário intuitivo
- ✅ Edição de regras existentes
- ✅ Ativação/desativação rápida
- ✅ Configuração de múltiplos canais
- ✅ Visualização de último disparo

---

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```env
# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@example.com
SMTP_PASSWORD=your-app-password

# Twilio (SMS)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+15555555555
```

### Customização de Mensagens

As mensagens de notificação são formatadas automaticamente, mas você pode customizar adicionando campos no `notification_config`:

```json
{
  "notification_config": {
    "WEBHOOK": {
      "recipient": "https://your-api.com/webhook",
      "custom_fields": {
        "environment": "production",
        "team": "backend",
        "priority": "high"
      }
    }
  }
}
```

---

## 📊 Melhores Práticas

### Fingerprinting

1. **Revise grupos regularmente**: Alguns erros podem ser agrupados incorretamente
2. **Use notas**: Documente soluções para referência futura
3. **Atribua responsáveis**: Facilita o acompanhamento
4. **Resolva grupos inteiros**: Quando corrigir a causa raiz

### Alertas

1. **Comece conservador**: Use thresholds altos e ajuste conforme necessário
2. **Use cooldown adequado**: Evite fadiga de alertas (15-30 minutos recomendado)
3. **Combine condições**: Use filtros para alertas específicos
4. **Teste antes de ativar**: Verifique se as notificações chegam corretamente
5. **Múltiplos canais**: Use Slack para equipe e Email para gerência
6. **Monitore logs de notificação**: Verifique se estão sendo enviadas com sucesso

---

## 🐛 Troubleshooting

### Notificações não estão sendo enviadas

1. Verifique se a regra está ativa
2. Confirme que não está em cooldown
3. Verifique logs de notificação: `GET /api/notifications?success_only=false`
4. Teste credenciais (SMTP, Twilio, etc.)
5. Verifique firewall/proxy

### Erros não estão sendo agrupados

1. Verifique se o fingerprint está sendo gerado
2. Confirme que mensagens são similares o suficiente
3. Stack traces muito diferentes podem criar grupos separados
4. Revise a função `generate_fingerprint()` em `models.py`

### Performance

1. Use índices no banco de dados (já configurados)
2. Limite janelas de tempo em condições de alerta
3. Configure cooldown apropriado
4. Considere arquivar grupos antigos

---

## 📈 Roadmap Futuro

- [ ] Integração com PagerDuty
- [ ] Integração com Microsoft Teams
- [ ] Dashboard de métricas de alertas
- [ ] Machine Learning para detecção de anomalias
- [ ] Templates de mensagens customizáveis
- [ ] Agendamento de alertas (horário comercial)
- [ ] Escalação automática de alertas
- [ ] Integração com Jira/GitHub Issues

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Áreas de interesse:

- Novos canais de notificação
- Melhorias no algoritmo de fingerprinting
- Novas condições de alerta
- Otimizações de performance

---

**Desenvolvido com ❤️ para melhorar o gerenciamento de erros**

