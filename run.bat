@echo off
echo Setting up Gmail MCP Application...

:: Get the current directory
set "SCRIPT_DIR=%~dp0"

:: Create a shortcut on the desktop
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = oWS.ExpandEnvironmentStrings("%USERPROFILE%\Desktop\Gmail MCP.lnk") >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "cmd.exe" >> CreateShortcut.vbs
echo oLink.Arguments = "/c cd /d ""%SCRIPT_DIR%"" && python setup.py" >> CreateShortcut.vbs
echo oLink.IconLocation = "%SystemRoot%\System32\SHELL32.dll,153" >> CreateShortcut.vbs
echo oLink.Description = "Gmail MCP Application" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%SCRIPT_DIR%" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs

cscript //nologo CreateShortcut.vbs
del CreateShortcut.vbs

echo Desktop shortcut created successfully!
echo Starting Gmail MCP Application...
echo Note: You can set up your credentials from within the application.
echo.

:: Run the application
python setup.py 