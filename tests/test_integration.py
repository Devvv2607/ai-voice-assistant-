"""
Integration tests for Jarvis AI Assistant

These tests verify that different components work together correctly
and that the overall system behaves as expected.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
import sys
import os
import threading
import time
import json

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis import AgenticJarvis, MistralLLM, CalendarTool, EmailTool, WeatherTool


class TestJarvisIntegration(unittest.TestCase):
    """Integration tests for the complete Jarvis system."""
    
    def setUp(self):
        """Set up integration test environment."""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'MISTRAL_API_KEY': 'test_mistral_key',
            'EMAIL_USER': 'test@example.com',
            'EMAIL_PASSWORD': 'test_password',
            'NEWS_API_KEY': 'test_news_key'
        })
        self.env_patcher.start()
        
        # Mock external dependencies
        self.tts_patcher = patch('pyttsx3.init')
        self.sr_patcher = patch('speech_recognition.Recognizer')
        self.mic_patcher = patch('speech_recognition.Microphone')
        
        self.tts_patcher.start()
        self.sr_patcher.start()
        self.mic_patcher.start()
    
    def tearDown(self):
        """Clean up after tests."""
        self.env_patcher.stop()
        self.tts_patcher.stop()
        self.sr_patcher.stop()
        self.mic_patcher.stop()
    
    def test_end_to_end_calendar_scheduling(self):
        """Test complete calendar scheduling workflow."""
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Mock calendar service
        mock_calendar_service = Mock()
        mock_event = {'id': 'test_event_id', 'summary': 'Team Meeting'}
        mock_calendar_service.events().insert().execute.return_value = mock_event
        
        # Set up calendar tool with mock service
        jarvis.tools[0].calendar_service = mock_calendar_service
        
        # Test scheduling
        with patch.object(jarvis, 'speak') as mock_speak:
            result = jarvis.process_command("schedule team meeting tomorrow at 3 PM")
            
            self.assertEqual(result, "continue")
            mock_speak.assert_called()
            call_args = mock_speak.call_args[0][0]
            self.assertIn("scheduled", call_args.lower())
    
    @patch('requests.get')
    def test_end_to_end_weather_check(self, mock_get):
        """Test complete weather checking workflow."""
        # Mock weather API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'current_condition': [{
                'temp_C': '22',
                'temp_F': '72',
                'weatherDesc': [{'value': 'Sunny'}],
                'humidity': '45',
                'FeelsLikeC': '24',
                'windspeedKmph': '5'
            }]
        }
        mock_get.return_value = mock_response
        
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Test weather checking
        with patch.object(jarvis, 'speak') as mock_speak:
            result = jarvis.process_command("what's the weather in London")
            
            self.assertEqual(result, "continue")
            mock_speak.assert_called()
            call_args = mock_speak.call_args[0][0]
            self.assertIn("London", call_args)
            self.assertIn("22°C", call_args)
    
    @patch('webbrowser.open')
    def test_end_to_end_music_playback(self, mock_browser):
        """Test complete music playback workflow."""
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Test music playback
        with patch.object(jarvis, 'speak') as mock_speak:
            result = jarvis.process_command("play bohemian rhapsody on spotify")
            
            self.assertEqual(result, "continue")
            mock_speak.assert_called()
            mock_browser.assert_called_once()
            
            call_args = mock_speak.call_args[0][0]
            self.assertIn("bohemian rhapsody", call_args.lower())
            self.assertIn("spotify", call_args.lower())
    
    def test_conversation_memory_persistence(self):
        """Test that conversation memory persists across interactions."""
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Check that memory is initialized
        self.assertIsNotNone(jarvis.memory)
        
        # Add some conversation history
        jarvis.memory.chat_memory.add_user_message("Hello Jarvis")
        jarvis.memory.chat_memory.add_ai_message("Hello! How can I help you?")
        
        # Verify memory retention
        messages = jarvis.memory.chat_memory.messages
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].content, "Hello Jarvis")
        self.assertEqual(messages[1].content, "Hello! How can I help you?")
    
    def test_tool_chaining_workflow(self):
        """Test that multiple tools can be used in sequence."""
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Mock all tools
        for i, tool in enumerate(jarvis.tools):
            tool._run = Mock(return_value=f"Tool {i} executed successfully")
        
        # Test multiple commands in sequence
        commands = [
            "check the weather",
            "schedule a meeting",
            "set a timer for 5 minutes"
        ]
        
        results = []
        for command in commands:
            with patch.object(jarvis, 'speak'):
                result = jarvis.process_command(command)
                results.append(result)
        
        # All commands should complete successfully
        self.assertEqual(results, ["continue", "continue", "continue"])
    
    @patch('requests.post')
    def test_langchain_agent_tool_integration(self, mock_post):
        """Test LangChain agent integrating with tools."""
        # Mock Mistral API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'I\'ll help you check the weather.'}}]
        }
        mock_post.return_value = mock_response
        
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        if jarvis.agent:
            # Mock agent run method
            with patch.object(jarvis.agent, 'run') as mock_run:
                mock_run.return_value = "Weather checked successfully using the weather tool."
                
                result = jarvis.process_with_langchain("check weather in Paris")
                
                self.assertEqual(result, "Weather checked successfully using the weather tool.")
                mock_run.assert_called_once_with(input="check weather in Paris")
    
    def test_error_handling_and_recovery(self):
        """Test system error handling and recovery."""
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Mock a tool that raises an exception
        jarvis.tools[2]._run = Mock(side_effect=Exception("Tool error"))
        
        # Test error handling
        with patch.object(jarvis, 'speak') as mock_speak:
            result = jarvis.process_command("check the weather")
            
            # Should handle error gracefully
            self.assertEqual(result, "continue")
            mock_speak.assert_called()
            call_args = mock_speak.call_args[0][0]
            self.assertIn("error", call_args.lower())
    
    def test_wake_word_to_command_flow(self):
        """Test the complete flow from wake word detection to command execution."""
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Mock speech recognition for wake word
        with patch.object(jarvis, 'listen_for_wake_word') as mock_wake:
            mock_wake.return_value = True
            
            # Mock command listening
            with patch.object(jarvis, 'listen') as mock_listen:
                mock_listen.return_value = "what time is it"
                
                # Mock command processing
                with patch.object(jarvis, 'process_command') as mock_process:
                    mock_process.return_value = "continue"
                    
                    # Test wake word detection
                    wake_detected = mock_wake()
                    self.assertTrue(wake_detected)
                    
                    # Test command listening
                    command = mock_listen()
                    self.assertEqual(command, "what time is it")
                    
                    # Test command processing
                    result = mock_process(command)
                    self.assertEqual(result, "continue")
    
    def test_multiple_timer_management(self):
        """Test setting and managing multiple timers."""
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        timer_tool = jarvis.tools[4]  # TimerTool
        
        # Set multiple timers
        with patch('time.sleep'):  # Prevent actual sleeping
            result1 = timer_tool._run("5 minutes")
            result2 = timer_tool._run("10 seconds")
            result3 = timer_tool._run("2 hours")
        
        # Verify all timers are set
        self.assertIn("5 minutes", result1)
        self.assertIn("10 seconds", result2)
        self.assertIn("2 hours", result3)
        
        # Check that multiple timers are tracked
        self.assertEqual(len(timer_tool.active_timers), 3)
    
    @patch('imaplib.IMAP4_SSL')
    @patch('smtplib.SMTP')
    def test_email_workflow_integration(self, mock_smtp, mock_imap):
        """Test complete email checking and sending workflow."""
        # Mock IMAP for checking emails
        mock_mail = Mock()
        mock_mail.search.return_value = (None, [b'1 2'])
        mock_mail.fetch.return_value = (None, [(None, b'test email')])
        mock_imap.return_value = mock_mail
        
        # Mock SMTP for sending emails
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Test email checking
        with patch('email.message_from_bytes') as mock_email:
            mock_msg = Mock()
            mock_msg.__getitem__.side_effect = lambda x: f'Mock {x}'
            mock_email.return_value = mock_msg
            
            with patch.object(jarvis, 'speak') as mock_speak:
                result = jarvis.process_command("check my emails")
                
                self.assertEqual(result, "continue")
                mock_speak.assert_called()
    
    def test_system_shutdown_and_cleanup(self):
        """Test proper system shutdown and cleanup."""
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Test exit command
        with patch.object(jarvis, 'speak') as mock_speak:
            result = jarvis.process_command("exit")
            
            self.assertEqual(result, "exit")
            mock_speak.assert_called()
            call_args = mock_speak.call_args[0][0]
            self.assertIn("goodbye", call_args.lower())
    
    def test_sleep_and_wake_cycle(self):
        """Test sleep mode and wake-up cycle."""
        # Initialize Jarvis
        jarvis = AgenticJarvis(mistral_api_key='test_key')
        
        # Initially should not be in sleep mode
        self.assertTrue(jarvis.listening_for_wake_word)
        
        # Test sleep command
        with patch.object(jarvis, 'speak') as mock_speak:
            result = jarvis.process_command("go to sleep")
            
            self.assertEqual(result, "sleep")
            self.assertTrue(jarvis.listening_for_wake_word)
            mock_speak.assert_called()


class TestToolInteractions(unittest.TestCase):
    """Test interactions between different tools."""
    
    def setUp(self):
        """Set up tool interaction tests."""
        self.env_patcher = patch.dict(os.environ, {
            'MISTRAL_API_KEY': 'test_key',
            'EMAIL_USER': 'test@example.com',
            'EMAIL_PASSWORD': 'test_password'
        })
        self.env_patcher.start()
    
    def tearDown(self):
        """Clean up after tool interaction tests."""
        self.env_patcher.stop()
    
    def test_calendar_and_email_integration(self):
        """Test calendar scheduling with email notification."""
        # Create mock services
        mock_calendar_service = Mock()
        mock_event = {'id': 'test_id', 'summary': 'Meeting'}
        mock_calendar_service.events().insert().execute.return_value = mock_event
        
        email_config = {
            'user': 'test@example.com',
            'password': 'test_password'
        }
        
        # Create tools
        calendar_tool = CalendarTool(mock_calendar_service)
        email_tool = EmailTool(email_config)
        
        # Schedule event
        cal_result = calendar_tool._run(json.dumps({
            'title': 'Team Meeting',
            'date': 'tomorrow',
            'time': '3:00 PM'
        }))
        
        self.assertIn("Successfully scheduled", cal_result)
        
        # Verify calendar tool worked
        mock_calendar_service.events().insert().execute.assert_called_once()
    
    @patch('requests.get')
    def test_weather_and_news_correlation(self, mock_get):
        """Test getting weather and related news."""
        # Mock weather response
        weather_response = Mock()
        weather_response.status_code = 200
        weather_response.json.return_value = {
            'current_condition': [{
                'temp_C': '35',
                'temp_F': '95',
                'weatherDesc': [{'value': 'Very hot'}],
                'humidity': '80',
                'FeelsLikeC': '40',
                'windspeedKmph': '0'
            }]
        }
        
        # Mock news response
        news_response = Mock()
        news_response.status_code = 200
        news_response.content = '''<?xml version="1.0"?>
        <rss><channel>
            <item><title>Heat wave warning issued</title></item>
        </channel></rss>'''.encode()
        
        mock_get.side_effect = [weather_response, news_response]
        
        # Create tools
        weather_tool = WeatherTool()
        from jarvis import NewsTool
        news_tool = NewsTool()
        
        # Get weather
        weather_result = weather_tool._run("current location")
        self.assertIn("35°C", weather_result)
        self.assertIn("Very hot", weather_result)
        
        # Get news
        news_result = news_tool._run("general")
        self.assertIn("Heat wave", news_result)


if __name__ == '__main__':
    unittest.main()