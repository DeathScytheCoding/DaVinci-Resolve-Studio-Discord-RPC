# DaVinci-Resolve-Studio-Discord-RPC
A Discord RPC client for DaVinci Resolve Studio

Currently the program is just a Python script and has to have the command prompt open to work correctly. I tried headless but the command prompt kept flashing every 15 seconds when it updated and would take me out of my games or take away keyboard control for a second. 

Installation:
You should be able to download v2.45+ and just run the exe without issue. Hopefully. If not submit a bug report. For now, if you would like the program to start with Windows, you will have to create a shortcut of the exe and put it in your Windows startup folder at AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup (you can get to roaming by typing %appdata% in the Windows search bar).

Function:
Once the script sees that Resolve.exe is open, it will wait 30 seconds and then update Discord with the activity. It will also try to get the current project name and display it under the status "editing". The script will also show when you are rendering a video with a percentage of completion displayed (at the moment this only works if the video you are rendering is first in the queue).
