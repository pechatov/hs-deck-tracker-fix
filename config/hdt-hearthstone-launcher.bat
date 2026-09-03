@echo off
setlocal

start "" "C:\Program Files (x86)\Battle.net\Battle.net.exe" --exec="launch WTCG"
timeout /t 12 /nobreak >NUL
start "" "C:\users\steamuser\AppData\Local\HearthstoneDeckTracker\Hearthstone Deck Tracker\Hearthstone Deck Tracker.exe"

set /a HEARTHSTONE_START_TIMEOUT=300
:wait_for_hearthstone_start
tasklist | findstr /I /C:"Hearthstone.exe" >NUL
if not errorlevel 1 goto wait_for_hearthstone_exit
if %HEARTHSTONE_START_TIMEOUT% LEQ 0 goto hearthstone_not_started
set /a HEARTHSTONE_START_TIMEOUT-=1
timeout /t 1 /nobreak >NUL
goto wait_for_hearthstone_start

:wait_for_hearthstone_exit
timeout /t 2 /nobreak >NUL
tasklist | findstr /I /C:"Hearthstone.exe" >NUL
if not errorlevel 1 goto wait_for_hearthstone_exit

taskkill /F /IM Battle.net.exe >NUL 2>&1
exit /b 0

:hearthstone_not_started
echo Hearthstone did not start within 5 minutes; leaving Battle.net open. 1>&2
exit /b 1
