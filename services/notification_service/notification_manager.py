"""
Enhanced Notification Manager - NEXUS Platform
Comprehensive notification system with email, SMS, and push notifications
"""

import asyncio
import json
import logging
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText

import aiohttp
import firebase_admin
from firebase_admin import credentials, messaging

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationTemplate:
    template_id: str
    subject: str
    body: str
    type: NotificationType
    variables: List[str]


@dataclass
class NotificationRequest:
    recipient: str
    type: NotificationType
    priority: NotificationPriority
    subject: Optional[str] = None
    body: Optional[str] = None
    template_id: Optional[str] = None
    template_vars: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    scheduled_time: Optional[datetime] = None


@dataclass
class NotificationResult:
    notification_id: str
    success: bool
    type: NotificationType
    recipient: str
    sent_at: datetime
    error_message: Optional[str] = None
    provider_response: Optional[Dict[str, Any]] = None


class EmailProvider:
    """Email notification provider"""

    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.username = os.getenv("SMTP_USERNAME")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@nexusplatform.com")

    def is_configured(self) -> bool:
        return bool(self.username and self.password)

    def send_email(
        self, to_email: str, subject: str, body: str, html_body: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            # Add text body
            text_part = MIMEText(body, "plain")
            msg.attach(text_part)

            # Add HTML body if provided
            if html_body:
                html_part = MIMEText(html_body, "html")
                msg.attach(html_part)

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()

            return {
                "success": True,
                "message_id": f"email_{datetime.now().timestamp()}",
            }

        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {"success": False, "error": str(e)}


class SMSProvider:
    """SMS notification provider using Twilio"""

    def __init__(self):
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number = os.getenv("TWILIO_FROM_NUMBER")

        if self.account_sid and self.auth_token:
            self.client = TwilioClient(self.account_sid, self.auth_token)
        else:
            self.client = None

    def is_configured(self) -> bool:
        return bool(self.client and self.from_number)

    def send_sms(self, to_number: str, message: str) -> Dict[str, Any]:
        """Send SMS using Twilio"""
        try:
            if not self.is_configured():
                raise Exception("Twilio not configured")

            message_obj = self.client.messages.create(
                body=message, from_=self.from_number, to=to_number
            )

            return {
                "success": True,
                "message_id": message_obj.sid,
                "status": message_obj.status,
            }

        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return {"success": False, "error": str(e)}


class PushProvider:
    """Push notification provider using Firebase"""

    def __init__(self):
        try:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                self.initialized = True
            else:
                self.initialized = False
        except Exception as e:
            logger.warning(f"Firebase initialization failed: {e}")
            self.initialized = False

    def is_configured(self) -> bool:
        return self.initialized

    def send_push_notification(
        self, token: str, title: str, body: str, data: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Send push notification using Firebase"""
        try:
            if not self.is_configured():
                raise Exception("Firebase not configured")

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
            )

            response = messaging.send(message)

            return {"success": True, "message_id": response}

        except Exception as e:
            logger.error(f"Push notification sending failed: {e}")
            return {"success": False, "error": str(e)}


class NotificationManager:
    """Comprehensive notification manager"""

    def __init__(self):
        self.redis_client = None
        self.templates: Dict[str, NotificationTemplate] = {}
        self.notification_history: List[NotificationResult] = []

        # Initialize providers
        self.email_provider = EmailProvider()
        self.sms_provider = SMSProvider()
        self.push_provider = PushProvider()

        # Load default templates
        self._load_default_templates()

        # Initialize Redis for queuing (optional)
        self._init_redis()

        logger.info("🔔 Notification Manager initialized")

    def _init_redis(self):
        """Initialize Redis client for notification queuing"""
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url)
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            self.redis_client = None

    def _load_default_templates(self):
        """Load default notification templates"""
        self.templates = {
            "welcome_email": NotificationTemplate(
                template_id="welcome_email",
                subject="Welcome to NEXUS Platform!",
                body="Welcome {user_name}! Your account has been created successfully.",
                type=NotificationType.EMAIL,
                variables=["user_name"],
            ),
            "password_reset": NotificationTemplate(
                template_id="password_reset",
                subject="Password Reset Request",
                body="Click here to reset your password: {reset_link}",
                type=NotificationType.EMAIL,
                variables=["reset_link"],
            ),
            "transaction_alert": NotificationTemplate(
                template_id="transaction_alert",
                subject="Transaction Alert",
                body="A {transaction_type} of ${amount} has been {action}.",
                type=NotificationType.PUSH,
                variables=["transaction_type", "amount", "action"],
            ),
            "security_alert": NotificationTemplate(
                template_id="security_alert",
                subject="Security Alert",
                body="Security event detected: {event_description}",
                type=NotificationType.SMS,
                variables=["event_description"],
            ),
            "budget_warning": NotificationTemplate(
                template_id="budget_warning",
                subject="Budget Alert",
                body="You've used {percentage}% of your {category} budget.",
                type=NotificationType.PUSH,
                variables=["percentage", "category"],
            ),
        }

    def render_template(
        self, template_id: str, variables: Dict[str, Any]
    ) -> tuple[str, str]:
        """Render a notification template with variables"""
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")

        template = self.templates[template_id]
        subject = template.subject
        body = template.body

        # Replace variables in subject and body
        for var, value in variables.items():
            subject = subject.replace(f"{{{var}}}", str(value))
            body = body.replace(f"{{{var}}}", str(value))

        return subject, body

    async def send_notification(
        self, request: NotificationRequest
    ) -> NotificationResult:
        """Send a notification"""
        notification_id = f"notif_{datetime.now().timestamp()}_{request.type.value}"

        try:
            # Handle template rendering
            if request.template_id:
                if not request.template_vars:
                    raise ValueError("Template variables required when using template")
                subject, body = self.render_template(
                    request.template_id, request.template_vars
                )
                subject = subject or request.subject
                body = body or request.body
            else:
                subject = request.subject
                body = request.body

            if not subject or not body:
                raise ValueError("Subject and body are required")

            # Route to appropriate provider
            result = await self._send_via_provider(
                request.type, request.recipient, subject, body, request.metadata
            )

            notification_result = NotificationResult(
                notification_id=notification_id,
                success=result["success"],
                type=request.type,
                recipient=request.recipient,
                sent_at=datetime.now(),
                error_message=result.get("error"),
                provider_response=result,
            )

            # Store in history
            self.notification_history.append(notification_result)

            # Store in Redis if available
            if self.redis_client:
                await self._store_in_redis(notification_result)

            return notification_result

        except Exception as e:
            logger.error(f"Notification sending failed: {e}")
            return NotificationResult(
                notification_id=notification_id,
                success=False,
                type=request.type,
                recipient=request.recipient,
                sent_at=datetime.now(),
                error_message=str(e),
            )

    async def _send_via_provider(
        self,
        notification_type: NotificationType,
        recipient: str,
        subject: str,
        body: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send notification via appropriate provider"""
        if notification_type == NotificationType.EMAIL:
            return self.email_provider.send_email(recipient, subject, body)
        elif notification_type == NotificationType.SMS:
            return self.sms_provider.send_sms(recipient, body)
        elif notification_type == NotificationType.PUSH:
            return self.push_provider.send_push_notification(
                recipient, subject, body, metadata
            )
        elif notification_type == NotificationType.IN_APP:
            # Handle in-app notifications (could integrate with WebSocket)
            return {"success": True, "message": "In-app notification queued"}
        elif notification_type == NotificationType.WEBHOOK:
            return await self._send_webhook(
                recipient, {"subject": subject, "body": body, "metadata": metadata}
            )
        else:
            raise ValueError(f"Unsupported notification type: {notification_type}")

    async def _send_webhook(
        self, webhook_url: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send webhook notification"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    return {
                        "success": response.status == 200,
                        "status_code": response.status,
                        "response": await response.text(),
                    }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _store_in_redis(self, result: NotificationResult):
        """Store notification result in Redis"""
        try:
            key = f"notification:{result.notification_id}"
            data = asdict(result)
            await self.redis_client.setex(key, 86400 * 30, json.dumps(data))  # 30 days
        except Exception as e:
            logger.warning(f"Failed to store notification in Redis: {e}")

    async def schedule_notification(
        self, request: NotificationRequest, delay_seconds: int
    ):
        """Schedule a notification for later delivery"""
        if self.redis_client:
            # Store in Redis queue with delay
            queue_data = asdict(request)
            queue_data["scheduled_for"] = (
                datetime.now() + timedelta(seconds=delay_seconds)
            ).isoformat()

            await self.redis_client.lpush("notification_queue", json.dumps(queue_data))
            await self.redis_client.expire("notification_queue", delay_seconds)
        else:
            # Fallback: use asyncio
            asyncio.create_task(self._delayed_send(request, delay_seconds))

    async def _delayed_send(self, request: NotificationRequest, delay: int):
        """Send notification after delay"""
        await asyncio.sleep(delay)
        await self.send_notification(request)

    async def get_notification_history(
        self, limit: int = 50
    ) -> List[NotificationResult]:
        """Get recent notification history"""
        if self.redis_client:
            # Get from Redis
            keys = await self.redis_client.keys("notification:*")
            if keys:
                # Get most recent notifications
                results = []
                for key in keys[:limit]:
                    data = await self.redis_client.get(key)
                    if data:
                        results.append(NotificationResult(**json.loads(data)))
                return sorted(results, key=lambda x: x.sent_at, reverse=True)

        # Fallback to in-memory history
        return self.notification_history[-limit:]

    async def bulk_send(
        self, requests: List[NotificationRequest]
    ) -> List[NotificationResult]:
        """Send multiple notifications"""
        tasks = [self.send_notification(request) for request in requests]
        return await asyncio.gather(*tasks)


# Global notification manager instance
notification_manager = NotificationManager()
