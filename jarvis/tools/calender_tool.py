"""
Calendar tool for LangChain integration.
Handles Google Calendar operations and scheduling.
"""

import json
from datetime import datetime, timedelta
import pytz
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun

from ..services.google_calender import GoogleCalendarService
from ..utils.text_processing import parse_date_time


class CalendarTool(BaseTool):
    """LangChain tool for calendar operations."""
    
    name = "calendar_scheduler"
    description = "Schedule calendar events, check calendar, or manage appointments. Input should be JSON with title, date, and time, or 'check' to view upcoming events."
    
    def __init__(self):
        """Initialize calendar tool with Google Calendar service."""
        super().__init__()
        self.calendar_service = GoogleCalendarService()
        self.ist = pytz.timezone('Asia/Kolkata')
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute calendar operations."""
        try:
            # Handle different types of queries
            if query.lower().strip() in ['check', 'show', 'list', 'upcoming']:
                return self._get_upcoming_events()
            elif query.startswith('{'):
                # JSON input for scheduling
                params = json.loads(query)
                return self._schedule_event(params)
            else:
                # Natural language input - parse and schedule
                params = self._parse_natural_language(query)
                return self._schedule_event(params)
                
        except Exception as e:
            return f"Calendar operation failed: {str(e)}"
    
    def _schedule_event(self, params: dict) -> str:
        """Schedule a calendar event."""
        if not self.calendar_service.is_configured():
            return "Google Calendar is not configured. Please set up credentials.json"
        
        try:
            title = params.get('title', 'New Event')
            date_str = params.get('date', 'today')
            time_str = params.get('time', '10:00 AM')
            duration = params.get('duration', 60)  # minutes
            description = params.get('description', 'Event created by Jarvis AI Assistant')
            
            # Parse date and time
            start_datetime = parse_date_time(date_str, time_str, self.ist)
            end_datetime = start_datetime + timedelta(minutes=duration)
            
            # Create event
            event = {
                'summary': title,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': 'Asia/Kolkata',
                },
                'description': description,
            }
            
            # Add to calendar
            created_event = self.calendar_service.create_event(event)
            
            if created_event:
                formatted_time = start_datetime.strftime('%B %d at %I:%M %p')
                return f"✅ Successfully scheduled '{title}' for {formatted_time}"
            else:
                return "❌ Failed to create calendar event"
                
        except Exception as e:
            return f"Error scheduling event: {str(e)}"
    
    def _get_upcoming_events(self, max_results: int = 5) -> str:
        """Get upcoming calendar events."""
        if not self.calendar_service.is_configured():
            return "Google Calendar is not configured."
        
        try:
            events = self.calendar_service.get_upcoming_events(max_results)
            
            if not events:
                return "📅 No upcoming events found."
            
            event_list = ["📅 Upcoming Events:"]
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary = event.get('summary', 'No title')
                
                # Parse and format datetime
                try:
                    if 'T' in start:  # DateTime format
                        dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                        formatted_time = dt.strftime('%b %d, %I:%M %p')
                    else:  # Date only format
                        dt = datetime.fromisoformat(start)
                        formatted_time = dt.strftime('%b %d (All day)')
                    
                    event_list.append(f"• {summary} - {formatted_time}")
                except:
                    event_list.append(f"• {summary} - {start}")
            
            return "\n".join(event_list)
            
        except Exception as e:
            return f"Error fetching events: {str(e)}"
    
    def _parse_natural_language(self, text: str) -> dict:
        """Parse natural language input into event parameters."""
        params = {
            'title': 'Meeting',
            'date': 'today',
            'time': '10:00 AM',
            'duration': 60
        }
        
        # Extract title (everything before time/date references)
        title_match = text.split(' at ')[0].split(' on ')[0].split(' tomorrow')[0].split(' today')[0]
        if title_match and not any(word in title_match.lower() for word in ['schedule', 'set', 'book']):
            params['title'] = title_match.strip()
        
        # Extract date
        if 'tomorrow' in text.lower():
            params['date'] = 'tomorrow'
        elif 'today' in text.lower():
            params['date'] = 'today'
        
        # Extract time
        import re
        time_patterns = [
            r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))',
            r'at\s+(\d{1,2}(?::\d{2})?)',
            r'(\d{1,2})\s*(?:o\'?clock)'
        ]
        
        for pattern in time_patterns:
            time_match = re.search(pattern, text.lower())
            if time_match:
                params['time'] = time_match.group(1)
                break
        
        # Extract duration
        duration_match = re.search(r'for\s+(\d+)\s*(?:minute|hour)', text.lower())
        if duration_match:
            duration_value = int(duration_match.group(1))
            if 'hour' in duration_match.group(0):
                params['duration'] = duration_value * 60
            else:
                params['duration'] = duration_value
        
        return params