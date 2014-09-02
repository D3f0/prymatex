#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from functools import reduce

from prymatex.qt import QtCore, QtGui, Qt

from prymatex.core import config
from prymatex.models.support import BundleItemTreeNode

# ===================================
# Completer Base Model
# ===================================
class CompletionBaseModel(QtCore.QAbstractTableModel):
    def __init__(self, **kwargs):
        super(CompletionBaseModel, self).__init__(**kwargs)
        self.editor = None
        self._prefix = None

    def completionPrefix(self):
        return self._prefix
        
    def setCompletionPrefix(self, prefix):
        self._prefix = prefix

    def setEditor(self, editor):
        self.editor = editor

    def setCurrentRow(self, index, completion_count):
        return False
    
    def modelSorting(self):
        #QCompleter.UnsortedModel
        #QCompleter.CaseSensitivelySortedModel
        #QCompleter.CaseInsensitivelySortedModel
        return QtGui.QCompleter.UnsortedModel

    def caseSensitivity(self):
        #QtCore.Qt.CaseInsensitive
        #QtCore.Qt.CaseSensitive
        return QtCore.Qt.CaseSensitive

    def fillModel(self, callback):
        raise NotImplemented
    
    def isReady(self):
        raise NotImplemented
    
    def activatedCompletion(self, index):
        raise NotImplemented

    def highlightedCompletion(self, index):
        raise NotImplemented

# ===================================
# Custom completer models
# ===================================
class WordsCompletionModel(CompletionBaseModel):
    def __init__(self, **kwargs):
        super(WordsCompletionModel, self).__init__(**kwargs)
        self.words = []
        self.suggestions = []
        self.icon = QtGui.QIcon()

    def setEditor(self, editor):
        #TODO: Que pasa si ya tiene bloques
        super(WordsCompletionModel, self).setEditor(editor)
        self.editor.registerBlockUserDataHandler(self)
        self.icon = self.editor.resources().get_icon('insert-text')
        
    # -------------------- Process User Data
    def contributeToBlockUserData(self, userData):
        userData.words = set()

    def processBlockUserData(self, text, cursor, block, userData):
        userData.words = set(
            reduce(lambda w1, w2: w1 + w2,
                map(lambda token: config.RE_WORD.findall(token.chunk),
                    userData.tokens()[::-1]
                )
        , []))

    def modelSorting(self):
        return QtGui.QCompleter.CaseSensitivelySortedModel

    def fillModel(self, callback):
        # TODO Palabras mas proximas al cursor o mas utilizadas
        self.suggestions = set()
        block = self.editor.document().begin()
        # TODO: No usar la linea actual, quiza algo de niveles de anidamiento
        while block.isValid():
            self.suggestions.update(self.editor.blockUserData(block).words)
            block = block.next()

        self.suggestions.update(self.editor.preferenceSettings().completions)
        if self.suggestions:
            self.suggestions = sorted(list(self.suggestions))
            callback(self)

    def isReady(self):
        return bool(self.suggestions)

    def activatedCompletion(self, index):
        suggestion = self.suggestions[index.row()]
        currentWord, start, end = self.editor.currentWord()
        cursor = self.editor.newCursorAtPosition(start, end)
        cursor.insertText(suggestion)
        
    def highlightedCompletion(self, index):
        suggestion = self.suggestions[index.row()]

    # -------------- Model overrite methods
    def columnCount(self, parent = None):
        return 1

    def rowCount(self, parent = None):
        return len(self.suggestions)

    def index(self, row, column, parent = QtCore.QModelIndex()):
        if row < len(self.suggestions):
            return self.createIndex(row, column, parent)
        else:
            return QtCore.QModelIndex()
            
    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        suggestion = self.suggestions[index.row()]
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            return suggestion
        elif role == QtCore.Qt.DecorationRole:
            return self.icon
        elif role == QtCore.Qt.ToolTipRole:
            return suggestion
        elif role == QtCore.Qt.MatchRole:
            #return text.fuzzy_match(self.prefix, suggestion) and self.prefix or suggestion
            return suggestion
    
    def setCurrentRow(self, index, completion_count):
        suggestion = self.suggestions[index.row()]
        return completion_count > 1 or suggestion != self.completionPrefix()
        
