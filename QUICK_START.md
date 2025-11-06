# 🚀 Quick Start - Error Dashboard

Guia rápido para começar a usar o Error Dashboard em minutos!

## ⚡ Start em 3 Passos

### 1️⃣ Inicie o Docker Compose

```bash
docker-compose up -d
```

Aguarde aproximadamente 30 segundos para todos os serviços iniciarem.

### 2️⃣ Popule com Dados de Exemplo

```bash
# Instale o requests se não tiver
pip install requests

# Execute o gerador de erros
python scripts/generate_sample_errors.py
```

### 3️⃣ Acesse o Dashboard

Abra seu navegador em: **http://localhost:3000**

---

## 🎯 URLs Importantes

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Dashboard** | http://localhost:3000 | Interface web do dashboard |
| **API** | http://localhost:8000 | API REST |
| **Swagger Docs** | http://localhost:8000/docs | Documentação interativa |
| **ReDoc** | http://localhost:8000/redoc | Documentação alternativa |

---

## 📝 Teste Rápido da API

### Criar um erro via cURL:

```bash
curl -X POST "http://localhost:8000/api/errors" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Meu primeiro erro de teste",
    "error_type": "APPLICATION",
    "severity": "MEDIUM",
    "source": "backend"
  }'
```

### Listar erros:

```bash
curl "http://localhost:8000/api/errors?limit=10"
```

### Ver estatísticas:

```bash
curl "http://localhost:8000/api/stats/summary?days=7"
```

---

## 🔧 Comandos Úteis

### Ver logs em tempo real:

```bash
docker-compose logs -f
```

### Parar os serviços:

```bash
docker-compose down
```

### Reiniciar tudo (limpar dados):

```bash
docker-compose down -v
docker-compose up -d
python scripts/generate_sample_errors.py
```

### Acessar banco de dados:

```bash
docker-compose exec postgres psql -U admin -d error_dashboard
```

---

## 🐛 Solução de Problemas

### Porta já em uso?

Se as portas 3000 ou 8000 já estiverem em uso, edite o `docker-compose.yml`:

```yaml
# Mudar porta do frontend
ports:
  - "3001:80"  # Era 3000:80

# Mudar porta do backend
ports:
  - "8001:8000"  # Era 8000:8000
```

### Containers não iniciam?

```bash
# Ver logs de erro
docker-compose logs

# Recriar containers
docker-compose down
docker-compose up -d --build
```

### Banco de dados vazio?

```bash
# Dentro do container backend
docker-compose exec backend python init_db.py
```

---

## 📱 Integração Rápida

### Python:

```python
import requests

requests.post('http://localhost:8000/api/errors', json={
    "message": "Erro de exemplo",
    "error_type": "APPLICATION",
    "severity": "HIGH",
    "source": "minha_app"
})
```

### JavaScript/Node:

```javascript
fetch('http://localhost:8000/api/errors', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Erro de exemplo',
    error_type: 'FRONTEND',
    severity: 'MEDIUM',
    source: 'meu_frontend'
  })
});
```

---

## ✅ Próximos Passos

1. ✅ Explore o dashboard em http://localhost:3000
2. ✅ Teste a API em http://localhost:8000/docs
3. ✅ Leia a documentação completa em `README.md`
4. ✅ Veja exemplos de integração em `API_DOCUMENTATION.md`
5. ✅ Personalize para suas necessidades

---

**Pronto! Seu dashboard de erros está funcionando! 🎉**

Para documentação completa, veja: `README.md`

