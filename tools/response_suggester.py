from googleapiclient.discovery import build
from .base_tool import BaseTool

class ResponseSuggester(BaseTool):
    """Tool for suggesting email responses"""
    
    def __init__(self):
        super().__init__()
        self.service = None
    
    def _ensure_service(self):
        """Ensure we have an authenticated Gmail service"""
        self.ensure_authenticated()
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def suggest_response(self, email_id: str) -> str:
        """Suggest a response for an email"""
        try:
            self._ensure_service()
            
            # Get the email
            message = self.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No subject')
            from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown sender')
            
            # Extract body
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                body = next((
                    part['body'].get('data', '')
                    for part in parts
                    if part['mimeType'] == 'text/plain'
                ), '')
            else:
                body = message['payload']['body'].get('data', '')
            
            import base64
            import quopri
            
            # Decode body
            try:
                decoded_body = base64.urlsafe_b64decode(body.encode('ASCII')).decode('utf-8')
            except:
                try:
                    decoded_body = quopri.decodestring(body).decode('utf-8')
                except:
                    decoded_body = "Could not decode email body"
            
            # Generate response suggestion
            suggestion = f"""
Suggested Response:
------------------
To: {from_email}
Subject: Re: {subject}

Dear {from_email.split('<')[0].strip()},

Thank you for your email regarding {subject}.

[Your response here based on the following email content:]

Original Email:
{decoded_body[:500]}{'...' if len(decoded_body) > 500 else ''}
"""
            return suggestion
            
        except Exception as e:
            return f"Error suggesting response: {str(e)}" 