class TabTriggerItemsCompletionModel(CompletionBaseModel):
    def __init__(self, **kwargs):
        super(TabTriggerItemsCompletionModel, self).__init__(**kwargs)
        self.triggers = []

    def fillModel(self, callback):
        leftScope, rightScope = self.editor.scope()
        self.triggers = self.editor.application().supportManager.getAllTabTriggerItemsByScope(leftScope, rightScope)
        if self.triggers:
            callback(self)
    
    # -------------- Model overrite methods
    def columnCount(self, parent = None):
        return 2

    def rowCount(self, parent = None):
        return len(self.triggers)

    def index(self, row, column, parent = QtCore.QModelIndex()):
        if row < len(self.triggers):
            return self.createIndex(row, column, parent)
        else:
            return QtCore.QModelIndex()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        suggestion = self.triggers[index.row()]
        if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
            #Es un bundle item
            if index.column() == 0:
                return suggestion.tabTrigger
            elif index.column() == 1:
                return suggestion.name
        elif role == QtCore.Qt.DecorationRole and index.column() == 0:
            return suggestion.icon()
        elif role == QtCore.Qt.ToolTipRole:
            return suggestion.name
        elif role == QtCore.Qt.MatchRole:
            return suggestion.tabTrigger

    def isReady(self):
        return bool(self.triggers)

    def activatedCompletion(self, index):
        trigger = self.triggers[index.row()]
        currentWord, start, end = self.editor.currentWord()
        cursor = self.editor.newCursorAtPosition(start, end)
        cursor.removeSelectedText()
        self.editor.insertBundleItem(trigger, textCursor = cursor)

    def highlightedCompletion(self, index):
        trigger = self.triggers[index.row()]
        
    def setCurrentRow(self, index, completion_count):
        return completion_count > 0

