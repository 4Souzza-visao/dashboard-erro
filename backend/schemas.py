from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from models import ErrorType, Severity, ErrorStatus


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

