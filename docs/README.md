# Jarvis AI Assistant Documentation

## Overview

Jarvis is a sophisticated voice-activated AI assistant powered by LangChain and Mistral AI. It combines natural language processing, speech recognition, and various integrated services to provide a comprehensive personal assistant experience.

## Features

### 🎤 Voice Interaction
- **Wake Word Detection**: Activates with "Hey Jarvis" or "Jarvis"
- **Natural Speech Recognition**: Understands conversational commands
- **Text-to-Speech**: Responds with natural voice synthesis
- **Ambient Noise Adaptation**: Automatically adjusts to environment

### 🧠 AI-Powered Intelligence
- **LangChain Integration**: Advanced reasoning and task planning
- **Mistral AI LLM**: Sophisticated language understanding
- **Context Memory**: Remembers conversation history
- **Tool Chaining**: Combines multiple tools for complex tasks

### 📅 Calendar Management
- **Smart Scheduling**: "Schedule team meeting tomorrow at 3 PM"
- **Google Calendar Integration**: Syncs with your Google Calendar
- **Natural Language Parsing**: Understands various date/time formats
- **Event Creation**: Automatically creates calendar events

### 📧 Email Operations
- **Inbox Monitoring**: Check latest emails
- **Email Composition**: Send emails through voice commands
- **SMTP/IMAP Support**: Works with Gmail and other providers
- **Smart Parsing**: Extracts recipients and content from speech

### 🌤️ Weather Information
- **Real-time Weather**: Current conditions for any location
- **Detailed Forecasts**: Temperature, humidity, wind speed
- **Location-aware**: Supports global weather queries
- **Multiple Sources**: Reliable weather data integration

### 🎵 Music Control
- **Multi-platform Support**: Spotify, YouTube, Apple Music
- **Voice Search**: "Play some jazz on Spotify"
- **Smart Query Processing**: Understands song names and artists
- **Browser Integration**: Opens music platforms automatically

### ⏰ Timer Management
- **Flexible Duration Parsing**: "Set a 10 minute timer"
- **Multiple Timers**: Run several timers simultaneously
- **System Notifications**: Cross-platform timer alerts
- **Natural Language**: "5 minutes", "1 hour 30 minutes", etc.

### 📰 News Updates
- **Real-time Headlines**: Latest news from multiple sources
- **Category Filtering**: Technology, business, sports, health
- **NewsAPI Integration**: High-quality news sources
- **RSS Fallbacks**: Reliable news even without API keys

## Architecture

### Modular Design
```
jarvis/
├── core/           # Main assistant logic
├── llm/            # Language model integrations
├── tools/          # LangChain tools for various functions
├── services/       # External service integrations
└── utils/          # Helper functions and constants
```

### Key Components

#### Assistant Core (`jarvis/core/`)
- **`assistant.py`**: Main AgenticJarvis class orchestrating all components
- **`speech.py`**: Speech recognition and text-to-speech management
- **`config.py`**: Configuration loading and validation

#### LLM Integration (`jarvis/llm/`)
- **`mistral.py`**: Mistral AI API wrapper for LangChain

#### Tools (`jarvis/tools/`)
- **`calendar_tool.py`**: Calendar event management
- **`email_tool.py`**: Email operations (send/receive)
- **`weather_tool.py`**: Weather information retrieval
- **`music_tool.py`**: Music platform control
- **`timer_tool.py`**: Timer and countdown management
- **`news_tool.py`**: News fetching and parsing

#### Services (`jarvis/services/`)
- **`google_calendar.py`**: Google Calendar API integration
- **`email_service.py`**: SMTP/IMAP email handling
- **`web_service.py`**: HTTP request utilities

## Usage Examples

### Basic Interaction
```
User: "Hey Jarvis"
Jarvis: "Yes, how can I help you?"

User: "What's the weather like in New York?"
Jarvis: "Weather in New York: Clear skies, 22°C (72°F), feels like 24°C, humidity 65%, wind 8 km/h"
```

### Calendar Management
```
User: "Schedule a team meeting tomorrow at 3 PM"
Jarvis: "Successfully scheduled 'team meeting' for March 15 at 03:00 PM"

User: "Set a reminder for my doctor's appointment next Monday at 10 AM"
Jarvis: "Calendar event created successfully for Monday, March 18 at 10:00 AM"
```

### Email Operations
```
User: "Check my latest emails"
Jarvis: "You have 3 new emails from..."

User: "Send an email to john@example.com about the project update"
Jarvis: "What would you like the email to say?"
```

### Timer and Reminders
```
User: "Set a timer for 15 minutes"
Jarvis: "Timer set for 15 minutes. I'll notify you when it's done!"

User: "Set a 45-minute timer for my workout"
Jarvis: "Timer set for 45 minutes. I'll notify you when it's done!"
```

