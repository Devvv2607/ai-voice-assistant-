"""
Email tool for LangChain integration.
Handles email checking, sending, and management operations.
"""

import json
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun

from ..services.email_service import EmailService
from ..core.config import config


class EmailTool(BaseTool):
    """LangChain tool for email operations."""
    
    name = "email_manager"
    description = "Check latest emails, send emails, or manage email operations. Use 'check' to get latest emails, 'count' for email count, or JSON with 'to', 'subject', 'body' to send."
    
    def __init__(self):
        """Initialize email tool with email service."""
        super().__init__()
        self.email_service = EmailService()
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Handle email operations."""
        if not self.email_service.is_configured():
            return "❌ Email is not configured. Please set EMAIL_USER and EMAIL_PASSWORD in environment variables."
        
        try:
            query_lower = query.lower().strip()
            
            if query_lower in ['check', 'inbox', 'latest']:
                return self._check_emails()
            elif query_lower in ['count', 'number']:
                return self._get_email_count()
            elif query.startswith('{'):
                # JSON input for sending email
                params = json.loads(query)
                return self._send_email(params)
            else:
                # Try to parse as natural language
                params = self._parse_email_request(query)
                if params.get('action') == 'send':
                    return self._send_email(params)
                else:
                    return self._check_emails()
                    
        except Exception as e:
            return f"❌ Email operation failed: {str(e)}"
    
    def _check_emails(self, max_emails: int = 3) -> str:
        """Check latest emails."""
        try:
            emails = self.email_service.get_latest_emails(max_emails)
            
            if not emails:
                return "📭 No emails in inbox."
            
            email_summaries = ["📧 Latest emails:"]
            for email_data in emails:
                sender = email_data.get('from', 'Unknown Sender')
                subject = email_data.get('subject', 'No Subject')
                date = email_data.get('date', 'Unknown Date')
                
                # Clean sender name
                if '<' in sender:
                    sender = sender.split('<')[0].strip().strip('"')
                
                email_summaries.append(f"• From: {sender}")
                email_summaries.append(f"  Subject: {subject}")
                email_summaries.append(f"  Date: {date}")
                email_summaries.append("")
            
            return "\n".join(email_summaries)
            
        except Exception as e:
            return f"❌ Error checking emails: {str(e)}"
    
    def _get_email_count(self) -> str:
        """Get total email count in inbox."""
        try:
            count = self.email_service.get_email_count()
            return f"📊 You have {count} emails in your inbox."
        except Exception as e:
            return f"❌ Error getting email count: {str(e)}"
    
    def _send_email(self, params: dict) -> str:
        """Send an email."""
        try:
            to_email = params.get('to')
            subject = params.get('subject', 'Message from Jarvis')
            body = params.get('body', 'This is a message sent by Jarvis AI Assistant.')
            
            if not to_email:
                return "❌ Need email address to send message. Please provide 'to' field."
            
            # Send email
            success = self.email_service.send_email(to_email, subject, body)
            
            if success:
                return f"✅ Email sent successfully to {to_email}"
            else:
                return f"❌ Failed to send email to {to_email}"
                
        except Exception as e:
            return f"❌ Error sending email: {str(e)}"
    
    def _parse_email_request(self, text: str) -> dict:
        """Parse natural language email request."""
        params = {'action': 'check'}
        
        # Check if it's a send request
        send_keywords = ['send', 'email', 'write', 'compose']
        if any(keyword in text.lower() for keyword in send_keywords):
            params['action'] = 'send'
            
            # Try to extract email address
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, text)
            if email_match:
                params['to'] = email_match.group()
            
            # Extract subject if mentioned
            subject_patterns = [
                r'subject[:\s]+([^,\n]+)',
                r'about\s+([^,\n]+)',
                r'regarding\s+([^,\n]+)'
            ]
            
            for pattern in subject_patterns:
                subject_match = re.search(pattern, text.lower())
                if subject_match:
                    params['subject'] = subject_match.group(1).strip()
                    break
        
        return params