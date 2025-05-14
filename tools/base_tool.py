from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
from typing import Optional

class BaseTool:
    """Base class for Gmail tools with authentication handling"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    
    def __init__(self):
        self.credentials = None
        self.connected_email = None
        self._client_id = None
        self._client_secret = None
        self._token_pickle = None
    
    def set_credentials(self, client_id: str, client_secret: str, token_pickle: Optional[str] = None):
        """Set OAuth credentials for the tool"""
        self._client_id = client_id
        self._client_secret = client_secret
        
        if token_pickle:
            try:
                # Convert hex string back to pickle bytes and load credentials
                pickle_bytes = bytes.fromhex(token_pickle)
                self.credentials = pickle.loads(pickle_bytes)
            except Exception as e:
                print(f"Error loading token pickle: {str(e)}")
                self.credentials = None
        else:
            # Try to load from token.pickle file if exists
            if os.path.exists("token.pickle"):
                try:
                    with open("token.pickle", "rb") as token:
                        self.credentials = pickle.load(token)
                except Exception as e:
                    print(f"Error loading token.pickle: {str(e)}")
                    self.credentials = None
            else:
                self.credentials = None
    
    def set_connected_email(self, email: str):
        """Set the email address to connect to"""
        self.connected_email = email
    
    def ensure_authenticated(self):
        """Ensure we have valid credentials"""
        if not self._client_id or not self._client_secret:
            raise ValueError("Client credentials not set. Please configure account first.")
        
        try:
            if not self.credentials:
                flow = InstalledAppFlow.from_client_config(
                    {
                        "installed": {
                            "client_id": self._client_id,
                            "client_secret": self._client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "redirect_uris": ["http://localhost"]
                        }
                    },
                    self.SCOPES
                )
                self.credentials = flow.run_local_server(port=0)
                
                # Save the credentials for future use
                with open("token.pickle", "wb") as token:
                    pickle.dump(self.credentials, token)
            
            elif not self.credentials.valid:
                if self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    # Save the refreshed credentials
                    with open("token.pickle", "wb") as token:
                        pickle.dump(self.credentials, token)
                else:
                    # If refresh token is missing, need to reauthorize
                    flow = InstalledAppFlow.from_client_config(
                        {
                            "installed": {
                                "client_id": self._client_id,
                                "client_secret": self._client_secret,
                                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                                "token_uri": "https://oauth2.googleapis.com/token",
                                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                                "redirect_uris": ["http://localhost"]
                            }
                        },
                        self.SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)
                    
                    # Save the new credentials
                    with open("token.pickle", "wb") as token:
                        pickle.dump(self.credentials, token)
        
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")
    
    def get_token_pickle(self) -> Optional[str]:
        """Get the token pickle as a hex string"""
        if self.credentials:
            return pickle.dumps(self.credentials).hex()
        return None 