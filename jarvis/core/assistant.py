"""
Main Jarvis AI Assistant class.
Coordinates all components and handles the main interaction loop.
"""

import time
import json
from typing import Optional
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory

# Import core components
from .config import config
from .speech import SpeechManager

# Import LLM
from ..llm.mistral import create_mistral_llm

# Import tools
from ..tools.calender_tool import CalendarTool
from ..tools.email_tool import EmailTool
from ..tools.weather_tool import WeatherTool
from ..tools.music_tool import MusicTool
from ..tools.timer_tool import TimerTool
from ..tools.news_tool import NewsTool

# Import utilities
from ..utils.text_processing import parse_command_intent, contains_wake_word


import os
print("[DEBUG] GEMINI_API_KEY:", os.getenv("GEMINI_API_KEY"))
print("[DEBUG] SERP_API_KEY:", os.getenv("SERP_API_KEY"))


class AgenticJarvis:
    """Main Jarvis AI Assistant class with LangChain integration."""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize the LangChain-powered Jarvis assistant."""
        self.gemini_api_key = gemini_api_key or getattr(config, 'gemini_api_key', None)
        self.listening_for_wake_word = True
        # Initialize components
        self.speech_manager = SpeechManager()
        self.llm = None
        self.tools = []  # Ensure self.tools always exists
        self.setup_langchain()
        # Display startup information
        self.display_capabilities()
    
    def setup_langchain(self):
        """Initialize LangChain components."""
        try:
            if self.gemini_api_key:
                from jarvis.llm.gemini import GeminiLLM
                self.llm = GeminiLLM(api_key=self.gemini_api_key)
            else:
                raise RuntimeError("No valid LLM API key found. Please set GEMINI_API_KEY.")

            # Initialize tools
            from jarvis.tools.web_search_tool import WebSearchTool
            self.tools = [
                CalendarTool(),
                EmailTool(),
                WeatherTool(),
                MusicTool(),
                TimerTool(),
                NewsTool(),
                WebSearchTool()
            ]

            # Initialize memory
            self.memory = ConversationBufferWindowMemory(
                memory_key="chat_history",
                k=10,
                return_messages=True
            )

            # Initialize agent if LLM is available
            if self.llm:
                self.agent = initialize_agent(
                    tools=self.tools,
                    llm=self.llm,
                    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
                    memory=self.memory,
                    verbose=False,
                    max_iterations=3,
                    early_stopping_method="generate"
                )
                print("✅ LangChain Agent: Ready")
            else:
                self.agent = None
                print("⚠️  LangChain Agent: Not available without LLM")
            
        except Exception as e:
            print(f"❌ LangChain setup error: {e}")
            self.agent = None
    
    def display_capabilities(self):
        """Display assistant capabilities and configuration status."""
        print("\n" + "="*70)
        print(f"🤖 {config.assistant_name.upper()} - LANGCHAIN-POWERED AI ASSISTANT")
        print("="*70)
        print(f"🎤 Say '{config.wake_words[0].title()}' to activate!")
        
        # Show service status
        status = config.validate_config()
        print(f"\n🔧 SERVICE STATUS:")
        print(f"🧠 Mistral LLM: {'✅ Ready' if status['mistral_llm'] else '⚠️  Limited'}")
        print(f"📅 Google Calendar: {'✅ Ready' if status['google_calendar'] else '⚠️  Not configured'}")
        print(f"📧 Email: {'✅ Ready' if status['email'] else '⚠️  Not configured'}")
        print(f"📰 News API: {'✅ Ready' if status['news_api'] else '⚠️  Using free sources'}")
        
        print(f"\n🚀 ENHANCED CAPABILITIES:")
        print("📅 Smart Calendar - 'Schedule team meeting tomorrow at 3 PM'")
        print("⏰ Intelligent Timers - 'Set a 10 minute timer for my pasta'")
        print("📰 Real-time News - 'Get me the latest technology news'")
        print("🎵 Music Control - 'Play some jazz on Spotify'")
        print("📧 Email Management - 'Check my emails and send reply'")
        print("🌤️  Weather Updates - 'What's the weather like in Tokyo?'")
        print("🧠 Advanced Q&A - 'Explain blockchain with examples'")
        print("🔗 Tool Chaining - Complex multi-step tasks")
        print("💭 Context Memory - Remembers conversation context")
        print("😴 Sleep Mode - 'Sleep' or 'Standby'")
        print("❌ Exit - 'Exit' or 'Quit'")
        print("="*70)
    
    def process_with_langchain(self, user_input: str) -> str:
        """Process user input using LangChain agent."""
        try:
            if self.agent:
                # Use LangChain agent for intelligent processing
                response = self.agent.run(input=user_input)
                return response
            else:
                # Fallback to basic tool processing
                return self.basic_tool_processing(user_input)
                
        except Exception as e:
            print(f"❌ LangChain processing error: {e}")
            return self.basic_tool_processing(user_input)
    
    def basic_tool_processing(self, user_input: str) -> str:
        """Basic tool processing without LangChain agent."""
        try:
            # Parse user intent
            intent_info = parse_command_intent(user_input)
            intent = intent_info['intent']
            params = intent_info['parameters']
            
            # Route to appropriate tool
            if intent == 'calendar' and len(self.tools) > 0:
                return self.tools[0]._run(json.dumps(params))
            elif intent == 'email' and len(self.tools) > 1:
                return self.tools[1]._run(params.get('action', 'check'))
            elif intent == 'weather' and len(self.tools) > 2:
                location = params.get('location', 'current location')
                return self.tools[2]._run(location)
            elif intent == 'music' and len(self.tools) > 3:
                return self.tools[3]._run(json.dumps(params))
            elif intent == 'timer' and len(self.tools) > 4:
                return self.tools[4]._run(user_input)
            elif intent == 'news' and len(self.tools) > 5:
                category = params.get('category', 'general')
                return self.tools[5]._run(category)
            elif len(self.tools) > 6:
                # Use WebSearchTool for general queries
                return self.tools[6]._run(user_input)
            else:
                print("[DEBUG] Fallback response triggered for input:", user_input)
                return "I'm not sure how to help with that. Try asking about calendar, email, weather, music, timers, news, or just have a conversation with me!"
                
        except Exception as e:
            return f"I encountered an error processing your request: {str(e)}"
    
    def handle_general_query(self, user_input: str) -> str:
        """Handle general queries and conversations. Uses WebSearchTool for general knowledge."""
        user_lower = user_input.lower()
        if any(word in user_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return "Hello! How can I assist you today?"
        elif any(word in user_lower for word in ['thank', 'thanks', 'appreciate']):
            return "You're welcome! Is there anything else I can help you with?"
        elif any(word in user_lower for word in ['help', 'what can you do', 'capabilities']):
            return "I can help you with: Calendar, Email, Weather, Music, Timers, News, and answering general questions. Just ask me naturally!"
        elif any(word in user_lower for word in ['how are you', 'status', 'working']):
            return "I'm working perfectly and ready to help!"
        else:
            # Use WebSearchTool for general knowledge questions
            if hasattr(self, 'tools') and len(self.tools) > 6:
                return self.tools[6]._run(user_input)
            return "I'm not sure how to help with that. Try asking about calendar, email, weather, music, timers, news, or just have a conversation with me!"
    
    def process_command(self, text: str) -> str:
        """Process user command using LangChain or basic processing."""
        if not text or text == "timeout":
            return "continue"
        
        # Handle control commands
        control_result = self.handle_control_commands(text)
        if control_result != "continue":
            return control_result
        
        # Process with LangChain or basic processing
        try:
            response = self.process_with_langchain(text)
            self.speech_manager.speak(response)
            return "continue"
        except Exception as e:
            error_msg = f"I encountered an error: {str(e)}. Please try again."
            self.speech_manager.speak(error_msg)
            return "continue"
    
    def handle_control_commands(self, text: str) -> str:
        """Handle system control commands."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['sleep', 'standby', 'go to sleep']):
            self.speech_manager.speak(f"Going to sleep mode. Say '{config.wake_words[0]}' to wake me up.")
            self.listening_for_wake_word = True
            return "sleep"
        
        elif any(word in text_lower for word in ['exit', 'quit', 'goodbye', 'bye']):
            self.speech_manager.speak("Goodbye! It was great assisting you today.")
            return "exit"
        
        elif any(word in text_lower for word in ['help', 'what can you do', 'capabilities']):
            help_text = """I can help you with:
            Calendar scheduling and management
            Email checking and sending
            Weather updates for any location
            Playing music on various platforms
            Setting timers and reminders
            Getting latest news and headlines
            Answering questions and having conversations
            And much more! Just ask me naturally."""
            self.speech_manager.speak(help_text)
            return "continue"
        
        return "continue"
    
    def run(self):
        """Main execution loop."""
        try:
            print(f"\n🚀 {config.assistant_name} is now active and ready!")
            self.speech_manager.speak(f"Hello! I'm {config.assistant_name}, your LangChain-powered AI assistant. I'm ready to help you with advanced tasks!")
            
            while True:
                try:
                    if self.listening_for_wake_word:
                        # Wait for wake word
                        if self.speech_manager.listen_for_wake_word():
                            self.speech_manager.speak("Yes, how can I help you?")
                            self.listening_for_wake_word = False
                        continue
                    
                    # Listen for command
                    user_input = self.speech_manager.listen()
                    
                    if user_input:
                        result = self.process_command(user_input)
                        
                        if result == "exit":
                            break
                        elif result == "sleep":
                            continue
                        elif result == "continue":
                            # Ask if user needs more help
                            self.speech_manager.speak("Is there anything else I can help you with?")
                            
                            # Wait for response
                            response = self.speech_manager.listen()
                            if response and any(word in response for word in ['no', 'nothing', 'that\'s all', 'thanks']):
                                self.speech_manager.speak(f"Alright! I'll go back to listening for '{config.wake_words[0]}'.")
                                self.listening_for_wake_word = True
                            elif response == "timeout":
                                self.speech_manager.speak(f"I'll go back to listening for '{config.wake_words[0]}'.")
                                self.listening_for_wake_word = True
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Keyboard interrupt detected")
                    self.speech_manager.speak("Goodbye!")
                    break
                except Exception as e:
                    print(f"❌ Error in main loop: {e}")
                    self.speech_manager.speak("I encountered an error. Let me restart.")
                    time.sleep(2)
                    continue
        
        except Exception as e:
            print(f"❌ Critical error: {e}")
            self.speech_manager.speak("I'm experiencing technical difficulties. Please restart me.")
    
    def get_status(self) -> dict:
        """Get current status of the assistant."""
        return {
            'listening_for_wake_word': self.listening_for_wake_word,
            'llm_available': self.llm is not None,
            'agent_available': self.agent is not None,
            'tools_count': len(self.tools),
            'services_status': config.validate_config()
        }