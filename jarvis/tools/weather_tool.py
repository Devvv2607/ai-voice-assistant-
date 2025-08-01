"""
Weather tool for LangChain integration.
Provides weather information for any location.
"""

import requests
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun


class WeatherTool(BaseTool):
    """LangChain tool for weather information."""
    
    name = "weather_checker"
    description = "Get current weather information for any location. Input should be the location name or 'current location'."
    
    def _run(
        self, 
        query: str, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Get weather information for specified location."""
        try:
            location = query.strip() or "current location"
            
            # Use wttr.in service for weather data (free and reliable)
            url = f"http://wttr.in/{location}?format=j1"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_weather_data(data, location)
            else:
                # Fallback to simple format
                return self._get_simple_weather(location)
                
        except Exception as e:
            return f"❌ Weather check failed for {location}: {str(e)}"
    
    def _format_weather_data(self, data: dict, location: str) -> str:
        """Format weather data into readable response."""
        try:
            current = data['current_condition'][0]
            
            # Current conditions
            temp_c = current['temp_C']
            temp_f = current['temp_F']
            desc = current['weatherDesc'][0]['value']
            humidity = current['humidity']
            feels_like_c = current['FeelsLikeC']
            feels_like_f = current['FeelsLikeF']
            wind_speed = current['windspeedKmph']
            wind_dir = current['winddir16Point']
            visibility = current['visibility']
            pressure = current['pressure']
            
            # Today's forecast
            today_forecast = data['weather'][0]
            max_temp_c = today_forecast['maxtempC']
            min_temp_c = today_forecast['mintempC']
            max_temp_f = today_forecast['maxtempF']
            min_temp_f = today_forecast['mintempF']
            
            # UV Index
            uv_index = today_forecast.get('uvIndex', 'N/A')
            
            weather_report = f"""🌤️ Weather in {location.title()}:

🌡️ Current: {desc}, {temp_c}°C ({temp_f}°F)
🤔 Feels like: {feels_like_c}°C ({feels_like_f}°F)
📊 Today's Range: {min_temp_c}°C to {max_temp_c}°C ({min_temp_f}°F to {max_temp_f}°F)

💧 Humidity: {humidity}%
💨 Wind: {wind_speed} km/h {wind_dir}
👁️ Visibility: {visibility} km
🔽 Pressure: {pressure} mb
☀️ UV Index: {uv_index}"""
            
            return weather_report
            
        except KeyError as e:
            return f"❌ Error parsing weather data: missing {e}"
        except Exception as e:
            return f"❌ Error formatting weather data: {str(e)}"
    
    def _get_simple_weather(self, location: str) -> str:
        """Get simple weather format as fallback."""
        try:
            url = f"http://wttr.in/{location}?format=%C+%t+%h+%w"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                weather_info = response.text.strip()
                return f"🌤️ Weather in {location.title()}: {weather_info}"
            else:
                return f"❌ Could not get weather information for {location}"
                
        except Exception as e:
            return f"❌ Weather service unavailable: {str(e)}"
    
    def get_forecast(self, location: str, days: int = 3) -> str:
        """Get weather forecast for multiple days."""
        try:
            url = f"http://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                weather_data = data.get('weather', [])
                
                forecast_lines = [f"📅 {days}-Day Forecast for {location.title()}:\n"]
                
                for i, day_data in enumerate(weather_data[:days]):
                    date = day_data['date']
                    max_temp = day_data['maxtempC']
                    min_temp = day_data['mintempC']
                    desc = day_data['hourly'][0]['weatherDesc'][0]['value']
                    
                    day_name = self._get_day_name(i)
                    forecast_lines.append(
                        f"{day_name}: {desc}, {min_temp}°C - {max_temp}°C"
                    )
                
                return "\n".join(forecast_lines)
            else:
                return f"❌ Could not get forecast for {location}"
                
        except Exception as e:
            return f"❌ Forecast unavailable: {str(e)}"
    
    def _get_day_name(self, day_offset: int) -> str:
        """Get day name for forecast."""
        from datetime import datetime, timedelta
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        today = datetime.now()
        target_day = today + timedelta(days=day_offset)
        
        if day_offset == 0:
            return "Today"
        elif day_offset == 1:
            return "Tomorrow"
        else:
            return days[target_day.weekday()]