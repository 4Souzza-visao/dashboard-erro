from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from database import Base
import enum


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


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(Integer, primary_key=True, index=True)
    
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
    metadata = Column(JSON, nullable=True)
    
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

