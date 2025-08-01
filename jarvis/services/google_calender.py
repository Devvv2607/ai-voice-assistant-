"""
Google Calendar service for Jarvis AI Assistant.
Handles Google Calendar API operations and authentication.
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pytz

from ..core.config import config


class GoogleCalendarService:
    """Service class for Google Calendar operations."""
    
    def __init__(self):
        """Initialize Google Calendar service."""
        self.service = None
        self.setup_calendar_api()
    
    def setup_calendar_api(self):
        """Setup Google Calendar API authentication."""
        try:
            calendar_config = config.calendar_config
            credentials_file = calendar_config['credentials_file']
            token_file = calendar_config['token_file']
            scopes = calendar_config['scopes']
            
            creds = None
            
            # Load existing token
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        print(f"Token refresh failed: {e}")
                        creds = None
                
                if not creds:
                    if os.path.exists(credentials_file):
                        flow = InstalledAppFlow.from_client_secrets_file(
                            credentials_file, scopes
                        )
                        creds = flow.run_local_server(port=0)
                    else:
                        print(f"⚠️  Google Calendar: {credentials_file} not found")
                        return
                
                # Save credentials for next run
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build service
            self.service = build('calendar', 'v3', credentials=creds)
            print("✅ Google Calendar: Ready")
            
        except Exception as e:
            print(f"❌ Calendar API setup error: {e}")
            self.service = None
    
    def is_configured(self) -> bool:
        """Check if Google Calendar is properly configured."""
        return self.service is not None
    
    def create_event(self, event_data: Dict) -> Optional[Dict]:
        """Create a new calendar event."""
        if not self.service:
            return None
        
        try:
            event = self.service.events().insert(
                calendarId='primary', 
                body=event_data
            ).execute()
            return event
        except Exception as e:
            print(f"Error creating event: {e}")
            return None
    
    def get_upcoming_events(self, max_results: int = 10) -> List[Dict]:
        """Get upcoming calendar events."""
        if not self.service:
            return []
        
        try:
            # Get current time in UTC
            now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            
            # Get events
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []
    
    def update_event(self, event_id: str, event_data: Dict) -> Optional[Dict]:
        """Update an existing calendar event."""
        if not self.service:
            return None
        
        try:
            event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event_data
            ).execute()
            return event
        except Exception as e:
            print(f"Error updating event: {e}")
            return None
    
    def delete_event(self, event_id: str) -> bool:
        """Delete a calendar event."""
        if not self.service:
            return False
        
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False
    
    def search_events(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for events by query."""
        if not self.service:
            return []
        
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                q=query,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except Exception as e:
            print(f"Error searching events: {e}")
            return []
    
    def get_calendar_info(self) -> Optional[Dict]:
        """Get primary calendar information."""
        if not self.service:
            return None
        
        try:
            calendar = self.service.calendars().get(calendarId='primary').execute()
            return calendar
        except Exception as e:
            print(f"Error getting calendar info: {e}")
            return None