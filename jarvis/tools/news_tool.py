"""
News tool for Jarvis AI Assistant.
Fetches latest news from various sources.
"""

import requests
from xml.etree import ElementTree as ET
from typing import Optional, Dict, List, Any
from langchain.callbacks.manager import CallbackManagerForToolRun

from .base import ConfigurableJarvisTool


class NewsTool(ConfigurableJarvisTool):
    """LangChain tool for news information."""
    
    name = "news_fetcher"
    description = "Get latest news. Input can be 'general', 'technology', 'business', 'sports', or 'health'."
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.news_api_key = self.get_config_value('news_api_key')
        self.default_country = self.get_config_value('country', 'us')
        self.articles_per_request = self.get_config_value('articles_per_request', 3)
        self.timeout = self.get_config_value('timeout', 10)
        
        # Fallback RSS feeds for when API is not available
        self.rss_feeds = {
            'general': 'https://rss.cnn.com/rss/edition.rss',
            'technology': 'https://feeds.feedburner.com/oreilly/radar',
            'business': 'https://feeds.bbci.co.uk/news/business/rss.xml',
            'sports': 'https://rss.cnn.com/rss/edition_sport.rss',
            'health': 'https://rss.cnn.com/rss/edition_health.rss'
        }
    
    def validate_config(self) -> None:
        """Validate news tool configuration."""
        # News API key is optional - we have RSS fallbacks
        pass
    
    def execute(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get news information based on category."""
        try:
            category = self._parse_category(query)
            
            # Try NewsAPI first if available
            if self.news_api_key:
                result = self._get_news_from_api(category)
                if result:
                    return result
            
            # Fallback to RSS feeds
            return self._get_news_from_rss(category)
            
        except Exception as e:
            return self.format_error_response("fetch news", str(e))
    
    def _parse_category(self, query: str) -> str:
        """Parse news category from query."""
        query_lower = query.lower().strip()
        
        # Map common terms to categories
        category_mappings = {
            'tech': 'technology',
            'business': 'business',
            'sport': 'sports',
            'health': 'health',
            'medical': 'health',
            'finance': 'business',
            'economy': 'business',
            'science': 'technology'
        }
        
        # Check for direct matches
        if query_lower in self.rss_feeds:
            return query_lower
        
        # Check mappings
        for term, category in category_mappings.items():
            if term in query_lower:
                return category
        
        return 'general'  # Default category
    
    def _get_news_from_api(self, category: str) -> Optional[str]:
        """Get news from NewsAPI."""
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                'apiKey': self.news_api_key,
                'country': self.default_country,
                'category': category,
                'pageSize': self.articles_per_request
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])
                
                if articles:
                    return self._format_news_articles(articles, f"Latest {category} headlines from NewsAPI")
            
            # If API fails, return None to trigger RSS fallback
            return None
            
        except Exception as e:
            self.logger.warning(f"NewsAPI request failed: {e}")
            return None
    
    def _get_news_from_rss(self, category: str) -> str:
        """Get news from RSS feeds as fallback."""
        try:
            rss_url = self.rss_feeds.get(category, self.rss_feeds['general'])
            
            response = requests.get(rss_url, timeout=self.timeout)
            
            if response.status_code == 200:
                articles = self._parse_rss_feed(response.content)
                return self._format_news_titles(articles, f"Latest {category} headlines")
            else:
                return f"Unable to fetch {category} news at the moment (HTTP {response.status_code})"
            
        except Exception as e:
            return self.format_error_response(f"fetch {category} news from RSS", str(e))
    
    def _parse_rss_feed(self, rss_content: bytes) -> List[Dict[str, str]]:
        """Parse RSS feed content and extract articles."""
        try:
            root = ET.fromstring(rss_content)
            articles = []
            
            # Handle different RSS formats
            items = root.findall('.//item')
            if not items:
                items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for item in items[:self.articles_per_request]:
                article = {}
                
                # Extract title
                title_elem = item.find('title')
                if title_elem is None:
                    title_elem = item.find('.//{http://www.w3.org/2005/Atom}title')
                article['title'] = title_elem.text if title_elem is not None else 'No title'
                
                # Extract description/summary
                desc_elem = item.find('description')
                if desc_elem is None:
                    desc_elem = item.find('.//{http://www.w3.org/2005/Atom}summary')
                if desc_elem is not None and desc_elem.text:
                    article['description'] = desc_elem.text[:150] + "..." if len(desc_elem.text) > 150 else desc_elem.text
                else:
                    article['description'] = 'No description available'
                
                # Extract link
                link_elem = item.find('link')
                if link_elem is None:
                    link_elem = item.find('.//{http://www.w3.org/2005/Atom}link')
                if link_elem is not None:
                    article['url'] = link_elem.text or link_elem.get('href', '')
                
                articles.append(article)
            
            return articles
            
        except ET.ParseError as e:
            self.logger.error(f"RSS parsing error: {e}")
            return []
    
    def _format_news_articles(self, articles: List[Dict], header: str) -> str:
        """Format news articles with descriptions."""
        if not articles:
            return "No news articles found."
        
        formatted_articles = []
        for article in articles:
            title = article.get('title', 'No title')
            description = article.get('description', 'No description')
            
            # Clean up description
            if description:
                description = description[:100] + "..." if len(description) > 100 else description
            
            formatted_articles.append(f"• {title}\n  {description}")
        
        return f"{header}:\n\n" + "\n\n".join(formatted_articles)
    
    def _format_news_titles(self, articles: List[Dict], header: str) -> str:
        """Format news articles with titles only."""
        if not articles:
            return "No news articles found."
        
        titles = [f"• {article.get('title', 'No title')}" for article in articles]
        return f"{header}:\n\n" + "\n".join(titles)
    
    def get_available_categories(self) -> List[str]:
        """Get list of available news categories."""
        return list(self.rss_feeds.keys())
    
    def add_rss_feed(self, category: str, url: str) -> None:
        """Add a new RSS feed for a category."""
        self.rss_feeds[category.lower()] = url
    
    def test_news_sources(self) -> Dict[str, bool]:
        """Test connectivity to various news sources."""
        results = {}
        
        # Test NewsAPI if available
        if self.news_api_key:
            try:
                response = requests.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={'apiKey': self.news_api_key, 'pageSize': 1},
                    timeout=5
                )
                results['NewsAPI'] = response.status_code == 200
            except Exception:
                results['NewsAPI'] = False
        
        # Test RSS feeds
        for category, url in self.rss_feeds.items():
            try:
                response = requests.get(url, timeout=5)
                results[f'RSS_{category}'] = response.status_code == 200
            except Exception:
                results[f'RSS_{category}'] = False
        
        return results