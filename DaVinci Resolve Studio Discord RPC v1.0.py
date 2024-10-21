import os
import sys
import time
import psutil
from pypresence import Presence

#define environment path variables
os.environ['RESOLVE_SCRIPT_API'] = r"%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
os.environ['RESOLVE_SCRIPT_LIB'] = r"C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
os.environ['PYTHONPATH'] = r"%PYTHONPATH%;%RESOLVE_SCRIPT_API%\Modules"

#Discord RPC client details

client_id = "1297429320243089419"
RPC = Presence(client_id)
startTime = time.time()

RPC.connect() #connect to discord

while True:
    os.system('cls')
    print("Hit ctrl + c to close program")
    
    if "Resolve.exe" in (i.name() for i in psutil.process_iter()):
        resolveOpen = True
        RPC.connect()
        time.sleep(30)
    else:
        RPC.close()
        print("Cannot find Resolve.exe")
        time.sleep(15)
        continue
    while "Resolve.exe" in (i.name() for i in psutil.process_iter()): #if resolve is open
        #clear console and update discord rpc
        #default when no projects are open
        os.system('cls')
        print("Hit ctrl + c to close program")
        
        #define dependency sources
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
                print("Unable to find module DaVinciResolveScript from $PYTHONPATH - trying default locations")
                try:
                    load_source('DaVinciResolveScript', expectedPath + "DaVinciResolveScript.py")
                    import DaVinciResolveScript as bmd
                except Exception as ex:
                    # No fallbacks ... report error:
                    print("Unable to find module DaVinciResolveScript - please ensure that the module DaVinciResolveScript is discoverable by python")
                    print("For a default DaVinci Resolve installation, the module is expected to be located in: " + expectedPath)
                    print(ex)
                    sys.exit()

            return bmd.scriptapp("Resolve")
        
        resolve = GetResolve()
        
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
                os.system('cls')
                print("Hit ctrl + c to close program")
                RPC.update(
                    state=project.GetName(),
                    details="Rendering Project: " + str(jobPercentage) + "%",
                    start=startTime,
                    large_image="small_img"
                    )
            else:
                #clear console and update discord rpc
                os.system('cls')
                print("Hit ctrl + c to close program")
                RPC.update(
                    state=project.GetName(),
                    details="Editing Project",
                    start=startTime,
                    large_image="small_img"
                    )
        except AttributeError as Err:
            print(Err)
            time.sleep(15)
            break
        time.sleep(15)
    time.sleep(15)
