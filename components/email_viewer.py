import gradio as gr
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
import pickle
import base64
from bs4 import BeautifulSoup
import google.generativeai as genai

class EmailViewer:
    def __init__(self, account_manager):
        self.account_manager = account_manager
        self.service = None
        self.model = None
    
    def _ensure_service(self):
        """Ensure we have an authenticated Gmail service"""
        # Get active account
        active_account = self.account_manager.get_active_account()
        if not active_account:
            raise ValueError("No active account selected. Please select an account in Account Management first.")
        
        if not active_account.is_active:
            raise ValueError("Selected account is not active. Please switch to it in Account Management first.")
        
        if not active_account.token_pickle:
            raise ValueError("Account not authenticated. Please authenticate the account first.")
        
        try:
            # Convert token pickle back to credentials
            credentials = pickle.loads(bytes.fromhex(active_account.token_pickle))
            
            # Create new service with these credentials
            self.service = build('gmail', 'v1', credentials=credentials)
            
            # Configure Gemini with the account's API key
            if active_account.gemini_api_key:
                genai.configure(api_key=active_account.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-001')
            else:
                self.model = None
                
        except Exception as e:
            raise ValueError(f"Error creating Gmail service: {str(e)}")
    
    def _get_email_summary(self, body_text: str) -> str:
        """Get a summary of the email content using Gemini"""
        try:
            if not self.model:
                return "Email summary not available. Please add a Gemini API key in Account Management."
                
            # Clean and truncate the text
            clean_text = ' '.join(body_text.strip().split())  # Normalize whitespace
            if len(clean_text) > 1000:
                clean_text = clean_text[:1000] + "..."
            
            if not clean_text:
                return "No content to summarize"
            
            # Generate summary
            prompt = f"Summarize this email content in 1-2 clear, informative sentences:\n\n{clean_text}"
            response = self.model.generate_content(prompt, generation_config={
                'temperature': 0.3,
                'top_p': 0.8,
                'top_k': 40,
                'max_output_tokens': 150
            })
            return response.text.strip()
        except Exception as e:
            return f"Could not generate summary: {str(e)}"
    
    def _get_email_body(self, msg) -> str:
        """Extract email body text from the message"""
        if 'payload' not in msg:
            return ""
        
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        text = base64.urlsafe_b64decode(part['body']['data']).decode()
                        return text
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html = base64.urlsafe_b64decode(part['body']['data']).decode()
                        soup = BeautifulSoup(html, 'html.parser')
                        return soup.get_text()
        elif 'body' in msg['payload']:
            if 'data' in msg['payload']['body']:
                text = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode()
                return text
        
        return ""
    
    def _has_attachments(self, msg) -> bool:
        """Check if the email has attachments"""
        if 'payload' not in msg:
            return False
        
        def check_parts(parts):
            for part in parts:
                if 'filename' in part and part['filename']:
                    return True
                if 'parts' in part:
                    if check_parts(part['parts']):
                        return True
            return False
        
        if 'parts' in msg['payload']:
            return check_parts(msg['payload']['parts'])
        elif 'body' in msg['payload'] and 'attachmentId' in msg['payload']['body']:
            return True
            
        return False
    
    def get_past_10_days(self):
        """Get list of past 10 days in YYYY-MM-DD format"""
        dates = []
        for i in range(10):
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))
        return dates
    
    def _format_email_html(self, msg, message_id: str) -> str:
        """Format a single email as HTML"""
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
        
        # Get email body and generate summary
        body_text = self._get_email_body(msg)
        summary = self._get_email_summary(body_text) if body_text else "No content to summarize"
        
        # Check for attachments
        has_attachments = self._has_attachments(msg)
        
        # Create Gmail link
        gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{message_id}"
        
        return f"""
        <div class="email-container">
            <div class="email-header">
                <div class="email-field">
                    <span class="email-label">From:</span>
                    <span class="email-value">{sender}</span>
                </div>
                <div class="email-field">
                    <span class="email-label">Subject:</span>
                    <span class="email-value">{subject}</span>
                </div>
                <div class="email-field">
                    <span class="email-label">Date:</span>
                    <span class="email-value">{date}</span>
                </div>
                <div class="email-field">
                    <span class="email-label">Attachments:</span>
                    <span class="{'attachment-yes' if has_attachments else 'attachment-no'}">
                        {' Yes' if has_attachments else ' No'}
                    </span>
                </div>
            </div>
            <div class="tools-section">
                <div class="tools-header">Tools & Actions</div>
                <div class="tools-grid">
                    <a href="{gmail_link}" target="_blank" class="tool-button">
                        <span class="tool-icon">📧</span>
                        <span class="tool-text">Open in Gmail</span>
                    </a>
                    <button onclick="navigator.clipboard.writeText('{message_id}')" class="tool-button">
                        <span class="tool-icon">📋</span>
                        <span class="tool-text">Copy Message ID</span>
                    </button>
                    {f'''
                    <a href="{gmail_link}/attachments" target="_blank" class="tool-button" style="background-color: #34d399;">
                        <span class="tool-icon">📎</span>
                        <span class="tool-text">View Attachments</span>
                    </a>
                    ''' if has_attachments else ''}
                </div>
            </div>
            <div class="email-summary">
                <div class="email-field">
                    <span class="email-label">Summary:</span>
                    <span class="email-value">{summary}</span>
                </div>
            </div>
        </div>
        """
    
    def get_recent_emails(self, max_results=10):
        """Get recent emails"""
        try:
            # Check if we have any active account first
            active_account = self.account_manager.get_active_account()
            if not active_account or not active_account.is_active:
                return """
                <div style="padding: 20px; background-color: #44403c; border: 1px solid #78716c; border-radius: 8px; margin: 20px 0; color: #fafaf9;">
                    <div style="font-size: 16px; margin-bottom: 10px;">
                        <span style="color: #f59e0b; margin-right: 8px;">⚠️</span>
                        <strong>No Active Account</strong>
                    </div>
                    <p style="margin: 0; font-size: 14px;">
                        Please select and activate an account in the Account Management section to view emails.
                    </p>
                </div>
                """

            self._ensure_service()
            
            # Get messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return "No emails found."
            
            # Add CSS styles for email formatting
            email_style = """
            <style>
                body {
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                }
                .email-container {
                    border: 1px solid #3d4144;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 25px;
                    background-color: #2d2d2d;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
                .email-header {
                    margin-bottom: 15px;
                    padding-bottom: 15px;
                    border-bottom: 2px solid #404040;
                }
                .email-field {
                    margin: 8px 0;
                    line-height: 1.5;
                }
                .email-label {
                    font-weight: 600;
                    color: #9ca3af;
                    display: inline-block;
                    width: 130px;
                    font-size: 14px;
                }
                .email-value {
                    color: #e0e0e0;
                    font-size: 14px;
                    word-break: break-word;
                }
                .email-summary {
                    margin-top: 15px;
                    padding: 15px;
                    background-color: #363636;
                    border-radius: 6px;
                    border: 1px solid #404040;
                }
                .tools-section {
                    margin: 15px 0;
                    padding: 12px;
                    background-color: #363636;
                    border-radius: 6px;
                }
                .tools-header {
                    font-weight: 500;
                    color: #9ca3af;
                    margin-bottom: 8px;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                .tools-grid {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                }
                .tool-button {
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 6px 10px;
                    background-color: #2563eb;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;
                    font-size: 12px;
                    font-weight: 500;
                    transition: all 0.2s ease;
                    min-width: 100px;
                    justify-content: center;
                }
                .tool-button:hover {
                    background-color: #1d4ed8;
                    transform: translateY(-1px);
                }
                .tool-icon {
                    font-size: 14px;
                }
                .attachment-yes {
                    color: #34d399;
                    font-weight: 600;
                    background-color: rgba(52, 211, 153, 0.1);
                    padding: 2px 8px;
                    border-radius: 12px;
                }
                .attachment-no {
                    color: #f87171;
                    font-weight: 600;
                    background-color: rgba(248, 113, 113, 0.1);
                    padding: 2px 8px;
                    border-radius: 12px;
                }
                .no-account-warning {
                    padding: 20px;
                    background-color: #44403c;
                    border: 1px solid #78716c;
                    border-radius: 8px;
                    margin: 20px 0;
                    color: #fafaf9;
                    font-size: 14px;
                }
                .warning-icon {
                    color: #f59e0b;
                    font-size: 18px;
                    margin-right: 8px;
                }
            </style>
            """
            
            # Check if we have a Gemini API key
            if not active_account.gemini_api_key:
                email_style += """
                <div class="no-account-warning">
                    <div class="warning-header">
                        <span class="warning-icon">⚠️</span>
                        <strong>No Gemini API Key</strong>
                    </div>
                    <p class="warning-message">
                        Email summaries are disabled. Please add your Gemini API key in Account Management to enable summaries.
                    </p>
                </div>
                """
            
            # Get full message details and format output
            email_details = [email_style]
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                email_details.append(self._format_email_html(msg, message['id']))
            
            return "\n".join(email_details)
            
        except Exception as e:
            return f"Error fetching emails: {str(e)}"
    
    def get_emails_by_date(self, date_str):
        """Get emails from a specific date"""
        try:
            # Check if we have any active account first
            active_account = self.account_manager.get_active_account()
            if not active_account or not active_account.is_active:
                return f"""
                <div style="padding: 20px; background-color: #44403c; border: 1px solid #78716c; border-radius: 8px; margin: 20px 0; color: #fafaf9;">
                    <div style="font-size: 16px; margin-bottom: 10px;">
                        <span style="color: #f59e0b; margin-right: 8px;">⚠️</span>
                        <strong>No Active Account</strong>
                    </div>
                    <p style="margin: 0; font-size: 14px;">
                        Please select and activate an account in the Account Management section to view emails.
                    </p>
                </div>
                """

            self._ensure_service()
            
            # Create date range query
            date = datetime.strptime(date_str, "%Y-%m-%d")
            next_date = date + timedelta(days=1)
            query = f"after:{date.strftime('%Y/%m/%d')} before:{next_date.strftime('%Y/%m/%d')}"
            
            # Get messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                labelIds=['INBOX']
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                return f"No emails found for {date_str}"
            
            # Add CSS styles for email formatting
            email_style = """
            <style>
                body {
                    background-color: #1a1a1a;
                    color: #e0e0e0;
                }
                .email-container {
                    border: 1px solid #3d4144;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 25px;
                    background-color: #2d2d2d;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
                }
                .email-header {
                    margin-bottom: 15px;
                    padding-bottom: 15px;
                    border-bottom: 2px solid #404040;
                }
                .email-field {
                    margin: 8px 0;
                    line-height: 1.5;
                }
                .email-label {
                    font-weight: 600;
                    color: #9ca3af;
                    display: inline-block;
                    width: 130px;
                    font-size: 14px;
                }
                .email-value {
                    color: #e0e0e0;
                    font-size: 14px;
                    word-break: break-word;
                }
                .email-summary {
                    margin-top: 15px;
                    padding: 15px;
                    background-color: #363636;
                    border-radius: 6px;
                    border: 1px solid #404040;
                }
                .gmail-link {
                    display: inline-block;
                    padding: 8px 16px;
                    background-color: #2563eb;
                    color: white !important;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 10px 10px 10px 0;
                    font-weight: 600;
                    font-size: 14px;
                }
                .gmail-link:hover {
                    background-color: #1d4ed8;
                }
                .copy-id {
                    display: inline-block;
                    cursor: pointer;
                    color: #60a5fa;
                    text-decoration: underline;
                    margin: 10px 0;
                    padding: 8px 16px;
                    background-color: #374151;
                    border: 1px solid #4b5563;
                    border-radius: 6px;
                    font-size: 14px;
                }
                .copy-id:hover {
                    background-color: #4b5563;
                }
                .attachment-yes {
                    color: #34d399;
                    font-weight: 600;
                    background-color: rgba(52, 211, 153, 0.1);
                    padding: 2px 8px;
                    border-radius: 12px;
                }
                .attachment-no {
                    color: #f87171;
                    font-weight: 600;
                    background-color: rgba(248, 113, 113, 0.1);
                    padding: 2px 8px;
                    border-radius: 12px;
                }
                .action-buttons {
                    margin: 15px 0;
                    padding: 10px 0;
                    border-top: 1px solid #404040;
                    border-bottom: 1px solid #404040;
                }
            </style>
            """
            
            # Get full message details and format output
            email_details = [email_style]
            for message in messages:
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
                
                # Get email body and generate summary
                body_text = self._get_email_body(msg)
                summary = self._get_email_summary(body_text) if body_text else "No content to summarize"
                
                # Check for attachments
                has_attachments = self._has_attachments(msg)
                
                # Create Gmail link
                gmail_link = f"https://mail.google.com/mail/u/0/#inbox/{message['id']}"
                
                email_details.append(f"""
                <div class="email-container">
                    <div class="email-header">
                        <div class="email-field">
                            <span class="email-label">From:</span>
                            <span class="email-value">{sender}</span>
                        </div>
                        <div class="email-field">
                            <span class="email-label">Subject:</span>
                            <span class="email-value">{subject}</span>
                        </div>
                        <div class="email-field">
                            <span class="email-label">Date:</span>
                            <span class="email-value">{date}</span>
                        </div>
                        <div class="email-field">
                            <span class="email-label">Attachments:</span>
                            <span class="{'attachment-yes' if has_attachments else 'attachment-no'}">
                                {' Yes' if has_attachments else ' No'}
                            </span>
                        </div>
                    </div>
                    <div class="action-buttons">
                        <a href="{gmail_link}" target="_blank" class="gmail-link">Open in Gmail</a>
                        <span class="copy-id" onclick="navigator.clipboard.writeText('{message['id']}')">
                            Copy Message ID
                        </span>
                    </div>
                    <div class="email-summary">
                        <div class="email-field">
                            <span class="email-label">Summary:</span>
                            <span class="email-value">{summary}</span>
                        </div>
                    </div>
                </div>
                """)
            
            return "\n".join(email_details)
            
        except Exception as e:
            return f"Error fetching emails: {str(e)}"
    
    def handle_date_selection(self, manual_date, dropdown_date):
        """Handle date selection from either input"""
        selected_date = manual_date if manual_date else dropdown_date
        if not selected_date:
            return "No date selected", "Please select a date"
        
        try:
            # Validate date format
            datetime.strptime(selected_date, "%Y-%m-%d")
            return f"Selected: {selected_date}", self.get_emails_by_date(selected_date)
        except ValueError:
            return "Invalid date format", "Please use YYYY-MM-DD format"
    
    def create_interface(self):
        """Create the email viewer interface"""
        with gr.Column() as email_viewer:
            with gr.Row():
                # Compact refresh button
                refresh_btn = gr.Button("🔄 Refresh", size="sm")
            
            with gr.Row():
                # Manual date input
                date_input = gr.Textbox(
                    placeholder="Enter date (YYYY-MM-DD)",
                    label="Select Date"
                )
                
                # Past 10 days dropdown
                dates_dropdown = gr.Dropdown(
                    choices=self.get_past_10_days(),
                    label="Quick Select Date",
                    value=None
                )
            
            # OK button to confirm date selection
            with gr.Row():
                ok_btn = gr.Button("✓ OK", size="sm", variant="primary")
            
            # Display areas for selected date and emails
            date_label = gr.Label(label="Selected Date")
            emails_display = gr.HTML(
                label="Emails",
                value="Please click Refresh to load emails."
            )
            
            # Connect refresh button to update emails
            refresh_btn.click(
                fn=self.get_recent_emails,
                outputs=emails_display
            )
            
            # Handle OK button click
            ok_btn.click(
                fn=self.handle_date_selection,
                inputs=[date_input, dates_dropdown],
                outputs=[date_label, emails_display]
            )
            
        return email_viewer 