import gradio as gr
import json
import os
from dataclasses import dataclass
from typing import List, Optional
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

@dataclass
class GmailAccount:
    name: str
    client_id: str
    client_secret: str
    auth_uri: str
    token_uri: str
    redirect_uris: List[str]
    is_active: bool = False
    token_pickle: Optional[str] = None
    gemini_api_key: Optional[str] = None

class AccountManager:
    def __init__(self, accounts_file="gmail_accounts.json"):
        self.accounts_file = accounts_file
        self.accounts = self._load_accounts()
        
        # Remove default account handling
        if self.accounts and not any(acc.is_active for acc in self.accounts):
            self.accounts[0].is_active = False
    
    def _load_accounts(self) -> List[GmailAccount]:
        """Load saved accounts from file"""
        try:
            # Load existing accounts from file
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, "r") as f:
                    accounts_data = json.load(f)
                    return [GmailAccount(**acc) for acc in accounts_data]
            return []
        except Exception as e:
            print(f"Error loading accounts: {str(e)}")
            return []

    def _save_accounts(self):
        """Save accounts to file"""
        try:
            accounts_data = [vars(acc) for acc in self.accounts]
            with open(self.accounts_file, "w") as f:
                json.dump(accounts_data, f, indent=2)
        except Exception as e:
            print(f"Error saving accounts: {str(e)}")

    def add_account(self, name: str, client_id: str, client_secret: str, 
                   auth_uri: str, token_uri: str, redirect_uri: str) -> tuple[str, str]:
        """Add a new Gmail account"""
        # Validate inputs
        if not all([name, client_id, client_secret, auth_uri, token_uri, redirect_uri]):
            return "Error", "All fields are required"
        
        # Check for duplicate names
        if any(acc.name == name for acc in self.accounts):
            return "Error", f"Account with name '{name}' already exists"
        
        # Create new account (not active by default)
        new_account = GmailAccount(
            name=name,
            client_id=client_id,
            client_secret=client_secret,
            auth_uri=auth_uri,
            token_uri=token_uri,
            redirect_uris=[redirect_uri],
            is_active=False
        )
        
        self.accounts.append(new_account)
        self._save_accounts()
        return "Success", f"Account '{name}' added successfully. Please select it in the Manage Accounts section to use it."

    def set_active_account(self, account_name: str) -> tuple[str, list[str], str]:
        """Set the active account and return updated dropdown choices"""
        if not account_name:
            return "Error", self._get_account_names(), "Please select an account"
        
        # Handle if we somehow got a list
        if isinstance(account_name, list) and len(account_name) > 0:
            account_name = account_name[0]
        
        # Remove "(Active)" from the account name if present
        clean_name = account_name.replace(" (Active)", "").strip()
        
        # Update active status
        found = False
        for acc in self.accounts:
            if acc.name == clean_name:
                acc.is_active = True
                found = True
            else:
                acc.is_active = False
        
        if not found:
            return "Error", self._get_account_names(), f"Account '{clean_name}' not found"
        
        self._save_accounts()
        return "Success", self._get_account_names(), f"Switched to account: {clean_name}"

    def _get_account_names(self) -> list[str]:
        """Get list of account names with active indicator"""
        names = []
        for acc in self.accounts:
            name = acc.name
            if acc.is_active:
                name += " (Active)"
            names.append(name)
        return names

    def get_active_account(self) -> Optional[GmailAccount]:
        """Get the currently active account"""
        for acc in self.accounts:
            if acc.is_active:
                return acc
        return None if not self.accounts else self.accounts[0]

    def remove_account(self, account_name: str) -> tuple[str, list[str], str]:
        """Remove an account and return updated dropdown choices"""
        if not account_name:
            return "Error", self._get_account_names(), "Please select an account"
        
        # Remove "(Active)" from the account name if present
        clean_name = account_name.replace(" (Active)", "").strip()
        
        # Find and remove the account
        removed_active = False
        for i, acc in enumerate(self.accounts):
            if acc.name == clean_name:
                if acc.is_active:
                    removed_active = True
                del self.accounts[i]
                self._save_accounts()
                
                # If we removed the active account, make sure no account is active
                if removed_active:
                    for remaining_acc in self.accounts:
                        remaining_acc.is_active = False
                    self._save_accounts()
                
                return "Success", self._get_account_names(), f"Account '{clean_name}' removed"
        
        return "Error", self._get_account_names(), f"Account '{clean_name}' not found"

    def create_interface(self):
        """Create the account management interface"""
        with gr.Column() as account_manager:
            with gr.Row():
                gr.Markdown("## Add New Gmail Account")
            
            with gr.Row():
                name_input = gr.Textbox(
                    label="Account Name",
                    placeholder="Enter a name for this account"
                )
            
            with gr.Row():
                client_id_input = gr.Textbox(
                    label="Client ID",
                    placeholder="Your Google OAuth client ID"
                )
            
            with gr.Row():
                client_secret_input = gr.Textbox(
                    label="Client Secret",
                    placeholder="Your Google OAuth client secret"
                )
            
            with gr.Row():
                auth_uri_input = gr.Textbox(
                    label="Auth URI",
                    value="https://accounts.google.com/o/oauth2/auth",
                    placeholder="Google OAuth authorization URI"
                )
            
            with gr.Row():
                token_uri_input = gr.Textbox(
                    label="Token URI",
                    value="https://oauth2.googleapis.com/token",
                    placeholder="Google OAuth token URI"
                )
            
            with gr.Row():
                redirect_uri_input = gr.Textbox(
                    label="Redirect URI",
                    value="http://localhost",
                    placeholder="OAuth redirect URI"
                )
            
            with gr.Row():
                save_btn = gr.Button("Save Account", variant="primary")
                status_label = gr.Label(label="Status")
            
            gr.Markdown("## Gemini API Key Management")
            
            with gr.Row():
                gemini_key_input = gr.Textbox(
                    label="Gemini API Key",
                    placeholder="Enter your Gemini API key (required for email summaries)",
                    type="password",
                    info="Get your API key from Google AI Studio"
                )
            
            with gr.Row():
                with gr.Column(scale=1):
                    save_gemini_btn = gr.Button("Save Gemini Settings", variant="primary")
                with gr.Column(scale=1):
                    remove_gemini_btn = gr.Button("Remove API Key", variant="stop")
                gemini_status_label = gr.Label(label="Gemini Status")
            
            gr.Markdown("## Manage Accounts")
            
            with gr.Row():
                # Get current accounts and active account
                account_names = self._get_account_names()
                active_account = next((name for name in account_names if "(Active)" in name), None)
                
                account_dropdown = gr.Dropdown(
                    choices=account_names,
                    label="Select Account",
                    value=active_account,
                    allow_custom_value=False
                )
            
            with gr.Row():
                switch_btn = gr.Button("Switch Account", variant="secondary")
                remove_btn = gr.Button("Remove Account", variant="stop")
                action_status = gr.Label(label="Action Status")
            
            # Connect save button with authentication flow
            def save_and_authenticate(name, client_id, client_secret, auth_uri, token_uri, redirect_uri):
                # First save the account
                status, message = self.add_account(name, client_id, client_secret, auth_uri, token_uri, redirect_uri)
                
                if status == "Success":
                    # Set this account as active
                    self.set_active_account(name)
                    
                    # Initialize authentication
                    try:
                        # Create the OAuth config
                        client_config = {
                            "installed": {
                                "client_id": client_id,
                                "client_secret": client_secret,
                                "auth_uri": auth_uri,
                                "token_uri": token_uri,
                                "redirect_uris": [redirect_uri],
                                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
                            }
                        }
                        
                        # Create and run the OAuth flow
                        flow = InstalledAppFlow.from_client_config(
                            client_config,
                            scopes=['https://www.googleapis.com/auth/gmail.modify']
                        )
                        credentials = flow.run_local_server(port=0)
                        
                        # Convert credentials to token pickle
                        token_pickle = pickle.dumps(credentials).hex()
                        
                        # Update the account with the token
                        for acc in self.accounts:
                            if acc.name == name:
                                acc.token_pickle = token_pickle
                                break
                        self._save_accounts()
                        
                        # Return success and update dropdown
                        account_names = self._get_account_names()
                        return "Success", "Account added and authenticated successfully"
                    except Exception as e:
                        return "Error", f"Authentication failed: {str(e)}"
                
                return status, message
            
            # Function to update dropdown choices
            def update_dropdown():
                choices = self._get_account_names()
                active = next((name for name in choices if "(Active)" in name), None)
                return gr.Dropdown(choices=choices, value=active)
            
            # Connect save button
            save_btn.click(
                fn=save_and_authenticate,
                inputs=[
                    name_input,
                    client_id_input,
                    client_secret_input,
                    auth_uri_input,
                    token_uri_input,
                    redirect_uri_input
                ],
                outputs=[status_label, status_label]
            ).then(
                fn=update_dropdown,
                outputs=account_dropdown
            )
            
            # Connect switch button
            switch_btn.click(
                fn=self.set_active_account,
                inputs=[account_dropdown],
                outputs=[action_status, account_dropdown, action_status]
            ).then(
                fn=update_dropdown,
                outputs=account_dropdown
            )
            
            # Connect remove button
            remove_btn.click(
                fn=self.remove_account,
                inputs=[account_dropdown],
                outputs=[action_status, account_dropdown, action_status]
            ).then(
                fn=update_dropdown,
                outputs=account_dropdown
            )
            
            def save_gemini_settings(api_key: str):
                active_account = self.get_active_account()
                if not active_account:
                    return "Error: No active account selected"
                
                if not api_key.strip():
                    return "Error: Gemini API key is required for email summaries"
                
                active_account.gemini_api_key = api_key.strip()
                self._save_accounts()
                
                return f"Success: Gemini API key saved for {active_account.name}"

            def remove_gemini_key():
                active_account = self.get_active_account()
                if not active_account:
                    return "", "Error: No active account selected"
                
                active_account.gemini_api_key = None
                self._save_accounts()
                
                return "", f"Success: Gemini API key removed from {active_account.name}"

            # Connect the save Gemini settings button
            save_gemini_btn.click(
                fn=save_gemini_settings,
                inputs=[gemini_key_input],
                outputs=[gemini_status_label]
            )

            # Connect the remove Gemini key button
            remove_gemini_btn.click(
                fn=remove_gemini_key,
                outputs=[gemini_key_input, gemini_status_label]
            )

            # Update Gemini fields when account changes
            def update_gemini_fields(account_name):
                if not account_name:
                    return ""
                
                clean_name = account_name.replace(" (Active)", "").strip()
                for acc in self.accounts:
                    if acc.name == clean_name:
                        return acc.gemini_api_key or ""
                return ""

            account_dropdown.change(
                fn=update_gemini_fields,
                inputs=[account_dropdown],
                outputs=[gemini_key_input]
            )
            
        return account_manager 