### Music Control
```
User: "Play some classical music on Spotify"
Jarvis: "Opening 'classical music' on Spotify"

User: "Search for The Beatles on YouTube"
Jarvis: "Opening 'The Beatles' on YouTube"
```

### News Updates
```
User: "Get me the latest technology news"
Jarvis: "Latest technology headlines: ..."

User: "What's happening in business news?"
Jarvis: "Latest business headlines: ..."
```

## Advanced Features

### Context Awareness
Jarvis maintains conversation context and can handle follow-up questions:
```
User: "What's the weather in London?"
Jarvis: "Weather in London: Cloudy, 15°C..."

User: "What about tomorrow?"
Jarvis: "Tomorrow's weather in London: Partly cloudy, 17°C..."
```

### Multi-step Tasks
Complex requests are broken down and executed in sequence:
```
User: "Schedule a meeting for tomorrow at 2 PM and send an email to the team about it"
Jarvis: "I'll schedule the meeting and send the email..."
```

### Error Handling
Robust error handling with helpful feedback:
```
User: "Schedule a meeting for yesterday"
Jarvis: "I can't schedule meetings in the past. Would you like to schedule it for today or tomorrow instead?"
```

## Configuration

### Environment Variables
Configure Jarvis through the `.env` file:
- `MISTRAL_API_KEY`: For advanced AI features
- `EMAIL_USER/EMAIL_PASSWORD`: For email integration
- `NEWS_API_KEY`: For news service (optional)

### Feature Flags
Enable/disable features in `jarvis/utils/constants.py`:
```python
FEATURE_FLAGS = {
    'ENABLE_SPEECH_RECOGNITION': True,
    'ENABLE_CALENDAR_INTEGRATION': True,
    'ENABLE_EMAIL_INTEGRATION': True,
    # ... more features
}
```

## Performance

### Response Times
- **Voice Recognition**: ~1-2 seconds
- **AI Processing**: ~2-3 seconds (with Mistral)
- **Tool Execution**: ~1-5 seconds (depending on service)
- **Total Response**: ~4-10 seconds typical

### Memory Usage
- **Base Application**: ~100-200 MB
- **With Speech Models**: ~300-500 MB
- **During Processing**: ~500-800 MB peak

### Network Requirements
- **Minimum**: 1 Mbps for basic functionality
- **Recommended**: 5+ Mbps for optimal performance
- **Offline Mode**: Limited functionality without internet

## Troubleshooting

### Common Issues

#### Speech Recognition Problems
- **Solution**: Check microphone permissions and adjust ambient noise
- **Command**: Test with `python -c "import speech_recognition; print('OK')"`

#### API Connection Errors
- **Solution**: Verify API keys and internet connection
- **Check**: Look at `jarvis.log` for detailed error messages

#### Calendar Integration Issues
- **Solution**: Ensure `credentials.json` is properly configured
- **Check**: Google Calendar API is enabled in Google Console

#### Email Authentication Failures
- **Solution**: Use App Passwords for Gmail, enable 2FA
- **Check**: Email server settings in `.env` file

### Debug Mode
Enable detailed logging by setting `DEBUG_MODE=true` in `.env`.

### Log Analysis
Check `jarvis.log` for detailed execution traces and error information.

## Security Considerations

### API Key Management
- Store API keys securely in `.env` file
- Never commit credentials to version control
- Regularly rotate API keys and passwords

### Network Security
- All API communications use HTTPS
- No sensitive data stored in logs
- OAuth2 for Google services integration

### Privacy
- Speech processing can be done locally
- No conversation data sent to external services unless explicitly configured
- User data remains on local device

## Contributing

### Development Setup
1. Clone repository
2. Run `python scripts/setup.py`
3. Configure `.env` with your API keys
4. Start development with `python main.py`

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include comprehensive docstrings
- Write unit tests for new features

### Testing
Run tests with:
```bash
python -m pytest tests/
```

## Support

### Getting Help
1. Check this documentation
2. Review `docs/SETUP.md` for setup issues
3. Check `docs/API_KEYS.md` for API configuration
4. Look at `jarvis.log` for error details

### Reporting Issues
When reporting issues, include:
- Jarvis version
- Operating system
- Error messages from logs
- Steps to reproduce

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Acknowledgments

- **LangChain**: Framework for LLM applications
- **Mistral AI**: Language model provider
- **Google**: Calendar and various APIs
- **OpenAI**: Inspiration for conversational AI
- **Contributors**: All developers who helped build Jarvis

---

*For more detailed setup instructions, see [SETUP.md](SETUP.md)*
*For API configuration guide, see [API_KEYS.md](API_KEYS.md)*