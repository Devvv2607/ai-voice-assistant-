"""
Web Search tool for Jarvis AI Assistant.
Allows answering general knowledge questions using SerpAPI.
"""
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import requests
import os

class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Answer general knowledge questions using web search. Input should be a question or query."

    def __init__(self):
        super().__init__()
        self.serp_api_key = os.getenv("SERP_API_KEY")
        self.search_url = "https://serpapi.com/search"

    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        # Remove or comment out this line at the module level:
        # print("[DEBUG] WebSearchTool called with query:", query)
        if not self.serp_api_key:
            return "Web search is not configured. Please set SERP_API_KEY in your .env file."
        params = {
            "q": query,
            "api_key": self.serp_api_key,
            "engine": "google"
        }
        try:
            response = requests.get(self.search_url, params=params, timeout=10)
            data = response.json()
            if "answer_box" in data and "answer" in data["answer_box"]:
                return data["answer_box"]["answer"]
            elif "organic_results" in data and len(data["organic_results"]) > 0:
                return data["organic_results"][0].get("snippet", "No answer found.")
            else:
                return "No answer found. Try rephrasing your question."
        except Exception as e:
            return f"Web search failed: {e}"
