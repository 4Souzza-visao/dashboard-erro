# 🚀 Guia Rápido - Fingerprinting e Alertas

## 📋 Início Rápido

### 1️⃣ Subir o Sistema

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar se está rodando
docker-compose ps
```

### 2️⃣ Acessar o Dashboard

Abra seu navegador em: **http://localhost:3000**

Você verá agora 4 páginas no menu:
- 🏠 **Dashboard** - Visão geral
- 🚨 **Logs de Erros** - Todos os erros
- 🔗 **Grupos de Erros** - Erros agrupados (NOVO!)
- 🔔 **Alertas** - Configuração de notificações (NOVO!)

---

## 🔗 Testando Fingerprinting

### Criar Erros Similares

```bash
# Erro 1
curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "User 123 not found",
    "error_type": "DATABASE",
    "severity": "HIGH",
    "source": "backend"
  }'

# Erro 2 (similar ao anterior)
curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "User 456 not found",
    "error_type": "DATABASE",
    "severity": "HIGH",
    "source": "backend"
  }'

# Erro 3 (similar aos anteriores)
curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "User 789 not found",
    "error_type": "DATABASE",
    "severity": "HIGH",
    "source": "backend"
  }'
```

### Verificar Agrupamento

```bash
# Ver grupos criados
curl "http://localhost:8000/api/groups"
```

**Resultado esperado**: Os 3 erros serão agrupados em 1 único grupo com `total_occurrences: 3`

### Visualizar no Dashboard

1. Acesse: http://localhost:3000/groups
2. Você verá 1 grupo com 3 ocorrências
3. Clique no grupo para ver detalhes
4. Veja os 3 erros individuais listados

---

## 🔔 Configurando Seu Primeiro Alerta

### Opção 1: Via Interface Web (Recomendado)

1. Acesse: **http://localhost:3000/alerts**
2. Clique em **"+ Nova Regra"**
3. Preencha o formulário:
   - **Nome**: "Alerta de Erros Críticos"
   - **Condição**: "Erro Crítico"
   - **Canal**: Marque "WEBHOOK"
   - **Webhook URL**: `https://webhook.site/unique-id` (use https://webhook.site para testar)
4. Clique em **"Criar Regra"**

### Opção 2: Via API

#### Alerta para Slack

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Erros Críticos - Slack",
    "description": "Notifica no Slack quando houver erro crítico",
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
```

**Como obter Webhook do Slack**:
1. Acesse: https://api.slack.com/apps
2. Crie um app ou selecione existente
3. Ative "Incoming Webhooks"
4. Adicione webhook ao workspace
5. Copie a URL

#### Alerta para Discord

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Pico de Erros - Discord",
    "description": "Alerta quando houver aumento súbito de erros",
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

**Como obter Webhook do Discord**:
1. Configurações do Servidor → Integrações
2. Criar webhook
3. Escolher canal
4. Copiar URL

---

## 🧪 Testando Alertas

### Teste 1: Erro Crítico

```bash
# Criar erro crítico (deve disparar alerta se configurado)
curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Database connection failed",
    "error_type": "DATABASE",
    "severity": "CRITICAL",
    "source": "backend"
  }'
```

**Resultado esperado**: 
- Notificação enviada para o canal configurado
- Aparece em http://localhost:3000/alerts com "Último disparo" atualizado

### Teste 2: Múltiplos Erros (Contagem)

Primeiro, crie uma regra de contagem:

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Muitos Erros",
    "condition": "ERROR_COUNT",
    "condition_params": {
      "threshold": 5,
      "time_window_minutes": 5
    },
    "notification_channels": ["WEBHOOK"],
    "notification_config": {
      "WEBHOOK": {
        "recipient": "https://webhook.site/your-unique-id"
      }
    },
    "cooldown_minutes": 10,
    "is_active": true
  }'
```

Depois, crie 5+ erros rapidamente:

```bash
for i in {1..6}; do
  curl -X POST "http://localhost:8000/api/errors" \
    -H "Content-Type: application/json" \
    -d "{
      \"message\": \"Test error $i\",
      \"error_type\": \"APPLICATION\",
      \"severity\": \"MEDIUM\",
      \"source\": \"backend\"
    }"
  sleep 1
done
```

**Resultado esperado**: Alerta disparado após 5º erro

### Verificar Logs de Notificação

