import gradio as gr
from tools import EmailDrafter, EmailAnalyzer, ResponseSuggester, EmailProcessor, EmailFinder, LabelManager
from components.email_viewer import EmailViewer
from components.account_manager import AccountManager
import os

# Initialize managers and tools
account_manager = AccountManager()
email_viewer = EmailViewer(account_manager)

# Initialize tools with active account
def initialize_tools():
    active_account = account_manager.get_active_account()
    if not active_account:
        return None
    
    tools = {
        'email_drafter': EmailDrafter(),
        'email_analyzer': EmailAnalyzer(),
        'response_suggester': ResponseSuggester(),
        'email_processor': EmailProcessor(),
        'email_finder': EmailFinder(),
        'label_manager': LabelManager()
    }
    
    # Configure each tool with the active account
    for tool in tools.values():
        tool.set_credentials(
            client_id=active_account.client_id,
            client_secret=active_account.client_secret,
            token_pickle=active_account.token_pickle if active_account.token_pickle else None
        )
    
    return tools

# Initialize tools
tools = initialize_tools()

def process_message(message, history):
    """Process user messages and interact with Gmail MCP tools."""
    global tools
    
    # Check if tools are initialized
    if not tools:
        active_account = account_manager.get_active_account()
        if not active_account:
            return "Please set up and select a Gmail account first", history
        tools = initialize_tools()
        if not tools:
            return "Error initializing tools. Please check your account settings.", history
    
    # Convert message to lowercase for easier processing
    msg = message.lower()
    
    if "connect email" in msg:
        try:
            email = message.split("connect email:")[1].strip()
            # Set email for all tools
            for tool in tools.values():
                tool.set_connected_email(email)
            return f"Successfully connected to {email}", history + [(message, f"Successfully connected to {email}")]
        except:
            return "Please format your message as: 'connect email: your.email@example.com'", history
    
    elif "draft email" in msg:
        try:
            # Extract email details from the message
            parts = message.split("to:")[1].split("subject:")[0].strip()
            subject = message.split("subject:")[1].split("context:")[0].strip()
            context = message.split("context:")[1].strip()
            
            response = tools['email_drafter'].draft_email(parts, subject, context)
            return response, history + [(message, response)]
        except:
            return "Please format your message as: 'draft email to: recipient@email.com subject: your subject context: your context'", history
    
    elif "send email" in msg:
        try:
            # Extract email details from the message
            parts = message.split("to:")[1].split("subject:")[0].strip()
            subject = message.split("subject:")[1].split("context:")[0].strip()
            context = message.split("context:")[1].strip()
            
            response = tools['email_drafter'].send_email(parts, subject, context)
            return response, history + [(message, response)]
        except:
            return "Please format your message as: 'send email to: recipient@email.com subject: your subject context: your context'", history
    
    elif "analyze email" in msg:
        try:
            email_content = message.split("analyze email:")[1].strip()
            response = tools['email_analyzer'].analyze_email(email_content)
            return response, history + [(message, response)]
        except:
            return "Please format your message as: 'analyze email: [paste email content or message ID]'", history
    
    elif "suggest response" in msg:
        try:
            email_content = message.split("suggest response:")[1].strip()
            response = tools['response_suggester'].suggest_response(email_content)
            return response, history + [(message, response)]
        except:
            return "Please format your message as: 'suggest response: [paste email to respond to]'", history
    
    elif "list emails" in msg:
        try:
            response = tools['email_analyzer'].list_recent_emails(5)
            return response, history + [(message, response)]
        except:
            return "Error listing recent emails. Please try again.", history
    
    elif "find email" in msg:
        try:
            parts = message.split("find email:")[1].split("count:")[0].strip()
            count = int(message.split("count:")[1].strip()) if "count:" in message else 1
            response = tools['email_finder'].find_emails(parts, count)
            return response, history + [(message, response)]
        except:
            return "Please format your message as: 'find email: name_or_email count: number_of_emails'", history
    
    elif "list labels" in msg:
        try:
            response = tools['label_manager'].list_labels()
            return response, history + [(message, response)]
        except:
            return "Error listing labels. Please try again.", history
    
    elif "add label" in msg:
        try:
            label = message.split("add label:")[1].split("to:")[0].strip()
            email_id = message.split("to:")[1].strip()
            response = tools['label_manager'].add_label_to_email(label, email_id)
            return response, history + [(message, response)]
        except:
            return "Please format your message as: 'add label: label_name to: email_id'", history
    
    elif "remove label" in msg:
        try:
            label = message.split("remove label:")[1].split("from:")[0].strip()
            email_id = message.split("from:")[1].strip()
            response = tools['label_manager'].remove_label_from_email(label, email_id)
            return response, history + [(message, response)]
        except:
            return "Please format your message as: 'remove label: label_name from: email_id'", history
    
    else:
        # Use the general email request processor
        response = tools['email_processor'].process_email_request(message)
        return response, history + [(message, response)]

# Command examples with their descriptions
COMMANDS = {
    "Draft Email": "draft email to:  subject: ",
    "Send Email": "send email to:  subject:  context: ",
    "Analyze Email": "analyze email: [paste email content or message ID]",
    "Suggest Response": "suggest response: [paste email to respond to]",
    "List Emails": "list emails",
    "Find Email": "find email: [name or email] count: [number]",
    "List Labels": "list labels",
    "Add Label": "add label: [label_name] to: [email_id]",
    "Remove Label": "remove label: [label_name] from: [email_id]"
}

# Create Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Gmail Assistant")
    
    # Create tabs for different sections
    with gr.Tabs() as tabs:
        # Gmail MCP Tab
        with gr.Tab("Gmail MCP"):
            # Main chat area
            chatbot = gr.Chatbot(height=450)
            
            # Message input with full width
            msg_input = gr.Textbox(
                show_label=False,
                placeholder="Type a command or message...",
                container=False
            )
            
            # Command buttons in a grid
            with gr.Row():
                for label, cmd in COMMANDS.items():
                    gr.Button(
                        label,
                        size="sm"
                    ).click(
                        lambda x: x,
                        inputs=[gr.Textbox(value=cmd, visible=False)],
                        outputs=[msg_input]
                    )
                clear = gr.Button("Clear Chat", size="sm")
            
            msg_input.submit(process_message, [msg_input, chatbot], [msg_input, chatbot])
            clear.click(lambda: None, None, chatbot, queue=False)
        
        # Account Management Tab
        with gr.Tab("Account Management"):
            account_manager.create_interface()
        
        # New Emails Tab
        with gr.Tab("New Emails"):
            email_viewer.create_interface()

if __name__ == "__main__":
    demo.launch() 