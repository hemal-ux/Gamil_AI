# Gmail AI Application

A modern Gmail client application with a Gradio UI that provides email management, summarization using Gemini AI, and multi-account support.

## Features

- 📧 Multi-account Gmail management
- 🤖 Email summarization using Google's Gemini AI
- 📎 Attachment detection and management
- 🔗 Direct Gmail links for each email
- 🎨 Modern dark theme interface
- 🔄 Real-time email updates
- can work with windows and macos

## Prerequisites

Before installing, make sure you have:

1. **Python 3.8 or higher**
   - Windows: Download from [python.org](https://www.python.org/downloads/)
   - macOS: Use Homebrew `brew install python@3.8` or download from python.org
   - Check installation: `python --version` or `python3 --version`

2. **Google OAuth Credentials**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create OAuth 2.0 credentials (Desktop Application)
   - Download credentials (you'll need Client ID and Client Secret)

3. **Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Save it for later use

## Installation

### Windows

1. Download or clone this repository
2. Open Command Prompt as Administrator
3. Navigate to the project directory
4. Double-click `run.bat` or run:
   ```
   python setup.py
   ```
5. To run a shortcut:
   - run this `app.py` after 'run.bat' or 'run.sh'
   - A "Gmail AI" shortcut will be created on your desktop

### macOS/Linux

1. Download or clone this repository
2. Open Terminal
3. Navigate to the project directory
4. Make the scripts executable and run:
   ```bash
   chmod +x run.sh create_app.sh
   ./run.sh
   ```
   Or simply run:
   ```bash
   python3 setup.py
   ```
5. To create an application in your Applications folder (macOS only):
   ```bash
   ./create_app.sh
   ```
   - This will create "Gmail MCP.app" in your Applications folder
   - You can now launch the application from Spotlight or Applications folder

The setup script will automatically:
- Check system requirements
- Create a virtual environment
- Install all required dependencies
- Start the application

## First-Time Setup

When you first run the application:

1. Click "Add New Gmail Account"
2. Enter your Google OAuth credentials:
   - Client ID
   - Client Secret
   - (Other fields will be pre-filled)
3. Add your Gemini API key in the "Gemini API Key Management" section
4. Follow the OAuth flow to authenticate your Gmail account

## Usage

1. **Managing Accounts**
   - Add multiple Gmail accounts
   - Switch between accounts
   - Remove accounts when needed
   - Each account can have its own Gemini API key

2. **Email Features**
   - View recent emails
   - Search by date
   - See email summaries (requires Gemini API key)
   - Quick access to attachments
   - Direct Gmail links

## Troubleshooting

If you encounter any issues:

1. **Python Issues**
   - Make sure Python 3.8+ is installed and in your system PATH
   - Try running `python --version` or `python3 --version`
   - On Windows, try running Command Prompt as Administrator

2. **Installation Issues**
   - Delete the `.venv` directory and try again
   - Make sure you have write permissions in the directory
   - Check your internet connection

3. **Windows-Specific Issues**
   - If you see `ModuleNotFoundError: No module named 'pyaudioop'`, follow these steps:
     1. Install Visual C++ Redistributable from [Microsoft's website](https://learn.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist)
     2. Try running Command Prompt as Administrator
     3. If the error persists, follow these manual installation steps:
        ```
        Step 1: Download PyAudio wheel file
        - Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
        - Find the correct version for your Python:
          - For Python 3.8: Download "PyAudio‑0.2.11‑cp38‑cp38‑win_amd64.whl"
          - For Python 3.9: Download "PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl"
          - For Python 3.10: Download "PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl"
          - For Python 3.11: Download "PyAudio‑0.2.11‑cp311‑cp311‑win_amd64.whl"
        
        Step 2: Install the wheel file
        - Open Command Prompt as Administrator
        - Navigate to where you downloaded the wheel file
        - Run this command (replace [filename] with the actual filename you downloaded):
          .venv\Scripts\pip.exe install [filename]
        
        Example:
        If you downloaded PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl to your Downloads folder:
        .venv\Scripts\pip.exe install C:\Users\YourUsername\Downloads\PyAudio‑0.2.11‑cp310‑cp310‑win_amd64.whl
        ```
   - If you see other audio-related errors:
     1. Make sure your system's audio drivers are up to date
     2. Try installing the application in a different directory
     3. Temporarily disable antivirus software during installation

4. **Authentication Issues**
   - Verify your Google OAuth credentials
   - Ensure Gmail API is enabled in Google Cloud Console
   - Check if your Gemini API key is valid

5. **Application Issues**
   - Check the terminal/command prompt for error messages
   - Verify all required fields are filled correctly
   - Make sure you're connected to the internet

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Open an issue in the repository
3. Include your system information and error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
