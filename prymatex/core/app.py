#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Cosas interesantes
#http://www.riverbankcomputing.co.uk/static/Docs/PyQt4/html/qfilesystemwatcher.html
import os, sys

from PyQt4 import QtGui, QtCore

import prymatex
from prymatex.core import exceptions

from prymatex.utils import coroutines
from prymatex.utils import decorator as deco
from prymatex.utils.i18n import ugettext as _
from prymatex.gui.style import PrymatexStyle

class PMXApplication(QtGui.QApplication):
    """
    The application instance.
    There can't be two apps running simultaneously, since configuration issues may occur.
    The application loads the PMX Support.
    """
    
    def __init__(self, profile, args):
        """
        Inicialización de la aplicación.
        """
        QtGui.QApplication.__init__(self, args)
        QtGui.QApplication.setStyle(PrymatexStyle())
        
        # Some init's
        self.setApplicationName(prymatex.__name__)
        self.setApplicationVersion(prymatex.__version__)
        self.setOrganizationDomain(prymatex.__url__)
        self.setOrganizationName(prymatex.__author__)

        self.buildSettings(profile)
        self.setupLogging()

        #Connects
        self.aboutToQuit.connect(self.closePrymatex)

    def loadGraphicalUserInterface(self):
        splash = QtGui.QSplashScreen(QtGui.QPixmap(":/images/prymatex/Prymatex_Splash.svg"))
        splash.show()
        try:
            # Loads
            self.setupSupportManager(callbackSplashMessage = splash.showMessage)   #Support Manager
            self.setupFileManager()      #File Manager
            self.setupProjectManager()   #Project Manager
            self.setupKernelManager()    #Console kernel Manager
            self.setupPluginManager()
            self.setupCoroutines()
            self.setupZeroMQContext()
    
            # Setup Dialogs
            self.setupDialogs()         #Config Dialog
            
            # Creates the Main Window
            self.createMainWindow()
            splash.finish(self.mainWindow)
          
        except KeyboardInterrupt:
            print("\nQuit signal catched during application startup. Quiting...")
            self.quit()
            
    def resetSettings(self):
        self.settings.clear()
        
    def buildSettings(self, profile):
        from prymatex.core.settings import PMXSettings
        self.settings = PMXSettings(profile)

    def checkSingleInstance(self):
        """
        Checks if there's another instance using current profile
        """
        self.fileLock = os.path.join(self.settings.PMX_VAR_PATH, 'prymatex.pid')

        if os.path.exists(self.fileLock):
            #Mejorar esto
            pass
            #raise exceptions.AlreadyRunningError('%s seems to be runnig. Please close the instance or run other profile.' % (self.settings.PMX_PROFILE_NAME))
        else:
            f = open(self.fileLock, 'w')
            f.write('%s' % self.applicationPid())
            f.close()

    def setupLogging(self):
        """
        @see PMXObject.debug, PMXObject.info, PMXObject.warn
        """
        import logging
        from datetime import datetime
        
        # File name
        d = datetime.now().strftime('%d-%m-%Y-%H-%M-%S')
        filename = os.path.join(self.settings.PMX_LOG_PATH, 'messages-%s.log' % d)
        logging.basicConfig(filename=filename, level=logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        
        logging.root.addHandler(ch)
        logging.root.info("Application startup")
        logging.root.debug("Application startup debug")
        
        self.logger = logging.root

    #========================================================
    # Managers
    #========================================================
    @deco.logtime
    def setupSupportManager(self, callbackSplashMessage = None):
        from prymatex.gui.support.manager import PMXSupportManager
        
        self.settings.registerConfigurable(PMXSupportManager)
        
        manager = PMXSupportManager(self)
        self.settings.configure(manager)
        
        #Prepare prymatex namespace
        sharePath = self.settings.value('PMX_SHARE_PATH')
        manager.addNamespace('prymatex', sharePath)
        manager.updateEnvironment({ #TextMate Compatible :P
                'TM_APP_PATH': self.settings.value('PMX_APP_PATH'),
                'TM_SUPPORT_PATH': manager.environment['PMX_SUPPORT_PATH'],
                'TM_BUNDLES_PATH': manager.environment['PMX_BUNDLES_PATH'],
                'TM_THEMES_PATH': manager.environment['PMX_THEMES_PATH'],
                'TM_PID': os.getpid(),
                #Prymatex 
                'PMX_APP_NAME': self.applicationName().title(),
                'PMX_APP_PATH': self.settings.value('PMX_APP_PATH'),
                'PMX_PREFERENCES_PATH': self.settings.value('PMX_PREFERENCES_PATH'),
                'PMX_VERSION': self.applicationVersion(),
                'PMX_PID': self.applicationPid()
        })

        #Prepare user namespace
        homePath = self.settings.value('PMX_HOME_PATH')
        manager.addNamespace('user', homePath)
        manager.updateEnvironment({
                'PMX_HOME_PATH': homePath,
                'PMX_PROFILE_PATH': self.settings.value('PMX_PROFILE_PATH'),
                'PMX_TMP_PATH': self.settings.value('PMX_TMP_PATH'),
                'PMX_LOG_PATH': self.settings.value('PMX_LOG_PATH')
        })
        manager.loadSupport(callbackSplashMessage)
        self.supportManager = manager

    def setupFileManager(self):
        from prymatex.core.filemanager import PMXFileManager
        
        self.settings.registerConfigurable(PMXFileManager)
        self.fileManager = PMXFileManager(self)
        self.settings.configure(self.fileManager)
        
        self.fileManager.fileChanged.connect(self.on_fileChanged)
        self.fileManager.fileDeleted.connect(self.on_fileDeleted)
    
    def setupProjectManager(self):
        from prymatex.gui.project.manager import PMXProjectManager
        
        self.settings.registerConfigurable(PMXProjectManager)
        self.projectManager = PMXProjectManager(self)
        self.settings.configure(self.projectManager)
        
        self.projectManager.loadProject()
    
    def setupKernelManager(self):
        try:
            from IPython.frontend.qt.kernelmanager import QtKernelManager
            self.kernelManager = QtKernelManager()
            self.kernelManager.start_kernel()
            self.kernelManager.start_channels()
            if hasattr(self.kernelManager, "connection_file"):
                ipconnection = self.kernelManager.connection_file
            else:
                shell_port = self.kernelManager.shell_address[1]
                iopub_port = self.kernelManager.sub_address[1]
                stdin_port = self.kernelManager.stdin_address[1]
                hb_port = self.kernelManager.hb_address[1]
                ipconnection = "--shell={0} --iopub={1} --stdin={2} --hb={3}".format(shell_port, iopub_port, stdin_port, hb_port)
            self.supportManager.updateEnvironment({ 
                    "PMX_IPYTHON_CONNECTION": ipconnection
            })
        except ImportError as e:
            print("Warning: %s" % e)
            self.kernelManager = None

    def setupPluginManager(self):
        from prymatex.core.plugin.manager import PMXPluginManager
        self.pluginManager = PMXPluginManager(self)
        defaultDirectory = self.settings.value('PMX_PLUGINS_PATH')
        self.pluginManager.addPluginDirectory(defaultDirectory)
        self.pluginManager.loadPlugins()
        #self.pluginManager.register("editor.default", PMXCodeEditor)
        #self.pluginManager.register("editor.graphicviz", PMXGraphicvizEditor)
        
    def setupCoroutines(self):
        self.scheduler = coroutines.Scheduler(self)

    def setupZeroMQContext(self):
        try:
            from prymatex.utils import zeromqt
            self.zmqContext = zeromqt.ZeroMQTContext(parent = self)
        except ImportError as e:
            print("Warning: %s" % e)
            self.zmqContext = None

    #========================================================
    # Dialogs
    #========================================================
    def setupDialogs(self):
        #Settings
        from prymatex.gui.settings.dialog import PMXSettingsDialog
        from prymatex.gui.settings.widgets import PMXGeneralWidget, PMXNetworkWidget
        from prymatex.gui.settings.environment import PMXEnvVariablesWidgets
        from prymatex.gui.settings.themes import PMXThemeConfigWidget
        from prymatex.gui.settings.widgets import PMXFileManagerSettings
        self.configDialog = PMXSettingsDialog(self)
        self.configDialog.register(PMXGeneralWidget)
        self.configDialog.register(PMXFileManagerSettings)
        self.configDialog.register(PMXThemeConfigWidget)
        self.configDialog.register(PMXEnvVariablesWidgets)
        self.configDialog.register(PMXNetworkWidget)
        
        #Bundle Editor
        from prymatex.gui.support.bundleeditor import PMXBundleEditor
        self.bundleEditor = PMXBundleEditor(self)
        #self.bundleEditor.setModal(True)
        
        #Dialog System
        if self.zmqContext:
            from prymatex.gui.dialogs.pmxdialog import PMXDialogSystem
            self.dialogSystem = PMXDialogSystem(self)
    
    def closePrymatex(self):
        self.logger.debug("Close")
        self.settings.setValue("mainWindowGeometry", self.mainWindow.saveGeometry())
        self.settings.setValue("mainWindowState", self.mainWindow.saveState())
        self.settings.sync()
        os.unlink(self.fileLock)
    
    def commitData(self):
        print("Commit data")
        
    def saveState(self, session_manager):
        self.logger.debug( "Save state %s" % session_manager)
    
    #---------------------------------------------------
    # Editors and mainWindow handle
    #---------------------------------------------------
    def createMainWindow(self):
        """
        Creates the windows
        """
        #Por ahora solo una mainWindow
        from prymatex.gui.mainwindow import PMXMainWindow
        #TODO: Testeame con mas de una
        for _ in range(1):
            self.mainWindow = PMXMainWindow(self)
                
            #Configure and add dockers
            self.pluginManager.populateMainWindow(self.mainWindow)
            
            geometry = self.settings.value("mainWindowGeometry")
            state = self.settings.value("mainWindowState")
            if geometry:
                self.mainWindow.restoreGeometry(geometry)
            if state:
                self.mainWindow.restoreState(state)
                
            self.mainWindow.addEmptyEditor()
            self.mainWindow.show()

    def currentEditor(self):
        return self.mainWindow.currentEditor()

    def findEditorForFile(self, filePath):
        #Para cada mainwindow buscar el editor
        return self.mainWindow, self.mainWindow.findEditorForFile(filePath)
            
    def getEditorInstance(self, filePath = None, project = None, parent = None):
        return self.pluginManager.createEditor(filePath, project, parent)

    def openFile(self, filePath, cursorPosition = (0,0), focus = True):
        '''
        Opens a file in current window
        '''
        if self.fileManager.isOpen(filePath):
            mainWindow, editor = self.findEditorForFile(filePath)
            if editor is not None:
                mainWindow.setCurrentEditor(editor)
                editor.setCursorPosition(cursorPosition)
        else:
            project = self.projectManager.findProjectForPath(filePath)
            editor = self.getEditorInstance(filePath, project, self.mainWindow)
            def appendChunksTask(editor, filePath):
                content = self.fileManager.openFile(filePath)
                editor.setReadOnly(True)
                for line in content.splitlines():
                    editor.appendPlainText(line)
                    yield
                editor.setReadOnly(False)
                yield coroutines.Return(editor, filePath)
            def on_editorReady(result):
                editor, filePath = result.value
                editor.setModified(False)
                editor.setCursorPosition(cursorPosition)
                self.mainWindow.tryCloseEmptyEditor()
                self.mainWindow.addEditor(editor, focus)
            task = self.scheduler.newTask( appendChunksTask(editor, filePath) )
            task.done.connect( on_editorReady  )

    def openDirectory(self, directoryPath):
        raise NotImplementedError("Directory contents should be opened as files here")        
    
    def handleUrlCommand(self, url):
        if isinstance(url, basestring):
            url = QtCore.QUrl(url)
        if url.scheme() == "txmt":
            #TODO: Controlar que sea un open
            sourceFile = url.queryItemValue('url')
            position = (0, 0)
            line = url.queryItemValue('line')
            if line:
                position = (int(line) - 1, position[1])
            column = url.queryItemValue('column')
            if column:
                position = (position[0], int(column) - 1)
            if sourceFile:
                self.openFile(sourceFile, position)
            else:
                self.currentEditor().setCursorPosition(position)

    def openArgumentFiles(self, args):
        for filePath in filter(lambda f: os.path.exists(f), args):
            if os.path.isfile(filePath):
                self.openFile(filePath)
            else:
                self.openDirectory(filePath)

    def on_fileChanged(self, filePath):
        message = "The file '%s' has been changed on the file system, Do you want to replace the editor contents with these changes?" % filePath
        #Yes No
        print(message)
        
    def on_fileDeleted(self, filePath):
        message = "The file '%s' has been deleted or is not accessible. Do you want to save your changes or close the editor without saving?" % filePath
        print(message)
    
    #---------------------------------------------------
    # Exceptions, Print exceptions in a window
    #---------------------------------------------------
    def replaceSysExceptHook(self):
        def displayExceptionDialog(exctype, value, traceback):
            ''' Display a nice dialog showing the python traceback'''
            from prymatex.gui.emergency.tracedialog import PMXTraceBackDialog
            sys.__excepthook__(exctype, value, traceback)
            PMXTraceBackDialog.fromSysExceptHook(exctype, value, traceback).exec_()

        sys.excepthook = displayExceptionDialog