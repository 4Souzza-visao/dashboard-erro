"""
Script para inicializar o banco de dados com dados de exemplo
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

# Criar tabelas
models.Base.metadata.create_all(bind=engine)


def generate_sample_errors(db: Session, count: int = 100):
    """Gera erros de exemplo para teste"""
    
    error_templates = [
        # HTTP Errors
        {
            "message": "404 Not Found - Resource not found",
            "error_type": models.ErrorType.HTTP,
            "severity": models.Severity.MEDIUM,
            "source": "backend",
            "endpoint": "/api/users/12345",
            "method": "GET",
            "status_code": 404,
        },
        {
            "message": "500 Internal Server Error - Unexpected error occurred",
            "error_type": models.ErrorType.HTTP,
            "severity": models.Severity.CRITICAL,
            "source": "backend",
            "endpoint": "/api/products",
            "method": "POST",
            "status_code": 500,
        },
        {
            "message": "403 Forbidden - Access denied to resource",
            "error_type": models.ErrorType.HTTP,
            "severity": models.Severity.HIGH,
            "source": "backend",
            "endpoint": "/api/admin/settings",
            "method": "PUT",
            "status_code": 403,
        },
        
        # Database Errors
        {
            "message": "Connection timeout to database",
            "error_type": models.ErrorType.DATABASE,
            "severity": models.Severity.CRITICAL,
            "source": "database",
            "stack_trace": "psycopg2.OperationalError: could not connect to server\nConnection timeout",
        },
        {
            "message": "Duplicate key violation: user_email_unique",
            "error_type": models.ErrorType.DATABASE,
            "severity": models.Severity.MEDIUM,
            "source": "database",
            "stack_trace": "sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint",
        },
        {
            "message": "Query execution timeout after 30 seconds",
            "error_type": models.ErrorType.DATABASE,
            "severity": models.Severity.HIGH,
            "source": "database",
        },
        
        # Auth Errors
        {
            "message": "Invalid authentication token",
            "error_type": models.ErrorType.AUTH,
            "severity": models.Severity.HIGH,
            "source": "backend",
            "endpoint": "/api/protected/resource",
            "method": "GET",
            "status_code": 401,
        },
        {
            "message": "Session expired - please login again",
            "error_type": models.ErrorType.AUTH,
            "severity": models.Severity.MEDIUM,
            "source": "backend",
            "status_code": 401,
        },
        {
            "message": "Invalid credentials provided",
            "error_type": models.ErrorType.AUTH,
            "severity": models.Severity.LOW,
            "source": "backend",
            "endpoint": "/api/login",
            "method": "POST",
            "status_code": 401,
        },
        
        # Validation Errors
        {
            "message": "Email format is invalid",
            "error_type": models.ErrorType.VALIDATION,
            "severity": models.Severity.LOW,
            "source": "backend",
            "endpoint": "/api/register",
            "method": "POST",
        },
        {
            "message": "Required field 'password' is missing",
            "error_type": models.ErrorType.VALIDATION,
            "severity": models.Severity.MEDIUM,
            "source": "backend",
        },
        {
            "message": "Value exceeds maximum length of 255 characters",
            "error_type": models.ErrorType.VALIDATION,
            "severity": models.Severity.LOW,
            "source": "backend",
        },
        
        # Performance Errors
        {
            "message": "Request timeout after 60 seconds",
            "error_type": models.ErrorType.PERFORMANCE,
            "severity": models.Severity.HIGH,
            "source": "backend",
            "endpoint": "/api/reports/generate",
            "method": "POST",
        },
        {
            "message": "Memory limit exceeded: heap out of memory",
            "error_type": models.ErrorType.PERFORMANCE,
            "severity": models.Severity.CRITICAL,
            "source": "backend",
            "stack_trace": "MemoryError: Cannot allocate memory\nHeap limit reached",
        },
        {
            "message": "Response time exceeded 5 seconds threshold",
            "error_type": models.ErrorType.PERFORMANCE,
            "severity": models.Severity.MEDIUM,
            "source": "backend",
        },
        
        # Integration Errors
        {
            "message": "External API call failed: Payment gateway timeout",
            "error_type": models.ErrorType.INTEGRATION,
            "severity": models.Severity.CRITICAL,
            "source": "external_service",
            "stack_trace": "requests.exceptions.Timeout: HTTPSConnectionPool timeout",
        },
        {
            "message": "Third-party service unavailable (503)",
            "error_type": models.ErrorType.INTEGRATION,
            "severity": models.Severity.HIGH,
            "source": "external_service",
        },
        {
            "message": "Invalid response format from external API",
            "error_type": models.ErrorType.INTEGRATION,
            "severity": models.Severity.MEDIUM,
            "source": "external_service",
        },
        
        # Application Errors
        {
            "message": "NullPointerException in user service",
            "error_type": models.ErrorType.APPLICATION,
            "severity": models.Severity.CRITICAL,
            "source": "backend",
            "stack_trace": "NullPointerException: Cannot invoke method on null object\nat UserService.processUser(UserService.java:45)",
        },
        {
            "message": "Unhandled exception in data processing pipeline",
            "error_type": models.ErrorType.APPLICATION,
            "severity": models.Severity.HIGH,
            "source": "backend",
        },
        {
            "message": "Failed to parse JSON configuration file",
            "error_type": models.ErrorType.APPLICATION,
            "severity": models.Severity.MEDIUM,
            "source": "backend",
        },
        
        # Frontend Errors
        {
            "message": "TypeError: Cannot read property 'map' of undefined",
            "error_type": models.ErrorType.FRONTEND,
            "severity": models.Severity.MEDIUM,
            "source": "frontend",
            "stack_trace": "TypeError: Cannot read property 'map' of undefined\nat Dashboard.render (Dashboard.jsx:23)",
        },
        {
            "message": "Network request failed: Failed to fetch",
            "error_type": models.ErrorType.FRONTEND,
            "severity": models.Severity.HIGH,
            "source": "frontend",
        },
        {
            "message": "React component rendering error",
            "error_type": models.ErrorType.FRONTEND,
            "severity": models.Severity.MEDIUM,
            "source": "frontend",
        },
    ]
    
    statuses = [models.ErrorStatus.OPEN, models.ErrorStatus.IN_PROGRESS, 
                models.ErrorStatus.RESOLVED, models.ErrorStatus.IGNORED]
    
    user_ids = ["user_001", "user_042", "user_123", "user_456", None]
    ip_addresses = ["192.168.1.100", "10.0.0.50", "172.16.0.25", "203.0.113.45", None]
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)",
        None
    ]
    
    print(f"Gerando {count} erros de exemplo...")
    
    for i in range(count):
        template = random.choice(error_templates)
        
        # Random timestamp within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
        
        error_data = {
            **template,
            "user_id": random.choice(user_ids),
            "session_id": f"sess_{random.randint(1000, 9999)}",
            "ip_address": random.choice(ip_addresses),
            "user_agent": random.choice(user_agents),
            "status": random.choice(statuses),
            "timestamp": timestamp,
            "occurrences": random.randint(1, 10),
            "metadata": {
                "server": f"server-{random.randint(1, 5)}",
                "environment": random.choice(["production", "staging", "development"])
            }
        }
        
        # Add resolved_at if status is RESOLVED
        if error_data["status"] == models.ErrorStatus.RESOLVED:
            error_data["resolved_at"] = timestamp + timedelta(hours=random.randint(1, 48))
        
        db_error = models.ErrorLog(**error_data)
        db.add(db_error)
    
    db.commit()
    print(f"✓ {count} erros criados com sucesso!")


def main():
    db = SessionLocal()
    try:
        print("Inicializando banco de dados...")
        
        # Limpar dados existentes (opcional)
        print("Limpando dados antigos...")
        db.query(models.ErrorLog).delete()
        db.commit()
        
        # Gerar dados de exemplo
        generate_sample_errors(db, count=100)
        
        # Estatísticas
        total = db.query(models.ErrorLog).count()
        critical = db.query(models.ErrorLog).filter(
            models.ErrorLog.severity == models.Severity.CRITICAL
        ).count()
        open_errors = db.query(models.ErrorLog).filter(
            models.ErrorLog.status == models.ErrorStatus.OPEN
        ).count()
        
        print("\n" + "="*50)
        print("BANCO DE DADOS INICIALIZADO COM SUCESSO!")
        print("="*50)
        print(f"Total de erros: {total}")
        print(f"Erros críticos: {critical}")
        print(f"Erros abertos: {open_errors}")
        print("="*50)
        
    finally:
        db.close()


if __name__ == "__main__":
    main()

