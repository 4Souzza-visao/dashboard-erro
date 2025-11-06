# 🚀 Deploy em Produção - Error Dashboard

Guia para colocar o Error Dashboard em produção de forma segura e escalável.

---

## ⚠️ Checklist Pré-Produção

Antes de fazer deploy em produção, certifique-se de implementar:

- [ ] Autenticação e autorização
- [ ] HTTPS/TLS configurado
- [ ] CORS com origens específicas
- [ ] Rate limiting
- [ ] Variáveis de ambiente seguras
- [ ] Backup automatizado do banco
- [ ] Monitoramento e alertas
- [ ] Log rotation
- [ ] Health checks configurados
- [ ] Documentação atualizada

---

## 🔒 Segurança

### 1. Autenticação JWT

Adicione autenticação JWT ao backend:

```python
# backend/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )
```

Proteja os endpoints:

```python
from fastapi import Depends

@app.get("/api/errors", dependencies=[Depends(verify_token)])
def get_errors(...):
    # ...
```

### 2. CORS Configurado

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dashboard.seudominio.com",
        "https://app.seudominio.com"
    ],  # Especifique domínios exatos
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
```

### 3. Rate Limiting

Instale slowapi:

```bash
pip install slowapi
```

Configure:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/errors")
@limiter.limit("100/minute")
async def create_error(request: Request, ...):
    # ...
```

### 4. Variáveis de Ambiente

Crie arquivo `.env` (NUNCA commite isso!):

```env
# Database
DATABASE_URL=postgresql://prod_user:SENHA_FORTE@db-host:5432/prod_db

# JWT
JWT_SECRET_KEY=chave-super-secreta-aleatoria-128-chars

# API
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=production

# CORS
CORS_ORIGINS=https://dashboard.seudominio.com,https://app.seudominio.com

# Monitoring
SENTRY_DSN=https://...
LOG_LEVEL=INFO
```

---

## 🐳 Docker Production

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - error_dashboard_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    # Não exponha a porta 5432 externamente em produção
    # Acesse apenas via rede interna

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    restart: always
    env_file:
      - .env
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - error_dashboard_network
    # Não exponha porta externa, use reverse proxy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        REACT_APP_API_URL: ${REACT_APP_API_URL}
    restart: always
    networks:
      - error_dashboard_network
    # Não exponha porta externa, use reverse proxy

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - error_dashboard_network

networks:
  error_dashboard_network:
    driver: bridge

volumes:
  postgres_data:
```

### Backend Dockerfile.prod

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

Adicione ao requirements.txt:
```
gunicorn==21.2.0
```

### Frontend Dockerfile.prod

```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
ARG REACT_APP_API_URL
ENV REACT_APP_API_URL=$REACT_APP_API_URL

RUN npm run build

FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## 🌐 Nginx Reverse Proxy

### nginx/nginx.conf

```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:80;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name dashboard.seudominio.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name dashboard.seudominio.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Docs
    location ~ ^/(docs|redoc|openapi.json) {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Logs
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
}
```

---

## 🔐 SSL/TLS com Let's Encrypt

### Usando Certbot

```bash
# Instalar certbot
sudo apt-get update
sudo apt-get install certbot

# Obter certificado
sudo certbot certonly --standalone -d dashboard.seudominio.com

# Copiar certificados
sudo cp /etc/letsencrypt/live/dashboard.seudominio.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/dashboard.seudominio.com/privkey.pem nginx/ssl/

# Renovação automática (adicionar ao crontab)
0 0 * * * certbot renew --quiet && docker-compose -f docker-compose.prod.yml restart nginx
```

---

## 💾 Backup Automático

### Script de Backup

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
POSTGRES_CONTAINER="error_dashboard_db"

# Criar backup
docker exec $POSTGRES_CONTAINER pg_dump -U admin error_dashboard > $BACKUP_DIR/backup_$DATE.sql

# Comprimir
gzip $BACKUP_DIR/backup_$DATE.sql

