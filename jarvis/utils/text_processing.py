"""
Text processing utilities for Jarvis AI Assistant.
Contains functions for parsing dates, times, and natural language.
"""

import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
import pytz


def parse_date_time(date_str: str, time_str: str, timezone=None) -> datetime:
    """Parse date and time strings into datetime object."""
    if timezone is None:
        timezone = pytz.timezone('Asia/Kolkata')
    
    # Parse date
    base_date = datetime.now(timezone)
    
    if date_str.lower() == 'today':
        target_date = base_date.date()
    elif date_str.lower() == 'tomorrow':
        target_date = (base_date + timedelta(days=1)).date()
    elif date_str.lower() == 'yesterday':
        target_date = (base_date - timedelta(days=1)).date()
    else:
        # Try to parse specific date formats
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            try:
                target_date = datetime.strptime(date_str, '%m/%d/%Y').date()
            except ValueError:
                target_date = base_date.date()
    
    # Parse time
    try:
        time_obj = datetime.strptime(time_str.upper(), '%I:%M %p').time()
    except ValueError:
        try:
            time_obj = datetime.strptime(time_str.upper(), '%I %p').time()
        except ValueError:
            try:
                time_obj = datetime.strptime(time_str, '%H:%M').time()
            except ValueError:
                time_obj = datetime.strptime('10:00 AM', '%I:%M %p').time()
    
    # Combine date and time
    combined_datetime = datetime.combine(target_date, time_obj)
    
    # Localize to timezone
    if timezone:
        combined_datetime = timezone.localize(combined_datetime)
    
    return combined_datetime


