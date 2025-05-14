from googleapiclient.discovery import build
from .base_tool import BaseTool

class EmailAnalyzer(BaseTool):
    """Tool for analyzing emails"""
    
    def __init__(self):
        super().__init__()
        self.service = None
    
    def _ensure_service(self):
        """Ensure we have an authenticated Gmail service"""
        self.ensure_authenticated()
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def analyze_email(self, email_id: str) -> str:
        """Analyze an email by its ID"""
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
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown date')
            
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
            
            analysis = f"""
Email Analysis:
--------------
From: {from_email}
Date: {date}
Subject: {subject}

Content Summary:
{decoded_body[:500]}{'...' if len(decoded_body) > 500 else ''}
"""
            return analysis
            
        except Exception as e:
            return f"Error analyzing email: {str(e)}"
    
    def list_recent_emails(self, count: int = 5) -> str:
        """List recent emails"""
        try:
            self._ensure_service()
            
            # Get recent messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=count,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return "No recent emails found."
            
            email_list = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No subject')
                from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown sender')
                date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown date')
                
                email_list.append(f"""
Email ID: {msg['id']}
From: {from_email}
Date: {date}
Subject: {subject}
""")
            
            return "\n".join(email_list)
            
        except Exception as e:
            return f"Error listing emails: {str(e)}" 