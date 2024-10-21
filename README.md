# DaVinci-Resolve-Studio-Discord-RPC
A Discord RPC client for DaVinci Resolve Studio

Currently the program is just a Python script and has to have the command prompt open to work correctly. I tried headless but the command prompt kept flashing every 15 seconds when it updated and would take me out of my games or take away keyboard control for a second. 

Dependencies:
- I included PyPresence in the download because I was not able to get it to work any other way. It has to be in the same folder as the Python script.
- PSutils needs to be installed through pip in order for the script to see if Resolve.exe is open.

Installation:
No installation, just download and run the .py script. 

Function:
Once the script sees that Resolve.exe is open, it will wait 30 seconds and then update Discord with the activity. It will also try to get the current project name and display it under the status "editing". The script will also show when you are rendering a video with a percentage of completion displayed (at the moment this only works if the video you are rendering is first in the queue).
