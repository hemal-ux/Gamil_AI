from googleapiclient.discovery import build
from .base_tool import BaseTool

class EmailProcessor(BaseTool):
    """Tool for processing general email requests"""
    
    def __init__(self):
        super().__init__()
        self.service = None
    
    def _ensure_service(self):
        """Ensure we have an authenticated Gmail service"""
        self.ensure_authenticated()
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def process_email_request(self, request: str) -> str:
        """Process a general email request"""
        try:
            self._ensure_service()
            
            # Basic request handling
            request = request.lower()
            
            if "unread" in request:
                return self._get_unread_emails()
            elif "important" in request:
                return self._get_important_emails()
            elif "starred" in request:
                return self._get_starred_emails()
            else:
                return "I can help you with: unread emails, important emails, or starred emails"
            
        except Exception as e:
            return f"Error processing request: {str(e)}"
    
    def _get_unread_emails(self) -> str:
        """Get unread emails"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['UNREAD', 'INBOX'],
                maxResults=5
            ).execute()
            
            return self._format_email_list(results.get('messages', []), "Unread")
        except Exception as e:
            return f"Error getting unread emails: {str(e)}"
    
    def _get_important_emails(self) -> str:
        """Get important emails"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['IMPORTANT'],
                maxResults=5
            ).execute()
            
            return self._format_email_list(results.get('messages', []), "Important")
        except Exception as e:
            return f"Error getting important emails: {str(e)}"
    
    def _get_starred_emails(self) -> str:
        """Get starred emails"""
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['STARRED'],
                maxResults=5
            ).execute()
            
            return self._format_email_list(results.get('messages', []), "Starred")
        except Exception as e:
            return f"Error getting starred emails: {str(e)}"
    
    def _format_email_list(self, messages: list, category: str) -> str:
        """Format a list of email messages"""
        if not messages:
            return f"No {category.lower()} emails found."
        
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
        
        return f"{category} Emails:\n\n" + "\n".join(email_list) 