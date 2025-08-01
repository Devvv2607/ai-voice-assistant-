# Jarvis AI Assistant Setup Guide

This comprehensive guide will walk you through setting up Jarvis AI Assistant from scratch.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 2GB free space
- **Network**: Internet connection for API services
- **Audio**: Microphone and speakers/headphones

### Hardware Recommendations
- **Microphone**: USB microphone or good quality built-in mic
- **Speakers**: External speakers or good headphones
- **Processing**: Multi-core CPU for better performance

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/jarvis-ai-assistant.git
cd jarvis-ai-assistant
```

### Step 2: Run Setup Script
```bash
python scripts/setup.py
```

This will:
- Check Python version compatibility
- Install all required dependencies
- Download NLTK data
- Create configuration files
- Set up directory structure
- Verify installation

### Step 3: Manual Setup (Alternative)
If the setup script fails, you can set up manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Create configuration files
cp config/.env.example .env
cp config/credentials.json.example credentials.json

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

## Configuration

### Step 1: Environment Variables
Edit the `.env` file with your configuration:

```bash
# Required for advanced AI features
MISTRAL_API_KEY=your_mistral_api_key_here

# Email integration (optional)
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_gmail_app_password

# News service (optional)
NEWS_API_KEY=your_news_api_key_here

# Application settings
JARVIS_TIMEZONE=Asia/Kolkata
NEWS_COUNTRY=us
DEBUG_MODE=false
```

### Step 2: Audio Setup

#### Windows
1. Go to Settings > System > Sound
2. Set your microphone as the default input device
3. Test microphone levels
4. Ensure speakers/headphones are working

#### macOS
1. Go to System Preferences > Sound
2. Select Input tab and choose your microphone
3. Adjust input level
4. Test output on Output tab

#### Linux (Ubuntu/Debian)
```bash
# Install additional audio packages if needed
sudo apt-get update
sudo apt-get install portaudio19-dev python3-pyaudio

# Test microphone
arecord -d 5 test.wav
aplay test.wav
```

### Step 3: API Keys Configuration

#### Mistral AI (Required for Advanced Features)
1. Go to [Mistral AI Console](https://console.mistral.ai/)
2. Create an account or sign in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key to `MISTRAL_API_KEY` in `.env`

#### News API (Optional)
1. Visit [NewsAPI](https://newsapi.org/)
2. Sign up for a free account
3. Get your API key from dashboard
4. Add to `NEWS_API_KEY` in `.env`

#### Email Setup (Optional)
For Gmail integration:
1. Enable 2-Factor Authentication on your Google account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate an app-specific password
4. Use this password (not your regular Gmail password) in `.env`

### Step 4: Google Calendar Integration (Optional)

#### Enable Google Calendar API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID)
5. Configure OAuth consent screen
6. Download the credentials JSON file

#### Setup Credentials
1. Rename downloaded file to `credentials.json`
2. Place it in the project root directory
3. First run will open browser for OAuth authorization
4. Grant calendar access permissions

#### Detailed Steps
```bash
# 1. Google Cloud Console Setup
# - Go to https://console.cloud.google.com/
# - Create new project: "Jarvis Assistant"
# - Enable APIs: Google Calendar API

# 2. Create Credentials
# - Go to Credentials tab
# - Click "Create Credentials" > "OAuth 2.0 Client ID"
# - Application type: "Desktop application"
# - Name: "Jarvis Calendar Integration"
# - Download JSON file

# 3. Configure OAuth Consent Screen
# - Go to OAuth consent screen tab
# - Choose "External" (for personal use)
# - Fill in application name: "Jarvis AI Assistant"
# - Add your email in developer contact information
# - Add scopes: ../auth/calendar (Google Calendar API)

# 4. Place credentials.json in project root
mv ~/Downloads/client_secret_*.json ./credentials.json
```

## Testing Installation

### Step 1: Basic Import Test
```bash
python -c "import jarvis; print('✅ Jarvis imported successfully')"
```

### Step 2: Audio Test
```bash
python -c "
import speech_recognition as sr
import pyttsx3

# Test speech recognition
r = sr.Recognizer()
print('✅ Speech recognition ready')

# Test text-to-speech
engine = pyttsx3.init()
engine.say('Audio test successful')
engine.runAndWait()
print('✅ Text-to-speech working')
"
```

### Step 3: API Connectivity Test
```bash
python -c "
from jarvis.services.web_service import check_internet_connectivity
from jarvis.tools.weather_tool import WeatherTool

print('🌐 Internet:', '✅ Connected' if check_internet_connectivity() else '❌ No connection')

# Test weather API
weather_tool = WeatherTool()
result = weather_tool.execute('London')
print('🌤️ Weather API:', '✅ Working' if 'Weather in London' in result else '❌ Failed')
"
```

### Step 4: Full System Test
```bash
python main.py
```

Say "Hey Jarvis" and try a simple command like "What's the weather like?"

## Troubleshooting

### Common Issues and Solutions

#### Issue: "ModuleNotFoundError: No module named 'jarvis'"
**Solution:**
```bash
# Ensure you're in the project directory
cd jarvis-ai-assistant

# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Issue: "Could not find PyAudio"
**Solution:**

