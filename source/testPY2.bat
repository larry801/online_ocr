rd /s /q C:\NVDA2019.2\userConfig\addons\onlineOCR
mkdir C:\NVDA2019.2\userConfig\addons\onlineOCR

xcopy /E /V /Y .\addon\*  C:\NVDA2019.2\userConfig\addons\onlineOCR
start "NVDA" "C:\NVDA2019.2\nvda.exe"
