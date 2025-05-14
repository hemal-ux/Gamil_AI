import requests
import json
from typing import List, Dict, Any
import os

class GmailMCP:
    def __init__(self):
        self.api_key = "AIzaSyAGRCq5pE__PlGSrt8bDXaco2YKP2XRqRM"
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.connected_email = None

    def set_connected_email(self, email: str):
        """Set the connected email address."""
        self.connected_email = email

    def get_connected_email(self) -> str:
        """Get the currently connected email address."""
        return self.connected_email if self.connected_email else "No email connected"

    def _call_gemini_api(self, prompt: str) -> str:
        """Make a direct API call to Gemini 2.0 Flash."""
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024,
                },
                "safetySettings": [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            }
            
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=self.headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
                return "No response generated."
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"

    def process_email_request(self, user_input: str) -> str:
        """Process email-related requests using Gemini 2.0 Flash."""
        context = """
        You are an email assistant powered by Gemini 2.0 Flash. You can help with:
        1. Drafting emails
        2. Summarizing emails
        3. Suggesting email responses
        4. Analyzing email content
        """
        
        full_prompt = f"{context}\n\nUser request: {user_input}"
        return self._call_gemini_api(full_prompt)

    def draft_email(self, to: str, subject: str, context: str) -> str:
        """Draft an email using Gemini 2.0 Flash."""
        prompt = f"""
        Draft a professional email with the following details:
        To: {to}
        Subject: {subject}
        Context: {context}
        
        Please provide a well-structured email that is professional and appropriate for the context.
        Use clear and concise language while maintaining a professional tone.
        """
        
        return self._call_gemini_api(prompt)

    def analyze_email(self, email_content: str) -> str:
        """Analyze email content using Gemini 2.0 Flash."""
        prompt = f"""
        Analyze the following email content and provide:
        1. Main points and key takeaways
        2. Tone and sentiment analysis
        3. Action items or requests (if any)
        4. Suggested response approach
        5. Potential follow-up questions
        
        Email content:
        {email_content}
        """
        
        return self._call_gemini_api(prompt)

    def suggest_response(self, email_content: str) -> str:
        """Suggest a response to an email using Gemini 2.0 Flash."""
        prompt = f"""
        Based on the following email, suggest a professional response:
        
        Original email:
        {email_content}
        
        Please provide a draft response that is:
        1. Professional and courteous
        2. Addresses all points in the original email
        3. Clear and concise
        4. Includes appropriate greetings and sign-offs
        5. Maintains a positive and constructive tone
        """
        
        return self._call_gemini_api(prompt) 