rd /s /q %APPDATA%\nvda\addons\onlineOCR
mkdir %APPDATA%\nvda\addons\onlineOCR

xcopy /E /V /Y .\addon\*  %APPDATA%\nvda\addons\onlineOCR
"C:\Program Files (x86)\NVDA\nvda_slave.exe" launchNVDA -r