#!/usr/bin/env python3
"""
Jarvis AI Assistant - Main Entry Point
A LangChain-powered voice assistant with advanced capabilities.
"""

import os
import sys
from jarvis.core.assistant import AgenticJarvis


def main():
    """Main function to initialize and run Jarvis."""
    print("🔧 Initializing Jarvis AI Assistant...")
    
    # Get Gemini API key from environment
    gemini_api_key = os.getenv('GEMINI_API_KEY')

    if not gemini_api_key:
        print("\n⚠️  GEMINI_API_KEY not found in environment variables.")
        print("Please set up your .env file with GEMINI_API_KEY and try again.")
        return

    try:
        # Initialize Jarvis with Gemini only
        jarvis = AgenticJarvis(gemini_api_key=gemini_api_key)
        # Run the assistant
        jarvis.run()
    except KeyboardInterrupt:
        print("\n👋 Jarvis shutdown initiated")
    except Exception as e:
        print(f"❌ Failed to start Jarvis: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()