```bash
# Ver todas as notificações enviadas
curl "http://localhost:8000/api/notifications"

# Ver apenas notificações com sucesso
curl "http://localhost:8000/api/notifications?success_only=true"

# Ver notificações de uma regra específica
curl "http://localhost:8000/api/notifications?alert_rule_id=1"
```

Ou na interface web: A página de alertas mostra "Último disparo" para cada regra.

---

## 📊 Casos de Uso Práticos

### Caso 1: Monitorar Erros de Produção

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Erros de Produção",
    "description": "Alerta para erros críticos em produção",
    "condition": "CRITICAL_ERROR",
    "source": "production",
    "notification_channels": ["SLACK", "EMAIL"],
    "notification_config": {
      "SLACK": {
        "recipient": "https://hooks.slack.com/services/YOUR/WEBHOOK"
      },
      "EMAIL": {
        "recipient": "oncall@company.com",
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_user": "alerts@company.com",
        "smtp_password": "your-password"
      }
    },
    "cooldown_minutes": 5,
    "is_active": true
  }'
```

### Caso 2: Monitorar Database

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Database Issues",
    "description": "Alerta quando houver muitos erros de database",
    "condition": "ERROR_COUNT",
    "error_type": "DATABASE",
    "condition_params": {
      "threshold": 10,
      "time_window_minutes": 5
    },
    "notification_channels": ["SLACK"],
    "notification_config": {
      "SLACK": {
        "recipient": "https://hooks.slack.com/services/YOUR/WEBHOOK"
      }
    },
    "cooldown_minutes": 15,
    "is_active": true
  }'
```

### Caso 3: Detectar Novos Erros

```bash
curl -X POST "http://localhost:8000/api/alerts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Novo Tipo de Erro",
    "description": "Alerta quando um novo erro aparecer",
    "condition": "NEW_ERROR_TYPE",
    "notification_channels": ["DISCORD"],
    "notification_config": {
      "DISCORD": {
        "recipient": "https://discord.com/api/webhooks/YOUR/WEBHOOK"
      }
    },
    "cooldown_minutes": 60,
    "is_active": true
  }'
```

---

## 🎯 Dicas e Melhores Práticas

### Fingerprinting

✅ **Faça**:
- Revise grupos regularmente para garantir agrupamento correto
- Use notas para documentar soluções
- Atribua responsáveis para facilitar acompanhamento
- Resolva grupos inteiros quando corrigir a causa raiz

❌ **Evite**:
- Deletar grupos sem investigar
- Ignorar grupos com muitas ocorrências

### Alertas

✅ **Faça**:
- Comece com thresholds conservadores
- Use cooldown de 15-30 minutos
- Teste alertas antes de ativar em produção
- Configure múltiplos canais para redundância
- Monitore logs de notificação

❌ **Evite**:
- Thresholds muito baixos (causa fadiga de alertas)
- Cooldown muito curto (spam)
- Alertar para tudo (priorize o importante)

---

## 🔍 Troubleshooting

### Notificações não estão sendo enviadas

```bash
# 1. Verificar se a regra está ativa
curl "http://localhost:8000/api/alerts"

# 2. Verificar logs de notificação
curl "http://localhost:8000/api/notifications?success_only=false"

# 3. Ver detalhes de falhas
curl "http://localhost:8000/api/notifications" | jq '.notifications[] | select(.sent_successfully == false)'
```

### Erros não estão sendo agrupados

```bash
# Ver grupos existentes
curl "http://localhost:8000/api/groups"

# Ver detalhes de um grupo
curl "http://localhost:8000/api/groups/1"

# Ver erros de um grupo
curl "http://localhost:8000/api/errors?group_id=1"
```

### Verificar saúde do sistema

```bash
# Health check
curl "http://localhost:8000/health"

# Ver logs do backend
docker-compose logs -f backend

# Ver logs do frontend
docker-compose logs -f frontend
```

---

## 📚 Próximos Passos

1. **Explore a documentação completa**: [FINGERPRINTING_E_ALERTAS.md](FINGERPRINTING_E_ALERTAS.md)
2. **Configure alertas para seu ambiente**
3. **Integre com suas aplicações** usando os exemplos de integração
4. **Customize conforme necessário**

---

## 🆘 Precisa de Ajuda?

- 📖 Documentação completa: [FINGERPRINTING_E_ALERTAS.md](FINGERPRINTING_E_ALERTAS.md)
- 📖 README principal: [README.md](README.md)
- 🔧 API Docs: http://localhost:8000/docs

---

**Boa sorte com seu monitoramento de erros! 🚀**

