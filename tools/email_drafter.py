from googleapiclient.discovery import build
from .base_tool import BaseTool

class EmailDrafter(BaseTool):
    """Tool for drafting and sending emails"""
    
    def __init__(self):
        super().__init__()
        self.service = None
    
    def _ensure_service(self):
        """Ensure we have an authenticated Gmail service"""
        self.ensure_authenticated()
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def draft_email(self, to: str, subject: str, context: str) -> str:
        """Draft an email with the given parameters"""
        try:
            self._ensure_service()
            
            # Create the email message
            message = {
                'message': {
                    'raw': self._create_message(to, subject, context)
                }
            }
            
            # Save the draft
            draft = self.service.users().drafts().create(
                userId='me',
                body=message
            ).execute()
            
            return f"Draft created successfully. Draft ID: {draft['id']}"
        except Exception as e:
            return f"Error creating draft: {str(e)}"
    
    def send_email(self, to: str, subject: str, context: str) -> str:
        """Send an email with the given parameters"""
        try:
            self._ensure_service()
            
            # Create the email message
            message = {
                'raw': self._create_message(to, subject, context)
            }
            
            # Send the email
            sent_message = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            return f"Email sent successfully. Message ID: {sent_message['id']}"
        except Exception as e:
            return f"Error sending email: {str(e)}"
    
    def _create_message(self, to: str, subject: str, body: str) -> str:
        """Create a base64 encoded email message"""
        from email.mime.text import MIMEText
        import base64
        
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        if self.connected_email:
            message['from'] = self.connected_email
        
        # Encode the message
        return base64.urlsafe_b64encode(message.as_bytes()).decode() 