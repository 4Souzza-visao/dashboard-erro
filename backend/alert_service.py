"""
Serviço de alertas para verificar condições e disparar notificações
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any, List
import models
from notification_service import NotificationService, format_error_notification
import logging

logger = logging.getLogger(__name__)


class AlertService:
    """Serviço para gerenciar e disparar alertas"""
    
    @staticmethod
    def check_and_trigger_alerts(db: Session, error: models.ErrorLog):
        """
        Verifica todas as regras de alerta ativas e dispara notificações se necessário
        
        Args:
            db: Sessão do banco de dados
            error: Erro recém-criado
        """
        # Buscar todas as regras ativas
        active_rules = db.query(models.AlertRule).filter(
            models.AlertRule.is_active == True
        ).all()
        
        for rule in active_rules:
            try:
                # Verificar se a regra se aplica a este erro
                if not AlertService._rule_applies_to_error(rule, error):
                    continue
                
                # Verificar cooldown
                if AlertService._is_in_cooldown(rule):
                    logger.info(f"Regra {rule.name} está em cooldown")
                    continue
                
                # Verificar condição
                should_trigger = AlertService._check_condition(db, rule, error)
                
                if should_trigger:
                    AlertService._trigger_alert(db, rule, error)
                    
            except Exception as e:
                logger.error(f"Erro ao processar regra de alerta {rule.id}: {str(e)}")
    
    @staticmethod
    def _rule_applies_to_error(rule: models.AlertRule, error: models.ErrorLog) -> bool:
        """Verifica se a regra se aplica ao erro"""
        # Verificar filtros
        if rule.error_type and rule.error_type != error.error_type:
            return False
        
        if rule.severity and rule.severity != error.severity:
            return False
        
        if rule.source and rule.source != error.source:
            return False
        
        return True
    
    @staticmethod
    def _is_in_cooldown(rule: models.AlertRule) -> bool:
        """Verifica se a regra está em período de cooldown"""
        if not rule.last_triggered:
            return False
        
        cooldown_end = rule.last_triggered + timedelta(minutes=rule.cooldown_minutes)
        return datetime.utcnow() < cooldown_end
    
    @staticmethod
    def _check_condition(db: Session, rule: models.AlertRule, error: models.ErrorLog) -> bool:
        """
        Verifica se a condição da regra foi atingida
        
        Returns:
            bool: True se deve disparar o alerta
        """
        condition = rule.condition
        params = rule.condition_params or {}
        
        if condition == models.AlertCondition.CRITICAL_ERROR:
            # Disparar para qualquer erro crítico
            return error.severity == models.Severity.CRITICAL
        
        elif condition == models.AlertCondition.ERROR_COUNT:
            # Disparar se X erros ocorreram em Y minutos
            threshold = params.get("threshold", 10)
            time_window = params.get("time_window_minutes", 5)
            
            start_time = datetime.utcnow() - timedelta(minutes=time_window)
            
            query = db.query(models.ErrorLog).filter(
                models.ErrorLog.timestamp >= start_time
            )
            
            # Aplicar filtros da regra
            if rule.error_type:
                query = query.filter(models.ErrorLog.error_type == rule.error_type)
            if rule.severity:
                query = query.filter(models.ErrorLog.severity == rule.severity)
            if rule.source:
                query = query.filter(models.ErrorLog.source == rule.source)
            
            count = query.count()
            return count >= threshold
        
        elif condition == models.AlertCondition.ERROR_RATE:
            # Disparar se taxa de erro excede X%
            threshold_percent = params.get("threshold_percent", 50)
            time_window = params.get("time_window_minutes", 15)
            
            start_time = datetime.utcnow() - timedelta(minutes=time_window)
            
            # Contar erros no período
            error_query = db.query(models.ErrorLog).filter(
                models.ErrorLog.timestamp >= start_time
            )
            
            if rule.error_type:
                error_query = error_query.filter(models.ErrorLog.error_type == rule.error_type)
            if rule.source:
                error_query = error_query.filter(models.ErrorLog.source == rule.source)
            
            error_count = error_query.count()
            
            # Para simplificar, vamos considerar que a taxa é baseada em um número mínimo de requisições
            # Em produção, você integraria com métricas de requisições totais
            min_requests = params.get("min_requests", 100)
            
            if error_count < 10:  # Muito poucos erros para calcular taxa
                return False
            
            # Calcular taxa (simplificado)
            error_rate = (error_count / min_requests) * 100
            return error_rate >= threshold_percent
        
        elif condition == models.AlertCondition.NEW_ERROR_TYPE:
            # Disparar se é um novo tipo de erro (primeira ocorrência)
            # Verificar se existe erro similar nos últimos 24h
            start_time = datetime.utcnow() - timedelta(hours=24)
            
            similar_errors = db.query(models.ErrorLog).filter(
                models.ErrorLog.timestamp < error.timestamp,
                models.ErrorLog.timestamp >= start_time,
                models.ErrorLog.error_type == error.error_type,
                models.ErrorLog.message == error.message
            ).count()
            
            return similar_errors == 0
        
        elif condition == models.AlertCondition.ERROR_SPIKE:
            # Disparar se houver aumento súbito de erros
            spike_multiplier = params.get("spike_multiplier", 3)
            time_window = params.get("time_window_minutes", 10)
            comparison_window = params.get("comparison_window_minutes", 60)
            
            current_time = datetime.utcnow()
            recent_start = current_time - timedelta(minutes=time_window)
            baseline_start = current_time - timedelta(minutes=comparison_window)
            baseline_end = recent_start
            
            # Contar erros recentes
            recent_query = db.query(models.ErrorLog).filter(
                models.ErrorLog.timestamp >= recent_start
            )
            
            # Contar erros baseline
            baseline_query = db.query(models.ErrorLog).filter(
                models.ErrorLog.timestamp >= baseline_start,
                models.ErrorLog.timestamp < baseline_end
            )
            
            # Aplicar filtros
            if rule.error_type:
                recent_query = recent_query.filter(models.ErrorLog.error_type == rule.error_type)
                baseline_query = baseline_query.filter(models.ErrorLog.error_type == rule.error_type)
            if rule.source:
                recent_query = recent_query.filter(models.ErrorLog.source == rule.source)
                baseline_query = baseline_query.filter(models.ErrorLog.source == rule.source)
            
            recent_count = recent_query.count()
            baseline_count = baseline_query.count()
            
            # Normalizar baseline para o mesmo período de tempo
            baseline_normalized = baseline_count * (time_window / comparison_window)
            
            # Verificar se houve spike
            if baseline_normalized == 0:
                return recent_count >= 5  # Threshold mínimo
            
            return recent_count >= (baseline_normalized * spike_multiplier)
        
        return False
    
    @staticmethod
    def _trigger_alert(db: Session, rule: models.AlertRule, error: models.ErrorLog):
        """
        Dispara o alerta enviando notificações pelos canais configurados
        
        Args:
            db: Sessão do banco de dados
            rule: Regra de alerta
            error: Erro que disparou o alerta
        """
        logger.info(f"Disparando alerta: {rule.name}")
        
        # Preparar dados do erro
        error_data = {
            "error_type": error.error_type.value,
            "severity": error.severity.value,
            "source": error.source,
            "message": error.message,
            "endpoint": error.endpoint,
            "timestamp": error.timestamp.isoformat()
        }
        
        # Contar ocorrências recentes se for um erro agrupado
        error_count = 1
        if error.group_id:
            group = db.query(models.ErrorGroup).filter(
                models.ErrorGroup.id == error.group_id
            ).first()
            if group:
                error_count = group.total_occurrences
        
        # Formatar mensagem
        subject, message = format_error_notification(error_data, error_count)
        
        # Adicionar informações da regra
        message += f"\n\n**Alert Rule:** {rule.name}"
        if rule.description:
            message += f"\n**Description:** {rule.description}"
        
        # Enviar notificações para cada canal
        for channel in rule.notification_channels:
            try:
                # Obter configuração do canal
                config = rule.notification_config or {}
                channel_config = config.get(channel, {})
                
                # Adicionar severidade ao config para Discord
                if channel == "DISCORD":
                    channel_config["severity"] = error.severity.value
                
                # Obter destinatário
                recipient = channel_config.get("recipient", "")
                
                if not recipient:
                    logger.warning(f"Destinatário não configurado para canal {channel}")
                    continue
                
                # Enviar notificação
                success, error_msg = NotificationService.send_notification(
                    channel=channel,
                    recipient=recipient,
                    subject=subject,
                    message=message,
                    config=channel_config
                )
                
                # Registrar log de notificação
                notification_log = models.NotificationLog(
                    alert_rule_id=rule.id,
                    channel=models.NotificationChannel[channel],
                    recipient=recipient,
                    subject=subject,
                    message=message,
                    sent_successfully=success,
                    error_message=error_msg,
                    metadata={
                        "error_id": error.id,
                        "error_type": error.error_type.value,
                        "severity": error.severity.value
                    }
                )
                db.add(notification_log)
                
                if success:
                    logger.info(f"Notificação enviada com sucesso via {channel}")
                else:
                    logger.error(f"Falha ao enviar notificação via {channel}: {error_msg}")
                
            except Exception as e:
                logger.error(f"Erro ao enviar notificação via {channel}: {str(e)}")
        
        # Atualizar timestamp do último disparo
        rule.last_triggered = datetime.utcnow()
        
        # Commit das mudanças
        db.commit()
        
        logger.info(f"Alerta {rule.name} processado com sucesso")

