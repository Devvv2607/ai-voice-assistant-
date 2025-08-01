"""
Music tool for Jarvis AI Assistant.
Handles music playback on various platforms.
"""

import webbrowser
import json
from typing import Optional, Dict, Any
from langchain.callbacks.manager import CallbackManagerForToolRun

from .base import BaseJarvisTool


class MusicTool(BaseJarvisTool):
    """LangChain tool for music operations."""
    
    name = "music_player"
    description = "Play music on various platforms. Input should be JSON with 'song' and 'platform' (spotify/youtube/apple)."
    
    def __init__(self):
        super().__init__()
        self.music_platforms = {
            'spotify': 'https://open.spotify.com/search/{query}',
            'youtube': 'https://www.youtube.com/results?search_query={query}',
            'apple': 'https://music.apple.com/search?term={query}'
        }
        self.default_platform = 'youtube'
    
    def execute(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Play music on specified platform."""
        try:
            # Parse query
            params = self._parse_music_params(query)
            song = params.get('song', 'music')
            platform = params.get('platform', self.default_platform).lower()
            
            # Validate platform
            if platform not in self.music_platforms:
                available_platforms = ', '.join(self.music_platforms.keys())
                return f"Unknown platform '{platform}'. Available platforms: {available_platforms}"
            
            # Format search query
            search_query = self._format_search_query(song)
            
            # Build URL
            url = self.music_platforms[platform].format(query=search_query)
            
            # Open in browser
            webbrowser.open(url)
            
            return self.format_success_response(
                f"Opening '{song}' on {platform.title()}",
                {"song": song, "platform": platform, "url": url}
            )
            
        except Exception as e:
            return self.format_error_response("play music", str(e))
    
    def _parse_music_params(self, query: str) -> Dict[str, Any]:
        """Parse music parameters from query."""
        # Try JSON first
        json_params = self.parse_json_query(query)
        if json_params:
            return json_params
        
        # Fallback to text parsing
        params = {'song': 'music', 'platform': self.default_platform}
        
        # Extract song name
        query_lower = query.lower().strip()
        
        # Remove common prefixes
        prefixes = ['play ', 'search for ', 'find ', 'look for ']
        for prefix in prefixes:
            if query_lower.startswith(prefix):
                query_lower = query_lower[len(prefix):]
                break
        
        # Extract platform
        platform_found = False
        for platform in self.music_platforms.keys():
            if platform in query_lower:
                params['platform'] = platform
                # Remove platform from song name
                query_lower = query_lower.replace(f' on {platform}', '').replace(f' {platform}', '')
                platform_found = True
                break
        
        # Set song name
        if query_lower.strip():
            params['song'] = query_lower.strip()
        
        return params
    
    def _format_search_query(self, song: str) -> str:
        """Format song name for URL search query."""
        # Replace spaces with appropriate characters for different platforms
        return song.replace(' ', '+').replace('&', '%26')
    
    def get_supported_platforms(self) -> list:
        """Get list of supported music platforms."""
        return list(self.music_platforms.keys())
    
    def add_platform(self, name: str, url_template: str) -> None:
        """Add a new music platform."""
        self.music_platforms[name.lower()] = url_template
    
    def set_default_platform(self, platform: str) -> bool:
        """Set default music platform."""
        if platform.lower() in self.music_platforms:
            self.default_platform = platform.lower()
            return True
        return False