"""
Web service utilities for Jarvis AI Assistant.
Provides common web request functionality and utilities.
"""

import requests
from typing import Dict, Any, Optional, Union
import logging
from urllib.parse import urljoin, urlparse
import time
from requests.adapters import HTTPAdapter
try:
    from urllib3.util.retry import Retry
except ImportError:
    from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class WebService:
    """
    Centralized web service for handling HTTP requests.
    Provides retry logic, timeout management, and error handling.
    """
    
    def __init__(self, 
                 timeout: int = 10,
                 max_retries: int = 3,
                 backoff_factor: float = 0.3,
                 user_agent: str = "Jarvis-AI-Assistant/1.0"):
        """
        Initialize web service with configuration.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Backoff factor for retries
            user_agent: User agent string for requests
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.user_agent = user_agent
        
        # Setup session with retry strategy
        self.session = requests.Session()
        self._setup_retry_strategy()
        self._setup_default_headers()
    
    def _setup_retry_strategy(self):
        """Configure retry strategy for the session."""
        retry_strategy = Retry(
            total=self.max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=self.backoff_factor
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _setup_default_headers(self):
        """Setup default headers for all requests."""
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def get(self, url: str, 
            params: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[int] = None) -> requests.Response:
        """
        Perform GET request with error handling.
        
        Args:
            url: Target URL
            params: Query parameters
            headers: Additional headers
            timeout: Request timeout (overrides default)
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: For request failures
        """
        return self._make_request('GET', url, params=params, headers=headers, timeout=timeout)
    
    def post(self, url: str,
             data: Optional[Union[Dict, str]] = None,
             json: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None,
             timeout: Optional[int] = None) -> requests.Response:
        """
        Perform POST request with error handling.
        
        Args:
            url: Target URL
            data: Form data
            json: JSON data
            headers: Additional headers
            timeout: Request timeout (overrides default)
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: For request failures
        """
        return self._make_request('POST', url, data=data, json=json, headers=headers, timeout=timeout)
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with comprehensive error handling.
        
        Args:
            method: HTTP method
            url: Target URL
            **kwargs: Additional request parameters
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: For request failures
        """
        # Use default timeout if not specified
        if 'timeout' not in kwargs or kwargs['timeout'] is None:
            kwargs['timeout'] = self.timeout
        
        # Merge headers
        if 'headers' in kwargs and kwargs['headers']:
            headers = self.session.headers.copy()
            headers.update(kwargs['headers'])
            kwargs['headers'] = headers
        
        try:
            logger.debug(f"Making {method} request to {url}")
            start_time = time.time()
            
            response = self.session.request(method, url, **kwargs)
            
            duration = time.time() - start_time
            logger.debug(f"Request completed in {duration:.2f}s with status {response.status_code}")
            
            # Raise for bad status codes
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out after {kwargs['timeout']}s")
            raise
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error for {url}")
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} for {url}")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            raise
    
    def get_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        GET request that returns JSON data.
        
        Args:
            url: Target URL
            **kwargs: Additional request parameters
            
        Returns:
            Parsed JSON data
            
        Raises:
            requests.RequestException: For request failures
            ValueError: For JSON parsing errors
        """
        response = self.get(url, **kwargs)
        try:
            return response.json()
        except ValueError as e:
            logger.error(f"Failed to parse JSON from {url}: {e}")
            raise
    
    def post_json(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        POST request that returns JSON data.
        
        Args:
            url: Target URL
            **kwargs: Additional request parameters
            
        Returns:
            Parsed JSON data
            
        Raises:
            requests.RequestException: For request failures
            ValueError: For JSON parsing errors
        """
        response = self.post(url, **kwargs)
        try:
            return response.json()
        except ValueError as e:
            logger.error(f"Failed to parse JSON from {url}: {e}")
            raise
    
    def download_file(self, url: str, file_path: str, chunk_size: int = 8192) -> bool:
        """
        Download file from URL to local path.
        
        Args:
            url: Source URL
            file_path: Destination file path
            chunk_size: Download chunk size in bytes
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.get(url, stream=True)
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        file.write(chunk)
            
            logger.info(f"Successfully downloaded {url} to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return False
    
    def is_url_accessible(self, url: str, method: str = 'HEAD') -> bool:
        """
        Check if URL is accessible.
        
        Args:
            url: URL to check
            method: HTTP method to use (HEAD or GET)
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            if method.upper() == 'HEAD':
                response = self.session.head(url, timeout=5)
            else:
                response = self.session.get(url, timeout=5)
            
            return response.status_code == 200
            
        except Exception:
            return False
    
    def get_domain(self, url: str) -> str:
        """
        Extract domain from URL.
        
        Args:
            url: Full URL
            
        Returns:
            Domain name
        """
        parsed = urlparse(url)
        return parsed.netloc
    
    def build_url(self, base_url: str, path: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Build URL from components.
        
        Args:
            base_url: Base URL
            path: Path to append
            params: Query parameters
            
        Returns:
            Complete URL
        """
        url = urljoin(base_url, path)
        
        if params:
            param_string = '&'.join(f"{k}={v}" for k, v in params.items())
            url += f"?{param_string}"
        
        return url
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Utility functions for common web operations
def fetch_text(url: str, timeout: int = 10) -> Optional[str]:
    """
    Simple utility to fetch text content from URL.
    
    Args:
        url: Target URL
        timeout: Request timeout
        
    Returns:
        Text content or None if failed
    """
    try:
        with WebService(timeout=timeout) as web:
            response = web.get(url)
            return response.text
    except Exception as e:
        logger.error(f"Failed to fetch text from {url}: {e}")
        return None


def fetch_json(url: str, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Simple utility to fetch JSON data from URL.
    
    Args:
        url: Target URL
        timeout: Request timeout
        
    Returns:
        JSON data or None if failed
    """
    try:
        with WebService(timeout=timeout) as web:
            return web.get_json(url)
    except Exception as e:
        logger.error(f"Failed to fetch JSON from {url}: {e}")
        return None


def check_internet_connectivity() -> bool:
    """
    Check if internet connection is available.
    
    Returns:
        True if connected, False otherwise
    """
    test_urls = [
        'https://www.google.com',
        'https://www.cloudflare.com',
        'https://httpbin.org/status/200'
    ]
    
    with WebService(timeout=5) as web:
        for url in test_urls:
            if web.is_url_accessible(url):
                return True
    
    return False