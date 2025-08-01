"""
Constants and configuration values for Jarvis AI Assistant.
"""

# Wake words for voice activation
WAKE_WORDS = [
    'hey jarvis',
    'jarvis',
    'hey davis',
    'davis'
]

# Supported music platforms
SUPPORTED_PLATFORMS = {
    'SPOTIFY': 'https://open.spotify.com/search/{query}',
    'YOUTUBE': 'https://www.youtube.com/results?search_query={query}',
    'APPLE_MUSIC': 'https://music.apple.com/search?term={query}'
}

# Default application settings
DEFAULT_SETTINGS = {
    'speech': {
        'rate': 180,
        'volume': 0.9,
        'voice_preference': 'female',
        'timeout': 8,
        'phrase_time_limit': 12,
        'calibration_duration': 2
    },
    'assistant': {
        'max_iterations': 3,
        'memory_window': 10,
        'listening_for_wake_word': True
    },
    'requests': {
        'timeout': 10,
        'max_retries': 3,
        'backoff_factor': 0.3
    },
    'news': {
        'articles_per_request': 3,
        'default_country': 'us'
    },
    'calendar': {
        'default_duration_hours': 1,
        'timezone': 'Asia/Kolkata'
    }
}

# API endpoints
API_ENDPOINTS = {
    'MISTRAL': 'https://api.mistral.ai/v1/chat/completions',
    'NEWS_API': 'https://newsapi.org/v2/top-headlines',
    'WEATHER': 'http://wttr.in/{location}?format=j1'
}

# File paths
FILE_PATHS = {
    'GOOGLE_CREDENTIALS': 'credentials.json',
    'GOOGLE_TOKEN': 'token.pickle',
    'ENV_FILE': '.env',
    'LOG_FILE': 'jarvis.log'
}

# Error messages
ERROR_MESSAGES = {
    'SPEECH_RECOGNITION_FAILED': "I couldn't understand that. Could you please repeat?",
    'SPEECH_TIMEOUT': "I didn't hear anything. Please try again.",
    'SPEECH_SERVICE_ERROR': "There's an issue with speech recognition service.",
    'NETWORK_ERROR': "I'm having trouble connecting to the internet.",
    'CONFIG_MISSING': "Configuration is missing or invalid.",
    'SERVICE_UNAVAILABLE': "The requested service is currently unavailable.",
    'PERMISSION_DENIED': "I don't have permission to perform that action.",
    'INVALID_INPUT': "The input provided is not valid.",
    'UNKNOWN_ERROR': "An unexpected error occurred. Please try again."
}

# Success messages
SUCCESS_MESSAGES = {
    'TASK_COMPLETED': "Task completed successfully!",
    'EMAIL_SENT': "Email sent successfully.",
    'CALENDAR_EVENT_CREATED': "Calendar event created successfully.",
    'TIMER_SET': "Timer set successfully.",
    'MUSIC_PLAYING': "Music is now playing.",
    'WEATHER_FETCHED': "Weather information retrieved.",
    'NEWS_FETCHED': "Latest news retrieved."
}

# Command categories for help system
COMMAND_CATEGORIES = {
    'calendar': [
        'schedule meeting',
        'create appointment',
        'add calendar event',
        'set reminder',
        'check calendar'
    ],
    'email': [
        'check emails',
        'send email',
        'read messages',
        'compose email'
    ],
    'weather': [
        'weather forecast',
        'temperature',
        'weather update',
        'check weather'
    ],
    'music': [
        'play music',
        'play song',
        'search music',
        'open spotify',
        'youtube music'
    ],
    'timer': [
        'set timer',
        'countdown',
        'remind me',
        'alarm'
    ],
    'news': [
        'latest news',
        'headlines',
        'tech news',
        'business news',
        'sports news'
    ],
    'control': [
        'help',
        'sleep',
        'standby',
        'exit',
        'quit',
        'what can you do'
    ]
}

# Regex patterns for text processing
REGEX_PATTERNS = {
    'TIME_12H': r'(\d{1,2}(?::\d{2})?\s*(?:am|pm))',
    'TIME_24H': r'(\d{1,2}:\d{2})',
    'DURATION': r'(\d+)\s*(?:minutes?|mins?|hours?|hrs?|seconds?|secs?)',
    'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'URL': r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
    'PHONE': r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
    'DATE': r'\b(?:today|tomorrow|yesterday|\d{1,2}[-/]\d{1,2}(?:[-/]\d{2,4})?)\b'
}

# Timezone mappings
TIMEZONE_MAPPINGS = {
    'IST': 'Asia/Kolkata',
    'EST': 'America/New_York',
    'PST': 'America/Los_Angeles',
    'GMT': 'GMT',
    'UTC': 'UTC',
    'CST': 'America/Chicago',
    'MST': 'America/Denver'
}

# News categories
NEWS_CATEGORIES = [
    'general',
    'business',
    'entertainment',
    'health',
    'science',
    'sports',
    'technology'
]

# System notification settings by platform
NOTIFICATION_SETTINGS = {
    'Windows': {
        'command': ['msg', '*'],
        'format': '{title}: {message}'
    },
    'Darwin': {  # macOS
        'command': ['osascript', '-e'],
        'format': 'display notification "{message}" with title "{title}"'
    },
    'Linux': {
        'command': ['notify-send'],
        'format': ['{title}', '{message}']
    }
}

# Logging configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'jarvis.log',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'jarvis': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_SPEECH_RECOGNITION': True,
    'ENABLE_TEXT_TO_SPEECH': True,
    'ENABLE_CALENDAR_INTEGRATION': True,
    'ENABLE_EMAIL_INTEGRATION': True,
    'ENABLE_WEATHER_SERVICE': True,
    'ENABLE_MUSIC_CONTROL': True,
    'ENABLE_NEWS_SERVICE': True,
    'ENABLE_TIMER_SERVICE': True,
    'ENABLE_SYSTEM_NOTIFICATIONS': True,
    'ENABLE_MEMORY_PERSISTENCE': False,
    'ENABLE_DEBUG_MODE': False
}

# Environment variable names
ENV_VARS = {
    'MISTRAL_API_KEY': 'MISTRAL_API_KEY',
    'NEWS_API_KEY': 'NEWS_API_KEY',
    'EMAIL_USER': 'EMAIL_USER',
    'EMAIL_PASSWORD': 'EMAIL_PASSWORD',
    'EMAIL_IMAP_SERVER': 'EMAIL_IMAP_SERVER',
    'EMAIL_SMTP_SERVER': 'EMAIL_SMTP_SERVER'
}