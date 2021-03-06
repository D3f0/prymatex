#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from string import Template
from functools import reduce

from prymatex import resources

from prymatex.qt import QtCore, QtGui
from prymatex.qt.compat import getSaveFileName
from prymatex.qt.helpers import (text_to_objectname, create_menu, extend_menu,
    add_actions, test_actions, center_widget, qbytearray_to_hex, hex_to_qbytearray)

from prymatex.core import exceptions
from prymatex.core.settings import (ConfigurableItem, ConfigurableHook)
from prymatex.core import (PrymatexComponentWidget, PrymatexComponent,
    PrymatexDock, PrymatexDialog, PrymatexStatusBar)

from prymatex.utils.i18n import ugettext as _
from prymatex.utils import html

from prymatex.widgets.docker import DockWidgetTitleBar
from prymatex.widgets.toolbar import DockWidgetToolBar
from prymatex.widgets.notification import OverlayNotifier
from prymatex.widgets.splitter import SplitterWidget

from .menubar import PrymatexMainMenuBar
from .statusbar import PrymatexMainStatusBar
from .processors import PrymatexMainCommandProcessor
from .actions import MainWindowActionsMixin, tabSelectableModelFactory

class PrymatexMainWindow(PrymatexComponentWidget, MainWindowActionsMixin, QtGui.QMainWindow):
    """Prymatex main window"""
    # --------------------- Signals
    currentEditorChanged = QtCore.Signal(object)

    # --------------------- Settings
    SETTINGS_GROUP = 'MainWindow'

    @ConfigurableItem(default = "$PMX_APP_NAME ($PMX_VERSION)")
    def windowTitleTemplate(self, titleTemplate):
         self.titleTemplate = Template(titleTemplate)

    @ConfigurableItem(default = False)
    def showTabsIfMoreThanOne(self, value):
        self.centralWidget().setShowTabs(not value)

    @ConfigurableItem(default = True)
    def showMenuBar(self, value):
        self.menuBar().setShown(value)

    @ConfigurableHook("CodeEditor.defaultTheme")
    def defaultTheme(self, themeUUID):
        theme = self.application.supportManager.getBundleItem(themeUUID)
        self.notifier.setPalette(theme.palette())

    _editorHistory = []
    _editorHistoryIndex = 0

    # Constructor
    def __init__(self, **kwargs):
        """The main window
        @param parent: The QObject parent, in this case it should be the QApp
        @param files_to_open: The set of files to be opened when the window is shown in the screen.
        """
        super(PrymatexMainWindow, self).__init__(**kwargs)
        self.setupUi()
        
        self.tabSelectableModel = tabSelectableModelFactory(self)

        # Connect Signals
        self.application.supportManager.bundleItemTriggered.connect(self.on_bundleItemTriggered)

        center_widget(self, scale = (0.9, 0.8))
        self.dockWidgets = []
        self.dialogs = []
        self.customComponentObjects = {}

        self.setAcceptDrops(True)

        self.notifier = OverlayNotifier(self)
        self.notifier.setBackgroundRole(QtGui.QPalette.Window)
        self.notifier.setForegroundRole(QtGui.QPalette.WindowText)
        font = self.font()
        font.setPointSize(font.pointSize() * 0.8)
        self.notifier.setFont(font)
        
        #Processor de comandos local a la main window
        self.commandProcessor = PrymatexMainCommandProcessor(self)
        self.bundleItem_handler = self.insertBundleItem

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.setWindowIcon(resources.get_icon("prymatex"))

        self.setupDockToolBars()
        
        self.setCentralWidget(SplitterWidget(parent = self))
        
        # Splitter signals
        self.centralWidget().currentWidgetChanged.connect(self.on_splitter_currentWidgetChanged)
        self.centralWidget().layoutChanged.connect(self.on_splitter_layoutChanged)
        self.centralWidget().tabCloseRequest.connect(self.closeEditor)
        self.centralWidget().tabCreateRequest.connect(self.addEmptyEditor)

        # Status and menu bars
        self.setStatusBar(PrymatexMainStatusBar(self))
        self.setMenuBar(PrymatexMainMenuBar(self))
        
        self.resize(801, 600)
        
    # ---------- Implements PrymatexComponentWidget
    def addComponent(self, component):
        if isinstance(component, PrymatexDock):
            self.addDock(component, component.PREFERED_AREA)
        elif isinstance(component, PrymatexDialog):
            self.addDialog(component)
        elif isinstance(component, PrymatexStatusBar):
            self.addStatusBar(component)

    def initialize(self, **kwargs):
        super(PrymatexMainWindow, self).initialize(**kwargs)
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
            menuExtensions = issubclass(klass, PrymatexComponent) and klass.contributeToMainMenu() or None
            if menuExtensions is not None:
                objects = []
                for name, settings in menuExtensions.items():
                    if not settings:
                        continue
    
                    # Find parent menu
                    parentMenu = self.findChild(QtGui.QMenu, 
                        text_to_objectname(name, prefix = "menu"))
                    # Extend
                    if parentMenu is not None:
                        # Fix menu extensions
                        if not isinstance(settings, list):
                            settings = [ settings ]
                        objects += extend_menu(parentMenu, settings,
                            dispatcher = self.componentInstanceDispatcher,
                            sequence_handler = self.application.registerShortcut,
                            icon_resolver = resources.get_icon)
                    else:
                        objs = create_menu(self, settings,
                            dispatcher = self.componentInstanceDispatcher,
                            allObjects = True,
                            sequence_handler = self.application.registerShortcut,
                            icon_resolver = resources.get_icon)
                        add_actions(self.menuBar(), [ objs[0] ], settings.get("before", None))
                        objects += objs

                # Store all new objects from creation or extension
                self.customComponentObjects.setdefault(klass, []).extend(objects)

                for componentClass in self.application.pluginManager.findComponentsForClass(klass):
                    extendMainMenu(componentClass)

        extendMainMenu(self.__class__)
        
        # Load some menus as atters of the main window
        self.menuPanels = self.findChild(QtGui.QMenu, "menuPanels")
        self.menuRecentFiles = self.findChild(QtGui.QMenu, "menuRecentFiles")
        self.menuBundles = self.findChild(QtGui.QMenu, "menuBundles")
        self.menuFocusGroup = self.findChild(QtGui.QMenu, "menuFocusGroup")
        self.menuMoveEditorToGroup = self.findChild(QtGui.QMenu, "menuMoveEditorToGroup")
        
        # Metemos las acciones de las dockers al menu panels
        dockIndex = 1
        for dock in self.dockWidgets:
            toggleAction = dock.toggleViewAction()
            if dock.SEQUENCE is not None:
                sequence = dock.SEQUENCE
            else:
                sequence = resources.get_sequence("Docks", dock.objectName(), "Alt+%d" % dockIndex)
                dockIndex += 1
            self.application.registerShortcut(toggleAction, sequence)
            if dock.ICON:
                toggleAction.setIcon(dock.ICON)
            self.menuPanels.addAction(toggleAction)
            self.addAction(toggleAction)

        # Metemos las acciones del support
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

    def environmentVariables(self):
        env = {}
        for docker in self.dockWidgets:
            env.update(docker.environmentVariables())
        return env

    @classmethod
    def contributeToSettings(cls):
        from prymatex.gui.settings.mainwindow import MainWindowSettingsWidget
        return [ MainWindowSettingsWidget ]

    # ---------- Override QMainWindow
    def show(self):
        QtGui.QMainWindow.show(self)
        
        # Test menu actions
        objects = self.customComponentObjects[self.__class__]
        test_actions(self, 
            filter(lambda obj: isinstance(obj, QtGui.QAction), objects))

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
        self.dockWidgets.append(dock)

    def addDialog(self, dialog):
        self.dialogs.append(dialog)

    def on_dockWidgetTitleBar_collpaseAreaRequest(self, dock):
        if not dock.isFloating():
            area = self.dockWidgetArea(dock)
            self.dockToolBars[area].show()

    def updateMenuForEditor(self, editor):
        # Primero las del editor
        self.logger.debug("Update editor %s objects" % editor)
        objects = self.customComponentObjects.get(editor.__class__, [])
        test_actions(editor, 
            filter(lambda obj: isinstance(obj, QtGui.QAction), objects))

        # Ahora sus children
        componentClass = self.application.findComponentsForClass(editor.__class__)
        for klass in componentClass:
            for componentInstance in editor.findChildren(klass):
                objects = self.customComponentObjects.get(klass, [])
                test_actions(componentInstance, 
                    filter(lambda obj: isinstance(obj, QtGui.QAction), objects))

    # -------------- Notifications
    def showMessage(self, *largs, **kwargs):
        message = self.notifier.message(*largs, **kwargs)
        message.show()
        return message

    def showTooltip(self, *largs, **kwargs):
        tooltip = self.notifier.tooltip(*largs, **kwargs)
        tooltip.show()
        return tooltip
        
    def showStatus(self, *largs, **kwargs):
        status = self.notifier.status(*largs, **kwargs)
        status.show()
        return status

    # ---------------- Create and manage groups
    def addEmptyGroup(self):
        pass
        
    def moveEditorToNewGroup(self):
        self.centralWidget().moveWidgetToNewGroup(self.currentEditor())
    
    def setCurrentGroup(self, group):
        self.centralWidget().setCurrentGroup(group)

    def moveEditorToGroup(self, group):
        self.centralWidget().moveWidgetToGroup(group, self.currentEditor())
        
    def closeGroup(self):
        pass
        
    def nextGroup(self):
        pass
        
    def previousGroup(self):
        pass
        
    def moveEditorToNextGroup(self):
        self.centralWidget().moveWidgetToNextGroup(self.currentEditor())
        
    def moveEditorToPreviousGroup(self):
        self.centralWidget().moveWidgetToPreviousGroup(self.currentEditor())

    # ---------------- Create and manage editors
    def addEmptyEditor(self):
        editor = self.application.createEditorInstance(parent = self)
        self.addEditor(editor)

    def removeEditor(self, editor):
        self.disconnect(editor, QtCore.SIGNAL("newLocationMemento"), self.on_editor_newLocationMemento)
        self.centralWidget().removeTabWidget(editor)
        # TODO Clean history ?

    def addEditor(self, editor, focus = True):
        self.centralWidget().addTabWidget(editor)
        self.connect(editor, QtCore.SIGNAL("newLocationMemento"), self.on_editor_newLocationMemento)
        if focus:
            self.setCurrentEditor(editor)

    def findEditorForFile(self, filePath):
        # Find open editor for fileInfo
        for editor in self.centralWidget().allWidgets():
            if editor.filePath() == filePath:
                return editor

    def editors(self):
        return self.centralWidget().allWidgets()

    def setCurrentEditor(self, editor):
        self.centralWidget().setCurrentWidget(editor)

    def currentEditor(self):
        return self.centralWidget().currentWidget()

    def on_splitter_currentWidgetChanged(self, editor):
        #Update Menu
        self.updateMenuForEditor(editor)

        #Avisar al manager si tenemos editor y preparar el handler
        self.application.supportManager.setEditorAvailable(editor is not None)
        self.bundleItem_handler = editor.bundleItemHandler() or self.insertBundleItem if editor is not None else self.insertBundleItem

        #Emitir señal de cambio
        self.currentEditorChanged.emit(editor)

        # Build title
        titleChunks = [ self.titleTemplate.safe_substitute(
            **self.application.supportManager.environmentVariables()) ]

        if editor is not None:
            self.addEditorToHistory(editor)
            editor.setFocus()
            self.application.checkExternalAction(self, editor)
            titleChunks.insert(0, editor.title())
        
        # Set window title
        self.setWindowTitle(" - ".join(titleChunks))
    
    def saveEditor(self, editor = None, saveAs = False):
        editor = editor or self.currentEditor()
        if editor.isExternalChanged():
            message = "The file '%s' has been changed on the file system, Do you want save the file with other name?"
            result = QtGui.QMessageBox.question(editor, _("File changed"),
                _(message) % editor.filePath(),
                buttons = QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                defaultButton = QtGui.QMessageBox.Yes)
            if result == QtGui.QMessageBox.Yes:
                saveAs = True
        if editor.isNew() or saveAs:
            fileDirectory = self.application.fileManager.directory(self.projectsDock.currentPath()) if editor.isNew() else editor.fileDirectory()
            fileName = editor.title()
            fileFilters = editor.fileFilters()
            # TODO Armar el archivo destino y no solo el basedir
            file_path, _ = getSaveFileName(
                self,
                caption = "Save file as" if saveAs else "Save file",
                basedir = fileDirectory,
                filters = fileFilters
            )
        else:
            file_path = editor.filePath()

        if file_path:
            editor.save(file_path)

    def closeEditor(self, editor = None, cancel = False):
        editor = editor or self.currentEditor()
        buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.No
        if cancel:
            buttons |= QtGui.QMessageBox.Cancel
        if editor is None: return
        while editor and editor.isModified():
            response = QtGui.QMessageBox.question(self, "Save",
                "Save %s" % editor.title(),
                buttons = buttons,
                defaultButton = QtGui.QMessageBox.Ok)
            if response == QtGui.QMessageBox.Ok:
                self.saveEditor(editor = editor)
            elif response == QtGui.QMessageBox.No:
                break
            elif response == QtGui.QMessageBox.Cancel:
                raise exceptions.UserCancelException()
        self.removeEditor(editor)
        self.application.deleteEditorInstance(editor)

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
                    "Save %s" % editor.title(),
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
        componentState = super(PrymatexMainWindow, self).componentState()

        componentState["editors"] = []
        for editor in self.editors():
            editorState = editor.componentState()
            editorState["name"] = editor.__class__.__name__
            editorState["modified"] = editor.isModified()
            if editor.hasFile():
                editorState["file"] = editor.filePath()
            componentState["editors"].append(editorState)

        # Store geometry
        componentState["geometry"] = qbytearray_to_hex(self.saveGeometry())

        # Store self
        componentState["self"] = qbytearray_to_hex(QtGui.QMainWindow.saveState(self))

        return componentState

    def setComponentState(self, componentState):
        super(PrymatexMainWindow, self).setComponentState(componentState)

        # Restore open documents
        for editorState in componentState.get("editors", []):
            editor = self.application.createEditorInstance(
                class_name = editorState["name"],
                file_path = editorState.get("file"),
                parent = self)
            editor.setComponentState(editorState)
            editor.setModified(editorState.get("modified", False))
            self.addEditor(editor)

        # Restore geometry
        if "geometry" in componentState:
            self.restoreGeometry(hex_to_qbytearray(componentState["geometry"]))

        # Restore self
        if "self" in componentState:
            QtGui.QMainWindow.restoreState(self, hex_to_qbytearray(componentState["self"]))

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

