import json
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


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

class App():
    def __init__(self):
        self.startupChk = 0

        self.root = tk.Tk()
        
        self.root.geometry('325x400')
        self.root.resizable(False, False)
        self.root.title('DaVinci Resolve Discord RPC')
        self.mainframe = tk.Frame(self.root)
        self.mainframe.pack(fill='both', expand=True)

        self.text = tk.Label(self.mainframe, text="Program Starting...", width=40, anchor='w')
        self.text.pack()
        
        self.text2 = tk.Label(self.mainframe, text="WIP, please leave bug reports and\nsuggestions on the Github issues page! v2.51", justify='center')
        self.text2.place(x=0, y=365)

        self.settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
        self.settings = self.load_settings()
        self.settings_window = None
        self.tray_icon = None
        self.tray_thread = None

        self.settings_button = tk.Button(self.mainframe, text="Settings", command=self.open_settings)
        self.settings_button.pack(pady=(10, 0))

        #self.chkbtn = Checkbutton(self.mainframe, text="Startup with Windows", variable=self.startupChk)
        #self.chkbtn.place(x=0, y=0)
        #self.chkbtn.pack()

        def stop_tray_icon():
           if self.tray_icon is not None:
               try:
                   self.tray_icon.stop()
               except Exception:
                   pass
               self.tray_icon = None
               self.tray_thread = None

        def quit_window(icon, item):
           stop_tray_icon()
           global progRunning
           progRunning = False
           self.root.destroy()

        def show_window(icon, item):
           stop_tray_icon()
           self.root.after(0, self.root.deiconify)

        def hide_window():
           self.root.withdraw()
           if self.tray_icon is None:
               image = Image.open(resource_path("imgs/favicon.ico"))
               menu = (item('Show', show_window), item('Quit', quit_window))
               self.tray_icon = pystray.Icon("DaVinci Discord RPC", image, "Scythe's DaVinci Discord RPC " + progVersion, menu)
               self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
               self.tray_thread.start()

        def on_close():
           behavior = self.settings.get("close_behavior", "minimize_to_tray")
           if behavior == "minimize_to_taskbar":
               self.root.iconify()
           elif behavior == "close_app":
               quit_window(None, None)
           else:
               hide_window()

        self.root.protocol('WM_DELETE_WINDOW', on_close)

        self.apply_startup_setting()

        threading.Thread(target=self.mainProgram, daemon=True).start()
        self.root.mainloop()
        return

    def load_settings(self):
        defaults = {
            "close_behavior": "minimize_to_tray",
            "start_with_windows": False,
            "show_project_name": True
        }
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            if not isinstance(loaded, dict):
                return defaults
            defaults.update(loaded)
        except Exception:
            pass
        return defaults

    def save_settings(self):
        self.settings["close_behavior"] = self.close_behavior_var.get()
        self.settings["start_with_windows"] = self.start_with_windows_var.get()
        self.settings["show_project_name"] = self.show_project_name_var.get()
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass
        self.apply_startup_setting()
        self.set_status("Settings saved")

    def apply_startup_setting(self):
        if self.settings.get("start_with_windows") and sys.platform.startswith("win"):
            try:
                import winreg
                run_key = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
                exe_path = sys.executable
                script_path = os.path.abspath(__file__)
                value = f'"{exe_path}" "{script_path}"'
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, "DaVinciDiscordRPC", 0, winreg.REG_SZ, value)
            except Exception:
                pass
        elif sys.platform.startswith("win"):
            try:
                import winreg
                run_key = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, run_key, 0, winreg.KEY_SET_VALUE) as key:
                    winreg.DeleteValue(key, "DaVinciDiscordRPC")
            except Exception:
                pass

    def open_settings(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            return

        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.resizable(False, False)
        self.settings_window.geometry("360x250")

        self.close_behavior_var = tk.StringVar(value=self.settings.get("close_behavior", "minimize_to_tray"))
        self.start_with_windows_var = tk.BooleanVar(value=self.settings.get("start_with_windows", False))
        self.show_project_name_var = tk.BooleanVar(value=self.settings.get("show_project_name", True))

        tk.Label(self.settings_window, text="When hitting X:", anchor='w').pack(fill='x', padx=10, pady=(10, 0))
        tk.Radiobutton(self.settings_window, text="Minimize to tray", variable=self.close_behavior_var, value="minimize_to_tray").pack(anchor='w', padx=20)
        tk.Radiobutton(self.settings_window, text="Minimize to taskbar", variable=self.close_behavior_var, value="minimize_to_taskbar").pack(anchor='w', padx=20)
        tk.Radiobutton(self.settings_window, text="Close app", variable=self.close_behavior_var, value="close_app").pack(anchor='w', padx=20)

        tk.Checkbutton(self.settings_window, text="Start with Windows", variable=self.start_with_windows_var).pack(anchor='w', padx=10, pady=(10, 0))
        tk.Checkbutton(self.settings_window, text="Show project name on Discord", variable=self.show_project_name_var).pack(anchor='w', padx=10, pady=(10, 0))

        tk.Button(self.settings_window, text="Save", command=self.save_settings).pack(pady=15)
        self.settings_window.protocol("WM_DELETE_WINDOW", self.settings_window.destroy)

    def set_status(self, text):
        try:
            if self.root.winfo_exists():
                self.root.after(0, lambda: self.text.config(text=text))
        except Exception:
            pass

    def mainProgram(self):
        #define environment path variables
        os.environ['RESOLVE_SCRIPT_API'] = r"%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
        os.environ['RESOLVE_SCRIPT_LIB'] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        os.environ['PYTHONPATH'] = r"%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules"

        # Discord RPC client details
        client_id = "1297429320243089419"
        RPC = None
        rpc_connected = False

        def disconnect_rpc():
            nonlocal RPC, rpc_connected
            if rpc_connected and RPC is not None:
                try:
                    RPC.clear()
                except Exception:
                    pass
                try:
                    RPC.close()
                except Exception:
                    pass
                RPC = None
                rpc_connected = False

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
                return bmd.scriptapp("Resolve")
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
        
        resolve = None

        resolveOpen = False
        startTime = 0

        while progRunning:
            #os.system('cls')
            #print("Hit ctrl + c to close program")
    
            if "Resolve.exe" in (i.name() for i in psutil.process_iter()):
                resolveOpen = True
                if resolve is None:
                    try:
                        resolve = GetResolve()
                    except Exception as ex:
                        self.set_status("Waiting for Resolve to finish loading...")
                        time.sleep(10)
                        continue
                if not rpc_connected:
                    RPC = Presence(client_id)
                    try:
                        RPC.connect()
                        rpc_connected = True
                    except Exception as ex:
                        self.set_status(f"Discord RPC failed: {ex}")
                        time.sleep(10)
                        continue
                self.set_status("Connecting to Resolve.exe...")
                if(startTime == 0):
                    startTime = time.time()
                time.sleep(10)
            else:
                resolveOpen = False
                newtext = "Cannot find Resolve.exe"
                self.set_status("Cannot find Resolve.exe")
                disconnect_rpc()
                resolve = None
                startTime = 0
                time.sleep(10)
                continue
            while resolveOpen:
                try:
                    projectManager = resolve.GetProjectManager()
            
                    project = projectManager.GetCurrentProject()
            
                    if project.IsRenderingInProgress():
                        #if rendering
                        jobList = project.GetRenderJobList()
                        currentRender = jobList[-1]
                        currentJobID = currentRender['JobId']
                        jobProgress = project.GetRenderJobStatus(currentJobID)
                        jobPercentage = jobProgress['CompletionPercentage']
                        #clear console and update discord rpc
                        #os.system('cls')
                        #print("Hit ctrl + c to close program")
                        if self.settings.get("show_project_name", True):
                            self.set_status("Rendering: " + project.GetName() + " - " + str(jobPercentage))
                            rpc_state = project.GetName()
                            rpc_details = "Rendering Project: " + str(jobPercentage) + "%"
                        else:
                            self.set_status("Rendering: " + str(jobPercentage) + "%")
                            rpc_state = "Rendering"
                            rpc_details = "Rendering Project"
                        RPC.update(
                            state=rpc_state,
                            details=rpc_details,
                            start=startTime,
                            large_image="small_img"
                            )
                    else:
                        #clear console and update discord rpc
                        #os.system('cls')
                        #print("Hit ctrl + c to close program")
                        if project.GetName() == "Untitled Project":
                            self.set_status("Sitting in Project Manager")
                            RPC.update(
                                state="Project Manager",
                                details="Sitting in",
                                start=startTime,
                                large_image="small_img"
                                )
                        else:
                            if self.settings.get("show_project_name", True):
                                self.set_status("Editing: " + project.GetName())
                                rpc_state = project.GetName()
                            else:
                                self.set_status("Editing")
                                rpc_state = "Editing"
                            RPC.update(
                                state=rpc_state,
                                details="Editing Project",
                                start=startTime,
                                large_image="small_img"
                                )
                except Exception as Err:
                    #print(Err)
                    resolve = None
                    self.set_status("Waiting for Resolve to finish loading...")
                    time.sleep(15)
                    break
                time.sleep(15)
                if "Resolve.exe" in (i.name() for i in psutil.process_iter()):
                    resolveOpen = True
                else:
                    resolveOpen = False
            if not resolveOpen:
                disconnect_rpc()
                resolve = None
            time.sleep(15)

        disconnect_rpc()
        if hasattr(self, 'tray_icon') and self.tray_icon is not None:
            try:
                self.tray_icon.stop()
            except Exception:
                pass

        #print("hello!")
        
if __name__ == '__main__':
    App()
