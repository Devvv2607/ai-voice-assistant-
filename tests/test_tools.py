"""
Tests for LangChain tools implementation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import pytest
import json
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis import CalendarTool, EmailTool, WeatherTool, MusicTool, TimerTool, NewsTool


class TestCalendarTool(unittest.TestCase):
    """Test cases for CalendarTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_calendar_service = Mock()
        self.calendar_tool = CalendarTool(self.mock_calendar_service)
    
    def test_tool_initialization(self):
        """Test CalendarTool initialization."""
        self.assertEqual(self.calendar_tool.name, "calendar_scheduler")
        self.assertIsNotNone(self.calendar_tool.description)
        self.assertEqual(self.calendar_tool.calendar_service, self.mock_calendar_service)
    
    def test_schedule_event_success(self):
        """Test successful event scheduling."""
        # Mock successful calendar event creation
        mock_event = {'id': 'test_event_id', 'summary': 'Test Meeting'}
        self.mock_calendar_service.events().insert().execute.return_value = mock_event
        
        query = json.dumps({
            'title': 'Test Meeting',
            'date': 'today',
            'time': '2:00 PM'
        })
        
        result = self.calendar_tool._run(query)
        
        self.assertIn("Successfully scheduled", result)
        self.assertIn("Test Meeting", result)
    
    def test_schedule_event_no_calendar_service(self):
        """Test event scheduling without calendar service."""
        tool = CalendarTool(None)
        
        result = tool._run("Test meeting")
        
        self.assertEqual(result, "Google Calendar is not configured.")
    
    def test_schedule_event_invalid_json(self):
        """Test event scheduling with invalid JSON."""
        result = self.calendar_tool._run("Just a plain text query")
        
        # Should handle non-JSON input gracefully
        self.assertIn("Successfully scheduled", result)


class TestEmailTool(unittest.TestCase):
    """Test cases for EmailTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.email_config = {
            'user': 'test@example.com',
            'password': 'test_password',
            'imap_server': 'imap.gmail.com',
            'smtp_server': 'smtp.gmail.com'
        }
        self.email_tool = EmailTool(self.email_config)
    
    def test_tool_initialization(self):
        """Test EmailTool initialization."""
        self.assertEqual(self.email_tool.name, "email_manager")
        self.assertEqual(self.email_tool.email_user, 'test@example.com')
        self.assertEqual(self.email_tool.email_password, 'test_password')
    
    def test_email_not_configured(self):
        """Test email tool without configuration."""
        tool = EmailTool({})
        
        result = tool._run("check")
        
        self.assertEqual(result, "Email is not configured.")
    
    @patch('imaplib.IMAP4_SSL')
    def test_check_emails_success(self, mock_imap):
        """Test successful email checking."""
        # Mock IMAP response
        mock_mail = Mock()
        mock_mail.search.return_value = (None, [b'1 2 3'])
        mock_mail.fetch.return_value = (None, [(None, b'test email content')])
        mock_imap.return_value = mock_mail
        
        with patch('email.message_from_bytes') as mock_email:
            mock_msg = Mock()
            mock_msg.__getitem__.side_effect = lambda x: f'Mock {x}'
            mock_email.return_value = mock_msg
            
            result = self.email_tool._run("check")
            
            self.assertIn("Latest emails", result)
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending."""
        # Mock SMTP
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        query = json.dumps({
            'to': 'recipient@example.com',
            'subject': 'Test Subject',
            'body': 'Test Body'
        })
        
        result = self.email_tool._run(query)
        
        self.assertIn("Email sent successfully", result)
        self.assertIn("recipient@example.com", result)


class TestWeatherTool(unittest.TestCase):
    """Test cases for WeatherTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.weather_tool = WeatherTool()
    
    def test_tool_initialization(self):
        """Test WeatherTool initialization."""
        self.assertEqual(self.weather_tool.name, "weather_checker")
        self.assertIsNotNone(self.weather_tool.description)
    
    @patch('requests.get')
    def test_get_weather_success(self, mock_get):
        """Test successful weather retrieval."""
        # Mock weather API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'current_condition': [{
                'temp_C': '25',
                'temp_F': '77',
                'weatherDesc': [{'value': 'Partly cloudy'}],
                'humidity': '60',
                'FeelsLikeC': '26',
                'windspeedKmph': '10'
            }]
        }
        mock_get.return_value = mock_response
        
        result = self.weather_tool._run("London")
        
        self.assertIn("Weather in London", result)
        self.assertIn("25°C", result)
        self.assertIn("Partly cloudy", result)
    
    @patch('requests.get')
    def test_get_weather_failure(self, mock_get):
        """Test weather retrieval failure."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        result = self.weather_tool._run("InvalidLocation")
        
        self.assertIn("Could not get weather", result)


