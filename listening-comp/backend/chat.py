# Create GeminiChat
# chat.py
from google import genai
import streamlit as st
import os
from typing import Optional, Dict, Any, List

# Model ID - Using the specific model requested with the full path
MODEL_ID = "models/gemini-2.0-flash"

# Function to load API key from environment or various locations
def get_gemini_api_key():
    # First try from environment variable
    api_key = os.environ.get("GEMINI_API_KEY", "")
    
    # If not in environment, try from streamlit secrets
    if not api_key:
        # Try direct access first
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except:
            api_key = ""
        
        # If that doesn't work, try fallback approaches
        if not api_key:
            try:
                # Try to read from the file directly if Streamlit secrets aren't working
                secrets_paths = [
                    # From project root
                    os.path.join(os.getcwd(), ".streamlit", "secrets.toml"),
                    # From frontend directory
                    os.path.join(os.getcwd(), "frontend", ".streamlit", "secrets.toml"),
                    # From one directory up 
                    os.path.join(os.path.dirname(os.getcwd()), ".streamlit", "secrets.toml")
                ]
                
                for path in secrets_paths:
                    if os.path.exists(path):
                        print(f"Found secrets file: {path}")
                        with open(path, 'r') as f:
                            for line in f:
                                if "GEMINI_API_KEY" in line:
                                    # Simple parsing of "KEY = value" format
                                    api_key = line.split('=')[1].strip().strip('"').strip("'")
                                    break
                        if api_key:
                            break
            except Exception as e:
                print(f"Error reading secrets file: {str(e)}")
    
    if not api_key:
        print("❌ API key not found! Please check your secrets.toml file or set GEMINI_API_KEY environment variable.")
    else:
        print("✅ API key found!")
        
    return api_key

class GeminiChat:
    def __init__(self, model_id: str = MODEL_ID):
        """Initialize Gemini chat client"""
        # Get API key using our robust method
        self.api_key = get_gemini_api_key()
        
        if not self.api_key:
            print("WARNING: No API key found. Chat functionality will not work.")
        
        # Create the Gemini client
        self.client = genai.Client(api_key=self.api_key)
        
        # Store the model ID
        self.model_id = model_id
        
        # Initialize chat history
        self.messages = []
    
    def generate_response(self, message: str, inference_config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Generate a response using Google Gemini API
        
        Args:
            message: Current user message
            inference_config: Configuration parameters for the model
        """
        try:
            # Add the new message to our history
            self.messages.append({"role": "user", "parts": [{"text": message}]})
            
            # Call the generate_content method with the full conversation history
            model = self.client.get_model(self.model_id)
            response = model.generate_content(
                self.messages,
                **(inference_config or {})
            )
            
            # Process the response
            if response and hasattr(response, "text"):
                # Add the response to our history
                self.messages.append({"role": "model", "parts": [{"text": response.text}]})
                return response.text
            else:
                print(f"No valid response received from the model. Response: {response}")
                return None
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            # Log the full error details for debugging
            import traceback
            import logging
            logging.error(traceback.format_exc())
            return None
    
    def reset_chat(self):
        """Reset the chat history"""
        self.messages = []


if __name__ == "__main__":
    # Test API key access
    api_key = get_gemini_api_key()
    print(f"API key found (masked): {api_key[:4]}...{api_key[-4:] if api_key else ''}")
    
    # Test chat
    chat = GeminiChat()
    while True:
        user_input = input("You: ")
        if user_input.lower() == '/exit':
            break
        response = chat.generate_response(user_input)
        print("Bot:", response)