"""
Email service for Jarvis AI Assistant.
Handles SMTP and IMAP operations for email management.
"""

import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional
from ..core.config import config


class EmailService:
    """Service class for email operations."""
    
    def __init__(self):
        """Initialize email service with configuration."""
        email_config = config.get_email_config()
        self.email_user = email_config.get('user')
        self.email_password = email_config.get('password')
        self.imap_server = email_config.get('imap_server', 'imap.gmail.com')
        self.smtp_server = email_config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = 587
        self.imap_port = 993
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(self.email_user and self.email_password)
    
    def get_latest_emails(self, count: int = 5) -> List[Dict]:
        """Get latest emails from inbox."""
        if not self.is_configured():
            return []
        
        try:
            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_user, self.email_password)
            mail.select('inbox')
            
            # Search for all emails
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            
            if not email_ids:
                mail.close()
                mail.logout()
                return []
            
            # Get latest emails
            latest_emails = []
            for email_id in email_ids[-count:]:
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Extract email information
                    email_info = {
                        'id': email_id.decode(),
                        'subject': self._decode_header(msg.get('subject', 'No Subject')),
                        'from': self._decode_header(msg.get('from', 'Unknown Sender')),
                        'date': msg.get('date', 'Unknown Date'),
                        'body': self._get_email_body(msg)
                    }
                    
                    latest_emails.append(email_info)
                    
                except Exception as e:
                    print(f"Error processing email {email_id}: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            # Return in reverse order (newest first)
            return list(reversed(latest_emails))
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def get_email_count(self) -> int:
        """Get total number of emails in inbox."""
        if not self.is_configured():
            return 0
        
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_user, self.email_password)
            mail.select('inbox')
            
            result, data = mail.search(None, 'ALL')
            email_ids = data[0].split()
            count = len(email_ids)
            
            mail.close()
            mail.logout()
            
            return count
            
        except Exception as e:
            print(f"Error getting email count: {e}")
            return 0
    
    def send_email(self, to_email: str, subject: str, body: str, html: bool = False) -> bool:
        """Send an email."""
        if not self.is_configured():
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            if html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server and send
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable TLS encryption
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_email_with_attachment(self, to_email: str, subject: str, body: str, 
                                 attachment_path: str) -> bool:
        """Send an email with attachment."""
        if not self.is_configured():
            return False
        
        try:
            from email.mime.base import MIMEBase
            from email import encoders
            import os
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachment
            if os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                
                encoders.encode_base64(part)
                filename = os.path.basename(attachment_path)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filename}'
                )
                msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Error sending email with attachment: {e}")
            return False
    
    def search_emails(self, query: str, count: int = 10) -> List[Dict]:
        """Search emails by subject or sender."""
        if not self.is_configured():
            return []
        
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            mail.login(self.email_user, self.email_password)
            mail.select('inbox')
            
            # Search emails
            search_criteria = f'(OR (SUBJECT "{query}") (FROM "{query}"))'
            result, data = mail.search(None, search_criteria)
            email_ids = data[0].split()
            
            if not email_ids:
                mail.close()
                mail.logout()
                return []
            
            # Get matching emails
            found_emails = []
            for email_id in email_ids[-count:]:
                try:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    email_info = {
                        'id': email_id.decode(),
                        'subject': self._decode_header(msg.get('subject', 'No Subject')),
                        'from': self._decode_header(msg.get('from', 'Unknown Sender')),
                        'date': msg.get('date', 'Unknown Date'),
                        'body': self._get_email_body(msg)
                    }
                    
                    found_emails.append(email_info)
                    
                except Exception as e:
                    print(f"Error processing search result {email_id}: {e}")
                    continue
            
            mail.close()
            mail.logout()
            
            return list(reversed(found_emails))
            
        except Exception as e:
            print(f"Error searching emails: {e}")
            return []
    
    def _decode_header(self, header: str) -> str:
        """Decode email header."""
        if not header:
            return ""
        
        try:
            decoded = email.header.decode_header(header)
            return ''.join([
                part.decode(encoding or 'utf-8') if isinstance(part, bytes) else str(part)
                for part, encoding in decoded
            ])
        except:
            return str(header)
    
    def _get_email_body(self, msg) -> str:
        """Extract email body text."""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)
                        if payload:
                            return payload.decode('utf-8', errors='ignore')[:200] + "..."
            else:
                payload = msg.get_payload(decode=True)
                if payload:
                    return payload.decode('utf-8', errors='ignore')[:200] + "..."
        except:
            pass
        
        return "Body not available"