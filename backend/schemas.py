from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from models import ErrorType, Severity, ErrorStatus, NotificationChannel, AlertCondition


# ==================== ERROR LOG SCHEMAS ====================

class ErrorLogBase(BaseModel):
    message: str = Field(..., description="Mensagem do erro")
    error_type: ErrorType = Field(..., description="Tipo do erro")
    severity: Severity = Field(..., description="Severidade do erro")
    source: str = Field(..., description="Origem do erro (frontend, backend, etc.)")
    stack_trace: Optional[str] = Field(None, description="Stack trace completo")
    endpoint: Optional[str] = Field(None, description="Endpoint onde ocorreu o erro")
    method: Optional[str] = Field(None, description="Método HTTP")
    status_code: Optional[int] = Field(None, description="Código de status HTTP")
    user_id: Optional[str] = Field(None, description="ID do usuário")
    session_id: Optional[str] = Field(None, description="ID da sessão")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    user_agent: Optional[str] = Field(None, description="User agent")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")


class ErrorLogCreate(ErrorLogBase):
    """Schema para criação de log de erro"""
    pass


class ErrorLogUpdate(BaseModel):
    """Schema para atualização de log de erro"""
    status: Optional[ErrorStatus] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class ErrorLogResponse(ErrorLogBase):
    """Schema de resposta de log de erro"""
    id: int
    group_id: Optional[int]
    status: ErrorStatus
    assigned_to: Optional[str]
    notes: Optional[str]
    timestamp: datetime
    resolved_at: Optional[datetime]
    occurrences: int

    class Config:
        from_attributes = True


class ErrorLogListResponse(BaseModel):
    """Schema de resposta para lista de logs"""
    total: int
    skip: int
    limit: int
    errors: List[ErrorLogResponse]


# ==================== ERROR GROUP SCHEMAS ====================

class ErrorGroupResponse(BaseModel):
    """Schema de resposta de grupo de erros"""
    id: int
    fingerprint: str
    message_pattern: str
    error_type: ErrorType
    severity: Severity
    source: str
    total_occurrences: int
    first_seen: datetime
    last_seen: datetime
    status: ErrorStatus
    assigned_to: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


class ErrorGroupUpdate(BaseModel):
    """Schema para atualização de grupo de erros"""
    status: Optional[ErrorStatus] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None


class ErrorGroupListResponse(BaseModel):
    """Schema de resposta para lista de grupos"""
    total: int
    skip: int
    limit: int
    groups: List[ErrorGroupResponse]


class ErrorGroupDetailResponse(ErrorGroupResponse):
    """Schema de resposta detalhada de grupo (com erros)"""
    recent_errors: List[ErrorLogResponse] = Field(default_factory=list)


# ==================== ALERT RULE SCHEMAS ====================

class AlertRuleBase(BaseModel):
    name: str = Field(..., description="Nome da regra de alerta")
    description: Optional[str] = Field(None, description="Descrição da regra")
    is_active: bool = Field(True, description="Se a regra está ativa")
    condition: AlertCondition = Field(..., description="Condição do alerta")
    error_type: Optional[ErrorType] = Field(None, description="Filtro por tipo de erro")
    severity: Optional[Severity] = Field(None, description="Filtro por severidade")
    source: Optional[str] = Field(None, description="Filtro por origem")
    condition_params: Optional[Dict[str, Any]] = Field(None, description="Parâmetros da condição")
    notification_channels: List[str] = Field(..., description="Canais de notificação")
    notification_config: Optional[Dict[str, Any]] = Field(None, description="Configurações de notificação")
    cooldown_minutes: int = Field(15, description="Tempo de cooldown em minutos")


class AlertRuleCreate(AlertRuleBase):
    """Schema para criação de regra de alerta"""
    pass


class AlertRuleUpdate(BaseModel):
    """Schema para atualização de regra de alerta"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    condition: Optional[AlertCondition] = None
    error_type: Optional[ErrorType] = None
    severity: Optional[Severity] = None
    source: Optional[str] = None
    condition_params: Optional[Dict[str, Any]] = None
    notification_channels: Optional[List[str]] = None
    notification_config: Optional[Dict[str, Any]] = None
    cooldown_minutes: Optional[int] = None


class AlertRuleResponse(AlertRuleBase):
    """Schema de resposta de regra de alerta"""
    id: int
    last_triggered: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertRuleListResponse(BaseModel):
    """Schema de resposta para lista de regras"""
    total: int
    rules: List[AlertRuleResponse]


# ==================== NOTIFICATION LOG SCHEMAS ====================

class NotificationLogResponse(BaseModel):
    """Schema de resposta de log de notificação"""
    id: int
    alert_rule_id: int
    channel: NotificationChannel
    recipient: str
    subject: Optional[str]
    message: str
    sent_successfully: bool
    error_message: Optional[str]
    metadata: Optional[Dict[str, Any]]
    sent_at: datetime

    class Config:
        from_attributes = True


class NotificationLogListResponse(BaseModel):
    """Schema de resposta para lista de notificações"""
    total: int
    skip: int
    limit: int
    notifications: List[NotificationLogResponse]


# ==================== STATISTICS SCHEMAS ====================

class StatsSummary(BaseModel):
    """Schema para resumo estatístico"""
    total_errors: int
    by_severity: Dict[str, int]
    by_type: Dict[str, int]
    by_source: Dict[str, int]
    by_status: Dict[str, int]
    error_rate: float
    period_days: int

