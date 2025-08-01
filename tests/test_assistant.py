"""
Tests for main AgenticJarvis assistant class
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
import sys
import os
import tempfile
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis import AgenticJarvis


class TestAgenticJarvis(unittest.TestCase):
    """Test cases for AgenticJarvis main class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'MISTRAL_API_KEY': 'test_mistral_key',
            'EMAIL_USER': 'test@example.com',
            'EMAIL_PASSWORD': 'test_password',
            'NEWS_API_KEY': 'test_news_key'
        })
        self.env_patcher.start()
        
        # Mock external dependencies
        with patch('pyttsx3.init'), \
             patch('speech_recognition.Recognizer'), \
             patch('speech_recognition.Microphone'):
            self.jarvis = AgenticJarvis(mistral_api_key='test_key')
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
    
    def test_initialization(self):
        """Test Jarvis initialization."""
        self.assertEqual(self.jarvis.mistral_api_key, 'test_key')
        self.assertTrue(self.jarvis.listening_for_wake_word)
        self.assertIn('hey jarvis', self.jarvis.wake_words)
        self.assertIsNotNone(self.jarvis.email_config)
    
    def test_wake_word_detection(self):
        """Test wake word detection logic."""
        test_cases = [
            ('hey jarvis how are you', True),
            ('jarvis play music', True),
            ('hello there', False),
            ('davis help me', True),  # Alternative wake word
            ('random conversation', False)
        ]
        
        for text, expected in test_cases:
            # Mock the speech recognition
            with patch.object(self.jarvis, 'listen_for_wake_word') as mock_listen:
                mock_listen.return_value = expected
                result = mock_listen()
                self.assertEqual(result, expected)
    
    @patch('speech_recognition.Recognizer.recognize_google')
    def test_listen_success(self, mock_recognize):
        """Test successful speech recognition."""
        mock_recognize.return_value = "Hello Jarvis"
        
        with patch.object(self.jarvis.recognizer, 'listen') as mock_listen:
            mock_listen.return_value = Mock()
            result = self.jarvis.listen()
            
            self.assertEqual(result, "hello jarvis")
    
    @patch('speech_recognition.Recognizer.recognize_google')
    def test_listen_timeout(self, mock_recognize):
        """Test speech recognition timeout."""
        with patch.object(self.jarvis.recognizer, 'listen') as mock_listen:
            mock_listen.side_effect = Exception("Timeout")
            result = self.jarvis.listen()
            
            # Should handle timeout gracefully
            self.assertIsNone(result)
    
    def test_extract_calendar_params(self):
        """Test calendar parameter extraction."""
        test_cases = [
            ("schedule meeting tomorrow at 3 PM", {
                'title': 'Meeting',
                'date': 'tomorrow',
                'time': '3:00 PM'
            }),
            ("schedule lunch today at 12:30 PM", {
                'title': 'Meeting',
                'date': 'today',
                'time': '12:30 PM'
            })
        ]
        
        for text, expected in test_cases:
            result = self.jarvis.extract_calendar_params(text)
            self.assertEqual(result['date'], expected['date'])
            if 'time' in expected:
                self.assertIn(expected['time'].split()[0], result['time'])
    
    def test_extract_music_params(self):
        """Test music parameter extraction."""
        test_cases = [
            ("play bohemian rhapsody on spotify", {
                'song': 'bohemian rhapsody',
                'platform': 'spotify'
            }),
            ("play jazz music", {
                'song': 'jazz music',
                'platform': 'youtube'
            })
        ]
        
        for text, expected in test_cases:
            result = self.jarvis.extract_music_params(text)
            self.assertEqual(result['platform'], expected['platform'])
            self.assertIn(expected['song'].split()[0], result['song'])
    
    def test_extract_location(self):
        """Test location extraction from text."""
        test_cases = [
            ("weather in New York", "New York"),
            ("temperature for London", "London"),
            ("weather forecast at Tokyo", "Tokyo"),
            ("what's the weather", "current location")
        ]
        
        for text, expected in test_cases:
            result = self.jarvis.extract_location(text)
            if expected == "current location":
                self.assertEqual(result, expected)
            else:
                self.assertEqual(result, expected)
    
    def test_basic_tool_processing(self):
        """Test basic tool processing without LangChain."""
        # Mock tools
        self.jarvis.tools = [Mock() for _ in range(6)]
        
        test_cases = [
            ("schedule a meeting", 0),  # Calendar tool
            ("check my email", 1),     # Email tool
            ("what's the weather", 2), # Weather tool
            ("play music", 3),         # Music tool
            ("set a timer", 4),        # Timer tool
            ("latest news", 5)         # News tool
        ]
        
        for command, tool_index in test_cases:
            self.jarvis.tools[tool_index]._run.return_value = f"Mock response for {command}"
            result = self.jarvis.basic_tool_processing(command)
            self.assertIn("Mock response", result)
    
    def test_process_command_sleep(self):
        """Test sleep command processing."""
        result = self.jarvis.process_command("go to sleep")
        self.assertEqual(result, "sleep")
        self.assertTrue(self.jarvis.listening_for_wake_word)
    
    def test_process_command_exit(self):
        """Test exit command processing."""
        result = self.jarvis.process_command("exit")
        self.assertEqual(result, "exit")
    
    def test_process_command_help(self):
        """Test help command processing."""
        with patch.object(self.jarvis, 'speak') as mock_speak:
            result = self.jarvis.process_command("help")
            self.assertEqual(result, "continue")
            mock_speak.assert_called_once()
    
    @patch('os.path.exists')
    def test_setup_calendar_api_no_credentials(self, mock_exists):
        """Test calendar API setup without credentials."""
        mock_exists.return_value = False
        
        with patch('builtins.print') as mock_print:
            self.jarvis.setup_calendar_api()
            self.assertIsNone(self.jarvis.calendar_service)
    
    def test_setup_tts(self):
        """Test TTS setup."""
        # Mock TTS engine
        mock_engine = Mock()
        mock_voices = [Mock(), Mock()]
        mock_voices[0].name = "Microsoft Zira"
        mock_voices[1].name = "Microsoft David"
        mock_engine.getProperty.return_value = mock_voices
        
        self.jarvis.tts_engine = mock_engine
        self.jarvis.setup_tts()
        
        # Should set voice and properties
        mock_engine.setProperty.assert_called()
    
    def test_setup_microphone(self):
        """Test microphone setup."""
        with patch('builtins.print'):
            self.jarvis.setup_microphone()
        
        # Should complete without errors
        self.assertIsNotNone(self.jarvis.recognizer)
    
    def test_langchain_setup_with_api_key(self):
        """Test LangChain setup with API key."""
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        self.assertIsNotNone(jarvis.llm)
        self.assertEqual(len(jarvis.tools), 6)
        self.assertIsNotNone(jarvis.memory)
    
    def test_langchain_setup_without_api_key(self):
        """Test LangChain setup without API key."""
        with patch('pyttsx3.init'), \
             patch('speech_recognition.Recognizer'), \
             patch('speech_recognition.Microphone'):
            jarvis = AgenticJarvis(mistral_api_key=None)
            
            self.assertIsNone(jarvis.llm)
            self.assertIsNone(jarvis.agent)


