import os
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "eu-west-1")
        self.sender_email = os.getenv("SES_SENDER_EMAIL", "noreply@brainaihub.tech")
        self.sender_name = os.getenv("SES_SENDER_NAME", "ReportForge")
        
        # Initialize SES client
        self.ses_client = boto3.client(
            'ses',
            region_name=self.aws_region,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        )
        
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
        Send magic link email to user using AWS SES
        
        Args:
            to_email: Recipient email address
            magic_link: Full URL of the magic link
            user_name: Optional user name for personalization
            
        Returns:
            True if email sent successfully, False otherwise
        """
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
            sender = f"{self.sender_name} <{self.sender_email}>"
            
            # Send email via SES
            response = self.ses_client.send_email(
                Source=sender,
                Destination={
                    'ToAddresses': [to_email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': html_body,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            message_id = response.get('MessageId')
            logger.info(f"Magic link email sent to {to_email}, MessageId: {message_id}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"SES ClientError sending to {to_email}: {error_code} - {error_message}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to send magic link to {to_email}: {str(e)}", exc_info=True)
            return False


# Singleton instance
email_service = EmailService()
