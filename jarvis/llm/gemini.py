"""
Gemini LLM integration for LangChain.
Custom wrapper for Gemini API to work with LangChain agents.
"""
from typing import Optional, List
from langchain.llms.base import LLM
from langchain.schema import LLMResult, Generation
import requests
from ..core.config import config

class GeminiLLM(LLM):
    """Custom Gemini LLM wrapper for LangChain."""
    def __init__(self, api_key: str):
        super().__init__()
        self._api_key = api_key  # Use private attribute
        self.model_name = "gemini-pro"
        self.max_tokens = 512
        self.temperature = 0.3

    @property
    def api_key(self):
        return self._api_key

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens
            }
        }
        try:
            response = requests.post(url, json=data, headers=headers, timeout=15)
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Gemini API error: {e}"

    @property
    def _llm_type(self) -> str:
        return "gemini"

    def _generate(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs) -> LLMResult:
        generations = [Generation(text=self._call(prompt, stop=stop)) for prompt in prompts]
        return LLMResult(generations=[generations])

    def get_model_info(self) -> dict:
        return {
            "model_name": self.model_name,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
