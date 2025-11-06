from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import models
import schemas
from database import engine, get_db
import uvicorn

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Error Dashboard API",
    description="API para gerenciamento e visualização de logs de erros",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """Endpoint raiz da API"""
    return {
        "message": "Error Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
def health_check():
    """Verifica o status da API"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


# ==================== ERROR LOGS ENDPOINTS ====================

@app.post("/api/errors", response_model=schemas.ErrorLogResponse, status_code=201)
def create_error_log(error: schemas.ErrorLogCreate, db: Session = Depends(get_db)):
    """
    Cria um novo log de erro
    
    - **message**: Mensagem do erro
    - **error_type**: Tipo do erro (HTTP, DATABASE, AUTH, etc.)
    - **severity**: Severidade (LOW, MEDIUM, HIGH, CRITICAL)
    - **source**: Origem do erro (frontend, backend, database, etc.)
    - **stack_trace**: Stack trace completo (opcional)
    - **user_id**: ID do usuário relacionado (opcional)
    - **endpoint**: Endpoint onde ocorreu o erro (opcional)
    - **method**: Método HTTP (opcional)
    - **status_code**: Código de status HTTP (opcional)
    - **metadata**: Dados adicionais em JSON (opcional)
    """
    db_error = models.ErrorLog(**error.model_dump())
    db.add(db_error)
    db.commit()
    db.refresh(db_error)
    return db_error


@app.get("/api/errors", response_model=schemas.ErrorLogListResponse)
def get_error_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    error_type: Optional[str] = None,
    severity: Optional[str] = None,
    source: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista logs de erros com filtros opcionais
    
    Filtros disponíveis:
    - **error_type**: HTTP, DATABASE, AUTH, VALIDATION, PERFORMANCE, INTEGRATION, APPLICATION, FRONTEND
    - **severity**: LOW, MEDIUM, HIGH, CRITICAL
    - **source**: frontend, backend, database, api, external_service
    - **status**: OPEN, IN_PROGRESS, RESOLVED, IGNORED
    - **start_date**: Data inicial
    - **end_date**: Data final
    - **search**: Busca por texto na mensagem ou stack trace
    """
    query = db.query(models.ErrorLog)
    
    # Apply filters
    if error_type:
        query = query.filter(models.ErrorLog.error_type == error_type)
    if severity:
        query = query.filter(models.ErrorLog.severity == severity)
    if source:
        query = query.filter(models.ErrorLog.source == source)
    if status:
        query = query.filter(models.ErrorLog.status == status)
    if start_date:
        query = query.filter(models.ErrorLog.timestamp >= start_date)
    if end_date:
        query = query.filter(models.ErrorLog.timestamp <= end_date)
    if search:
        query = query.filter(
            (models.ErrorLog.message.ilike(f"%{search}%")) |
            (models.ErrorLog.stack_trace.ilike(f"%{search}%"))
        )
    
    total = query.count()
    errors = query.order_by(models.ErrorLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "errors": errors
    }


@app.get("/api/errors/{error_id}", response_model=schemas.ErrorLogResponse)
def get_error_log(error_id: int, db: Session = Depends(get_db)):
    """Obtém detalhes de um erro específico"""
    error = db.query(models.ErrorLog).filter(models.ErrorLog.id == error_id).first()
    if not error:
        raise HTTPException(status_code=404, detail="Error log not found")
    return error


@app.patch("/api/errors/{error_id}", response_model=schemas.ErrorLogResponse)
def update_error_log(error_id: int, update: schemas.ErrorLogUpdate, db: Session = Depends(get_db)):
    """
    Atualiza um log de erro (ex: mudar status para RESOLVED)
    
    Campos atualizáveis:
    - **status**: OPEN, IN_PROGRESS, RESOLVED, IGNORED
    - **assigned_to**: Responsável pela correção
    - **notes**: Notas adicionais
    """
    error = db.query(models.ErrorLog).filter(models.ErrorLog.id == error_id).first()
    if not error:
        raise HTTPException(status_code=404, detail="Error log not found")
    
    update_data = update.model_dump(exclude_unset=True)
    if "status" in update_data and update_data["status"] == "RESOLVED":
        update_data["resolved_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(error, key, value)
    
    db.commit()
    db.refresh(error)
    return error


@app.delete("/api/errors/{error_id}", status_code=204)
def delete_error_log(error_id: int, db: Session = Depends(get_db)):
    """Deleta um log de erro"""
    error = db.query(models.ErrorLog).filter(models.ErrorLog.id == error_id).first()
    if not error:
        raise HTTPException(status_code=404, detail="Error log not found")
    
    db.delete(error)
    db.commit()
    return None


# ==================== STATISTICS ENDPOINTS ====================

@app.get("/api/stats/summary", response_model=schemas.StatsSummary)
def get_stats_summary(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Obtém resumo estatístico dos erros
    
    - **total_errors**: Total de erros no período
    - **by_severity**: Distribuição por severidade
    - **by_type**: Distribuição por tipo
    - **by_source**: Distribuição por origem
    - **by_status**: Distribuição por status
    - **error_rate**: Taxa de erros por dia
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total errors
    total_errors = db.query(models.ErrorLog).filter(
        models.ErrorLog.timestamp >= start_date
    ).count()
    
    # By severity
    by_severity = {}
    for severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        count = db.query(models.ErrorLog).filter(
            models.ErrorLog.timestamp >= start_date,
            models.ErrorLog.severity == severity
        ).count()
        by_severity[severity] = count
    
    # By type
    by_type = {}
    for error_type in ["HTTP", "DATABASE", "AUTH", "VALIDATION", "PERFORMANCE", "INTEGRATION", "APPLICATION", "FRONTEND"]:
        count = db.query(models.ErrorLog).filter(
            models.ErrorLog.timestamp >= start_date,
            models.ErrorLog.error_type == error_type
        ).count()
        by_type[error_type] = count
    
    # By source
    by_source = {}
    for source in ["frontend", "backend", "database", "api", "external_service"]:
        count = db.query(models.ErrorLog).filter(
            models.ErrorLog.timestamp >= start_date,
            models.ErrorLog.source == source
        ).count()
        by_source[source] = count
    
    # By status
    by_status = {}
    for status in ["OPEN", "IN_PROGRESS", "RESOLVED", "IGNORED"]:
        count = db.query(models.ErrorLog).filter(
            models.ErrorLog.timestamp >= start_date,
            models.ErrorLog.status == status
        ).count()
        by_status[status] = count
    
    # Error rate per day
    error_rate = round(total_errors / days, 2) if days > 0 else 0
    
    return {
        "total_errors": total_errors,
        "by_severity": by_severity,
        "by_type": by_type,
        "by_source": by_source,
        "by_status": by_status,
        "error_rate": error_rate,
        "period_days": days
    }


@app.get("/api/stats/timeline")
def get_timeline_stats(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtém dados de timeline de erros por dia"""
    from sqlalchemy import func, cast, Date
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        cast(models.ErrorLog.timestamp, Date).label('date'),
        func.count(models.ErrorLog.id).label('count')
    ).filter(
        models.ErrorLog.timestamp >= start_date
    ).group_by(
        cast(models.ErrorLog.timestamp, Date)
    ).order_by('date').all()
    
    timeline_data = [
        {"date": str(result.date), "count": result.count}
        for result in results
    ]
    
    return {"timeline": timeline_data}


@app.get("/api/stats/top-errors")
def get_top_errors(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Obtém os erros mais frequentes"""
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        models.ErrorLog.message,
        models.ErrorLog.error_type,
        func.count(models.ErrorLog.id).label('count')
    ).filter(
        models.ErrorLog.timestamp >= start_date
    ).group_by(
        models.ErrorLog.message,
        models.ErrorLog.error_type
    ).order_by(
        func.count(models.ErrorLog.id).desc()
    ).limit(limit).all()
    
    top_errors = [
        {
            "message": result.message,
            "error_type": result.error_type,
            "count": result.count
        }
        for result in results
    ]
    
    return {"top_errors": top_errors}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

