import tkinter as tk
from tkinter import Checkbutton, ttk
import os
import sys
import time
import threading
import psutil
from pypresence import Presence
from pystray import MenuItem as item
import pystray
from PIL import Image

progVersion = "v2.43"
progRunning = True

class App():
    def __init__(self):
        self.startupChk = 0

        self.root = tk.Tk()
        
        self.root.geometry('325x400')
        self.root.resizable(False, False)
        self.root.title('DaVinci Resolve Discord RPC')
        self.mainframe = tk.Frame(self.root)
        self.mainframe.pack(fill='both', expand=True)

        self.text = tk.Text(self.mainframe, height=1, width=40)
        self.text.insert("1.0", "Program Starting...")
        self.text.pack()
        
        
        self.text2 = tk.Text(self.mainframe, height=2, width=40)
        #self.text2 = tk.Label(self.mainframe, text="WIP, please leave bug reports and suggestions on the Github issues page!")
        #self.text2.grid(row=2, column=2)
        self.text2.insert("1.0", "WIP, please leave bug reports and\nsuggestions on the Github issues page!")
        self.text2.place(x=0, y=365)
        self.text2.tag_configure("center", justify='center')
        self.text2.tag_add("center", 1.0, "end")
        #self.text2.grid(row=3, column=3)

        #self.chkbtn = Checkbutton(self.mainframe, text="Startup with Windows", variable=self.startupChk)
        #self.chkbtn.place(x=0, y=0)
        #self.chkbtn.pack()

        def quit_window(icon, item):
           icon.stop()
           self.root.destroy()
           progRunning = False

        def show_window(icon, item):
           icon.stop()
           self.root.after(0,self.root.deiconify())

        def hide_window():
           self.root.withdraw()
           image=Image.open("imgs/favicon.ico")
           menu=(item('Show', show_window), item('Quit', quit_window))
           icon=pystray.Icon("DaVinci Discord RPC", image, "Scythe's DaVinci Discord RPC " + progVersion, menu)
           icon.run()

        self.root.protocol('WM_DELETE_WINDOW', hide_window)

        threading.Thread(target=self.mainProgram).start()
        self.root.mainloop()
        return

    def mainProgram(self):
        #define environment path variables
        os.environ['RESOLVE_SCRIPT_API'] = r"%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
        os.environ['RESOLVE_SCRIPT_LIB'] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        os.environ['PYTHONPATH'] = r"%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules"

        #Discord RPC client details
        client_id = "1297429320243089419"
        RPC = Presence(client_id)

        RPC.connect()

        def load_source(module_name, file_path):
            if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
                import importlib.util

                module = None
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec:
                    module = importlib.util.module_from_spec(spec)
                if module:
                    sys.modules[module_name] = module
                    spec.loader.exec_module(module)
                return module
            else:
                import imp
                return imp.load_source(module_name, file_path)

        #get Resolve object
        def GetResolve():
            try:
                # The PYTHONPATH needs to be set correctly for this import statement to work.
                # An alternative is to import the DaVinciResolveScript by specifying absolute path (see ExceptionHandler logic)
                import DaVinciResolveScript as bmd
            except ImportError:
                if sys.platform.startswith("darwin"):
                    expectedPath = "/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/"
                elif sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
                    import os
                    expectedPath = os.getenv('PROGRAMDATA') + "\\Blackmagic Design\\DaVinci Resolve\\Support\\Developer\\Scripting\\Modules\\"
                elif sys.platform.startswith("linux"):
                    expectedPath = "/opt/resolve/Developer/Scripting/Modules/"

                # check if the default path has it...
                #print("Unable to find module DaVinciResolveScript from $PYTHONPATH - trying default locations")
                try:
                    load_source('DaVinciResolveScript', expectedPath + "DaVinciResolveScript.py")
                    import DaVinciResolveScript as bmd
                except Exception as ex:
                    # No fallbacks ... report error:
                    #print("Unable to find module DaVinciResolveScript - please ensure that the module DaVinciResolveScript is discoverable by python")
                    #print("For a default DaVinci Resolve installation, the module is expected to be located in: " + expectedPath)
                    #print(ex)
                    sys.exit()

            return bmd.scriptapp("Resolve")
        
        resolve = GetResolve()

        resolveOpen = False
        startTime = 0

        while progRunning:
            #os.system('cls')
            #print("Hit ctrl + c to close program")
    
            if "Resolve.exe" in (i.name() for i in psutil.process_iter()):
                resolveOpen = True
                self.text.delete("1.0","end")
                self.text.insert("1.0", "Connecting to Resolve.exe...", "center")
                RPC.connect()
                if(startTime == 0):
                    startTime = time.time()
                time.sleep(30)
            else:
                resolveOpen = False
                newtext = "Cannot find Resolve.exe"
                self.text.delete("1.0","end")
                self.text.insert("1.0", "Cannot find Resolve.exe", "center")
                RPC.close()
                #print("Cannot find Resolve.exe")
                startTime = 0
                time.sleep(15)
                continue
            while resolveOpen:
                try:
                    projectManager = resolve.GetProjectManager()
            
                    project = projectManager.GetCurrentProject()
            
                    if project.IsRenderingInProgress():
                        #if rendering
                        jobList = project.GetRenderJobList()
                        currentRender = jobList[0]
                        currentJobID = currentRender['JobId']
                        jobProgress = project.GetRenderJobStatus(currentJobID)
                        jobPercentage = jobProgress['CompletionPercentage']
                        #clear console and update discord rpc
                        #os.system('cls')
                        #print("Hit ctrl + c to close program")
                        self.text.delete("1.0","end")
                        self.text.insert("1.0", "Rendering: " + project.GetName() + " - " + str(jobPercentage), "center")
                        RPC.update(
                            state=project.GetName(),
                            details="Rendering Project: " + str(jobPercentage) + "%",
                            start=startTime,
                            large_image="small_img"
                            )
                    else:
                        #clear console and update discord rpc
                        #os.system('cls')
                        #print("Hit ctrl + c to close program")
                        self.text.delete("1.0","end")
                        self.text.insert("1.0", "Editing: " + project.GetName(), "center")
                        RPC.update(
                            state=project.GetName(),
                            details="Editing Project",
                            start=startTime,
                            large_image="small_img"
                            )
                except AttributeError as Err:
                    #print(Err)
                    time.sleep(15)
                    break
                time.sleep(15)
                if "Resolve.exe" in (i.name() for i in psutil.process_iter()):
                    resolveOpen = True
                else:
                    resolveOpen = False
            time.sleep(15)

        #print("hello!")

        self.root.after(2000, self.mainProgram)
        
if __name__ == '__main__':
    App()