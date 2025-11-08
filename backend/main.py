from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
import models
import schemas
from database import engine, get_db
from alert_service import AlertService
import uvicorn
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Error Dashboard API",
    description="API para gerenciamento e visualização de logs de erros com fingerprinting e alertas",
    version="2.0.0",
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
def create_error_log(
    error: schemas.ErrorLogCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cria um novo log de erro com fingerprinting automático e verificação de alertas
    
    - **message**: Mensagem do erro
    - **error_type**: Tipo do erro (HTTP, DATABASE, AUTH, etc.)
    - **severity**: Severidade (LOW, MEDIUM, HIGH, CRITICAL)
    - **source**: Origem do erro (frontend, backend, database, etc.)
    - **stack_trace**: Stack trace completo (opcional)
    - **user_id**: ID do usuário relacionado (opcional)
    - **endpoint**: Endpoint onde ocorreu o erro (opcional)
    - **method**: Método HTTP (opcional)
    - **status_code**: Código de status HTTP (opcional)
    - **error_metadata**: Dados adicionais em JSON (opcional)
    """
    # Gerar fingerprint para agrupar erros similares
    fingerprint = models.generate_fingerprint(
        error_type=error.error_type.value,
        message=error.message,
        endpoint=error.endpoint,
        stack_trace=error.stack_trace
    )
    
    # Verificar se já existe um grupo com este fingerprint
    error_group = db.query(models.ErrorGroup).filter(
        models.ErrorGroup.fingerprint == fingerprint
    ).first()
    
    if error_group:
        # Atualizar grupo existente
        error_group.total_occurrences += 1
        error_group.last_seen = datetime.utcnow()
        # Atualizar severidade se o novo erro for mais severo
        severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        if severity_order[error.severity.value] > severity_order[error_group.severity.value]:
            error_group.severity = error.severity
    else:
        # Criar novo grupo
        error_group = models.ErrorGroup(
            fingerprint=fingerprint,
            message_pattern=error.message,
            error_type=error.error_type,
            severity=error.severity,
            source=error.source,
            total_occurrences=1
        )
        db.add(error_group)
        db.flush()  # Para obter o ID do grupo
    
    # Criar o erro e associar ao grupo
    db_error = models.ErrorLog(**error.model_dump())
    db_error.group_id = error_group.id
    db.add(db_error)
    db.commit()
    db.refresh(db_error)
    
    # Verificar alertas em background
    background_tasks.add_task(AlertService.check_and_trigger_alerts, db, db_error)
    
    logger.info(f"Erro criado: ID={db_error.id}, Grupo={error_group.id}, Fingerprint={fingerprint[:16]}...")
    
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


# ==================== ERROR GROUPS ENDPOINTS ====================

@app.get("/api/groups", response_model=schemas.ErrorGroupListResponse)
def get_error_groups(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    error_type: Optional[str] = None,
    severity: Optional[str] = None,
    source: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista grupos de erros com filtros opcionais
    
    Grupos são criados automaticamente usando fingerprinting para agrupar erros similares
    """
    query = db.query(models.ErrorGroup)
    
    # Apply filters
    if error_type:
        query = query.filter(models.ErrorGroup.error_type == error_type)
    if severity:
        query = query.filter(models.ErrorGroup.severity == severity)
    if source:
        query = query.filter(models.ErrorGroup.source == source)
    if status:
        query = query.filter(models.ErrorGroup.status == status)
    
    total = query.count()
    groups = query.order_by(models.ErrorGroup.last_seen.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "groups": groups
    }


@app.get("/api/groups/{group_id}", response_model=schemas.ErrorGroupDetailResponse)
def get_error_group(group_id: int, db: Session = Depends(get_db)):
    """Obtém detalhes de um grupo de erros incluindo erros recentes"""
    group = db.query(models.ErrorGroup).filter(models.ErrorGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Error group not found")
    
    # Buscar erros recentes deste grupo (últimos 10)
    recent_errors = db.query(models.ErrorLog).filter(
        models.ErrorLog.group_id == group_id
    ).order_by(models.ErrorLog.timestamp.desc()).limit(10).all()
    
    # Converter para dict e adicionar erros recentes
    group_dict = {
        "id": group.id,
        "fingerprint": group.fingerprint,
        "message_pattern": group.message_pattern,
        "error_type": group.error_type,
        "severity": group.severity,
        "source": group.source,
        "total_occurrences": group.total_occurrences,
        "first_seen": group.first_seen,
        "last_seen": group.last_seen,
        "status": group.status,
        "assigned_to": group.assigned_to,
        "notes": group.notes,
        "recent_errors": recent_errors
    }
    
    return group_dict


@app.patch("/api/groups/{group_id}", response_model=schemas.ErrorGroupResponse)
def update_error_group(
    group_id: int, 
    update: schemas.ErrorGroupUpdate, 
    db: Session = Depends(get_db)
):
    """
    Atualiza um grupo de erros (status, atribuição, notas)
    
    Ao atualizar o status de um grupo, todos os erros do grupo também são atualizados
    """
    group = db.query(models.ErrorGroup).filter(models.ErrorGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Error group not found")
    
    update_data = update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(group, key, value)
    
    # Se o status mudou, atualizar todos os erros do grupo
    if "status" in update_data:
        db.query(models.ErrorLog).filter(
            models.ErrorLog.group_id == group_id
        ).update({"status": update_data["status"]})
    
    db.commit()
    db.refresh(group)
    return group


@app.delete("/api/groups/{group_id}", status_code=204)
def delete_error_group(group_id: int, db: Session = Depends(get_db)):
    """
    Deleta um grupo de erros e todos os erros associados
    """
    group = db.query(models.ErrorGroup).filter(models.ErrorGroup.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Error group not found")
    
    # Deletar todos os erros do grupo
    db.query(models.ErrorLog).filter(models.ErrorLog.group_id == group_id).delete()
    
    # Deletar o grupo
    db.delete(group)
    db.commit()
    return None


# ==================== ALERT RULES ENDPOINTS ====================

@app.get("/api/alerts", response_model=schemas.AlertRuleListResponse)
def get_alert_rules(db: Session = Depends(get_db)):
    """Lista todas as regras de alerta"""
    rules = db.query(models.AlertRule).order_by(models.AlertRule.created_at.desc()).all()
    return {
        "total": len(rules),
        "rules": rules
    }


@app.get("/api/alerts/{rule_id}", response_model=schemas.AlertRuleResponse)
def get_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    """Obtém detalhes de uma regra de alerta"""
    rule = db.query(models.AlertRule).filter(models.AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    return rule


@app.post("/api/alerts", response_model=schemas.AlertRuleResponse, status_code=201)
def create_alert_rule(rule: schemas.AlertRuleCreate, db: Session = Depends(get_db)):
    """
    Cria uma nova regra de alerta
    
    Exemplo de configuração para ERROR_COUNT:
    ```json
    {
      "name": "High Error Rate",
      "condition": "ERROR_COUNT",
      "condition_params": {
        "threshold": 10,
        "time_window_minutes": 5
      },
      "notification_channels": ["SLACK", "EMAIL"],
      "notification_config": {
        "SLACK": {
          "recipient": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
        },
        "EMAIL": {
          "recipient": "admin@example.com",
          "smtp_host": "smtp.gmail.com",
          "smtp_port": 587,
          "smtp_user": "your-email@gmail.com",
          "smtp_password": "your-password"
        }
      }
    }
    ```
    """
    db_rule = models.AlertRule(**rule.model_dump())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    logger.info(f"Regra de alerta criada: {db_rule.name} (ID={db_rule.id})")
    return db_rule


@app.patch("/api/alerts/{rule_id}", response_model=schemas.AlertRuleResponse)
def update_alert_rule(
    rule_id: int, 
    update: schemas.AlertRuleUpdate, 
    db: Session = Depends(get_db)
):
    """Atualiza uma regra de alerta"""
    rule = db.query(models.AlertRule).filter(models.AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(rule, key, value)
    
    db.commit()
    db.refresh(rule)
    logger.info(f"Regra de alerta atualizada: {rule.name} (ID={rule.id})")
    return rule


@app.delete("/api/alerts/{rule_id}", status_code=204)
def delete_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    """Deleta uma regra de alerta"""
    rule = db.query(models.AlertRule).filter(models.AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    db.delete(rule)
    db.commit()
    logger.info(f"Regra de alerta deletada: ID={rule_id}")
    return None


@app.post("/api/alerts/{rule_id}/toggle", response_model=schemas.AlertRuleResponse)
def toggle_alert_rule(rule_id: int, db: Session = Depends(get_db)):
    """Ativa/desativa uma regra de alerta"""
    rule = db.query(models.AlertRule).filter(models.AlertRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    rule.is_active = not rule.is_active
    db.commit()
    db.refresh(rule)
    
    status = "ativada" if rule.is_active else "desativada"
    logger.info(f"Regra de alerta {status}: {rule.name} (ID={rule.id})")
    return rule


# ==================== NOTIFICATION LOGS ENDPOINTS ====================

@app.get("/api/notifications", response_model=schemas.NotificationLogListResponse)
def get_notification_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    alert_rule_id: Optional[int] = None,
    channel: Optional[str] = None,
    success_only: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Lista logs de notificações enviadas"""
    query = db.query(models.NotificationLog)
    
    if alert_rule_id:
        query = query.filter(models.NotificationLog.alert_rule_id == alert_rule_id)
    if channel:
        query = query.filter(models.NotificationLog.channel == channel)
    if success_only is not None:
        query = query.filter(models.NotificationLog.sent_successfully == success_only)
    
    total = query.count()
    notifications = query.order_by(models.NotificationLog.sent_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "notifications": notifications
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