class TestMusicTool(unittest.TestCase):
    """Test cases for MusicTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.music_tool = MusicTool()
    
    def test_tool_initialization(self):
        """Test MusicTool initialization."""
        self.assertEqual(self.music_tool.name, "music_player")
        self.assertIsNotNone(self.music_tool.description)
    
    @patch('webbrowser.open')
    def test_play_music_json_input(self, mock_browser):
        """Test playing music with JSON input."""
        query = json.dumps({
            'song': 'Bohemian Rhapsody',
            'platform': 'spotify'
        })
        
        result = self.music_tool._run(query)
        
        self.assertIn("Opening 'Bohemian Rhapsody' on Spotify", result)
        mock_browser.assert_called_once()
    
    @patch('webbrowser.open')
    def test_play_music_text_input(self, mock_browser):
        """Test playing music with plain text input."""
        result = self.music_tool._run("Hotel California")
        
        self.assertIn("Opening 'Hotel California' on Youtube", result)
        mock_browser.assert_called_once()


class TestTimerTool(unittest.TestCase):
    """Test cases for TimerTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.timer_tool = TimerTool()
    
    def test_tool_initialization(self):
        """Test TimerTool initialization."""
        self.assertEqual(self.timer_tool.name, "timer_manager")
        self.assertIsNotNone(self.timer_tool.description)
        self.assertEqual(len(self.timer_tool.active_timers), 0)
    
    def test_parse_duration_minutes(self):
        """Test duration parsing for minutes."""
        duration = self.timer_tool._parse_duration("5 minutes")
        self.assertEqual(duration, 300)  # 5 * 60
    
    def test_parse_duration_seconds(self):
        """Test duration parsing for seconds."""
        duration = self.timer_tool._parse_duration("30 seconds")
        self.assertEqual(duration, 30)
    
    def test_parse_duration_hours(self):
        """Test duration parsing for hours."""
        duration = self.timer_tool._parse_duration("2 hours")
        self.assertEqual(duration, 7200)  # 2 * 3600
    
    def test_parse_duration_default(self):
        """Test duration parsing with default."""
        duration = self.timer_tool._parse_duration("invalid input")
        self.assertEqual(duration, 60)  # Default 1 minute
    
    def test_format_duration(self):
        """Test duration formatting."""
        # Test seconds
        formatted = self.timer_tool._format_duration(30)
        self.assertEqual(formatted, "30 seconds")
        
        # Test minutes
        formatted = self.timer_tool._format_duration(300)
        self.assertEqual(formatted, "5 minutes")
        
        # Test hours
        formatted = self.timer_tool._format_duration(7200)
        self.assertEqual(formatted, "2 hours")
    
    @patch('time.sleep')
    def test_set_timer(self, mock_sleep):
        """Test timer setting."""
        result = self.timer_tool._run("5 minutes")
        
        self.assertIn("Timer set for 5 minutes", result)
        self.assertEqual(len(self.timer_tool.active_timers), 1)


class TestNewsTool(unittest.TestCase):
    """Test cases for NewsTool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.news_tool = NewsTool()
        self.news_tool_with_api = NewsTool("test_api_key")
    
    def test_tool_initialization(self):
        """Test NewsTool initialization."""
        self.assertEqual(self.news_tool.name, "news_fetcher")
        self.assertIsNotNone(self.news_tool.description)
        self.assertIsNone(self.news_tool.news_api_key)
        self.assertEqual(self.news_tool_with_api.news_api_key, "test_api_key")
    
    @patch('requests.get')
    def test_get_news_api_success(self, mock_get):
        """Test successful news retrieval with API."""
        # Mock NewsAPI response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'articles': [
                {
                    'title': 'Test News 1',
                    'description': 'Test description 1'
                },
                {
                    'title': 'Test News 2',
                    'description': 'Test description 2'
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.news_tool_with_api._run("technology")
        
        self.assertIn("Latest headlines", result)
        self.assertIn("Test News 1", result)
    
    @patch('requests.get')
    def test_get_free_news_success(self, mock_get):
        """Test successful free news retrieval."""
        # Mock RSS response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = '''<?xml version="1.0"?>
        <rss>
            <channel>
                <item>
                    <title>Free News 1</title>
                </item>
                <item>
                    <title>Free News 2</title>
                </item>
            </channel>
        </rss>'''.encode()
        mock_get.return_value = mock_response
        
        result = self.news_tool._run("general")
        
        self.assertIn("Latest headlines", result)


if __name__ == '__main__':
    unittest.main()