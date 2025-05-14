#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to create macOS application bundle
create_app_bundle() {
    APP_NAME="Gmail MCP.app"
    APP_PATH="/Applications/$APP_NAME"
    CONTENTS_PATH="$APP_PATH/Contents"
    MACOS_PATH="$CONTENTS_PATH/MacOS"
    RESOURCES_PATH="$CONTENTS_PATH/Resources"

    # Create the directory structure
    mkdir -p "$MACOS_PATH"
    mkdir -p "$RESOURCES_PATH"

    # Create the launcher script
    cat > "$MACOS_PATH/launcher.sh" << EOL
#!/bin/bash
cd "$SCRIPT_DIR"
python3 setup.py
EOL

    # Make the launcher script executable
    chmod +x "$MACOS_PATH/launcher.sh"

    # Create Info.plist
    cat > "$CONTENTS_PATH/Info.plist" << EOL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher.sh</string>
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
EOL

    echo "Created Gmail MCP application bundle in Applications folder"
}

# Create the application bundle if it doesn't exist
if [ ! -d "/Applications/Gmail MCP.app" ]; then
    echo "Creating Gmail MCP application bundle..."
    create_app_bundle
fi

# Run the application
cd "$SCRIPT_DIR"
python3 setup.py 