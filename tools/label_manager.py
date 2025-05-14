from googleapiclient.discovery import build
from .base_tool import BaseTool

class LabelManager(BaseTool):
    """Tool for managing Gmail labels"""
    
    def __init__(self):
        super().__init__()
        self.service = None
    
    def _ensure_service(self):
        """Ensure we have an authenticated Gmail service"""
        self.ensure_authenticated()
        if not self.service:
            self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def list_labels(self) -> str:
        """List all Gmail labels"""
        try:
            self._ensure_service()
            
            # Get all labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            if not labels:
                return "No labels found."
            
            # Format labels
            label_list = []
            for label in labels:
                label_list.append(f"""
Label ID: {label['id']}
Name: {label['name']}
Type: {label['type']}
""")
            
            return "Gmail Labels:\n\n" + "\n".join(label_list)
            
        except Exception as e:
            return f"Error listing labels: {str(e)}"
    
    def add_label_to_email(self, label_name: str, email_id: str) -> str:
        """Add a label to an email"""
        try:
            self._ensure_service()
            
            # Get or create the label
            label_id = self._get_or_create_label(label_name)
            
            # Modify the email's labels
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            return f"Successfully added label '{label_name}' to email {email_id}"
            
        except Exception as e:
            return f"Error adding label: {str(e)}"
    
    def remove_label_from_email(self, label_name: str, email_id: str) -> str:
        """Remove a label from an email"""
        try:
            self._ensure_service()
            
            # Get the label ID
            label_id = self._get_label_id(label_name)
            if not label_id:
                return f"Label '{label_name}' not found"
            
            # Modify the email's labels
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': [label_id]}
            ).execute()
            
            return f"Successfully removed label '{label_name}' from email {email_id}"
            
        except Exception as e:
            return f"Error removing label: {str(e)}"
    
    def _get_or_create_label(self, label_name: str) -> str:
        """Get a label ID by name or create it if it doesn't exist"""
        # Try to get existing label
        label_id = self._get_label_id(label_name)
        if label_id:
            return label_id
        
        # Create new label
        label = self.service.users().labels().create(
            userId='me',
            body={
                'name': label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show'
            }
        ).execute()
        
        return label['id']
    
    def _get_label_id(self, label_name: str) -> str:
        """Get a label ID by name"""
        results = self.service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        for label in labels:
            if label['name'].lower() == label_name.lower():
                return label['id']
        
        return None 