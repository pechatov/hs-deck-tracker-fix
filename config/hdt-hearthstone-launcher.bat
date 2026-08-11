@echo off
start "" "C:\Program Files (x86)\Battle.net\Battle.net.exe" --exec="launch WTCG"
timeout /t 12 /nobreak >NUL
start "" "C:\users\steamuser\AppData\Local\HearthstoneDeckTracker\Hearthstone Deck Tracker\Hearthstone Deck Tracker.exe"
