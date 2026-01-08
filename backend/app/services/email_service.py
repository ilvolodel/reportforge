import os
import logging
import smtplib
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "email-smtp.eu-west-1.amazonaws.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SMTP_SENDER_EMAIL", "noreply@brainaihub.tech")
        self.sender_name = os.getenv("SMTP_SENDER_NAME", "ReportForge")
        
        # Initialize Jinja2 for email templates
        template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "email")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
    
    def send_magic_link(
        self,
        to_email: str,
        magic_link: str,
        user_name: Optional[str] = None
    ) -> bool:
        """
        Send magic link email to user using AWS SES SMTP
        
        Args:
            to_email: Recipient email address
            magic_link: Full URL of the magic link
            user_name: Optional user name for personalization
            
        Returns:
            True if email sent successfully, False otherwise
        """
        logger.info(f"🔄 Starting email send process for {to_email}")
        logger.info(f"📧 SMTP Config: {self.smtp_host}:{self.smtp_port}, user={self.smtp_username[:10]}...")
        try:
            # Load and render email template
            template = self.jinja_env.get_template("magic_link.html")
            html_body = template.render(
                magic_link=magic_link,
                user_name=user_name or to_email.split("@")[0],
                expiry_minutes=os.getenv("MAGIC_LINK_EXPIRY_MINUTES", "15")
            )
            
            # Prepare email
            subject = os.getenv("MAGIC_LINK_SUBJECT", "Your ReportForge Magic Link")
            
            # Create MIME message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Attach HTML content
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Connect to AWS SES SMTP and send email
            logger.info(f"Connecting to SMTP: {self.smtp_host}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Upgrade to secure connection
                server.login(self.smtp_username, self.smtp_password)
                
                logger.info(f"Sending magic link email to {to_email}")
                server.sendmail(self.sender_email, [to_email], msg.as_string())
            
            logger.info(f"✅ Magic link email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending to {to_email}: {str(e)}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send magic link to {to_email}: {str(e)}", exc_info=True)
            return False


# Singleton instance
email_service = EmailService()
