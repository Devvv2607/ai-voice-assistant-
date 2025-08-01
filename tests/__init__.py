# Test package initialization
"""
Test suite for Jarvis AI Assistant

This package contains comprehensive tests for all components of the Jarvis AI Assistant,
including unit tests, integration tests, and mock tests for external services.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

# Test configuration
TEST_CONFIG = {
    'mock_responses': True,
    'timeout': 10,
    'test_data_dir': 'test_data',
    'mock_api_keys': {
        'mistral': 'test_mistral_key',
        'news': 'test_news_key',
        'email_user': 'test@example.com',
        'email_password': 'test_password'
    }
}