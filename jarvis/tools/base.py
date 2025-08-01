"""
Base classes for Jarvis tools.
Provides common functionality and structure for all tools.
"""

from abc import ABC, abstractmethod
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from typing import Optional, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class BaseJarvisTool(BaseTool, ABC):
    """
    Base class for all Jarvis tools.
    Extends LangChain's BaseTool with common functionality.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Main execution method for the tool.
        Handles error logging and provides structured response.
        """
        try:
            self.logger.info(f"Executing {self.name} with query: {query}")
            result = self.execute(query, run_manager)
            self.logger.info(f"Successfully executed {self.name}")
            return result
        except Exception as e:
            error_msg = f"Error in {self.name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return error_msg
    
    @abstractmethod
    def execute(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Abstract method to be implemented by each tool.
        Contains the actual tool logic.
        """
        pass
    
    def parse_json_query(self, query: str) -> Dict[str, Any]:
        """
        Helper method to parse JSON queries safely.
        Returns empty dict if parsing fails.
        """
        try:
            if query.strip().startswith('{') and query.strip().endswith('}'):
                return json.loads(query)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON query: {query}, Error: {e}")
        return {}
    
    def format_success_response(self, message: str, data: Optional[Dict] = None) -> str:
        """Format a successful response message."""
        if data:
            return f"{message}\nDetails: {json.dumps(data, indent=2)}"
        return message
    
    def format_error_response(self, operation: str, error: str) -> str:
        """Format an error response message."""
        return f"Failed to {operation}: {error}"


class ConfigurableJarvisTool(BaseJarvisTool):
    """
    Base class for tools that require configuration.
    Provides common configuration validation.
    """
    
    def __init__(self, config: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.validate_config()
    
    @abstractmethod
    def validate_config(self) -> None:
        """Validate tool-specific configuration."""
        pass
    
    def is_configured(self, required_keys: list) -> bool:
        """Check if all required configuration keys are present."""
        return all(
            key in self.config and self.config[key] 
            for key in required_keys
        )
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Safely get configuration value with fallback."""
        return self.config.get(key, default)


class AsyncJarvisTool(BaseJarvisTool):
    """
    Base class for tools that may need async operations.
    Currently provides sync interface but can be extended for async.
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def aexecute(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Async version of execute method.
        Default implementation calls sync execute method.
        """
        return self.execute(query, run_manager)