def extract_duration(text: str) -> int:
    """Extract duration in minutes from text."""
    patterns = [
        (r'(\d+)\s*(?:minutes?|mins?)', lambda x: int(x)),
        (r'(\d+)\s*(?:hours?|hrs?)', lambda x: int(x) * 60),
        (r'(\d+)\s*(?:seconds?|secs?)', lambda x: max(1, int(x) // 60)),
        (r'(\d+\.?\d*)\s*(?:hours?|hrs?)', lambda x: int(float(x) * 60)),
    ]
    
    for pattern, converter in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return converter(match.group(1))
    
    # Default duration
    return 60


def extract_email_address(text: str) -> Optional[str]:
    """Extract email address from text."""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    match = re.search(email_pattern, text)
    return match.group() if match else None


def extract_phone_number(text: str) -> Optional[str]:
    """Extract phone number from text."""
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
        r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
        r'\b\d{10}\b',  # 1234567890
        r'\b\+\d{1,3}\s*\d{10}\b',  # +1 1234567890
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group()
    
    return None


def extract_location(text: str) -> str:
    """Extract location from text."""
    location_patterns = [
        r'(?:in|at|for|near)\s+([A-Za-z\s,]+?)(?:\s+(?:today|tomorrow|weather|forecast|temperature)|$)',
        r'weather\s+(?:in|at|for|near)\s+([A-Za-z\s,]+)',
        r'(?:city|location|place):\s*([A-Za-z\s,]+)',
    ]
    
    for pattern in location_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Clean up common words
            location = re.sub(r'\b(the|weather|forecast|temperature)\b', '', location, flags=re.IGNORECASE).strip()
            if location and len(location) > 1:
                return location
    
    return "current location"


def extract_music_info(text: str) -> Dict[str, str]:
    """Extract music information from text."""
    info = {
        'song': '',
        'artist': '',
        'platform': 'youtube'
    }
    
    # Extract song name
    song_patterns = [
        r'play\s+["\'](.*?)["\']',  # play "song name"
        r'play\s+(.*?)\s+(?:by|on|from)',  # play song by artist
        r'play\s+(.*?)(?:\s*$)',  # play song
    ]
    
    for pattern in song_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['song'] = match.group(1).strip()
            break
    
    # Extract artist
    artist_patterns = [
        r'by\s+(.*?)(?:\s+on|\s*$)',  # by artist
        r'artist\s+(.*?)(?:\s+on|\s*$)',  # artist name
    ]
    
    for pattern in artist_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['artist'] = match.group(1).strip()
            break
    
    # Extract platform
    platforms = {
        'spotify': ['spotify'],
        'youtube': ['youtube', 'yt'],
        'apple': ['apple', 'apple music', 'itunes'],
        'soundcloud': ['soundcloud'],
    }
    
    text_lower = text.lower()
    for platform, keywords in platforms.items():
        if any(keyword in text_lower for keyword in keywords):
            info['platform'] = platform
            break
    
    return info


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove special characters (keep alphanumeric and basic punctuation)
    text = re.sub(r'[^\w\s\-\.,!?@]', '', text)
    
    return text


def extract_numbers(text: str) -> list:
    """Extract all numbers from text."""
    return [int(match) for match in re.findall(r'\d+', text)]


def contains_wake_word(text: str, wake_words: list) -> bool:
    """Check if text contains any of the wake words."""
    text_lower = text.lower()
    return any(wake_word in text_lower for wake_word in wake_words)


def extract_timer_duration(text: str) -> int:
    """Extract timer duration in seconds from text."""
    patterns = [
        (r'(\d+)\s*(?:hours?|hrs?)', lambda x: int(x) * 3600),
        (r'(\d+)\s*(?:minutes?|mins?)', lambda x: int(x) * 60),
        (r'(\d+)\s*(?:seconds?|secs?)', lambda x: int(x)),
        (r'(\d+\.?\d*)\s*(?:hours?|hrs?)', lambda x: int(float(x) * 3600)),
    ]
    
    for pattern, converter in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return converter(match.group(1))
    
    # Try to extract just numbers and assume minutes
    numbers = extract_numbers(text)
    if numbers:
        return numbers[0] * 60  # Default to minutes
    
    return 60  # Default 1 minute


def format_duration(seconds: int) -> str:
    """Format duration in seconds to readable string."""
    if seconds >= 3600:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        if minutes > 0:
            return f"{hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours != 1 else ''}"
    elif seconds >= 60:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes} minute{'s' if minutes != 1 else ''} {remaining_seconds} second{'s' if remaining_seconds != 1 else ''}"
        else:
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        return f"{seconds} second{'s' if seconds != 1 else ''}"


def extract_calendar_event_info(text: str) -> Dict[str, str]:
    """Extract calendar event information from text."""
    info = {
        'title': 'Meeting',
        'date': 'today',
        'time': '10:00 AM',
        'duration': '60',
        'description': ''
    }
    
    # Extract title (before time/date keywords)
    title_stopwords = ['schedule', 'set', 'book', 'create', 'add']
    title_indicators = ['at', 'on', 'for', 'tomorrow', 'today']
    
    # Find the main content for title
    title_text = text
    for stopword in title_stopwords:
        title_text = re.sub(f'\\b{stopword}\\b', '', title_text, flags=re.IGNORECASE).strip()
    
    # Extract everything before time/date indicators
    for indicator in title_indicators:
        if indicator in title_text.lower():
            title_text = title_text.lower().split(indicator)[0].strip()
            break
    
    if title_text and len(title_text.strip()) > 0:
        info['title'] = title_text.strip().title()
    
    # Extract date
    if 'tomorrow' in text.lower():
        info['date'] = 'tomorrow'
    elif 'today' in text.lower():
        info['date'] = 'today'
    elif 'next week' in text.lower():
        info['date'] = 'next week'
    
    # Extract time
    time_patterns = [
        r'(\d{1,2}:\d{2}\s*(?:am|pm))',
        r'(\d{1,2}\s*(?:am|pm))',
        r'at\s+(\d{1,2}(?::\d{2})?)',
    ]
    
    for pattern in time_patterns:
        match = re.search(pattern, text.lower())
        if match:
            info['time'] = match.group(1).strip()
            break
    
    # Extract duration
    duration_match = re.search(r'for\s+(\d+)\s*(minute|hour)', text.lower())
    if duration_match:
        duration_value = int(duration_match.group(1))
        unit = duration_match.group(2)
        if unit == 'hour':
            info['duration'] = str(duration_value * 60)
        else:
            info['duration'] = str(duration_value)
    
    return info


def is_question(text: str) -> bool:
    """Check if text is a question."""
    question_words = ['what', 'when', 'where', 'who', 'why', 'how', 'is', 'are', 'can', 'could', 'would', 'should']
    text_lower = text.lower().strip()
    
    # Ends with question mark
    if text_lower.endswith('?'):
        return True
    
    # Starts with question word
    for word in question_words:
        if text_lower.startswith(word + ' '):
            return True
    
    return False


def extract_news_category(text: str) -> str:
    """Extract news category from text."""
    categories = {
        'technology': ['tech', 'technology', 'computer', 'software', 'ai', 'artificial intelligence'],
        'business': ['business', 'finance', 'economy', 'market', 'stock'],
        'sports': ['sports', 'football', 'basketball', 'soccer', 'baseball', 'tennis'],
        'health': ['health', 'medical', 'medicine', 'wellness', 'fitness'],
        'entertainment': ['entertainment', 'movie', 'music', 'celebrity', 'hollywood'],
        'science': ['science', 'research', 'study', 'discovery', 'space'],
        'politics': ['politics', 'political', 'government', 'election', 'policy']
    }
    
    text_lower = text.lower()
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    return 'general'


def parse_command_intent(text: str) -> Dict[str, any]:
    """Parse user input to determine intent and extract parameters."""
    text_lower = text.lower().strip()
    
    intent_patterns = {
        'calendar': {
            'keywords': ['schedule', 'meeting', 'appointment', 'calendar', 'book', 'plan'],
            'action': 'calendar'
        },
        'email': {
            'keywords': ['email', 'mail', 'message', 'send', 'inbox'],
            'action': 'email'
        },
        'weather': {
            'keywords': ['weather', 'temperature', 'forecast', 'climate'],
            'action': 'weather'
        },
        'music': {
            'keywords': ['play', 'music', 'song', 'audio', 'listen'],
            'action': 'music'
        },
        'timer': {
            'keywords': ['timer', 'alarm', 'countdown', 'remind'],
            'action': 'timer'
        },
        'news': {
            'keywords': ['news', 'headlines', 'current events', 'latest'],
            'action': 'news'
        },
        'question': {
            'keywords': ['what', 'how', 'why', 'when', 'where', 'who'],
            'action': 'question'
        }
    }
    
    result = {
        'intent': 'unknown',
        'action': 'general',
        'confidence': 0.0,
        'parameters': {}
    }
    
    # Check each intent pattern
    max_matches = 0
    for intent, config in intent_patterns.items():
        matches = sum(1 for keyword in config['keywords'] if keyword in text_lower)
        if matches > max_matches:
            max_matches = matches
            result['intent'] = intent
            result['action'] = config['action']
            result['confidence'] = matches / len(config['keywords'])
    
    # Extract specific parameters based on intent
    if result['intent'] == 'calendar':
        result['parameters'] = extract_calendar_event_info(text)
    elif result['intent'] == 'music':
        result['parameters'] = extract_music_info(text)
    elif result['intent'] == 'weather':
        result['parameters'] = {'location': extract_location(text)}
    elif result['intent'] == 'timer':
        result['parameters'] = {'duration': extract_timer_duration(text)}
    elif result['intent'] == 'news':
        result['parameters'] = {'category': extract_news_category(text)}
    elif result['intent'] == 'email':
        result['parameters'] = {
            'email_address': extract_email_address(text),
            'action': 'send' if any(word in text_lower for word in ['send', 'write', 'compose']) else 'check'
        }
    
    return result