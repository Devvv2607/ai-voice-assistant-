"""
Timer tool for Jarvis AI Assistant.
Handles timer and countdown operations.
"""

import time
import threading
import platform
import subprocess
import re
from typing import Optional, Dict, Any
from langchain.callbacks.manager import CallbackManagerForToolRun

from .base import BaseJarvisTool


class TimerTool(BaseJarvisTool):
    """LangChain tool for timer operations."""
    
    name = "timer_manager"
    description = "Set timers. Input should be duration in seconds or descriptive text like '5 minutes'."
    
    def __init__(self):
        super().__init__()
        self.active_timers = {}
        self.timer_counter = 0
        self.system_type = platform.system()
    
    def execute(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Set a timer based on the query."""
        try:
            # Parse duration from query
            duration = self._parse_duration(query)
            if duration <= 0:
                return "Invalid timer duration. Please specify a positive time."
            
            # Create timer
            self.timer_counter += 1
            timer_id = self.timer_counter
            
            # Format time string for display
            time_str = self._format_duration(duration)
            
            # Start timer thread
            timer_thread = threading.Thread(
                target=self._timer_thread,
                args=(timer_id, duration, time_str),
                daemon=True
            )
            
            self.active_timers[timer_id] = {
                'thread': timer_thread,
                'duration': duration,
                'time_str': time_str,
                'start_time': time.time()
            }
            
            timer_thread.start()
            
            return self.format_success_response(
                f"Timer set for {time_str}. I'll notify you when it's done!",
                {
                    "timer_id": timer_id,
                    "duration": duration,
                    "duration_text": time_str,
                    "active_timers": len(self.active_timers)
                }
            )
            
        except Exception as e:
            return self.format_error_response("set timer", str(e))
    
    def _timer_thread(self, timer_id: int, duration: int, time_str: str):
        """Timer thread that runs in background."""
        try:
            time.sleep(duration)
            
            # Check if timer is still active (not cancelled)
            if timer_id in self.active_timers:
                self._timer_complete_notification(time_str)
                # Clean up timer
                del self.active_timers[timer_id]
                
        except Exception as e:
            self.logger.error(f"Timer thread error: {e}")
    
    def _timer_complete_notification(self, time_str: str):
        """Handle timer completion notification."""
        message = f"⏰ TIMER COMPLETE! Your {time_str} timer is done!"
        print(f"\n{message}")
        
        # System notification
        try:
            self._send_system_notification("Jarvis Timer", f"{time_str} complete!")
        except Exception as e:
            self.logger.warning(f"Failed to send system notification: {e}")
    
    def _send_system_notification(self, title: str, message: str):
        """Send system notification based on platform."""
        try:
            if self.system_type == "Windows":
                subprocess.run(['msg', '*', f'{title}: {message}'], 
                             check=False, timeout=5)
            elif self.system_type == "Darwin":  # macOS
                subprocess.run([
                    'osascript', '-e', 
                    f'display notification "{message}" with title "{title}"'
                ], check=False, timeout=5)
            elif self.system_type == "Linux":
                subprocess.run(['notify-send', title, message], 
                             check=False, timeout=5)
        except subprocess.TimeoutExpired:
            self.logger.warning("System notification timed out")
        except Exception as e:
            self.logger.warning(f"System notification failed: {e}")
    
    def _parse_duration(self, text: str) -> int:
        """Parse duration from text input."""
        text = text.lower().strip()
        
        # Define pattern matchers with their conversion functions
        patterns = [
            (r'(\d+)\s*(?:hours?|hrs?|h)\s*(?:and\s*)?(?:(\d+)\s*(?:minutes?|mins?|m))?', self._parse_hours_minutes),
            (r'(\d+)\s*(?:minutes?|mins?|m)\s*(?:and\s*)?(?:(\d+)\s*(?:seconds?|secs?|s))?', self._parse_minutes_seconds),
            (r'(\d+)\s*(?:seconds?|secs?|s)', lambda h, m=None: int(h)),
            (r'(\d+)\s*(?:minutes?|mins?|m)', lambda m, s=None: int(m) * 60),
            (r'(\d+)\s*(?:hours?|hrs?|h)', lambda h, m=None: int(h) * 3600),
        ]
        
        for pattern, converter in patterns:
            match = re.search(pattern, text)
            if match:
                groups = match.groups()
                return converter(*[g for g in groups if g is not None])
        
        # Try to extract just numbers (default to minutes)
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0]) * 60  # Default to minutes
        
        # Default fallback
        return 60  # 1 minute
    
    def _parse_hours_minutes(self, hours: str, minutes: str = None) -> int:
        """Convert hours and minutes to seconds."""
        total_seconds = int(hours) * 3600
        if minutes:
            total_seconds += int(minutes) * 60
        return total_seconds
    
    def _parse_minutes_seconds(self, minutes: str, seconds: str = None) -> int:
        """Convert minutes and seconds to seconds."""
        total_seconds = int(minutes) * 60
        if seconds:
            total_seconds += int(seconds)
        return total_seconds
    
    def _format_duration(self, duration: int) -> str:
        """Format duration as readable string."""
        if duration >= 3600:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            
            parts = []
            if hours > 0:
                parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if minutes > 0:
                parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
            if seconds > 0 and hours == 0:  # Only show seconds if no hours
                parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
            
            return " ".join(parts)
            
        elif duration >= 60:
            minutes = duration // 60
            seconds = duration % 60
            
            parts = [f"{minutes} minute{'s' if minutes != 1 else ''}"]
            if seconds > 0:
                parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
            
            return " ".join(parts)
        else:
            return f"{duration} second{'s' if duration != 1 else ''}"
    
    def get_active_timers(self) -> Dict[int, Dict[str, Any]]:
        """Get information about active timers."""
        active = {}
        current_time = time.time()
        
        for timer_id, timer_info in self.active_timers.items():
            elapsed = current_time - timer_info['start_time']
            remaining = max(0, timer_info['duration'] - elapsed)
            
            active[timer_id] = {
                'duration_text': timer_info['time_str'],
                'total_duration': timer_info['duration'],
                'elapsed': elapsed,
                'remaining': remaining,
                'remaining_text': self._format_duration(int(remaining))
            }
        
        return active
    
    def cancel_timer(self, timer_id: int) -> bool:
        """Cancel a specific timer."""
        if timer_id in self.active_timers:
            del self.active_timers[timer_id]
            return True
        return False
    
    def cancel_all_timers(self) -> int:
        """Cancel all active timers."""
        count = len(self.active_timers)
        self.active_timers.clear()
        return count