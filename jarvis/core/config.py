"""
Configuration management for Jarvis AI Assistant.
Handles environment variables, API keys, and settings.
"""

import os
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for Jarvis assistant."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # API Keys
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.serp_api_key = os.getenv('SERP_API_KEY')
        
        # Email Configuration
        self.email_config = {
            'user': os.getenv('EMAIL_USER'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'imap_server': os.getenv('EMAIL_IMAP_SERVER', 'imap.gmail.com'),
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        }
        
        # Speech Configuration
        self.speech_config = {
            'rate': int(os.getenv('TTS_RATE', '180')),
            'volume': float(os.getenv('TTS_VOLUME', '0.9')),
            'voice_preference': os.getenv('TTS_VOICE_PREFERENCE', 'female')
        }
        
        # Assistant Configuration
        self.wake_words = ['hey jarvis', 'jarvis', 'hey davis', 'davis']
        self.assistant_name = os.getenv('ASSISTANT_NAME', 'Jarvis')
        
        # LLM Configuration
        self.llm_config = {
            'model_name': os.getenv('MISTRAL_MODEL', 'mistral-small-latest'),
            'max_tokens': int(os.getenv('MISTRAL_MAX_TOKENS', '500')),
            'temperature': float(os.getenv('MISTRAL_TEMPERATURE', '0.3'))
        }
        
        # Calendar Configuration
        self.calendar_config = {
            'credentials_file': os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json'),
            'token_file': os.getenv('GOOGLE_TOKEN_FILE', 'token.pickle'),
            'scopes': ['https://www.googleapis.com/auth/calendar']
        }
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration and return status of each service."""
        status = {
            'mistral_llm': bool(self.mistral_api_key),
            'email': bool(self.email_config['user'] and self.email_config['password']),
            'news_api': bool(self.news_api_key),
            'google_calendar': os.path.exists(self.calendar_config['credentials_file']),
            'serp_api': bool(self.serp_api_key)
        }
        return status
    
    def get_email_config(self) -> Dict[str, Optional[str]]:
        """Get email configuration."""
        return self.email_config.copy()
    
    def get_llm_config(self) -> Dict[str, any]:
        """Get LLM configuration."""
        return self.llm_config.copy()
    
    def get_speech_config(self) -> Dict[str, any]:
        """Get speech configuration."""
        return self.speech_config.copy()
    
    def is_service_enabled(self, service: str) -> bool:
        """Check if a specific service is enabled."""
        status = self.validate_config()
        return status.get(service, False)


# Global configuration instance
config = Config()