class SuggestionsCompletionModel(CompletionBaseModel):
    #display The title to display in the suggestions list
    #insert Snippet to insert after selection
    #image An image name, see the :images option
    #match Typed text to filter on (defaults to display)

    def __init__(self, **kwargs):
        super(SuggestionsCompletionModel, self).__init__(**kwargs)
        self.suggestions = []
        self.completionCallback = None

    def setSuggestions(self, suggestions):
        self.suggestions = suggestions

    def setCompletionCallback(self, callback):
        self.completionCallback = callback

    # -------------- Model overrite methods
    def columnCount(self, parent = None):
        return 1

    def rowCount(self, parent = None):
        return len(self.suggestions)

    def index(self, row, column, parent = QtCore.QModelIndex()):
        if row < len(self.suggestions):
            return self.createIndex(row, column, parent)
        else:
            return QtCore.QModelIndex()

    def data(self, index, role = QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None
        suggestion = self.suggestions[index.row()]
        if role == QtCore.Qt.DisplayRole:
            if 'display' in suggestion:
                return suggestion['display']
            elif 'title' in suggestion:
                return suggestion['title']
        elif role == QtCore.Qt.EditRole:
            if 'match' in suggestion:
                return suggestion['match']
            elif 'display' in suggestion:
                return suggestion['display']
            elif 'title' in suggestion:
                return suggestion['title']
        elif role == QtCore.Qt.DecorationRole:
            if index.column() == 0 and 'image' in suggestion:
                return self.editor.resources().get_icon(suggestion['image'])
        elif role == QtCore.Qt.ToolTipRole:
            if 'tooltip' in suggestion:
                if 'tooltip_format' in suggestion:
                    print(suggestion["tooltip_format"])
                return suggestion['tooltip']
        elif role == QtCore.Qt.MatchRole:
            return suggestion['display']

    def fillModel(self, callback):
        pass

    def isReady(self):
        return bool(self.suggestions)

    def activatedCompletion(self, index):
        self.completionCallback(self.suggestions[index.row()])

    def highlightedCompletion(self, index):
        suggestion = self.suggestions[index.row()]
        if 'tooltip' in suggestion and suggestion['tooltip']:
            self.editor.showTooltip(suggestion['tooltip'])
            
    def setCurrentRow(self, index, completion_count):
        suggestion = self.suggestions[index.row()]
        return suggestion.get('insert') != self.completionPrefix()

# ===================================
# Completer
# ===================================
class CodeEditorCompleter(QtGui.QCompleter):
    def __init__(self, editor):
        super(CodeEditorCompleter, self).__init__(parent = editor)
        self.editor = editor
        self.editor.registerKeyPressHandler(QtCore.Qt.Key_Enter, 
            self.__insert_completion, important = True)
        self.editor.registerKeyPressHandler(QtCore.Qt.Key_Return, 
            self.__insert_completion, important = True)
        self.editor.registerKeyPressHandler(QtCore.Qt.Key_Tab, 
            self.__insert_completion, important = True)

        self._start_position = 0
        # Models
        self.completionModels = [ ]

        self.completerTasks = [ ]
        
        # Role
        self.setCompletionRole(QtCore.Qt.MatchRole)
        
        # Popup table view
        self.setPopup(QtGui.QTableView(self.editor))
        self.popup().setAlternatingRowColors(True)
        self.popup().verticalHeader().setVisible(False)
        self.popup().horizontalHeader().setStretchLastSection(True)
        self.popup().horizontalHeader().setVisible(False)
        self.popup().setShowGrid(False)
        self.popup().setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.popup().setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.popup().setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.activated[QtCore.QModelIndex].connect(self.activatedCompletion)
        self.highlighted[QtCore.QModelIndex].connect(self.highlightedCompletion)

        self.setWidget(self.editor)
    
    def __insert_completion(self, event):
        if self.isVisible():
            event.ignore()
            return True
        return False

    def completionPrefixRange(self):
        prefix = self.completionPrefix()
        return prefix, self._start_position, self._start_position + len(prefix) + 1
        
    def startPosition(self):
        return self._start_position

    def setPalette(self, palette):
        self.popup().setPalette(palette)
        self.popup().viewport().setPalette(palette)

    def isVisible(self):
        return self.completionMode() == QtGui.QCompleter.PopupCompletion and self.popup().isVisible()

    def hide(self):
        if self.completionMode() == QtGui.QCompleter.PopupCompletion:
            self.popup().hide()

    def fixPopupView(self):
        if self.completionMode() == QtGui.QCompleter.PopupCompletion:
            self.popup().resizeColumnsToContents()
            self.popup().resizeRowsToContents()
            width = self.popup().verticalScrollBar().sizeHint().width()
            for columnIndex in range(self.model().columnCount()):
                width += self.popup().columnWidth(columnIndex)
            self.popup().setMinimumWidth(width > 212 and width or 212)
            height = self.popup().rowHeight(0) * self.completionCount()
            self.popup().setMinimumHeight(height > 343 and 343 or height)

    def activatedCompletion(self, index):
        self.model().activatedCompletion(self.completionModel().mapToSource(index))
        
    def highlightedCompletion(self, index):
        self.model().highlightedCompletion(self.completionModel().mapToSource(index))
        
    def setCurrentRow(self, index):
        if not QtGui.QCompleter.setCurrentRow(self, index):
            return False
        cIndex = self.completionModel().index(index, 0)
        if self.completionMode() == QtGui.QCompleter.PopupCompletion:
            self.popup().setCurrentIndex(cIndex)
        return self.model().setCurrentRow(
            self.completionModel().mapToSource(cIndex), self.completionCount())

    def setCompletionPrefix(self, prefix):
        self._start_position = self.editor.textCursor().position() - len(prefix or "")
        for model in self.completionModels:
            model.setCompletionPrefix(prefix)
        QtGui.QCompleter.setCompletionPrefix(self, prefix)
        if self.model() is not None:
            self.fixPopupView()
    
    def setModel(self, model):
        # Esto esta bueno pero cuando cambias de modelo tenes que hacer algo mas
        #self.setModelSorting(model.modelSorting())
        #self.setCaseSensitivity(model.caseSensitivity())
        QtGui.QCompleter.setModel(self, model)

    def trySetModel(self, model):
        current_model = self.model()
        if model not in self.completionModels:
            return False
        self.setModel(model)
        if self.setCurrentRow(0):
            self.fixPopupView()
        else:
            self.setModel(current_model)
        return self.model() != current_model
        
    def registerModel(self, completionModel):
        self.completionModels.append(completionModel)
        completionModel.setEditor(self.editor)
    
    def unregisterModel(self, completionModel):
        self.completionModels.remove(completionModel)
        completionModel.setEditor(None)

    def trySetNextModel(self):
        current = model = self.model() or self.completionModels[-1]
        while True:
            index = (self.completionModels.index(model) + 1) % len(self.completionModels)
            model = self.completionModels[index]
            if model.isReady() and self.trySetModel(model):
                return True
            if current == model:
                break
        return False

    def runCompleter(self, rect, model = None):
        if self.isVisible():
            if model is not None and self.trySetModel(model):
                self.complete(rect)
        elif not self.isVisible():
            for completerTask in self.completerTasks:
                completerTask.cancel()
            self.setModel(None)
            def _go(model):
                # First win
                if self.model() is None and self.trySetModel(model):
                    self.complete(rect)
            if model is not None:
                _go(model)
            self.completerTasks = self.editor.application().schedulerManager.tasks(
                lambda model: model.fillModel(_go), self.completionModels)
