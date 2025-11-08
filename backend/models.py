from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum as SQLEnum, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum
import hashlib


class ErrorType(str, enum.Enum):
    HTTP = "HTTP"
    DATABASE = "DATABASE"
    AUTH = "AUTH"
    VALIDATION = "VALIDATION"
    PERFORMANCE = "PERFORMANCE"
    INTEGRATION = "INTEGRATION"
    APPLICATION = "APPLICATION"
    FRONTEND = "FRONTEND"


class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    IGNORED = "IGNORED"


class NotificationChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    SLACK = "SLACK"
    WEBHOOK = "WEBHOOK"
    SMS = "SMS"
    DISCORD = "DISCORD"


class AlertCondition(str, enum.Enum):
    ERROR_COUNT = "ERROR_COUNT"  # X erros em Y minutos
    ERROR_RATE = "ERROR_RATE"  # Taxa de erro excede X%
    CRITICAL_ERROR = "CRITICAL_ERROR"  # Qualquer erro crítico
    NEW_ERROR_TYPE = "NEW_ERROR_TYPE"  # Novo tipo de erro detectado
    ERROR_SPIKE = "ERROR_SPIKE"  # Aumento súbito de erros


class ErrorGroup(Base):
    """Agrupa erros similares usando fingerprinting"""
    __tablename__ = "error_groups"

    id = Column(Integer, primary_key=True, index=True)
    
    # Fingerprint único para identificar erros similares
    fingerprint = Column(String(64), unique=True, nullable=False, index=True)
    
    # Informações do grupo
    message_pattern = Column(Text, nullable=False)  # Padrão da mensagem
    error_type = Column(SQLEnum(ErrorType), nullable=False, index=True)
    severity = Column(SQLEnum(Severity), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    
    # Estatísticas do grupo
    total_occurrences = Column(Integer, default=1)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Status do grupo
    status = Column(SQLEnum(ErrorStatus), default=ErrorStatus.OPEN, index=True)
    assigned_to = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relacionamento com erros individuais
    errors = relationship("ErrorLog", back_populates="group")
    
    def __repr__(self):
        return f"<ErrorGroup(id={self.id}, fingerprint={self.fingerprint}, occurrences={self.total_occurrences})>"


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Fingerprinting - relacionamento com grupo
    group_id = Column(Integer, ForeignKey("error_groups.id"), nullable=True, index=True)
    group = relationship("ErrorGroup", back_populates="errors")
    
    # Error identification
    message = Column(Text, nullable=False, index=True)
    error_type = Column(SQLEnum(ErrorType), nullable=False, index=True)
    severity = Column(SQLEnum(Severity), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)  # frontend, backend, database, etc.
    
    # Error details
    stack_trace = Column(Text, nullable=True)
    endpoint = Column(String(500), nullable=True)
    method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE, etc.
    status_code = Column(Integer, nullable=True)
    
    # User and context
    user_id = Column(String(100), nullable=True, index=True)
    session_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Additional metadata
    error_metadata = Column(JSON, nullable=True)
    
    # Status tracking
    status = Column(SQLEnum(ErrorStatus), default=ErrorStatus.OPEN, index=True)
    assigned_to = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Count of occurrences (if grouping similar errors)
    occurrences = Column(Integer, default=1)

    def __repr__(self):
        return f"<ErrorLog(id={self.id}, type={self.error_type}, severity={self.severity}, message={self.message[:50]})>"


class AlertRule(Base):
    """Regras de alerta para notificações automáticas"""
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Configuração da regra
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Condições do alerta
    condition = Column(SQLEnum(AlertCondition), nullable=False)
    
    # Filtros (opcional - se None, aplica a todos)
    error_type = Column(SQLEnum(ErrorType), nullable=True)
    severity = Column(SQLEnum(Severity), nullable=True)
    source = Column(String(100), nullable=True)
    
    # Parâmetros da condição (armazenados como JSON)
    # Ex: {"threshold": 10, "time_window": 5} para ERROR_COUNT
    condition_params = Column(JSON, nullable=True)
    
    # Canais de notificação
    notification_channels = Column(JSON, nullable=False)  # Lista de canais
    
    # Configurações de notificação
    notification_config = Column(JSON, nullable=True)  # Configurações específicas por canal
    
    # Cooldown para evitar spam (em minutos)
    cooldown_minutes = Column(Integer, default=15)
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<AlertRule(id={self.id}, name={self.name}, condition={self.condition}, active={self.is_active})>"


class NotificationLog(Base):
    """Log de notificações enviadas"""
    __tablename__ = "notification_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Relacionamento com a regra de alerta
    alert_rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False, index=True)
    
    # Informações da notificação
    channel = Column(SQLEnum(NotificationChannel), nullable=False)
    recipient = Column(String(500), nullable=False)  # Email, webhook URL, etc.
    
    # Conteúdo
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    
    # Status
    sent_successfully = Column(Boolean, default=False)
    error_message = Column(Text, nullable=True)
    
    # Metadados
    notification_metadata = Column(JSON, nullable=True)
    
    # Timestamp
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<NotificationLog(id={self.id}, channel={self.channel}, success={self.sent_successfully})>"


def generate_fingerprint(error_type: str, message: str, endpoint: str = None, stack_trace: str = None) -> str:
    """
    Gera um fingerprint único para agrupar erros similares
    
    O fingerprint é baseado em:
    - Tipo do erro
    - Mensagem normalizada (sem números, IDs, etc.)
    - Endpoint (se disponível)
    - Primeiras linhas do stack trace (se disponível)
    """
    import re
    
    # Normalizar mensagem (remover números, IDs, timestamps, etc.)
    normalized_message = re.sub(r'\d+', 'N', message)
    normalized_message = re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'UUID', normalized_message)
    normalized_message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL', normalized_message)
    normalized_message = re.sub(r'https?://[^\s]+', 'URL', normalized_message)
    
    # Construir string para hash
    fingerprint_parts = [error_type, normalized_message]
    
    if endpoint:
        # Normalizar endpoint (remover IDs numéricos)
        normalized_endpoint = re.sub(r'/\d+', '/ID', endpoint)
        fingerprint_parts.append(normalized_endpoint)
    
    if stack_trace:
        # Pegar apenas as primeiras 3 linhas do stack trace
        stack_lines = stack_trace.split('\n')[:3]
        normalized_stack = '\n'.join(stack_lines)
        # Remover números de linha
        normalized_stack = re.sub(r'line \d+', 'line N', normalized_stack)
        fingerprint_parts.append(normalized_stack)
    
    # Gerar hash SHA256
    fingerprint_string = '|'.join(fingerprint_parts)
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()

