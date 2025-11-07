
# 🔧 Comandos Úteis - Error Dashboard v2.0

## 🐳 Docker

```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Ver logs apenas do backend
docker-compose logs -f backend

# Ver logs apenas do frontend
docker-compose logs -f frontend

# Parar serviços
docker-compose down

# Parar e remover volumes (limpar dados)
docker-compose down -v

# Reiniciar serviços
docker-compose restart

# Ver status dos containers
docker-compose ps

# Reconstruir imagens
docker-compose build

# Reconstruir e iniciar
docker-compose up -d --build
```

## 🔗 Grupos de Erros (Fingerprinting)

```bash
# Listar todos os grupos
curl "http://localhost:8000/api/groups"

# Listar grupos com filtros
curl "http://localhost:8000/api/groups?error_type=DATABASE&severity=CRITICAL"

# Obter detalhes de um grupo específico
curl "http://localhost:8000/api/groups/1"

# Atualizar status de um grupo
curl -X PATCH "http://localhost:8000/api/groups/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "RESOLVED", "notes": "Fixed in v1.2.3"}'

# Atribuir grupo a alguém
curl -X PATCH "http://localhost:8000/api/groups/1" \
  -H "Content-Type: application/json" \
  -d '{"assigned_to": "dev_team"}'

# Deletar grupo e todos os erros associados
curl -X DELETE "http://localhost:8000/api/groups/1"
```

## 🔔 Alertas

```bash
# Listar todas as regras de alerta
curl "http://localhost:8000/api/alerts"

# Obter detalhes de uma regra
curl "http://localhost:8000/api/alerts/1"

# Criar alerta para erros críticos (Slack)
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Critical Errors - Slack",
    "condition": "CRITICAL_ERROR",
    "notification_channels": ["SLACK"],
    "notification_config": {
      "SLACK": {
        "recipient": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
      }
    },
    "cooldown_minutes": 15,
    "is_active": true
  }'

# Criar alerta de contagem de erros (Discord)
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Error Count",
    "condition": "ERROR_COUNT",
    "condition_params": {
      "threshold": 10,
      "time_window_minutes": 5
    },
    "notification_channels": ["DISCORD"],
    "notification_config": {
      "DISCORD": {
        "recipient": "https://discord.com/api/webhooks/YOUR/WEBHOOK"
      }
    },
    "cooldown_minutes": 15,
    "is_active": true
  }'

# Criar alerta de pico de erros (Webhook)
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Error Spike Detection",
    "condition": "ERROR_SPIKE",
    "condition_params": {
      "spike_multiplier": 3,
      "time_window_minutes": 10,
      "comparison_window_minutes": 60
    },
    "notification_channels": ["WEBHOOK"],
    "notification_config": {
      "WEBHOOK": {
        "recipient": "https://webhook.site/your-unique-id"
      }
    },
    "cooldown_minutes": 30,
    "is_active": true
  }'

# Atualizar regra de alerta
curl -X PATCH "http://localhost:8000/api/alerts/1" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'

# Ativar/desativar regra (toggle)
curl -X POST "http://localhost:8000/api/alerts/1/toggle"

# Deletar regra
curl -X DELETE "http://localhost:8000/api/alerts/1"
```

## 📬 Logs de Notificações

```bash
# Listar todas as notificações
curl "http://localhost:8000/api/notifications"

# Listar apenas notificações bem-sucedidas
curl "http://localhost:8000/api/notifications?success_only=true"

# Listar notificações de uma regra específica
curl "http://localhost:8000/api/notifications?alert_rule_id=1"

# Listar notificações de um canal específico
curl "http://localhost:8000/api/notifications?channel=SLACK"

# Listar com paginação
curl "http://localhost:8000/api/notifications?skip=0&limit=20"
```

## 🚨 Criar Erros (para testes)

```bash
# Erro simples
curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test error",
    "error_type": "APPLICATION",
    "severity": "MEDIUM",
    "source": "backend"
  }'

# Erro crítico (dispara alerta se configurado)
curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Database connection failed",
    "error_type": "DATABASE",
    "severity": "CRITICAL",
    "source": "backend",
    "stack_trace": "Traceback...",
    "endpoint": "/api/users",
    "method": "GET"
  }'

# Criar múltiplos erros similares (para testar fingerprinting)
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/errors" \
    -H "Content-Type: application/json" \
    -d "{
      \"message\": \"User $i not found\",
      \"error_type\": \"DATABASE\",
      \"severity\": \"HIGH\",
      \"source\": \"backend\"
    }"
  sleep 1
done

# Criar erros rapidamente (para testar alerta de contagem)
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/errors" \
    -H "Content-Type: application/json" \
    -d "{
      \"message\": \"Rapid test error $i\",
      \"error_type\": \"APPLICATION\",
      \"severity\": \"MEDIUM\",
      \"source\": \"backend\"
    }" &
done
wait
```

## 📊 Estatísticas

```bash
# Resumo estatístico (últimos 7 dias)
curl "http://localhost:8000/api/stats/summary?days=7"

# Resumo dos últimos 30 dias
curl "http://localhost:8000/api/stats/summary?days=30"

# Timeline de erros
curl "http://localhost:8000/api/stats/timeline?days=7"

# Top erros mais frequentes
curl "http://localhost:8000/api/stats/top-errors?limit=10&days=7"
```

