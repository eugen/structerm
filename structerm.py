#!/usr/bin/python
# -*- coding: utf-8 -*- 

import ctypes, os, sys, subprocess

libcef_so = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libcef.so')
if os.path.exists(libcef_so):
    # Import local module
    ctypes.CDLL(libcef_so, ctypes.RTLD_GLOBAL)
    if 0x02070000 <= sys.hexversion < 0x03000000:
        import cefpython_py27 as cefpython
    else:
        raise Exception("Unsupported python version: %s" % sys.version)
else:
    # Import from package
    from cefpython3 import cefpython

import wx
import time
import re
import uuid
import platform

CommandHandlers = {}
Plugins = []
import plugins.ps
Plugins.append(plugins.ps.ps.PsHandler)

def initializePlugins():
    for plugin in Plugins:
        instance = plugin()
        for cmd in plugin.CommandsHandled:
            CommandHandlers[cmd] = instance

def GetApplicationPath(file=None):
    import re, os, platform
    # If file is None return current directory without trailing slash.
    if file is None:
        file = ""
    # Only when relative path.
    if not file.startswith("/") and not file.startswith("\\") and (
            not re.search(r"^[\w-]+:", file)):
        if hasattr(sys, "frozen"):
            path = os.path.dirname(sys.executable)
        elif "__file__" in globals():
            path = os.path.dirname(os.path.realpath(__file__))
        else:
            path = os.getcwd()
        path = path + os.sep + file
        if platform.system() == "Windows":
            path = re.sub(r"[/\\]+", re.escape(os.sep), path)
        path = re.sub(r"[/\\]+$", "", path)
        return path

    return str(file)

def ExceptHook(excType, excValue, traceObject):
    import traceback, os, time, codecs
    # This hook does the following: in case of exception write it to
    # the "error.log" file, display it to the console, shutdown CEF
    # and exit application immediately by ignoring "finally" (os._exit()).
    errorMsg = "\n".join(traceback.format_exception(excType, excValue,
            traceObject))
    print("Exception occurred: %s\n" % [errorMsg])
    cefpython.QuitMessageLoop()
    cefpython.Shutdown()
    os._exit(1)

class MainFrame(wx.Frame):
    browser = None
    mainPanel = None

    def __init__(self):
        wx.Frame.__init__(self, parent=None, id=wx.ID_ANY,
                title='Structerm', size=(800,600))
        self.CreateMenu()

        # Cannot attach browser to the main frame as this will cause
        # the menu not to work.
        self.mainPanel = wx.Panel(self)

        windowInfo = cefpython.WindowInfo()
        windowInfo.SetAsChild(self.mainPanel.GetGtkWidget())
        # Linux requires adding "file://" for local files,
        # otherwise /home/some will be replaced as http://home/some
        self.browser = cefpython.CreateBrowserSync(
            windowInfo,
            # If there are problems with Flash you can disable it here,
            # by disabling all plugins.
            browserSettings={"plugins_disabled": True},
            navigateUrl="file://"+GetApplicationPath("structerm.html"))

        clientHandler = ClientHandler(self.browser)
        self.browser.SetClientHandler(clientHandler)
        jsBindings = cefpython.JavascriptBindings(
            bindToFrames=False, bindToPopups=True)
        jsBindings.SetFunction("PyPrint", PyPrint)
        jsBindings.SetObject("external", JavascriptExternal(self.browser))
        self.browser.SetJavascriptBindings(jsBindings)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def CreateMenu(self):
        filemenu = wx.Menu()
        exit = filemenu.Append(2, "Exit")
        self.Bind(wx.EVT_MENU, self.OnClose, exit)
        aboutmenu = wx.Menu()
        aboutmenu.Append(1, "About")
        self.Bind(wx.EVT_MENU, lambda _: PyPrint("The About menu option is not implemented!"))
        menubar = wx.MenuBar()
        menubar.Append(filemenu,"&File")
        menubar.Append(aboutmenu, "&Help")
        self.SetMenuBar(menubar)

    def OnClose(self, event):
        self.browser.CloseBrowser()
        self.Destroy()

    def OnIdle(self, event):
        cefpython.MessageLoopWork()

def PyPrint(message):
    print(message)

class JavascriptExternal:
    mainBrowser = None
    
    def __init__(self, mainBrowser):
        self.mainBrowser = mainBrowser

    def ExecuteCommand(self, cmd, *args):
        if(cmd in CommandHandlers):
            output = CommandHandlers[cmd].handle(cmd, args)
        else:
            try:
                output = subprocess.check_output(cmd.strip().split())
            except subprocess.CalledProcessError as e:
                output = e.output
            except OSError as e:
                output = "%s: command not found" % cmd

        self.mainBrowser.GetMainFrame().ExecuteFunction("sre.renderOutput", cmd, output)

class ClientHandler:

    def __init__(self, mainBrowser):
        self.mainBrowser = mainBrowser

    def OnConsoleMessage(self, browser, message, source, line):
        print("DisplayHandler::OnConsoleMessage()")
        print("message = %s" % message)
        print("source = %s" % source)
        print("line = %s" % line)

    def OnKeyEvent(self, browser, event, eventHandle):
        #print("KeyboardHandler::OnKeyEvent(): native_key_code = %s" % event["native_key_code"])
        pass

class MyApp(wx.App):
    timer = None
    timerID = 1
    timerCount = 0

    def OnInit(self):
        self.CreateTimer()
        frame = MainFrame()
        self.SetTopWindow(frame)
        frame.Show()
        return True

    def CreateTimer(self):
        self.timer = wx.Timer(self, self.timerID)
        self.timer.Start(10) # 10ms
        wx.EVT_TIMER(self, self.timerID, self.OnTimer)

    def OnTimer(self, event):
        self.timerCount += 1
        cefpython.MessageLoopWork()

    def OnExit(self):
        # When app.MainLoop() returns, MessageLoopWork() should
        # not be called anymore.
        self.timer.Stop()

if __name__ == '__main__':
    initializePlugins()

    sys.excepthook = ExceptHook
    cefpython.g_debug = False
    cefpython.g_debugFile = GetApplicationPath("debug.log")
    settings = {
        "log_severity": cefpython.LOGSEVERITY_INFO, # LOGSEVERITY_VERBOSE
        "log_file": GetApplicationPath("debug.log"), # Set to "" to disable.
        "release_dcheck_enabled": True, # Enable only when debugging.
        # This directories must be set on Linux
        "locales_dir_path": cefpython.GetModuleDirectory()+"/locales",
        "resources_dir_path": cefpython.GetModuleDirectory(),
        "browser_subprocess_path": "%s/%s" % (
            cefpython.GetModuleDirectory(), "subprocess")
    }
    print("browser_subprocess_path="+settings["browser_subprocess_path"])
    cefpython.Initialize(settings)
    print('wx.version=%s' % wx.version())
    app = MyApp(False)
    app.MainLoop()
    # Let wx.App destructor do the cleanup before calling cefpython.Shutdown().
    del app
    cefpython.Shutdown()
