from googleapiclient.discovery import build
from .base_tool import BaseTool

class EmailFinder(BaseTool):
    """Tool for finding emails"""
    
    def __init__(self):
        super().__init__()
        self.service = None
    
    def _ensure_service(self):
        """Ensure we have an authenticated Gmail service"""
        self.ensure_authenticated()
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def find_emails(self, query: str, count: int = 5) -> str:
        """Find emails matching the query"""
        try:
            self._ensure_service()
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=count
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return f"No emails found matching query: {query}"
            
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
            
            return f"Search Results for '{query}':\n\n" + "\n".join(email_list)
            
        except Exception as e:
            return f"Error finding emails: {str(e)}" 