## 🔍 Buscar Erros

```bash
# Listar todos os erros
curl "http://localhost:8000/api/errors"

# Filtrar por tipo
curl "http://localhost:8000/api/errors?error_type=DATABASE"

# Filtrar por severidade
curl "http://localhost:8000/api/errors?severity=CRITICAL"

# Filtrar por status
curl "http://localhost:8000/api/errors?status=OPEN"

# Filtrar por período
curl "http://localhost:8000/api/errors?start_date=2024-11-01T00:00:00Z&end_date=2024-11-07T23:59:59Z"

# Busca textual
curl "http://localhost:8000/api/errors?search=database"

# Combinar filtros
curl "http://localhost:8000/api/errors?error_type=DATABASE&severity=CRITICAL&status=OPEN"

# Paginação
curl "http://localhost:8000/api/errors?skip=0&limit=50"

# Obter detalhes de um erro específico
curl "http://localhost:8000/api/errors/1"

# Atualizar erro
curl -X PATCH "http://localhost:8000/api/errors/1" \
  -H "Content-Type: application/json" \
  -d '{"status": "RESOLVED", "notes": "Fixed"}'

# Deletar erro
curl -X DELETE "http://localhost:8000/api/errors/1"
```

## 🔧 Utilitários

```bash
# Health check
curl "http://localhost:8000/health"

# Informações da API
curl "http://localhost:8000/"

# Acessar documentação Swagger
open http://localhost:8000/docs

# Acessar documentação ReDoc
open http://localhost:8000/redoc

# Acessar dashboard
open http://localhost:3000

# Acessar página de grupos
open http://localhost:3000/groups

# Acessar página de alertas
open http://localhost:3000/alerts
```

## 🧪 Scripts de Teste

### Testar Fingerprinting

```bash
#!/bin/bash
# test_fingerprinting.sh

echo "Criando erros similares..."

curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{"message": "User 123 not found", "error_type": "DATABASE", "severity": "HIGH", "source": "backend"}'

curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{"message": "User 456 not found", "error_type": "DATABASE", "severity": "HIGH", "source": "backend"}'

curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{"message": "User 789 not found", "error_type": "DATABASE", "severity": "HIGH", "source": "backend"}'

echo -e "\n\nVerificando grupos criados..."
curl "http://localhost:8000/api/groups" | jq '.groups[] | {id, message_pattern, total_occurrences}'
```

### Testar Alerta de Contagem

```bash
#!/bin/bash
# test_alert_count.sh

echo "Criando regra de alerta..."

curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Alert",
    "condition": "ERROR_COUNT",
    "condition_params": {"threshold": 5, "time_window_minutes": 5},
    "notification_channels": ["WEBHOOK"],
    "notification_config": {"WEBHOOK": {"recipient": "https://webhook.site/unique-id"}},
    "cooldown_minutes": 10,
    "is_active": true
  }'

echo -e "\n\nCriando 6 erros rapidamente..."

for i in {1..6}; do
  curl -X POST "http://localhost:8000/api/errors" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test $i\", \"error_type\": \"APPLICATION\", \"severity\": \"MEDIUM\", \"source\": \"backend\"}"
  sleep 1
done

echo -e "\n\nVerificando notificações..."
sleep 2
curl "http://localhost:8000/api/notifications" | jq '.notifications[0]'
```

## 🔑 Variáveis de Ambiente (para produção)

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/error_dashboard
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@example.com
SMTP_PASSWORD=your-app-password
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+15555555555
```

## 📦 Backup e Restore

```bash
# Backup do banco de dados
docker-compose exec db pg_dump -U postgres error_dashboard > backup.sql

# Restore do banco de dados
docker-compose exec -T db psql -U postgres error_dashboard < backup.sql

# Backup de volumes
docker run --rm -v dashboard-de-erro_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data
```

## 🧹 Limpeza

```bash
# Limpar logs antigos (exemplo: mais de 30 dias)
curl -X DELETE "http://localhost:8000/api/errors?before_date=2024-10-01T00:00:00Z"

# Limpar grupos resolvidos
curl "http://localhost:8000/api/groups?status=RESOLVED" | \
  jq -r '.groups[].id' | \
  xargs -I {} curl -X DELETE "http://localhost:8000/api/groups/{}"

# Limpar notificações antigas
# (implementar endpoint se necessário)
```

## 📊 Monitoramento

```bash
# Ver uso de recursos
docker stats

# Ver espaço em disco
docker system df

# Limpar recursos não utilizados
docker system prune -a

# Ver logs de erro do PostgreSQL
docker-compose logs db | grep ERROR
```

## 🔍 Debug

```bash
# Entrar no container do backend
docker-compose exec backend bash

# Entrar no container do banco
docker-compose exec db psql -U postgres error_dashboard

# Ver variáveis de ambiente
docker-compose exec backend env

# Testar conectividade
docker-compose exec backend ping db
```

---

**Dica**: Salve este arquivo como referência rápida para comandos frequentes!