# Manter apenas últimos 30 dias
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

Adicionar ao crontab:
```bash
0 2 * * * /path/to/scripts/backup.sh
```

### Restaurar Backup

```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: ./restore.sh backup_file.sql.gz"
    exit 1
fi

gunzip -c $BACKUP_FILE | docker exec -i error_dashboard_db psql -U admin -d error_dashboard
```

---

## 📊 Monitoramento

### Integração com Sentry

```python
# backend/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if os.getenv("ENVIRONMENT") == "production":
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=1.0,
        environment="production"
    )
```

### Health Check Endpoint

```python
@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        # Verificar DB
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow(),
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )
```

### Monitoring com Prometheus

```python
# requirements.txt
prometheus-fastapi-instrumentator==6.1.0

# main.py
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 🚀 Deploy

### Deploy Inicial

```bash
# 1. Clonar repositório no servidor
git clone <repo-url>
cd dashboard-de-erro

# 2. Configurar variáveis de ambiente
cp .env.example .env
nano .env  # Editar com valores de produção

# 3. Build e start
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. Verificar logs
docker-compose -f docker-compose.prod.yml logs -f

# 5. Inicializar banco (primeira vez)
docker-compose -f docker-compose.prod.yml exec backend python init_db.py
```

### Updates/Patches

```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild
docker-compose -f docker-compose.prod.yml build

# 3. Rolling update
docker-compose -f docker-compose.prod.yml up -d --no-deps --build backend
docker-compose -f docker-compose.prod.yml up -d --no-deps --build frontend
```

### Rollback

```bash
# 1. Checkout versão anterior
git checkout <commit-hash>

# 2. Rebuild e restart
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## 📈 Escalabilidade

### Database Connection Pooling

```python
# database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # Conexões permanentes
    max_overflow=10,       # Conexões extras em pico
    pool_timeout=30,       # Timeout para obter conexão
    pool_recycle=3600,     # Reciclar conexões a cada hora
)
```

### Horizontal Scaling (múltiplas instâncias)

```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 1G
```

### Caching com Redis

```yaml
services:
  redis:
    image: redis:alpine
    restart: always
    networks:
      - error_dashboard_network
```

```python
# requirements.txt
redis==5.0.1

# cache.py
import redis
from functools import wraps

redis_client = redis.Redis(host='redis', port=6379, db=0)

def cache(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

## 🔧 Troubleshooting Produção

### Logs

```bash
# Application logs
docker-compose -f docker-compose.prod.yml logs backend --tail=100 -f

# Nginx logs
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/error.log

# Database logs
docker-compose -f docker-compose.prod.yml logs postgres --tail=100
```

### Performance

```bash
# Ver uso de recursos
docker stats

# Conectar ao banco e ver queries lentas
docker exec -it error_dashboard_db psql -U admin -d error_dashboard

# Ver queries ativas
SELECT pid, now() - query_start as duration, query 
FROM pg_stat_activity 
WHERE state = 'active' 
ORDER BY duration DESC;
```

---

## ✅ Checklist Final

- [ ] SSL/TLS configurado e funcionando
- [ ] Backup automático rodando
- [ ] Monitoramento ativo (Sentry, logs, etc.)
- [ ] Rate limiting configurado
- [ ] CORS restrito
- [ ] Autenticação implementada
- [ ] Health checks funcionando
- [ ] Documentação atualizada
- [ ] Testes em staging
- [ ] Plano de rollback testado
- [ ] Alertas configurados
- [ ] Runbook de incidentes pronto

---

## 📞 Suporte Produção

Em caso de incidentes:

1. Verificar health check: `https://dashboard.seudominio.com/health`
2. Verificar logs: `docker-compose logs -f`
3. Verificar métricas: Prometheus/Grafana
4. Rollback se necessário
5. Investigar root cause
6. Documentar post-mortem

---

**Boa sorte com seu deploy! 🚀**