*Windows:*
```bash
pip install pipwin
pipwin install pyaudio
```

*macOS:*
```bash
brew install portaudio
pip install pyaudio
```

*Linux:*
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

#### Issue: "Speech recognition not working"
**Solution:**
1. Check microphone permissions
2. Test microphone in system settings
3. Adjust ambient noise calibration:
```python
# In jarvis/core/speech.py, increase calibration duration
self.recognizer.adjust_for_ambient_noise(source, duration=5)  # Increase from 2 to 5
```

#### Issue: "Google Calendar authentication failed"
**Solution:**
1. Delete `token.pickle` if it exists
2. Ensure `credentials.json` is in project root
3. Check Google Cloud Console settings
4. Verify Calendar API is enabled
5. Run first-time setup:
```bash
python -c "
from jarvis.services.google_calendar import GoogleCalendarService
service = GoogleCalendarService()
print('Calendar service initialized')
"
```

#### Issue: "Mistral API errors"
**Solution:**
1. Verify API key in `.env` file
2. Check API key validity at Mistral Console
3. Ensure sufficient API quota
4. Test API connection:
```bash
python -c "
import os
from jarvis.llm.mistral import MistralLLM

api_key = os.getenv('MISTRAL_API_KEY')
if api_key:
    llm = MistralLLM(api_key=api_key)
    response = llm._call('Hello, this is a test')
    print('✅ Mistral API working:', response[:50])
else:
    print('❌ MISTRAL_API_KEY not found in environment')
"
```

#### Issue: "Email authentication failed"
**Solution:**
1. Enable 2-Factor Authentication on Gmail
2. Generate App Password (not regular password)
3. Use App Password in `.env` file
4. Check email server settings:
```python
# Test email configuration
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_16_char_app_password
EMAIL_IMAP_SERVER=imap.gmail.com
EMAIL_SMTP_SERVER=smtp.gmail.com
```

#### Issue: "Permission denied" on Linux/macOS
**Solution:**
```bash
# Make sure script is executable
chmod +x scripts/setup.py

# Install with user permissions
pip install --user -r requirements.txt

# Fix audio permissions (Linux)
sudo usermod -a -G audio $USER
# Then logout and login again
```

### Advanced Troubleshooting

#### Enable Debug Mode
Add to `.env`:
```bash
DEBUG_MODE=true
```

This will provide detailed logging in `jarvis.log`.

#### Check System Resources
```bash
# Monitor CPU and memory usage
top
# or
htop

# Check disk space
df -h

# Check Python memory usage
python -c "
import psutil
process = psutil.Process()
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"
```

#### Network Diagnostics
```bash
# Test internet connectivity
ping google.com

# Test API endpoints
curl -I https://api.mistral.ai
curl -I https://newsapi.org
curl -I https://wttr.in
```

#### Audio Diagnostics
```bash
# List audio devices (Linux)
arecord -l
aplay -l

# Test recording (Linux/macOS)
arecord -d 3 -f cd test.wav
aplay test.wav

# Windows PowerShell audio test
# Get-WmiObject Win32_SoundDevice
```

## Performance Optimization

### Memory Optimization
```python
# In .env file, adjust these settings:
SPEECH_TIMEOUT=5          # Reduce from 8 to save memory
REQUEST_TIMEOUT=8         # Reduce from 10
NEWS_ARTICLES_COUNT=2     # Reduce from 3
```

### CPU Optimization
- Close unnecessary applications
- Use SSD storage if available
- Ensure adequate cooling

### Network Optimization
- Use wired connection if possible
- Close bandwidth-heavy applications
- Consider API request caching

## Security Setup

### File Permissions
```bash
# Protect sensitive files
chmod 600 .env
chmod 600 credentials.json
chmod 600 token.pickle
```

### Firewall Configuration
```bash
# Allow Python through firewall (Windows)
# Go to Windows Defender Firewall > Allow an app

# Linux iptables (if needed)
sudo iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
sudo iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT
```

### API Key Security
- Never commit `.env` to version control
- Regularly rotate API keys
- Monitor API usage and quotas
- Use environment variables in production

## Next Steps

After successful setup:

1. **Customize Wake Words**: Edit `WAKE_WORDS` in `jarvis/utils/constants.py`
2. **Add Custom Tools**: Create new tools in `jarvis/tools/`
3. **Extend Functionality**: Add new services in `jarvis/services/`
4. **Configure Notifications**: Adjust system notification settings
5. **Create Shortcuts**: Set up desktop shortcuts or aliases

## Getting Help

If you encounter issues not covered here:

1. **Check Logs**: Look at `jarvis.log` for detailed error messages
2. **Search Issues**: Check GitHub issues for similar problems
3. **Create Issue**: Report new bugs with system info and logs
4. **Community**: Join discussions in project community channels

## Maintenance

### Regular Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Check for project updates
git pull origin main
```

### Backup Important Files
- `.env` (without committing to version control)
- `credentials.json`
- `token.pickle`
- Custom configuration files

### Monitor Performance
- Check `jarvis.log` regularly
- Monitor API usage and quotas
- Update API keys before expiration

---

*For API-specific setup instructions, see [API_KEYS.md](API_KEYS.md)*
*For general usage information, see [README.md](README.md)*