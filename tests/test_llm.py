"""
Tests for MistralLLM implementation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis import MistralLLM


class TestMistralLLM(unittest.TestCase):
    """Test cases for MistralLLM class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test_api_key"
        self.llm = MistralLLM(api_key=self.api_key)
    
    def test_llm_initialization(self):
        """Test LLM initialization with parameters."""
        self.assertEqual(self.llm.api_key, self.api_key)
        self.assertEqual(self.llm.model_name, "mistral-small-latest")
        self.assertEqual(self.llm.max_tokens, 500)
        self.assertEqual(self.llm.temperature, 0.3)
    
    def test_llm_type_property(self):
        """Test _llm_type property."""
        self.assertEqual(self.llm._llm_type, "mistral")
    
    @patch('requests.post')
    def test_successful_api_call(self, mock_post):
        """Test successful API call to Mistral."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [
                {
                    'message': {
                        'content': 'Test response from Mistral'
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        result = self.llm._call("Test prompt")
        
        self.assertEqual(result, "Test response from Mistral")
        mock_post.assert_called_once()
        
        # Verify API call parameters
        call_args = mock_post.call_args
        self.assertIn("https://api.mistral.ai/v1/chat/completions", call_args[1]['url'])
        self.assertIn("Authorization", call_args[1]['headers'])
        self.assertEqual(call_args[1]['headers']['Authorization'], f"Bearer {self.api_key}")
    
    @patch('requests.post')
    def test_api_call_failure(self, mock_post):
        """Test API call failure handling."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        result = self.llm._call("Test prompt")
        
        self.assertEqual(result, "Error: Unable to get response from Mistral API")
    
    @patch('requests.post')
    def test_api_call_exception(self, mock_post):
        """Test API call exception handling."""
        # Mock exception
        mock_post.side_effect = requests.RequestException("Network error")
        
        result = self.llm._call("Test prompt")
        
        self.assertIn("Error calling Mistral API", result)
        self.assertIn("Network error", result)
    
    @patch('requests.post')
    def test_api_call_timeout(self, mock_post):
        """Test API call timeout handling."""
        # Mock timeout
        mock_post.side_effect = requests.Timeout("Request timeout")
        
        result = self.llm._call("Test prompt")
        
        self.assertIn("Error calling Mistral API", result)
        self.assertIn("Request timeout", result)
    
    @patch('requests.post')
    def test_empty_choices_response(self, mock_post):
        """Test handling of empty choices in response."""
        # Mock response with empty choices
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'choices': []}
        mock_post.return_value = mock_response
        
        result = self.llm._call("Test prompt")
        
        self.assertEqual(result, "Error: Unable to get response from Mistral API")
    
    def test_custom_parameters(self):
        """Test LLM with custom parameters."""
        custom_llm = MistralLLM(
            api_key="test_key",
            model_name="mistral-large-latest",
            max_tokens=1000,
            temperature=0.7
        )
        
        self.assertEqual(custom_llm.model_name, "mistral-large-latest")
        self.assertEqual(custom_llm.max_tokens, 1000)
        self.assertEqual(custom_llm.temperature, 0.7)


if __name__ == '__main__':
    unittest.main()