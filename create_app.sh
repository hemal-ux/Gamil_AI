#!/bin/bash

# Get the absolute path of the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Create the application bundle structure
APP_NAME="Gmail MCP.app"
APP_PATH="$HOME/Applications/$APP_NAME"
CONTENTS_PATH="$APP_PATH/Contents"
MACOS_PATH="$CONTENTS_PATH/MacOS"
RESOURCES_PATH="$CONTENTS_PATH/Resources"

echo "Creating Gmail MCP Application..."

# Create the directory structure
mkdir -p "$MACOS_PATH"
mkdir -p "$RESOURCES_PATH"

# Create the Info.plist file
cat > "$CONTENTS_PATH/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>GmailMCP</string>
    <key>CFBundleIdentifier</key>
    <string>com.gmail.mcp</string>
    <key>CFBundleName</key>
    <string>Gmail MCP</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
</dict>
</plist>
EOF

# Create the launcher script
cat > "$MACOS_PATH/GmailMCP" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
python3 setup.py
EOF

# Make the launcher script executable
chmod +x "$MACOS_PATH/GmailMCP"

echo "Application bundle created at: $APP_PATH"
echo "You can now launch Gmail MCP from your Applications folder" 