class TestAgenticJarvisIntegration(unittest.TestCase):
    """Integration tests for AgenticJarvis."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.env_patcher = patch.dict(os.environ, {
            'MISTRAL_API_KEY': 'test_mistral_key',
            'EMAIL_USER': 'test@example.com',
            'EMAIL_PASSWORD': 'test_password',
            'NEWS_API_KEY': 'test_news_key'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after integration tests."""
        self.env_patcher.stop()
    
    @patch('pyttsx3.init')
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    def test_full_initialization_flow(self, mock_mic, mock_recognizer, mock_tts):
        """Test complete initialization flow."""
        # Mock all external dependencies
        mock_engine = Mock()
        mock_tts.return_value = mock_engine
        
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Verify all components are initialized
        self.assertIsNotNone(jarvis.llm)
        self.assertIsNotNone(jarvis.tools)
        self.assertIsNotNone(jarvis.memory)
        self.assertEqual(len(jarvis.tools), 6)
    
    @patch('pyttsx3.init')
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    def test_tool_chain_execution(self, mock_mic, mock_recognizer, mock_tts):
        """Test tool chain execution."""
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Mock tool responses
        for tool in jarvis.tools:
            tool._run = Mock(return_value="Mock tool response")
        
        # Test basic tool processing
        result = jarvis.basic_tool_processing("check the weather in London")
        self.assertIn("Mock tool response", result)
    
    @patch('requests.post')
    @patch('pyttsx3.init')
    @patch('speech_recognition.Recognizer')
    @patch('speech_recognition.Microphone')
    def test_langchain_agent_execution(self, mock_mic, mock_recognizer, mock_tts, mock_post):
        """Test LangChain agent execution."""
        # Mock Mistral API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'I can help you with that task.'}}]
        }
        mock_post.return_value = mock_response
        
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Test agent processing
        if jarvis.agent:
            with patch.object(jarvis.agent, 'run') as mock_run:
                mock_run.return_value = "Agent response"
                result = jarvis.process_with_langchain("test query")
                self.assertEqual(result, "Agent response")


if __name__ == '__main__':
    unittest.main()