# Create GeminiChat
# chat.py
from google import genai
import streamlit as st
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
load_dotenv()

# Model ID used for the LLM
MODEL_ID = "gemini-2.0-flash"

class GeminiChat:
    def __init__(self, model_id: str = MODEL_ID):
        """Initialize Gemini chat client"""
        self.api_key = os.getenv("GEMINI_API_KEY")      
        if not self.api_key:
            print("WARNING: No API key found. Chat functionality will not work.")
        
        # Create the Gemini client
        self.client = genai.Client(api_key=self.api_key)
        
        # Store the model ID
        self.model_id = MODEL_ID

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
            
            # Generate a response from the model
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=self.messages)
            
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
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API key found (masked): {api_key[:4]}...{api_key[-4:] if api_key else ''}")
    
    # Test chat
    chat = GeminiChat()
    while True:
        user_input = input("You: ")
        if user_input.lower() == '/exit':
            break
        response = chat.generate_response(user_input)
        print("Bot:", response)