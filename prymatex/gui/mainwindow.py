#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import itertools
from string import Template

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from prymatex.ui.mainwindow import Ui_MainWindow
from prymatex.gui.actions import MainWindowActions
from prymatex.core.settings import pmxConfigPorperty
from prymatex.core.base import PMXObject
from prymatex.core import exceptions
from prymatex.utils.i18n import ugettext as _
from prymatex.gui import utils

class PMXMainWindow(QtGui.QMainWindow, Ui_MainWindow, MainWindowActions, PMXObject):
    '''Prymatex main window'''
    ##########################################################
    # Signals
    ##########################################################
    newFileCreated = pyqtSignal(str)
    
    ##########################################################
    # Settings
    ##########################################################
    SETTINGS_GROUP = 'MainWindow'

    windowTitleTemplate = pmxConfigPorperty(default = "$PMX_APP_NAME")
    
    @pmxConfigPorperty(default = True)
    def showMenuBar(self, value):
        self._showMenuBar = value
        self.menuBar().setShown(value)
    
    # Constructor
    def __init__(self):
        '''
        The main window
        @param parent: The QObject parent, in this case it should be the QApp
        @param files_to_open: The set of files to be opened when the window
                              is shown in the screen.
        '''
        QtGui.QMainWindow.__init__(self)
        self.setupUi(self)
        self.currentEditor = None
        
        self.setupDockers()
        self.setupDialogs()
        self.setupMenu()
        self.setupStatusBar()
        
        # Connect Signals
        self.splitTabWidget.tabWindowChanged.connect(self.setCurrentEditor)
        self.application.supportManager.bundleItemTriggered.connect(lambda item: self.currentEditor.insertBundleItem(item))
        
        utils.centerWidget(self, scale = (0.9, 0.8))
        self.configure()
        
        self.addEditor(self.application.getEditorInstance(parent = self))

    #============================================================
    # Setups
    #============================================================
    def setupStatusBar(self):
        from prymatex.gui.statusbar import PMXStatusBar
        from prymatex.gui.codeeditor.status import PMXCodeEditorStatus
        status = PMXStatusBar(self)
        status.addPermanentWidget(PMXCodeEditorStatus(self))
        self.setStatusBar(status)
        
    def setupDockers(self):
        '''
        Basic panels, dock objects. More docks should be available via plugins
        '''
        from prymatex.gui.dockers.fstree import PMXFileSystemDock
        from prymatex.gui.dockers.project import PMXProjectDock
        from prymatex.gui.dockers.symbols import PMXSymboldListDock
        from prymatex.gui.dockers.browser import PMXBrowserDock
        from prymatex.gui.dockers.console import PMXConsoleDock
        from prymatex.gui.dockers.logger import QtLogHandler, PMXLoggerDock
        
        self.setDockOptions(QtGui.QMainWindow.AllowTabbedDocks | QtGui.QMainWindow.AllowNestedDocks | QtGui.QMainWindow.AnimatedDocks)
        
        self.paneFileSystem = PMXFileSystemDock(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.paneFileSystem)
        self.menuPanels.addAction(self.paneFileSystem.toggleViewAction())
        self.paneFileSystem.hide()
        '''
        self.paneProject = PMXProjectDock(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.paneProject)
        self.menuPanels.addAction(self.paneProject.toggleViewAction())
        self.paneProject.hide()
        
        self.paneSymbolList = PMXSymboldListDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.paneSymbolList)
        self.menuPanels.addAction(self.paneSymbolList.toggleViewAction())
        self.paneSymbolList.hide()
        '''
        self.paneBrowser = PMXBrowserDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.paneBrowser)
        self.menuPanels.addAction(self.paneBrowser.toggleViewAction())
        self.paneBrowser.hide()
        
        self.paneConsole = PMXConsoleDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.paneConsole)
        self.menuPanels.addAction(self.paneConsole.toggleViewAction())
        self.paneConsole.hide()
        
        self.paneLogging = PMXLoggerDock(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.paneLogging)
        self.menuPanels.addAction(self.paneLogging.toggleViewAction())
        self.paneLogging.hide()
    
    def setupDialogs(self):
        from prymatex.gui.filterdlg import PMXFilterDialog
        from prymatex.gui.dialogs import PMXNewFromTemplateDialog
        from prymatex.gui.support.bundleselector import PMXBundleItemSelector
        
        # Create dialogs
        self.dialogNewFromTemplate = PMXNewFromTemplateDialog(self)
        self.dialogFilter = PMXFilterDialog(self)
        self.bundleItemSelector = PMXBundleItemSelector(self)

    #============================================================
    # Create and manage editors
    #============================================================
    def addEditor(self, editor):
        self.statusBar().addEditor(editor)
        self.splitTabWidget.addTab(editor)
        self.setCurrentEditor(editor)
    
    def removeEditor(self, editor):
        self.statusBar().removeEditor(editor)
        self.splitTabWidget.removeTab(editor)

    def getEditorForFile(self, fileInfo):
        for editor in self.splitTabWidget.getAllWidgets():
            if editor.fileInfo == fileInfo:
                return editor

    def setCurrentEditor(self, editor):
        print editor
        self.currentEditor = editor
        
        #Set editor to statusbar
        self.statusBar().setCurrentEditor(editor)
        
        #Update window title
        template = Template(self.windowTitleTemplate)
        title = [ editor.getTabTitle() ]
        title.append(template.safe_substitute(**editor.buildEnvironment(self.application.supportManager.buildEnvironment())))
        self.setWindowTitle(" - ".join(title))
        self.currentEditor.setFocus(QtCore.Qt.MouseFocusReason)
        if self.sender() != self.splitTabWidget:
            self.splitTabWidget.setCurrentWidget(editor)
        
    def openFile(self, fileInfo, cursorPosition = (0,0)):
        editor = self.getEditorForFile(fileInfo)
        if editor is None:
            editor = self.application.getEditorInstance(fileInfo, self)
            content = self.application.fileManager.openFile(fileInfo)
            editor.setPlainText(content)
            editor.setFileInfo(fileInfo)
            self.addEditor(editor)
        else:
            editor.setCursorPosition(cursorPosition)
            self.setCurrentEditor(editor)
    
    def saveFile(self, editor = None, saveAs = False):
        editor = editor or self.currentEditor
        if editor.isNew() or saveAs:
            fileInfo = self.application.fileManager.getSaveFile(title = "Save file" if saveAs else "Save file as")
            if fileInfo is not None:
                self.application.fileManager.saveFile(fileInfo, editor.toPlainText())
                editor.setFileInfo(fileInfo)
                editor.setModified(False)
        else:
            self.application.fileManager.saveFile(editor.fileInfo, editor.toPlainText())
            editor.setModified(False)
    
    def closeFile(self, editor = None):
        editor = editor or self.currentEditor
        while editor.isModified():
            response = QtGui.QMessageBox.question(self, "Save", 
                "Save %s" % editor.getTabTitle(), 
                buttons = QtGui.QMessageBox.Ok | QtGui.QMessageBox.No | QtGui.QMessageBox.Cancel, 
                defaultButton = QMessageBox.Ok)
            if response == QtGui.QMessageBox.Ok:
                self.saveFile(editor = editor)
            elif response == QtGui.QMessageBox.No:
                break
            elif response == QtGui.QMessageBox.Cancel:
                return
        self.removeEditor(editor)

    def openUrl(self, url):
        if isinstance(url, (str, unicode)):
            url = QtCore.QUrl(url)
        source = url.queryItemValue('url')
        if source:
            source = QtCore.QUrl(source)
            editor = self.openFile(source.path())
            line = url.queryItemValue('line')
            if line:
                editor.codeEdit.goToLine(int(line))
            column = url.queryItemValue('column')
            if column:
                editor.codeEdit.goToColumn(int(column))
    
    def closeEvent(self, event):
        try:
            for w in self.splitTabWidget.getAllWidgets():
                w.close()
        except exceptions.UserCancelException:
            event.ignore()
