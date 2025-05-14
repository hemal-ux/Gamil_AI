import requests
import json
from typing import List, Dict, Any
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import socket
from urllib.parse import urlparse, parse_qs

class BaseMCP:
    def __init__(self):
        self.api_key = "AIzaSyAGRCq5pE__PlGSrt8bDXaco2YKP2XRqRM"
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.headers = {
            'Content-Type': 'application/json'
        }
        self.connected_email = None
        self.credentials = None
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
                      'https://www.googleapis.com/auth/gmail.send',
                      'https://www.googleapis.com/auth/gmail.modify']
        self.CLIENT_SECRET_FILE = 'client_secret.json'
        self._authenticate()

    def _authenticate(self):
        """Authenticate using Google OAuth."""
        creds = None
        # The file token.pickle stores the user's access and refresh tokens
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CLIENT_SECRET_FILE,
                    self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.credentials = creds
        
        # Get user's email address
        try:
            service = build('gmail', 'v1', credentials=creds)
            profile = service.users().getProfile(userId='me').execute()
            self.connected_email = profile['emailAddress']
        except Exception as e:
            print(f"Error getting email address: {str(e)}")
            self.connected_email = "Error connecting email"

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