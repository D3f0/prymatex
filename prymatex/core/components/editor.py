#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.qt import QtGui, QtCore
from prymatex.qt.helpers.icons import combine_icons

from prymatex import resources

from prymatex.core.components.base import (PrymatexComponentWidget, 
    PrymatexKeyHelper, PrymatexAddon, Key_Any)

from prymatex.utils.decorators import deprecated

class PrymatexEditor(PrymatexComponentWidget):
    UNTITLED_FILE_TEMPLATE = "Untitled"
    
    def __init__(self, file_path = None, **kwargs):
        super(PrymatexEditor, self).__init__(**kwargs)
        self._file_path = file_path
        self._project = None
        self._external_action = None
        self._title = self.UNTITLED_FILE_TEMPLATE

    def open(self, file_path):
        """ Open file """
        self.application.fileManager.openFile(file_path)
        self.setFilePath(file_path)

    def save(self, file_path):
        """ Save content of editor in a file """
        self.application.fileManager.writeFile(file_path, self.toPlainText())
        if file_path != self._file_path:
            if self._file_path is not None:
                self.application.fileManager.closeFile(self._file_path)
                self.application.fileManager.openFile(file_path)
            self.setFilePath(file_path)
        self.setModified(False)
        self.setExternalAction(None)
    
    def close(self):
        """ Close editor """
        if self._file_path is not None:
            self.application.fileManager.closeFile(self._file_path)

    def reload(self):
        """ Reload current file """
        self.setModified(False)
        self.setExternalAction(None)

    def project(self):
        return self._project

    def filePath(self):
        return self._file_path
    
    def setFilePath(self, file_path):
        self._file_path = file_path
        self._project = self.application.projectManager.findProjectForPath(self._file_path)
        self._title = self.application.fileManager.basename(file_path)
        self.emit(QtCore.SIGNAL("modificationChanged"), False)

    def icon(self):
        baseIcon = QtGui.QIcon()
        if self._file_path is not None:
            baseIcon = resources.get_icon(self._file_path)
        if self.isModified():
            baseIcon = resources.get_icon("document-save")
        if self._external_action is not None:
            importantIcon = resources.get_icon("emblem-important")
            baseIcon = combine_icons(baseIcon, importantIcon, 0.8)
        return baseIcon
    
    def title(self):
        return self._title

    def tooltip(self):
        return self.hasFile() and self.filePath() or self.title()
    
    def fileDirectory(self):
        return self.application.fileManager.dirname(self._file_path)
    
    def fileName(self):
        return self.application.fileManager.basename(self._file_path)
        
    def fileFilters(self):
        return []
    
    def hasFile(self):
        return bool(self._file_path)
        
    @deprecated
    def isNew(self):
        return not self.hasFile()
        
    def isEmpty(self):
        return True
    
    def isModified(self):
        return False
    
    def setModified(self, modified):
        pass 
    
    def isLoading(self):
        """Returns true if the editor is still loading from disk, and not ready for use."""
        return False

    def isDirty(self):
        """Returns true if there are any unsaved modifications to the buffer."""
        return not self.isScratch() and self.isModified()
    
    def isReadOnly(self):
        """Returns true if the editor may not be modified."""
        return False
    
    def isScratch(self):
        """Returns true if the editor is a scratch editor. Scratch editors never report as being dirty."""
        return self._file_path is None
        
    def externalAction(self):
        return self._external_action
        
    def setExternalAction(self, action):
        self._external_action = action
        self.emit(QtCore.SIGNAL("modificationChanged"), False)

    def isExternalChanged(self):
        return self._external_action == self.application.fileManager.CHANGED

    def isExternalDeleted(self):
        # FIXME: Rename or move files make produces bogus behavior 
        return self._external_action == self.application.fileManager.DELETED    

    #------------ Bundle Item Handler
    def bundleItemHandler(self):
        return None
        
    #------------ Global navigation api
    def saveLocationMemento(self, memento):
        self.emit(QtCore.SIGNAL("newLocationMemento"), memento)
        
    def restoreLocationMemento(self, memento):
        pass
    
    def contributeToTabMenu(self):
        ''' When an editor is right clicked on it's tab, the editor
        can provide custom actions to the menu through this callback'''
        return []
    
    # ---------- For Plugin Manager administrator
    @classmethod
    def acceptFile(cls, file_path, mimetype):
        return True

#======================================================================
# Key Helper
#======================================================================    
class PrymatexEditorKeyHelper(PrymatexKeyHelper):
    def __init__(self, **kwargs):
        super(PrymatexEditorKeyHelper, self).__init__(**kwargs)
        self.editor = kwargs.get("parent")

#======================================================================
# Addon
#======================================================================    
class PrymatexEditorAddon(PrymatexAddon):
    def __init__(self, **kwargs):
        super(PrymatexEditorAddon, self).__init__(**kwargs)
        self.editor = kwargs.get("parent")
