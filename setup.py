import os
import sys
import subprocess
import platform
import venv
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"Current Python version: {platform.python_version()}")
        sys.exit(1)

def check_system_requirements():
    """Check if system meets requirements"""
    print(f"\nSystem Information:")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Architecture: {platform.machine()}\n")

def install_windows_dependencies(pip_cmd):
    """Install Windows-specific dependencies"""
    try:
        # Try installing PyAudio using pip
        print("\nInstalling Windows-specific dependencies...")
        subprocess.check_call([pip_cmd, "install", "PyAudio"])
        print("✓ PyAudio installed successfully")
    except subprocess.CalledProcessError:
        print("\n⚠️ Could not install PyAudio using pip.")
        print("Installing PyAudio using pipwin...")
        try:
            # Install pipwin first
            subprocess.check_call([pip_cmd, "install", "pipwin"])
            # Then use pipwin to install PyAudio
            subprocess.check_call([Path(".venv") / "Scripts" / "pipwin.exe", "install", "PyAudio"])
            print("✓ PyAudio installed successfully using pipwin")
        except subprocess.CalledProcessError as e:
            print("\n⚠️ Error installing PyAudio. Please try installing it manually:")
            print("1. Download the appropriate PyAudio wheel from:")
            print("   https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
            print("2. Install it using:")
            print("   pip install [downloaded_wheel_file]")
            input("\nPress Enter to continue anyway (some features might not work)...")

def create_venv(venv_path):
    """Create a virtual environment"""
    print("\nCreating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print("✓ Virtual environment created successfully")
    except Exception as e:
        print(f"Error creating virtual environment: {e}")
        sys.exit(1)

def get_python_command():
    """Get the correct python command based on OS"""
    if platform.system() == "Windows":
        return str(Path(".venv") / "Scripts" / "python.exe")
    return str(Path(".venv") / "bin" / "python")

def get_pip_command():
    """Get the correct pip command based on OS"""
    if platform.system() == "Windows":
        return str(Path(".venv") / "Scripts" / "pip.exe")
    return str(Path(".venv") / "bin" / "pip")

def setup_workspace():
    """Setup the workspace directory"""
    # Create necessary directories if they don't exist
    os.makedirs('components', exist_ok=True)
    
    # Create empty gmail_accounts.json if it doesn't exist
    accounts_file = Path('gmail_accounts.json')
    if not accounts_file.exists():
        with open(accounts_file, 'w') as f:
            f.write('[]')

def main():
    print("Gmail MCP Application Setup")
    print("==========================")
    
    # Check system requirements
    check_system_requirements()
    check_python_version()
    
    # Setup workspace
    setup_workspace()
    
    # Create virtual environment if it doesn't exist
    venv_path = Path(".venv")
    if not venv_path.exists():
        create_venv(venv_path)
    
    # Get the correct commands for the OS
    python_cmd = get_python_command()
    pip_cmd = get_pip_command()
    
    try:
        # Upgrade pip
        print("\nUpgrading pip...")
        subprocess.check_call([python_cmd, "-m", "pip", "install", "--upgrade", "pip"])
        print("✓ Pip upgraded successfully")
        
        # Install requirements
        print("\nInstalling dependencies...")
        subprocess.check_call([pip_cmd, "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        
        # Install Windows-specific dependencies if needed
        if platform.system() == "Windows":
            install_windows_dependencies(pip_cmd)
        
        # Run the application
        print("\nStarting the Gmail MCP application...")
        print("\nNote: If you haven't set up your credentials yet, you can do so from within the app.")
        print("The application will guide you through the setup process.")
        
        subprocess.check_call([python_cmd, "app.py"])
        
    except subprocess.CalledProcessError as e:
        print(f"\nError during setup: {e}")
        if platform.system() == "Windows":
            print("\nTroubleshooting steps for Windows:")
            print("1. Try running Command Prompt as Administrator")
            print("2. Make sure you have the latest Visual C++ Redistributable installed")
            print("3. If audio-related errors persist, try installing PyAudio manually")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSetup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 