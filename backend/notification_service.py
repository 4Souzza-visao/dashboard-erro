"""
Serviço de notificações para envio de alertas
Suporta múltiplos canais: Email, Slack, Webhook, SMS, Discord
"""

import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Serviço para envio de notificações em múltiplos canais"""
    
    @staticmethod
    def send_notification(
        channel: str,
        recipient: str,
        subject: str,
        message: str,
        config: Optional[Dict[str, Any]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Envia notificação através do canal especificado
        
        Args:
            channel: Canal de notificação (EMAIL, SLACK, WEBHOOK, SMS, DISCORD)
            recipient: Destinatário (email, webhook URL, etc.)
            subject: Assunto da notificação
            message: Mensagem da notificação
            config: Configurações adicionais do canal
            
        Returns:
            tuple: (sucesso: bool, mensagem_erro: Optional[str])
        """
        try:
            if channel == "EMAIL":
                return NotificationService._send_email(recipient, subject, message, config)
            elif channel == "SLACK":
                return NotificationService._send_slack(recipient, subject, message, config)
            elif channel == "WEBHOOK":
                return NotificationService._send_webhook(recipient, subject, message, config)
            elif channel == "SMS":
                return NotificationService._send_sms(recipient, message, config)
            elif channel == "DISCORD":
                return NotificationService._send_discord(recipient, subject, message, config)
            else:
                return False, f"Canal de notificação desconhecido: {channel}"
        except Exception as e:
            logger.error(f"Erro ao enviar notificação via {channel}: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def _send_email(recipient: str, subject: str, message: str, config: Optional[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """
        Envia notificação por email
        
        Configuração necessária em config:
        - smtp_host: Host do servidor SMTP
        - smtp_port: Porta do servidor SMTP
        - smtp_user: Usuário SMTP
        - smtp_password: Senha SMTP
        - from_email: Email do remetente
        """
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            if not config:
                return False, "Configuração SMTP não fornecida"
            
            smtp_host = config.get("smtp_host")
            smtp_port = config.get("smtp_port", 587)
            smtp_user = config.get("smtp_user")
            smtp_password = config.get("smtp_password")
            from_email = config.get("from_email", smtp_user)
            
            if not all([smtp_host, smtp_user, smtp_password]):
                return False, "Configuração SMTP incompleta"
            
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = recipient
            msg['Subject'] = subject
            
            body = MIMEText(message, 'html')
            msg.attach(body)
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email enviado com sucesso para {recipient}")
            return True, None
            
        except Exception as e:
            logger.error(f"Erro ao enviar email: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def _send_slack(webhook_url: str, subject: str, message: str, config: Optional[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """
        Envia notificação para Slack via webhook
        
        Args:
            webhook_url: URL do webhook do Slack
            subject: Título da mensagem
            message: Conteúdo da mensagem
            config: Configurações adicionais (opcional)
        """
        try:
            payload = {
                "text": subject,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"🚨 {subject}"
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Notificação Slack enviada com sucesso")
                return True, None
            else:
                error_msg = f"Slack retornou status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Slack: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def _send_webhook(webhook_url: str, subject: str, message: str, config: Optional[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """
        Envia notificação via webhook genérico
        
        Args:
            webhook_url: URL do webhook
            subject: Assunto
            message: Mensagem
            config: Configurações adicionais (headers, método HTTP, etc.)
        """
        try:
            method = config.get("method", "POST") if config else "POST"
            headers = config.get("headers", {}) if config else {}
            headers.setdefault("Content-Type", "application/json")
            
            payload = {
                "subject": subject,
                "message": message,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "error-dashboard"
            }
            
            # Adicionar campos customizados se fornecidos
            if config and "custom_fields" in config:
                payload.update(config["custom_fields"])
            
            response = requests.request(
                method=method,
                url=webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if 200 <= response.status_code < 300:
                logger.info(f"Webhook enviado com sucesso para {webhook_url}")
                return True, None
            else:
                error_msg = f"Webhook retornou status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            logger.error(f"Erro ao enviar webhook: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def _send_sms(phone_number: str, message: str, config: Optional[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """
        Envia notificação via SMS (Twilio)
        
        Configuração necessária em config:
        - twilio_account_sid: Account SID do Twilio
        - twilio_auth_token: Auth Token do Twilio
        - twilio_phone_number: Número de telefone Twilio
        """
        try:
            if not config:
                return False, "Configuração Twilio não fornecida"
            
            account_sid = config.get("twilio_account_sid")
            auth_token = config.get("twilio_auth_token")
            from_phone = config.get("twilio_phone_number")
            
            if not all([account_sid, auth_token, from_phone]):
                return False, "Configuração Twilio incompleta"
            
            # Usar API REST do Twilio
            url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
            
            response = requests.post(
                url,
                auth=(account_sid, auth_token),
                data={
                    "From": from_phone,
                    "To": phone_number,
                    "Body": message[:160]  # Limitar a 160 caracteres
                },
                timeout=10
            )
            
            if response.status_code == 201:
                logger.info(f"SMS enviado com sucesso para {phone_number}")
                return True, None
            else:
                error_msg = f"Twilio retornou status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            logger.error(f"Erro ao enviar SMS: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def _send_discord(webhook_url: str, subject: str, message: str, config: Optional[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """
        Envia notificação para Discord via webhook
        
        Args:
            webhook_url: URL do webhook do Discord
            subject: Título da mensagem
            message: Conteúdo da mensagem
            config: Configurações adicionais (opcional)
        """
        try:
            # Determinar cor do embed baseado na severidade (se fornecida)
            color = 15158332  # Vermelho padrão
            if config and "severity" in config:
                severity = config["severity"]
                color_map = {
                    "LOW": 3066993,      # Azul
                    "MEDIUM": 16776960,  # Amarelo
                    "HIGH": 16744192,    # Laranja
                    "CRITICAL": 15158332 # Vermelho
                }
                color = color_map.get(severity, 15158332)
            
            payload = {
                "embeds": [
                    {
                        "title": f"🚨 {subject}",
                        "description": message,
                        "color": color,
                        "timestamp": datetime.utcnow().isoformat(),
                        "footer": {
                            "text": "Error Dashboard"
                        }
                    }
                ]
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info(f"Notificação Discord enviada com sucesso")
                return True, None
            else:
                error_msg = f"Discord retornou status {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            logger.error(f"Erro ao enviar notificação Discord: {str(e)}")
            return False, str(e)


def format_error_notification(error_data: Dict[str, Any], error_count: int = 1) -> tuple[str, str]:
    """
    Formata dados de erro para notificação
    
    Args:
        error_data: Dados do erro
        error_count: Número de ocorrências
        
    Returns:
        tuple: (subject, message)
    """
    error_type = error_data.get("error_type", "UNKNOWN")
    severity = error_data.get("severity", "UNKNOWN")
    message = error_data.get("message", "Sem mensagem")
    source = error_data.get("source", "unknown")
    
    # Emoji baseado na severidade
    emoji_map = {
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🟠",
        "CRITICAL": "🔴"
    }
    emoji = emoji_map.get(severity, "⚠️")
    
    subject = f"{emoji} [{severity}] {error_type} Error"
    
    if error_count > 1:
        subject += f" ({error_count} occurrences)"
    
    message_parts = [
        f"**Error Type:** {error_type}",
        f"**Severity:** {severity}",
        f"**Source:** {source}",
        f"**Message:** {message}",
    ]
    
    if error_count > 1:
        message_parts.append(f"**Occurrences:** {error_count}")
    
    if "endpoint" in error_data and error_data["endpoint"]:
        message_parts.append(f"**Endpoint:** {error_data['endpoint']}")
    
    if "timestamp" in error_data:
        message_parts.append(f"**Time:** {error_data['timestamp']}")
    
    formatted_message = "\n".join(message_parts)
    
    return subject, formatted_message

