##!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from string import Template

from prymatex.qt import QtCore, QtGui
from prymatex.qt.compat import getSaveFileName
from prymatex.qt.helpers import text2objectname
from prymatex.qt.helpers.widgets import center_widget
from prymatex.qt.helpers.menus import create_menu, extend_menu, update_menu, add_actions

from prymatex import resources

from prymatex.core import exceptions
from prymatex.core.settings import pmxConfigPorperty
from prymatex.core import PMXBaseComponent, PMXBaseDock, PMXBaseDialog, PMXBaseStatusBar

from prymatex.utils.i18n import ugettext as _
from prymatex.utils import html

from prymatex.gui.mainmenu import MainMenuMixin, tabSelectableModelFactory
from prymatex.gui.statusbar import PMXStatusBar
from prymatex.gui.processors import MainWindowCommandProcessor

from prymatex.widgets.docker import DockWidgetTitleBar
from prymatex.widgets.toolbar import DockWidgetToolBar
from prymatex.widgets.message import PopupMessageWidget
from prymatex.widgets.splitter import SplitTabWidget

from functools import reduce

class PMXMainWindow(QtGui.QMainWindow, MainMenuMixin, PMXBaseComponent):
    """Prymatex main window"""
    # --------------------- Signals
    currentEditorChanged = QtCore.Signal(object)

    # --------------------- Settings
    SETTINGS_GROUP = 'MainWindow'

    @pmxConfigPorperty(default = "$PMX_APP_NAME ($PMX_VERSION)")
    def windowTitleTemplate(self, titleTemplate):
         self.titleTemplate = Template(titleTemplate)

    @pmxConfigPorperty(default = True)
    def showMenuBar(self, value):
        self.menuBar().setShown(value)

    _editorHistory = []
    _editorHistoryIndex = 0

    # Constructor
    def __init__(self, parent = None):
        """The main window
        @param parent: The QObject parent, in this case it should be the QApp
        @param files_to_open: The set of files to be opened when the window is shown in the screen.
        """
        QtGui.QMainWindow.__init__(self)
        PMXBaseComponent.__init__(self)

        self.setupUi()
        
        self.tabSelectableModel = tabSelectableModelFactory(self)

        # Connect Signals
        self.splitTabWidget.currentWidgetChanged.connect(self.on_currentWidgetChanged)
        self.splitTabWidget.currentWidgetChanged.connect(self.setWindowTitleForEditor)
        self.splitTabWidget.tabCloseRequest.connect(self.closeEditor)
        self.splitTabWidget.tabCreateRequest.connect(self.addEmptyEditor)
        self.application.supportManager.bundleItemTriggered.connect(self.on_bundleItemTriggered)

        center_widget(self, scale = (0.9, 0.8))
        self.dockers = []
        self.dialogs = []
        self.customComponentObjects = {}

        self.setAcceptDrops(True)

        self.popupMessage = PopupMessageWidget(self)

        #Processor de comandos local a la main window
        self.commandProcessor = MainWindowCommandProcessor(self)
        self.bundleItem_handler = self.insertBundleItem

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowIcon(resources.getIcon("prymatex"))

        self.setupDockToolBars()
        
        self.splitTabWidget = SplitTabWidget(self)
        self.setCentralWidget(self.splitTabWidget)
        
        # Status and menu bars
        self.setStatusBar(PMXStatusBar(self))
        self.setMenuBar(QtGui.QMenuBar(self))
        
        self.resize(801, 600)
        
    # ---------- Implements PMXBaseComponent's interface
    def addComponent(self, component):
        if isinstance(component, PMXBaseDock):
            self.addDock(component, component.PREFERED_AREA)
        elif isinstance(component, PMXBaseDialog):
            self.addDialog(component)
        elif isinstance(component, PMXBaseStatusBar):
            self.addStatusBar(component)

    def initialize(self, application):
        PMXBaseComponent.initialize(self, application)
        # Dialogs
        self.selectorDialog = self.findChild(QtGui.QDialog, "SelectorDialog")
        self.aboutDialog = self.findChild(QtGui.QDialog, "AboutDialog")
        self.settingsDialog = self.findChild(QtGui.QDialog, "SettingsDialog")
        self.bundleEditorDialog = self.findChild(QtGui.QDialog, "BundleEditorDialog")
        self.profileDialog = self.findChild(QtGui.QDialog, "ProfileDialog")
        self.templateDialog = self.findChild(QtGui.QDialog, "TemplateDialog")
        self.projectDialog = self.findChild(QtGui.QDialog, "ProjectDialog")

        # Dockers
        self.browserDock = self.findChild(QtGui.QDockWidget, "BrowserDock")
        self.terminalDock = self.findChild(QtGui.QDockWidget, "TerminalDock")
        self.projectsDock = self.findChild(QtGui.QDockWidget, "ProjectsDock")

        # Build Main Menu
        def extendMainMenu(klass):
            menuExtensions = klass.contributeToMainMenu()
            objects = []
            for name, settings in menuExtensions.items():
                if not settings:
                    continue

                # Find parent menu
                parentMenu = self.findChild(QtGui.QMenu,
                    text2objectname(name, prefix = "menu"))
                # Extend
                if parentMenu:
                    # Fix menu extensions
                    if not isinstance(settings, list):
                        settings = [ settings ]
                    objects += extend_menu(parentMenu, settings,
                        dispatcher = self.componentInstanceDispatcher,
                        shortcut_handler = self.shortcutHandler)
                else:
                    objs = create_menu(self, settings,
                        dispatcher = self.componentInstanceDispatcher,
                        allObjects = True,
                        shortcut_handler = self.shortcutHandler)
                    add_actions(self.menuBar(), [ objs[0] ], settings.get("before", None))
                    objects += objs

            # Store all new objects from creation or extension
            self.customComponentObjects.setdefault(klass, []).extend(objects)

            for componentClass in application.pluginManager.findComponentsForClass(klass):
                extendMainMenu(componentClass)

        extendMainMenu(self.__class__)
        
        # Load some menus as atters of the main window
        self.menuPanels = self.findChild(QtGui.QMenu, "menuPanels")
        self.menuRecentFiles = self.findChild(QtGui.QMenu, "menuRecentFiles")
        self.menuBundles = self.findChild(QtGui.QMenu, "menuBundles")
        
        # Metemos las acciones de las dockers al menu panels
        for dock in self.dockers:
            toggleAction = dock.toggleViewAction()
            self.menuPanels.addAction(toggleAction)
            self.addAction(toggleAction)

        self.application.supportManager.appendMenuToBundleMenuGroup(self.menuBundles)
        
    def componentInstanceDispatcher(self, handler, *largs):
        obj = self.sender()
        componentClass = None
        for cmpClass, objects in self.customComponentObjects.items():
            if obj in objects:
                componentClass = cmpClass
                break

        componentInstances = [ self ]
        for componentClass in self.application.componentHierarchyForClass(componentClass):
            componentInstances = reduce(
                lambda ai, ci: ai + ci.findChildren(componentClass),
                componentInstances, [])

        widget = self.application.focusWidget()
        self.logger.debug("Trigger %s over %s" % (obj, componentInstances))

        # TODO Tengo todas pero solo se lo aplico a la ultima que es la que generalmente esta en uso
        handler(componentInstances[-1], *largs)

    def shortcutHandler(self, action, sequence):
        action.setShortcut(sequence.key())

    def environmentVariables(self):
        env = {}
        for docker in self.dockers:
            env.update(docker.environmentVariables())
        return env

    @classmethod
    def contributeToSettings(cls):
        from prymatex.gui.settings.mainwindow import MainWindowSettingsWidget
        return [ MainWindowSettingsWidget ]

    # --------------- Bundle Items
    def on_bundleItemTriggered(self, bundleItem):
        if self.bundleItem_handler is not None:
            self.bundleItem_handler(bundleItem)

    def insertBundleItem(self, bundleItem, **processorSettings):
        '''Insert selected bundle item in current editor if possible'''
        assert not bundleItem.isEditorNeeded(), "Bundle Item needs editor"

        self.commandProcessor.configure(processorSettings)
        bundleItem.execute(self.commandProcessor)

    # Browser error
    def showErrorInBrowser(self, title, summary, exitcode = -1, **settings):
        commandScript = '''
source "$TM_SUPPORT_PATH/lib/webpreview.sh"

html_header '%(name)s error'
echo -e '<pre>%(output)s</pre>'
echo -e '<p>Exit code was: %(exitcode)d</p>'
html_footer
        ''' % {
                'name': html.escape(title),
                'output': html.htmlize(summary),
                'exitcode': exitcode}
        bundle = self.application.supportManager.getBundle(self.application.supportManager.defaultBundleForNewBundleItems)
        command = self.application.supportManager.buildAdHocCommand(commandScript,
            bundle,
            name = "%s error" % title,
            commandOutput = 'showAsHTML')
        self.bundleItem_handler(command, **settings)

    # -------------------- Setups
    def setupDockToolBars(self):
        self.dockToolBars = {
            QtCore.Qt.LeftDockWidgetArea: DockWidgetToolBar("Left Dockers", QtCore.Qt.LeftDockWidgetArea, self),
            QtCore.Qt.RightDockWidgetArea: DockWidgetToolBar("Right Dockers", QtCore.Qt.RightDockWidgetArea, self),
            QtCore.Qt.TopDockWidgetArea: DockWidgetToolBar("Top Dockers", QtCore.Qt.TopDockWidgetArea, self),
            QtCore.Qt.BottomDockWidgetArea: DockWidgetToolBar("Bottom Dockers", QtCore.Qt.BottomDockWidgetArea, self),
        }
        for dockArea, toolBar in self.dockToolBars.items():
            self.addToolBar(DockWidgetToolBar.DOCK_AREA_TO_TB[dockArea], toolBar)
            toolBar.hide()

    def toggleDockToolBarVisibility(self):
        for toolBar in list(self.dockToolBars.values()):
            if toolBar.isVisible():
                toolBar.hide()
            else:
                toolBar.show()

    # ---------- Componer la mainWindow
    def addStatusBar(self, statusBar):
        self.statusBar().addPermanentWidget(statusBar)

    def addDock(self, dock, area):
        self.addDockWidget(area, dock)
        titleBar = DockWidgetTitleBar(dock)
        titleBar.collpaseAreaRequest.connect(self.on_dockWidgetTitleBar_collpaseAreaRequest)
        dock.setTitleBarWidget(titleBar)
        dock.hide()
        self.dockers.append(dock)

    def addDialog(self, dialog):
        self.dialogs.append(dialog)

    def on_dockWidgetTitleBar_collpaseAreaRequest(self, dock):
        if not dock.isFloating():
            area = self.dockWidgetArea(dock)
            self.dockToolBars[area].show()

    def globalCallback(self):
        """Global callback"""
        widget = self.application.focusWidget()
        action = self.sender()
        callback = action.data()
        getattr(widget, callback, lambda : None)()

    def updateMenuForEditor(self, editor):
        def set_objects(instance, objects):
            for obj in objects:
                if isinstance(obj, QtGui.QAction):
                    obj.setVisible(not hasattr(obj, "testVisible") or \
                        obj.testVisible(instance))
                    obj.setEnabled(not hasattr(obj, "testEnabled") or \
                        obj.testEnabled(instance))
                    if obj.isCheckable():
                        obj.setChecked(hasattr(obj, "testChecked") and \
                            obj.testChecked(instance))

        # Primero las del editor
        self.logger.debug("Update editor %s objects" % editor)
        objects = self.customComponentObjects.get(editor.__class__, [])
        set_objects(editor, objects)

        # Ahora sus children
        componentClass = self.application.findComponentsForClass(editor.__class__)
        for klass in componentClass:
            for componentInstance in editor.findChildren(klass):
                objects = self.customComponentObjects.get(klass, [])
                set_objects(componentInstance, objects)

    def showMessage(self, *largs, **kwargs):
        self.popupMessage.showMessage(*largs, **kwargs)

    # ---------------- Create and manage editors
    def addEmptyEditor(self):
        editor = self.application.createEditorInstance(parent = self)
        self.addEditor(editor)
        return editor

    def removeEditor(self, editor):
        self.disconnect(editor, QtCore.SIGNAL("newLocationMemento"), self.on_editor_newLocationMemento)
        self.splitTabWidget.removeTab(editor)
        # TODO Ver si el remove borra el editor y como acomoda el historial
        del editor

    def addEditor(self, editor, focus = True):
        self.splitTabWidget.addTab(editor)
        self.connect(editor, QtCore.SIGNAL("newLocationMemento"), self.on_editor_newLocationMemento)
        if focus:
            self.setCurrentEditor(editor)

    def findEditorForFile(self, filePath):
        # Find open editor for fileInfo
        for editor in self.splitTabWidget.allWidgets():
            if editor.filePath == filePath:
                return editor

    def editors(self):
        return self.splitTabWidget.allWidgets()

    def setCurrentEditor(self, editor):
        self.splitTabWidget.setCurrentWidget(editor)

    def currentEditor(self):
        return self.splitTabWidget.currentWidget()

    def on_currentWidgetChanged(self, editor):
        #Update Menu
        self.updateMenuForEditor(editor)

        #Avisar al manager si tenemos editor y preparar el handler
        self.application.supportManager.setEditorAvailable(editor is not None)
        self.bundleItem_handler = editor.bundleItemHandler() or self.insertBundleItem if editor is not None else self.insertBundleItem

        #Emitir señal de cambio
        self.currentEditorChanged.emit(editor)

        if editor is not None:
            self.addEditorToHistory(editor)
            editor.setFocus()
            self.application.checkExternalAction(self, editor)

    def setWindowTitleForEditor(self, editor):
        #Set Window Title for editor, editor can be None
        titleChunks = [ self.titleTemplate.safe_substitute(**self.application.supportManager.environmentVariables()) ]
        if editor is not None:
            titleChunks.insert(0, editor.tabTitle())
        self.setWindowTitle(" - ".join(titleChunks))

    def saveEditor(self, editor = None, saveAs = False):
        editor = editor or self.currentEditor()
        if editor.isExternalChanged():
            message = "The file '%s' has been changed on the file system, Do you want save the file with other name?"
            result = QtGui.QMessageBox.question(editor, _("File changed"),
                _(message) % editor.filePath,
                buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                defaultButton = QtGui.QMessageBox.Yes)
            if result == QtGui.QMessageBox.Yes:
                saveAs = True
        if editor.isNew() or saveAs:
            fileDirectory = self.application.fileManager.directory(self.projectsDock.currentPath()) if editor.isNew() else editor.fileDirectory()
            fileName = editor.fileName()
            fileFilters = editor.fileFilters()
            # TODO Armar el archivo destino y no solo el basedir
            filePath, _ = getSaveFileName(
                self,
                caption = "Save file as" if saveAs else "Save file",
                basedir = fileDirectory,
                filters = fileFilters
            )
        else:
            filePath = editor.filePath

        if filePath:
            editor.save(filePath)

    def closeEditor(self, editor = None, cancel = False):
        editor = editor or self.currentEditor()
        buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.No
        if cancel:
            buttons |= QtGui.QMessageBox.Cancel
        if editor is None: return
        while editor and editor.isModified():
            response = QtGui.QMessageBox.question(self, "Save",
                "Save %s" % editor.tabTitle(),
                buttons = buttons,
                defaultButton = QtGui.QMessageBox.Ok)
            if response == QtGui.QMessageBox.Ok:
                self.saveEditor(editor = editor)
            elif response == QtGui.QMessageBox.No:
                break
            elif response == QtGui.QMessageBox.Cancel:
                raise exceptions.UserCancelException()
        editor.close()
        self.removeEditor(editor)

    def tryCloseEmptyEditor(self, editor = None):
        editor = editor or self.currentEditor()
        if editor is not None and editor.isNew() and not editor.isModified():
            self.closeEditor(editor)

    # ---------------- Handle location history
    def on_editor_newLocationMemento(self, memento):
        self.addHistoryEntry({"editor": self.sender(), "memento": memento})

    def addEditorToHistory(self, editor):
        if self._editorHistory and self._editorHistory[self._editorHistoryIndex]["editor"] == editor:
            return
        self.addHistoryEntry({"editor": editor})

    def addHistoryEntry(self, entry):
        self._editorHistory = [entry] + self._editorHistory[self._editorHistoryIndex:]
        self._editorHistoryIndex = 0

    # ---------------- MainWindow Events
    def closeEvent(self, event):
        for editor in self.editors():
            while editor and editor.isModified():
                response = QtGui.QMessageBox.question(self, "Save",
                    "Save %s" % editor.tabTitle(),
                    buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel,
                    defaultButton = QtGui.QMessageBox.Ok)
                if response == QtGui.QMessageBox.Ok:
                    self.saveEditor(editor = editor)
                elif response == QtGui.QMessageBox.No:
                    break
                elif response == QtGui.QMessageBox.Cancel:
                    event.ignore()
                    return

    # ---------- MainWindow State
    def componentState(self):
        #Documentos abiertos
        openDocumentsOnQuit = []
        for editor in self.editors():
            if not editor.isNew():
                openDocumentsOnQuit.append((editor.filePath, editor.cursorPosition()))
        state = {
            "self": QtGui.QMainWindow.saveState(self),
            "dockers": dict([(dock.objectName(), dock.componentState()) for dock in self.dockers]),
            "documents": openDocumentsOnQuit,
            "geometry": self.saveGeometry(),
        }
        return state

    def setComponentState(self, state):
        # Restore dockers
        for dock in self.dockers:
            dockName = dock.objectName()
            if dockName in state["dockers"]:
                dock.setComponentState(state["dockers"][dockName])

        # Restore Main window
        self.restoreGeometry(state["geometry"])
        for doc in state["documents"]:
            self.application.openFile(*doc, mainWindow = self)
        QtGui.QMainWindow.restoreState(self, state["self"])

    # ------------ Drag and Drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        def collectFiles(paths):
            from glob import glob
            '''Recursively collect fileInfos'''
            for path in paths:
                if os.path.isfile(path):
                    yield path
                elif os.path.isdir(path):
                    dirSubEntries = glob(os.path.join(path, '*'))
                    for entry in collectFiles(dirSubEntries):
                        yield entry

        urls = [url.toLocalFile() for url in event.mimeData().urls()]

        for path in collectFiles(urls):
            # TODO: Take this code somewhere else, this should change as more editor are added
            if not self.canBeOpened(path):
                self.logger.debug("Skipping dropped element %s" % path)
                continue
            self.logger.debug("Opening dropped file %s" % path)
            #self.openFile(QtCore.QFileInfo(path), focus = False)
            self.application.openFile(path)

    FILE_SIZE_THERESHOLD = 1024 ** 2 # 1MB file is enough, ain't it?
    STARTSWITH_BLACKLIST = ['.', '#', ]
    ENDSWITH_BLACKLIST = ['~', 'pyc', 'bak', 'old', 'tmp', 'swp', '#', ]

    def canBeOpened(self, path):
        # Is there any support for it?
        if not self.application.supportManager.findSyntaxByFileType(path):
            return False
        for start in self.STARTSWITH_BLACKLIST:
            if path.startswith(start):
                return False
        for end in self.ENDSWITH_BLACKLIST:
            if path.endswith(end):
                return False
        if os.path.getsize(path) > self.FILE_SIZE_THERESHOLD:
            return False
        return True

