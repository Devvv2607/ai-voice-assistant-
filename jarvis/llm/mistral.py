"""
Mistral LLM integration for LangChain.
Custom wrapper for Mistral API to work with LangChain agents.
"""

import requests
from typing import Optional, List
from langchain.llms.base import LLM
from langchain.schema import LLMResult, Generation
from ..core.config import config


class MistralLLM(LLM):
    """Custom Mistral LLM wrapper for LangChain."""
    
    def __init__(self, api_key: str):
        """Initialize Mistral LLM with API key."""
        super().__init__()
        self._api_key = api_key  # Use private attribute to avoid Pydantic error
        llm_config = config.get_llm_config()
        self._model_name = llm_config.get('model_name', 'mistral-small-latest')
        self._max_tokens = llm_config.get('max_tokens', 500)
        self._temperature = llm_config.get('temperature', 0.3)

    @property
    def api_key(self):
        return self._api_key

    @property
    def model_name(self):
        return self._model_name

    @property
    def max_tokens(self):
        return self._max_tokens

    @property
    def temperature(self):
        return self._temperature
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call the Mistral API."""
        try:
            url = "https://api.mistral.ai/v1/chat/completions"
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Add stop sequences if provided
            if stop:
                payload["stop"] = stop
            
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('choices'):
                    return data['choices'][0]['message']['content'].strip()
                else:
                    return "Error: No response choices from Mistral API"
            else:
                return f"Error: Mistral API returned status {response.status_code}"
            
        except requests.exceptions.Timeout:
            return "Error: Mistral API request timed out"
        except requests.exceptions.RequestException as e:
            return f"Error: Network error calling Mistral API: {str(e)}"
        except Exception as e:
            return f"Error calling Mistral API: {str(e)}"
    
    @property
    def _llm_type(self) -> str:
        """Return identifier of llm type."""
        return "mistral"
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        **kwargs
    ) -> LLMResult:
        """Generate responses for multiple prompts."""
        generations = []
        for prompt in prompts:
            response = self._call(prompt, stop=stop)
            generations.append([Generation(text=response)])
        
        return LLMResult(generations=generations)
    
    def get_model_info(self) -> dict:
        """Get information about the current model configuration."""
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "api_configured": bool(self.api_key)
        }


def create_mistral_llm(api_key: Optional[str] = None) -> Optional[MistralLLM]:
    """Factory function to create Mistral LLM instance."""
    if not api_key:
        api_key = config.mistral_api_key
    
    if not api_key:
        print("⚠️  No Mistral API key found")
        return None
    
    try:
        llm = MistralLLM(api_key=api_key)
        print("✅ Mistral LLM: Ready")
        return llm
    except Exception as e:
        print(f"❌ Failed to initialize Mistral LLM: {e}")
        return None

## MistralLLM is deprecated in this project. Do not instantiate or use.