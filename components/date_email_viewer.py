import gradio as gr
from tools import EmailFinder, EmailAnalyzer
from datetime import datetime

class DateEmailViewer:
    def __init__(self):
        self.email_finder = EmailFinder()
        self.email_analyzer = EmailAnalyzer()
    
    def get_emails_by_date(self, date_str):
        """Fetch emails for a specific date"""
        try:
            # Convert date string to proper format for Gmail search
            selected_date = datetime.strptime(date_str, "%Y-%m-%d")
            formatted_date = selected_date.strftime("%Y/%m/%d")
            
            # Use EmailFinder to get emails from specific date
            search_query = f"after:{formatted_date} before:{formatted_date}+1d"
            emails_response = self.email_finder.find_emails(search_query, 50)  # Increased count for daily emails
            
            if "No emails found" in emails_response:
                return "No emails found for this date."
            
            # Parse the response to get individual email details
            email_sections = emails_response.split("\n\n")[1:]  # Skip the header
            
            formatted_emails = []
            for section in email_sections:
                if not section.strip():
                    continue
                
                # Extract email ID
                email_id = section.split("ID: ")[1].split("\n")[0]
                
                # Get email summary using EmailAnalyzer
                summary = self.email_analyzer.analyze_email(email_id)
                
                # Combine original email info with summary
                formatted_email = f"{section}\nSummary: {summary}\n{'='*50}"
                formatted_emails.append(formatted_email)
            
            return "\n\n".join(formatted_emails)
        except Exception as e:
            return f"Error fetching emails: {str(e)}"
    
    def create_interface(self, date_str):
        """Create the date-specific email viewer interface"""
        with gr.Column() as date_viewer:
            # Display area for date-specific emails
            emails_display = gr.Textbox(
                label=f"Emails from {date_str}",
                lines=20,
                value=self.get_emails_by_date(date_str)
            )
            
        return date_viewer 