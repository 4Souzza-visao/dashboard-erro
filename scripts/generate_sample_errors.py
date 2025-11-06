"""
Script para gerar erros de exemplo via API
Execute este script para popular o dashboard com dados de teste
"""
import requests
import random
from datetime import datetime, timedelta

API_URL = "http://localhost:8000"


def generate_errors(count=50):
    """Gera erros de exemplo através da API"""
    
    error_samples = [
        # HTTP Errors
        {
            "message": "404 Not Found - User profile not found",
            "error_type": "HTTP",
            "severity": "MEDIUM",
            "source": "backend",
            "endpoint": "/api/users/99999",
            "method": "GET",
            "status_code": 404,
            "user_id": "user_123",
            "ip_address": "192.168.1.100"
        },
        {
            "message": "500 Internal Server Error - Database connection failed",
            "error_type": "HTTP",
            "severity": "CRITICAL",
            "source": "backend",
            "endpoint": "/api/orders",
            "method": "POST",
            "status_code": 500,
            "stack_trace": "Traceback (most recent call last):\n  File 'app.py', line 45\n    raise DatabaseError()",
            "metadata": {"request_id": "req_12345"}
        },
        {
            "message": "401 Unauthorized - Invalid API key",
            "error_type": "AUTH",
            "severity": "HIGH",
            "source": "backend",
            "endpoint": "/api/admin/users",
            "method": "GET",
            "status_code": 401,
        },
        
        # Database Errors
        {
            "message": "Connection pool exhausted",
            "error_type": "DATABASE",
            "severity": "CRITICAL",
            "source": "database",
            "stack_trace": "psycopg2.pool.PoolError: connection pool exhausted",
        },
        {
            "message": "Foreign key constraint violation",
            "error_type": "DATABASE",
            "severity": "MEDIUM",
            "source": "database",
        },
        
        # Validation Errors
        {
            "message": "Invalid email format",
            "error_type": "VALIDATION",
            "severity": "LOW",
            "source": "backend",
            "endpoint": "/api/users/register",
            "method": "POST",
        },
        {
            "message": "Password must be at least 8 characters",
            "error_type": "VALIDATION",
            "severity": "LOW",
            "source": "backend",
        },
        
        # Performance Errors
        {
            "message": "Query execution time exceeded 10 seconds",
            "error_type": "PERFORMANCE",
            "severity": "HIGH",
            "source": "database",
            "metadata": {"query_time": 12.5, "query": "SELECT * FROM large_table"}
        },
        {
            "message": "Memory usage exceeded 90% threshold",
            "error_type": "PERFORMANCE",
            "severity": "CRITICAL",
            "source": "backend",
            "metadata": {"memory_usage": "94%", "server": "prod-01"}
        },
        
        # Integration Errors
        {
            "message": "Payment gateway API timeout",
            "error_type": "INTEGRATION",
            "severity": "CRITICAL",
            "source": "external_service",
            "stack_trace": "requests.exceptions.Timeout: Request timeout after 30s",
            "metadata": {"service": "stripe", "timeout": 30}
        },
        {
            "message": "Email service unavailable",
            "error_type": "INTEGRATION",
            "severity": "HIGH",
            "source": "external_service",
        },
        
        # Frontend Errors
        {
            "message": "Cannot read property 'id' of undefined",
            "error_type": "FRONTEND",
            "severity": "MEDIUM",
            "source": "frontend",
            "stack_trace": "TypeError: Cannot read property 'id' of undefined\nat UserProfile.js:45",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        },
        {
            "message": "Failed to load chunk",
            "error_type": "FRONTEND",
            "severity": "MEDIUM",
            "source": "frontend",
        },
        
        # Application Errors
        {
            "message": "Unhandled exception in background job",
            "error_type": "APPLICATION",
            "severity": "HIGH",
            "source": "backend",
            "stack_trace": "Exception: Unexpected error in job processor\nat process_job()",
        },
    ]
    
    print(f"Gerando {count} erros via API...")
    success_count = 0
    
    for i in range(count):
        error_data = random.choice(error_samples).copy()
        
        # Adicionar variação aos dados
        if random.random() > 0.5:
            error_data["user_id"] = f"user_{random.randint(100, 999)}"
        if random.random() > 0.5:
            error_data["ip_address"] = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        
        try:
            response = requests.post(f"{API_URL}/api/errors", json=error_data, timeout=5)
            if response.status_code == 201:
                success_count += 1
                print(f"✓ Erro {i+1}/{count} criado: {error_data['message'][:50]}...")
            else:
                print(f"✗ Falha ao criar erro {i+1}: {response.status_code}")
        except Exception as e:
            print(f"✗ Erro na requisição {i+1}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Concluído! {success_count}/{count} erros criados com sucesso")
    print(f"{'='*60}")
    print(f"\nAcesse o dashboard em: http://localhost:3000")
    print(f"Documentação da API: {API_URL}/docs")


if __name__ == "__main__":
    print("="*60)
    print("GERADOR DE ERROS DE EXEMPLO")
    print("="*60)
    print(f"API URL: {API_URL}\n")
    
    try:
        # Verificar se a API está acessível
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ API está online e acessível\n")
            generate_errors(count=50)
        else:
            print("✗ API retornou status inesperado")
    except requests.exceptions.ConnectionError:
        print("✗ Não foi possível conectar à API")
        print("Certifique-se de que o Docker Compose está rodando:")
        print("  docker-compose up -d")
    except Exception as e:
        print(f"✗ Erro: {e}")

