#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import unicode_literals

import re
import operator

from prymatex.qt import QtCore, QtGui

from prymatex.core import PMXBaseEditor
from prymatex.widgets.texteditor import TextEditWidget

from prymatex import resources
from prymatex.core.settings import pmxConfigPorperty
from prymatex.qt.helpers.menus import extend_menu
from prymatex.models.support import BundleItemTreeNode

from .userdata import CodeEditorBlockUserData, CodeEditorScopeData
from .addons import CodeEditorAddon
from .sidebar import CodeEditorSideBar, SideBarWidgetAddon
from .processors import (PMXCommandProcessor, PMXSnippetProcessor,
        PMXMacroProcessor)
from .modes import CodeEditorBaseMode

from .highlighter import PMXSyntaxHighlighter
from .models import (SymbolListModel, BookmarkListModel,
        bundleItemSelectableModelFactory, bookmarkSelectableModelFactory,
        symbolSelectableModelFactory)
from .completer import (CodeEditorCompleter, WordsCompletionModel,
        TabTriggerItemsCompletionModel, SuggestionsCompletionModel)

from prymatex.support import (PMXSnippet, PMXMacro, PMXCommand, PMXSyntax,
    PMXDragCommand, PMXPreferenceSettings, PMXPreferenceMasterSettings)

from prymatex.utils import text
from prymatex.utils.i18n import ugettext as _
from functools import reduce

class CodeEditor(TextEditWidget, PMXBaseEditor):
    # Aca vamos a guardar los scopes de los editores, quiza esto pueda
    # ser un objeto factory, por ahora la fabricacion la hace el editor
    # en el factory method flyweightScopeDataFactory
    SCOPES = {}
    STANDARD_SIZES = (70, 78, 80, 100, 120)
    # -------------------- Signals
    syntaxChanged = QtCore.Signal(object)
    themeChanged = QtCore.Signal()
    modeChanged = QtCore.Signal(str)
    blocksRemoved = QtCore.Signal(QtGui.QTextBlock, int)
    blocksAdded = QtCore.Signal(QtGui.QTextBlock, int)

    aboutToHighlightChange = QtCore.Signal()
    highlightChanged = QtCore.Signal()

    # ------------------ Flags
    ShowTabsAndSpaces     = 1<<0
    ShowLineAndParagraphs = 1<<1
    WordWrap              = 1<<2
    MarginLine            = 1<<3
    IndentGuide           = 1<<4
    HighlightCurrentLine  = 1<<5

    # ------------------- Settings
    SETTINGS_GROUP = 'CodeEditor'

    removeTrailingSpaces = pmxConfigPorperty(default = False)
    autoBrackets = pmxConfigPorperty(default = True)
    smartHomeSmartEnd = pmxConfigPorperty(default = True)
    enableAutoCompletion = pmxConfigPorperty(default = True)
    wordLengthToComplete = pmxConfigPorperty(default = 3)

    marginLineSize = pmxConfigPorperty(default = 80)
    wordWrapSize = pmxConfigPorperty(valueType = int)
    indentUsingSpaces = pmxConfigPorperty(default = True)
    adjustIndentationOnPaste = pmxConfigPorperty(default = False)

    @pmxConfigPorperty(default = 4)
    def indentationWidth(self, size):
        self.repaint()

    @pmxConfigPorperty(default = 4)
    def tabWidth(self, size):
        self.setTabStopWidth(size * self.characterWidth())

    @pmxConfigPorperty(default = ("Monospace", 9))
    def defaultFont(self, value):
        font = QtGui.QFont(*value)
        font.setStyleStrategy(QtGui.QFont.ForceIntegerMetrics)
        font.setStyleStrategy(QtGui.QFont.PreferAntialias)
        self.setFont(font)

    @pmxConfigPorperty(default = "3130E4FA-B10E-11D9-9F75-000D93589AF6", tm_name = 'OakDefaultLanguage')
    def defaultSyntax(self, uuid):
        syntax = self.application.supportManager.getBundleItem(uuid)
        self.setSyntax(syntax)

    @pmxConfigPorperty(default = '766026CB-703D-4610-B070-8DE07D967C5F', tm_name = 'OakThemeManagerSelectedTheme')
    def defaultTheme(self, uuid):
        theme = self.application.supportManager.getTheme(uuid)

        self.colours = theme.settings()

        #Set color for QPlainTextEdit
        appStyle = """QPlainTextEdit {background-color: %s;
        color: %s;
        selection-background-color: %s; }""" % (
            self.colours['background'].name(),
            self.colours['foreground'].name(),
            self.colours['selection'].name())

        self.setStyleSheet(appStyle)
        self.syntaxHighlighter.stop()
        self.aboutToHighlightChange.emit()

        self.syntaxHighlighter.setTheme(theme)
        self.themeChanged.emit()

        # Run
        self.syntaxHighlighter.runAsyncHighlight(self.highlightChanged.emit)

    @pmxConfigPorperty(default = MarginLine | IndentGuide | HighlightCurrentLine)
    def defaultFlags(self, flags):
        self.setFlags(flags)

    # --------------------- init
    def __init__(self, parent = None):
        TextEditWidget.__init__(self, parent)
        PMXBaseEditor.__init__(self)

        self.__blockUserDataHandlers = []

        self.braces = []
        #Current braces for cursor position (leftBrace <|> rightBrace, oppositeLeftBrace, oppositeRightBrace)
        # <|> the cursor is allways here
        self._currentBraces = (None, None, None, None)

        #Sidebars
        self.leftBar = CodeEditorSideBar(self)
        self.rightBar = CodeEditorSideBar(self)

        #Models
        self.bookmarkListModel = BookmarkListModel(self)
        self.symbolListModel = SymbolListModel(self)
        self.bundleItemSelectableModel = bundleItemSelectableModelFactory(self)
        self.symbolSelectableModel = symbolSelectableModelFactory(self)
        self.bookmarkSelectableModel = bookmarkSelectableModelFactory(self)

        #Processors
        self.commandProcessor = PMXCommandProcessor(self)
        self.macroProcessor = PMXMacroProcessor(self)
        self.snippetProcessor = PMXSnippetProcessor(self)

        #Highlighter
        self.syntaxHighlighter = PMXSyntaxHighlighter(self)

        # TODO Quiza algo como que los modos se registren solos?
        self.codeEditorModes = []

        #Completer
        self.completer = CodeEditorCompleter(self)
        self.completer.addModel(WordsCompletionModel(self))
        self.completer.addModel(TabTriggerItemsCompletionModel(self))
        self.suggestionsCompletionModel = SuggestionsCompletionModel(self)
        self.completer.addModel(self.suggestionsCompletionModel)

        #Block Count
        self.lastBlockCount = self.document().blockCount()
        #Connect context menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showEditorContextMenu)

        self.completerTask = self.application.schedulerManager.idleTask()

        #Register text formaters
        self.registerTextCharFormatBuilder("line", self.textCharFormat_line_builder)
        self.registerTextCharFormatBuilder("selection", self.textCharFormat_selection_builder)
        self.registerTextCharFormatBuilder("brace", self.textCharFormat_brace_builder)

        # Sidebars signals
        self.rightBar.updateRequest.connect(self.updateViewportMargins)
        self.leftBar.updateRequest.connect(self.updateViewportMargins)

        # Document signals
        self.document().undoCommandAdded.connect(self.on_document_undoCommandAdded)

        # Editor signals
        self.blockCountChanged.connect(self.on_blockCountChanged)
        self.updateRequest.connect(self.updateSideBars)
        self.syntaxChanged.connect(self.on_syntaxChanged)
        self.themeChanged.connect(self.highlightEditor)
        # TODO Algo mejor para acomodar el ancho del tabulador
        self.fontChanged.connect(lambda ed = self: ed.setTabStopWidth(ed.tabWidth * ed.characterWidth()))
        
        # By default
        self.showMarginLine = True
        self.showIndentGuide = True
        self.showHighlightCurrentLine = True
        print(self.wordWrapSize)

    def initialize(self, mainWindow):
        PMXBaseEditor.initialize(self, mainWindow)
        self.syntaxHighlighter.setDocument(self.document())

        # Get dialogs
        self.selectorDialog = self.mainWindow.findChild(QtGui.QDialog, "SelectorDialog")
        self.browserDock = self.mainWindow.findChild(QtGui.QDockWidget, "BrowserDock")

        # Ultimo en conectar esta señal, para poder hacer el update
        self.cursorPositionChanged.connect(self.setCurrentBraces)
        self.cursorPositionChanged.connect(self.highlightEditor)

    # ----------- Override from PMXBaseComponent
    def addComponent(self, component):
        PMXBaseEditor.addComponent(self, component)
        if isinstance(component, SideBarWidgetAddon):
            self.addSideBarWidget(component)
        elif isinstance(component, CodeEditorBaseMode):
            self.addCodeEditorMode(component)

    def addSideBarWidget(self, widget):
        if widget.ALIGNMENT == QtCore.Qt.AlignRight:
            self.rightBar.addWidget(widget)
        else:
            self.leftBar.addWidget(widget)

    def addCodeEditorMode(self, codeEditorMode):
        self.codeEditorModes.append(codeEditorMode)

    def on_syntaxChanged(self, syntax):
        # Set the basic scope
        self.setBasicScope(( syntax.scopeName, ))

        # Set braces
        self.braces = self.basicScope().settings.smartTypingPairs

        self.showMessage("Syntax changed to <b>%s</b>" % syntax.name)

    def showMessage(self, *largs, **kwargs):
        self.application.showMessage(*largs, **kwargs)

    def setPlainText(self, text):
        from time import time
        self.syntaxHighlighter.stop()
        self.aboutToHighlightChange.emit()
        TextEditWidget.setPlainText(self, text)
        self.highlightTime = time()
        def highlightReady(editor):
            def _ready():
                editor.highlightChanged.emit()
                self.logger.info("Time %f" % (time() - self.highlightTime))
            return _ready
        self.syntaxHighlighter.runAsyncHighlight(highlightReady(self))
        #self.syntaxHighlighter.runAsyncHighlight(lambda editor = self: editor.highlightChanged.emit())

    # --------------- Block User Data
    def registerBlockUserDataHandler(self, handler):
        self.__blockUserDataHandlers.append(handler)

    def blockUserData(self, block):
        userData = block.userData()
        if not userData:
            userData = CodeEditorBlockUserData()
            # Indent and content
            userData.indent = ""

            # Folding
            userData.foldingMark = PMXPreferenceMasterSettings.FOLDING_NONE
            userData.foldedLevel = 0
            userData.folded = False

            # Now the handlers
            for handler in self.__blockUserDataHandlers:
                handler.contributeToBlockUserData(userData)
            block.setUserData(userData)
        return userData

    def processBlockUserData(self, sourceText, block, userData):
        # Indent
        indent = text.white_space(sourceText)
        if indent != userData.indent:
            userData.indent = indent
        # Folding
        # TODO: Ver si lo puedo sacar del scope basico o hace falta tomar de algun lugar
        # Principio, fin de la linea
        foldingMark = self.basicScope().settings.folding(sourceText)
        if foldingMark != userData.foldingMark:
            userData.foldingMark = foldingMark
        # Handlers
        for handler in self.__blockUserDataHandlers:
            handler.processBlockUserData(sourceText, block, userData)

    def on_blockCountChanged(self, newBlockCount):
        self.logger.debug("block Count changed")
        block = self.textCursor().block()
        if self.lastBlockCount > self.document().blockCount():
            self.blocksRemoved.emit(block, self.lastBlockCount - newBlockCount)
        else:
            self.blocksAdded.emit(block, newBlockCount - self.lastBlockCount)
        self.lastBlockCount = self.document().blockCount()

    # ------------- Base Editor Api
    @classmethod
    def acceptFile(cls, filePath, mimetype):
        return re.compile("text/.*").match(mimetype) is not None

    def open(self, filePath):
        """ Custom open for large files """
        PMXBaseEditor.open(self, filePath)
        content = self.application.fileManager.readFile(filePath)
        self.setPlainText(content)

    def close(self):
        PMXBaseEditor.close(self)
        # Stp'highlighter
        self.syntaxHighlighter.stop()
        TextEditWidget.close(self)

    def reload(self):
        PMXBaseEditor.reload(self)
        content = self.application.fileManager.readFile(self.filePath)
        self.updatePlainText(content)

    def componentState(self):
        """Returns a Python dictionary containing the state of the editor."""
        state = {}
        #Bookmarks
        state['bookmarks'] = self.bookmarkListModel.lineNumbers()

        #UserDatas
        state['data'] = []

        return state

    def setComponentState(self, state):
        """Restore the state from the given state (returned by a previous call to state())."""
        pass

    def isModified(self):
        return self.document().isModified()

    def isEmpty(self):
        return self.document().isEmpty()

    def setModified(self, modified):
        self.document().setModified(modified)

    def setFilePath(self, filePath):
        extension = self.application.fileManager.extension(filePath)
        syntax = self.application.supportManager.findSyntaxByFileType(extension)
        if syntax is not None:
            self.setSyntax(syntax)
        PMXBaseEditor.setFilePath(self, filePath)

    def tabTitle(self):
        #Podemos marcar de otra forma cuando algo cambia :P
        return PMXBaseEditor.tabTitle(self)

    def fileFilters(self):
        return [ "%s (%s)" % (self.syntax().bundle.name, " ".join(["*." + ft for ft in self.syntax().fileTypes])) ]
        #return PMXBaseEditor.fileFilters(self)

    # ---------------------- Scopes
    def setBasicScope(self, scopeStack):
        self.__basicScope = self.flyweightScopeDataFactory(scopeStack)

    def basicScope(self):
        return self.__basicScope

    @classmethod
    def flyweightScopeDataFactory(cls, path):
        if path in cls.SCOPES:
            return cls.SCOPES[path]
        scope = cls.application.supportManager.scopeFactory(path)
        return cls.SCOPES.setdefault(path, CodeEditorScopeData(
                scope = scope,
                settings = cls.application.supportManager.getPreferenceSettings(scope, scope),
                group = scope.rootGroupName()))

    def tokenAtPosition(self, position):
        if position < 0:
            position = 0
        elif position > self.document().characterCount():
            position = self.document().characterCount()
        block = self.document().findBlock(position)
        return self.blockUserData(block).tokenAtPosition(position - block.position()) or self.basicScope()

    def scope(self, cursor = None):
        cursor = cursor or self.textCursor()
        leftToken, rightToken = (self.tokenAtPosition(cursor.selectionStart() - 1),
            self.tokenAtPosition(cursor.selectionEnd()))
        # Cursor scope
        leftCursor = self.newCursorAtPosition(cursor.selectionStart())
        rightCursor = self.newCursorAtPosition(cursor.selectionEnd())
        leftPath, rightPath = [], []
        if cursor.hasSelection():
            # If there is one or more selections: dyn.selection.
            # TODO If there is a single zero-width selection: dyn.caret.mixed.columnar.
            # TODO If there are multiple carets and/or selections: dyn.caret.mixed.
            leftPath.append("dyn.selection")
            rightPath.append("dyn.selection")
        # When there is only a single caret or a single continuous selection
        # the left scope may contain: dyn.caret.begin.line or dyn.caret.begin.document
        if leftCursor.atBlockStart():
            leftPath.append("dyn.caret.begin.line")
        if leftCursor.atStart():
            leftPath.append("dyn.caret.begin.document")
        # Likewise the right scope may contain: dyn.caret.end.line or dyn.caret.end.document.
        if rightCursor.atBlockEnd():
            rightPath.append("dyn.caret.end.line")
        if rightCursor.atEnd():
            rightPath.append("dyn.caret.end.document")
        lcs, rcs = (self.application.supportManager.scopeFactory(leftPath),
            self.application.supportManager.scopeFactory(rightPath))

        # TODO Attribute scope cache
        attrScope = self.application.supportManager.attributeScopes(
            self.filePath, self.project and self.project.directory)
        return leftToken.scope + lcs + attrScope, rightToken.scope + rcs + attrScope

    def settings(self, cursor = None):
        cursor = cursor or self.textCursor()
        leftToken, rightToken = (self.tokenAtPosition(cursor.selectionStart() - 1),
            self.tokenAtPosition(cursor.selectionEnd()))
        return leftToken.settings, rightToken.settings

    # ------------ Obteniendo datos del editor
    def tabKeyBehavior(self, cursor = None):
        if not self.indentUsingSpaces:
            return '\t'
        else:
            #Insertar un numero multiplo de espacios a la posicion del cursor
            cursor = cursor or self.textCursor()
            spaces = self.indentationWidth - (cursor.columnNumber() % self.indentationWidth)
            return ' ' * spaces

    # Flags
    def getFlags(self):
        flags = 0
        options = self.document().defaultTextOption()
        if options.flags() & QtGui.QTextOption.ShowTabsAndSpaces:
            flags |= self.ShowTabsAndSpaces
        if options.flags() & QtGui.QTextOption.ShowLineAndParagraphSeparators:
            flags |= self.ShowLineAndParagraphs
        if self.showMarginLine:
            flags |= self.MarginLine
        if self.showIndentGuide:
            flags |= self.IndentGuide
        if self.showHighlightCurrentLine:
            flags |= self.HighlightCurrentLine
        if options.wrapMode() & QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere:
            flags |= self.WordWrap
        return flags

    def setFlags(self, flags):
        options = self.document().defaultTextOption()
        oFlags = options.flags()
        if flags & self.ShowTabsAndSpaces:
            oFlags |= QtGui.QTextOption.ShowTabsAndSpaces
        else:
            oFlags &= ~QtGui.QTextOption.ShowTabsAndSpaces
        if flags & self.ShowLineAndParagraphs:
            oFlags |= QtGui.QTextOption.ShowLineAndParagraphSeparators
        else:
            oFlags &= ~QtGui.QTextOption.ShowLineAndParagraphSeparators
        if flags & self.WordWrap:
            options.setWrapMode(QtGui.QTextOption.WrapAtWordBoundaryOrAnywhere)
        else:
            options.setWrapMode(QtGui.QTextOption.NoWrap)
        options.setFlags(oFlags)
        self.document().setDefaultTextOption(options)
        self.showMarginLine = bool(flags & self.MarginLine)
        self.showIndentGuide = bool(flags & self.IndentGuide)
        self.showHighlightCurrentLine = bool(flags & self.HighlightCurrentLine)

    # ------------------- Syntax
    def syntax(self):
        return self.syntaxHighlighter.syntax

    def setSyntax(self, syntax):
        if self.syntaxHighlighter.syntax != syntax:
            self.syntaxHighlighter.stop()
            self.aboutToHighlightChange.emit()

            # Set syntax
            self.syntaxHighlighter.setSyntax(syntax)
            self.syntaxChanged.emit(syntax)

            # Run
            self.syntaxHighlighter.runAsyncHighlight(self.highlightChanged.emit)

    # -------------------- SideBars
    def updateViewportMargins(self):
        #self.setViewportMargins(self.leftBar.width(), 0, 0, 0)
        self.setViewportMargins(self.leftBar.width(), 0, self.rightBar.width(), 0)

    def updateSideBars(self, rect, dy):
        if dy:
            self.rightBar.scroll(0, dy)
            self.leftBar.scroll(0, dy)
        else:
            self.rightBar.update(0, rect.y(), self.rightBar.width(), rect.height())
            self.leftBar.update(0, rect.y(), self.leftBar.width(), rect.height())

    def updateSideBarsGeometry(self):
        cr = self.contentsRect()
        self.leftBar.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.leftBar.width(), cr.height()))
        rightBarPosition = cr.right() - self.rightBar.width()
        if self.application.platform == "win32" and self.verticalScrollBar().isVisible():
            rightBarPosition -= self.verticalScrollBar().width()
        self.rightBar.setGeometry(QtCore.QRect(rightBarPosition, cr.top(), self.rightBar.width(), cr.height()))

    # -------------- Braces
    def setCurrentBraces(self, cursor = None):
        cursor = QtGui.QTextCursor(cursor) if cursor is not None else QtGui.QTextCursor(self.textCursor())
        cursor.clearSelection()
        openBraces = [pair[0] for pair in self.braces]
        closeBraces = [pair[1] for pair in self.braces]

        leftChar = cursor.document().characterAt(cursor.position() - 1)
        rightChar = cursor.document().characterAt(cursor.position())

        self._currentBraces = (None, None, None, None)

        # TODO si no hay para uno no hay para ninguno, quitar el que esta si el findTypingPair retorna None
        if leftChar in openBraces:
            leftCursor = QtGui.QTextCursor(cursor)
            leftCursor.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
            index = openBraces.index(leftChar)
            otherBrace = self.findTypingPair(leftChar, closeBraces[index], leftCursor)
            if otherBrace is not None:
                self._currentBraces = (leftCursor, None, otherBrace, None)
        if rightChar in openBraces:
            rightCursor = QtGui.QTextCursor(cursor)
            rightCursor.movePosition(QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.KeepAnchor)
            index = openBraces.index(rightChar)
            otherBrace = self.findTypingPair(rightChar, closeBraces[index], rightCursor)
            if otherBrace is not None:
                self._currentBraces = (self._currentBraces[0], rightCursor, self._currentBraces[2], otherBrace)
        if leftChar in closeBraces and self._currentBraces[0] is None:  #Tener uno implica tener los dos por el if
            leftCursor = QtGui.QTextCursor(cursor)
            leftCursor.movePosition(QtGui.QTextCursor.PreviousCharacter, QtGui.QTextCursor.KeepAnchor)
            otherBrace = self.findTypingPair(leftChar, openBraces[closeBraces.index(leftChar)], leftCursor, True)
            if otherBrace is not None:
                self._currentBraces = (leftCursor, self._currentBraces[1], otherBrace, self._currentBraces[3])
        if rightChar in closeBraces and self._currentBraces[1] is None: #Tener uno implica tener los dos por el if
            rightCursor = QtGui.QTextCursor(cursor)
            rightCursor.movePosition(QtGui.QTextCursor.NextCharacter, QtGui.QTextCursor.KeepAnchor)
            otherBrace = self.findTypingPair(rightChar, openBraces[closeBraces.index(rightChar)], rightCursor, True)
            if otherBrace is not None:
                self._currentBraces = (self._currentBraces[0], rightCursor, self._currentBraces[2], otherBrace)

    def currentBracesPairs(self, cursor = None, direction = "both"):
        """ Retorna el otro cursor correspondiente al cursor (brace)
        pasado o actual del editor, puede retornar None en caso de no
        estar cerrado el brace"""
        cursor = cursor or self.textCursor()
        brace1, brace2 = (None, None)
        if cursor.hasSelection():
            for index in [0, 1]:
                if self._currentBraces[index] is not None and cursor.selectedText() == self._currentBraces[index].selectedText():
                    brace1 = QtGui.QTextCursor(self._currentBraces[index + 2]) if self._currentBraces[index + 2] is not None else None
                    brace2 = cursor
                    break
        else:
            #print map(lambda c: c is not None and c.selectedText() or "None", self._currentBraces)
            if direction in ("left", "both"):
                brace1 = self._currentBraces[0]
                brace2 = self._currentBraces[2]
            if (brace1 is None or brace2 is None) and direction in ("right", "both"):
                brace1 = self._currentBraces[1]
                brace2 = self._currentBraces[3]
        if (brace1 is not None and brace2 is not None) and brace1.selectionStart() > brace2.selectionStart():
            return (brace2, brace1)
        return (brace1, brace2)

    def beforeBrace(self, cursor):
        return self._currentBraces[1] is not None and self._currentBraces[1].position() - 1 == cursor.position()

    def afterBrace(self, cursor):
        return self._currentBraces[0] is not None and self._currentBraces[0].position() + 1 == cursor.position()

    def besideBrace(self, cursor):
        return self.beforeBrace(cursor) or self.afterBrace(cursor)

    def surroundBraces(self, cursor):
        #TODO: Esto esta mal
        return self.beforeBrace(cursor) and self.afterBrace(cursor)

    #-------------------- Highlight Editor
    def textCharFormat_line_builder(self):
        textCharFormat = QtGui.QTextCharFormat()
        textCharFormat.setBackground(self.colours['lineHighlight'])
        textCharFormat.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        return textCharFormat

    def textCharFormat_brace_builder(self):
        textCharFormat = QtGui.QTextCharFormat()
        textCharFormat.setForeground(self.colours['caret'])
        textCharFormat.setFontUnderline(True)
        textCharFormat.setUnderlineColor(self.colours['foreground'])
        textCharFormat.setBackground(QtCore.Qt.transparent)
        return textCharFormat

    def textCharFormat_selection_builder(self):
        textCharFormat = QtGui.QTextCharFormat()
        textCharFormat.setBackground(self.colours['selection'])
        return textCharFormat

    def highlightEditor(self):
        cursor = self.textCursor()
        cursor.clearSelection()
        if self.showHighlightCurrentLine:
            self.setExtraSelectionCursors("line", [ cursor ])
        else:
            self.clearExtraSelectionCursors("line")
        self.setExtraSelectionCursors("brace", [cursor for cursor in list(self._currentBraces) if cursor is not None])
        self.updateExtraSelections()

    # ------------ Override event handlers
    def focusInEvent(self, event):
        # TODO No es para este evento pero hay que poner en alugn lugar el update de las side bars
        TextEditWidget.focusInEvent(self, event)
        self.updateSideBarsGeometry()

    def resizeEvent(self, event):
        TextEditWidget.resizeEvent(self, event)
        self.updateSideBarsGeometry()

    def paintEvent(self, event):
        TextEditWidget.paintEvent(self, event)
        page_bottom = self.viewport().height()
        
        characterWidth = self.characterWidth()
        characterHeight = self.characterHeight()

        painter = QtGui.QPainter(self.viewport())
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        painter.setPen(self.colours['selection'])
        block = self.firstVisibleBlock()
        offset = self.contentOffset()
        while block.isValid() and self.blockUserData(block):
            # The top left position of the block in the document
            # position = self.blockBoundingGeometry(block).topLeft() + offset
            blockGeometry = self.blockBoundingGeometry(block)
            blockGeometry.translate(offset)
            # Check if the position of the block is out side of the visible area
            if blockGeometry.top() > page_bottom:
                break
            if block.isVisible():
                positionY = blockGeometry.top()
                if self.isFolded(block):
                    painter.drawPixmap(characterWidth * block.length() + offset.x() + 10,
                        positionY + characterHeight - resources.getImage("foldingellipsis").height(),
                        resources.getImage("foldingellipsis"))
                if self.showIndentGuide:
                    blockPattern = block
                    while blockPattern.isValid() and self.blockUserData(blockPattern).blank():
                        blockPattern = blockPattern.next()
                    if blockPattern.isValid():
                        indentLen = len(self.blockUserData(blockPattern).indent)
                        padding = characterWidth + offset.x()
                        for s in range(0, indentLen // self.indentationWidth):
                            positionX = (characterWidth * self.indentationWidth * s) + padding
                            painter.drawLine(positionX, positionY, positionX, positionY + characterHeight)

            block = block.next()

        if self.showMarginLine:
            pos_margin = characterWidth * self.marginLineSize
            painter.drawLine(pos_margin + offset.x(), 0, pos_margin + offset.x(), self.viewport().height())

        painter.end()

    # ----------------- Mouse Events
    def wheelEvent(self, event):
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if event.delta() == 120:
                self.zoomIn()
            elif event.delta() == -120:
                self.zoomOut()
            event.ignore()
        else:
            TextEditWidget.wheelEvent(self, event)

    def mouseReleaseEvent(self, event):
        freehanded = False
        if freehanded:
            #Modo freehanded
            cursor = self.cursorForPosition(event.pos())
            if not self.cursorRect(cursor).contains(event.pos()):
                cursor.beginEditBlock()
                while not self.cursorRect(cursor).top() <= event.pos().y() <= self.cursorRect(cursor).bottom():
                    cursor.insertText("\n")
                    print(cursor.position(), self.cursorRect(cursor))
                while self.cursorRect(cursor).x() <= event.pos().x():
                    cursor.insertText(" ")
                    print(cursor.position(), self.cursorRect(cursor))
                cursor.endEditBlock()
                self.setTextCursor(cursor)
            else:
                TextEditWidget.mouseReleaseEvent(self, event)
        else:
            TextEditWidget.mouseReleaseEvent(self, event)

    # -------------------- Keyboard Events
    def runKeyHelper(self, event):
        #Intento con los helpers
        cursor = self.textCursor()
        for helper in self.findHelpers(event.key()):
            #Buscar Entre los helpers
            if helper.accept(event, cursor):
                helper.execute(event, cursor)
                return True
        return False

    def keyPressEvent(self, event):
        """This method is called whenever a key is pressed.
        The key code is stored in event.key()"""

        if not ((self.enableAutoCompletion and self.completer.pre_key_event(event))
            or self.runKeyHelper(event)):
            TextEditWidget.keyPressEvent(self, event)

            if self.enableAutoCompletion:
                self.completer.post_key_event(event)

    # ------------ Insert API
    def insertNewLine(self, cursor = None):
        cursor = cursor or self.textCursor()
        block = cursor.block()
        positionInBlock = cursor.positionInBlock()
        userData = self.blockUserData(block)
        _, settings = self.settings(cursor)
        indentMarks = settings.indent(block.text()[:positionInBlock])
        if settings.INDENT_INCREASE in indentMarks:
            self.logger.debug("Increase indent")
            indent = userData.indent + self.tabKeyBehavior()
        elif settings.INDENT_NEXTLINE in indentMarks:
            #TODO: Creo que este no es el correcto
            self.logger.debug("Increase next line indent")
            indent = userData.indent + self.tabKeyBehavior()
        elif settings.UNINDENT in indentMarks:
            self.logger.debug("Unindent")
            indent = ""
        elif settings.INDENT_DECREASE in indentMarks:
            self.logger.debug("Decrease indent")
            indent = userData.indent[:-len(self.tabKeyBehavior())]
        else:
            self.logger.debug("Preserve indent")
            indent = userData.indent[:positionInBlock]
        cursor.insertText("\n%s" % indent)
        self.ensureCursorVisible()

    # ------------ Bundle Items
    def bundleItemHandler(self):
        return self.insertBundleItem

    def insertBundleItem(self, item, **processorSettings):
        """Inserta un bundle item"""

        if item.TYPE == PMXSnippet.TYPE:
            self.snippetProcessor.configure(processorSettings)
            item.execute(self.snippetProcessor)
        elif item.TYPE in ( PMXCommand.TYPE, PMXDragCommand.TYPE ):
            self.commandProcessor.configure(processorSettings)
            item.execute(self.commandProcessor)
        elif item.TYPE == PMXMacro.TYPE:
            self.macroProcessor.configure(processorSettings)
            item.execute(self.macroProcessor)
        elif item.TYPE == PMXSyntax.TYPE:
            self.setSyntax(item)

    def selectBundleItem(self, items, **processorSettings):
        #Tengo mas de uno que hago?, muestro un menu
        syntax = any([item.TYPE == 'syntax' for item in items])

        def insertBundleItem(index):
            if index >= 0:
                self.insertBundleItem(items[index], **processorSettings)

        self.showFlatPopupMenu(items, insertBundleItem, cursorPosition = not syntax)

    def executeCommand(self, commandScript = None, commandInput = "none", commandOutput = "insertText"):
        if commandScript is None:
            commandScript = self.textCursor().selectedText() if self.textCursor().hasSelection() else self.textCursor().block().text()
        command = self.application.supportManager.buildAdHocCommand(
            commandScript, self.syntax().bundle,
            commandInput=commandInput, commandOutput=commandOutput)
        self.insertBundleItem(command)

    def environmentVariables(self):
        environment = PMXBaseEditor.environmentVariables(self)
        cursor = self.textCursor()
        block = cursor.block()
        line = block.text()

        # TODO un shortcut para esto de obtener el path
        leftScope, rightScope = self.scope(cursor)
        current_word, start, end = self.currentWord()

        theme = self.application.supportManager.getTheme(self.defaultTheme)

        # Build environment
        environment.update({
                'TM_CURRENT_LINE': line,
                'TM_LINE_INDEX': cursor.positionInBlock(),
                'TM_LINE_NUMBER': block.blockNumber() + 1,
                'TM_CURRENT_THEME_PATH': theme.currentSourcePath(),
                'TM_COLUMN_NUMBER': cursor.positionInBlock() + 1,
                'TM_SCOPE': "%s" % rightScope,
                'TM_LEFT_SCOPE': "%s" % leftScope,
                'TM_MODE': self.syntax().name,
                'TM_SOFT_TABS': self.indentUsingSpaces and 'YES' or 'NO',
                'TM_TAB_SIZE': self.tabWidth
        })

        if current_word:
            self.logger.debug("Add current word to environment")
            environment['TM_CURRENT_WORD'] = current_word
        if self.filePath is not None:
            self.logger.debug("Add file path to environment")
            environment['TM_FILEPATH'] = self.filePath
            environment['TM_FILENAME'] = self.application.fileManager.basename(self.filePath)
            environment['TM_DIRECTORY'] = self.application.fileManager.dirname(self.filePath)
        if self.project is not None:
            self.logger.debug("Add project to environment")
            environment.update(self.project.environmentVariables())
        if cursor.hasSelection():
            self.logger.debug("Add selection to environment")
            environment['TM_SELECTED_TEXT'] = self.selectedTextWithEol(cursor)
            start, end = self.selectionBlockStartEnd()
            environment['TM_INPUT_START_COLUMN'] = cursor.selectionStart() - start.position() + 1
            environment['TM_INPUT_START_LINE'] = start.blockNumber() + 1
            environment['TM_INPUT_START_LINE_INDEX'] = cursor.selectionStart() - start.position()
        return environment
    
    # ---------- Completer
    def showCompleter(self, suggestions, alreadyTyped=None, caseInsensitive=True, callback = None):
        self.suggestionsCompletionModel.setSuggestions(suggestions)
        self.suggestionsCompletionModel.setCallback(callback)
        alreadyTyped, start, end = self.currentWord(direction="left")
        self.completer.setCaseSensitivity( QtCore.Qt.CaseInsensitive and \
            caseInsensitive or QtCore.Qt.CaseSensitive)
        #self.completer.setActivatedCallback(callback)
        self.completer.complete(self.cursorRect(),
            model = self.suggestionsCompletionModel,
            prefix = alreadyTyped)

    # ---------- Folding
    def _find_block_fold_peer(self, block, direction = "down"):
        """ Direction are 'down' or up"""
        if direction == "down":
            assert self.isFoldingStartMarker(block), "Block isn't folding start"
        else:
            assert self.isFoldingStopMarker(block), "Block isn't folding stop"
        nest = 0
        while block.isValid():
            userData = self.blockUserData(block)
            if userData.foldingMark == PMXPreferenceMasterSettings.FOLDING_START:
                nest += 1
            elif userData.foldingMark == PMXPreferenceMasterSettings.FOLDING_STOP:
                nest -= 1
            if nest == 0:
                return block
            block = block.next() if direction == "down" else block.previous()

    def _find_indented_block_fold_close(self, block):
        assert self.isFoldingIndentedBlockStart(block), "Block isn't folding indented start"
        indent = self.blockUserData(block).indent
        indentedBlock = self.findIndentedBlock(block, indent = indent, comparison = operator.le)
        while self.isFoldingIndentedBlockIgnore(indentedBlock):
            indentedBlock = self.findIndentedBlock(indentedBlock, indent = indent, comparison = operator.le)
        if indentedBlock.isValid():
            return self.findNoBlankBlock(indentedBlock, "up")
        else:
            return self.document().lastBlock()

    def isFoldingStartMarker(self, block):
        return self.blockUserData(block).foldingMark == PMXPreferenceMasterSettings.FOLDING_START

    def isFoldingStopMarker(self, block):
        return self.blockUserData(block).foldingMark == PMXPreferenceMasterSettings.FOLDING_STOP

    def isFoldingIndentedBlockStart(self, block):
        return self.blockUserData(block).foldingMark == PMXPreferenceMasterSettings.FOLDING_INDENTED_START

    def isFoldingIndentedBlockIgnore(self, block):
        return self.blockUserData(block).foldingMark == PMXPreferenceMasterSettings.FOLDING_INDENTED_IGNORE

    def isFoldingMark(self, block):
        return self.isFoldingStartMarker(block) or self.isFoldingStopMarker(block) or self.isFoldingIndentedBlockStart(block)

    def isFolded(self, block):
        return self.isFoldingMark(block) and self.blockUserData(block).folded

    def codeFoldingFold(self, milestone):
        block = endBlock = None
        if self.isFoldingStartMarker(milestone):
            startBlock = block = milestone.next()
            endBlock = self._find_block_fold_peer(milestone, "down")
        elif self.isFoldingStopMarker(milestone):
            endBlock = milestone
            milestone = self._find_block_fold_peer(endBlock, "up")
            startBlock = block = milestone.next()
        elif self.isFoldingIndentedBlockStart(milestone):
            startBlock = block = milestone.next()
            endBlock = self._find_indented_block_fold_close(milestone)

        if block and endBlock and milestone:
            # Go!
            while block.isValid():
                userData = self.blockUserData(block)
                userData.foldedLevel += 1
                block.setVisible(userData.foldedLevel == 0)
                if block == endBlock:
                    break
                block = block.next()

            milestone.userData().folded = True
            self.document().markContentsDirty(startBlock.position(), endBlock.position())

    def codeFoldingUnfold(self, milestone):
        endBlock = None
        startBlock = block = milestone.next()
        if self.isFoldingStartMarker(milestone):
            endBlock = self._find_block_fold_peer(milestone, "down")
        elif self.isFoldingIndentedBlockStart(milestone):
            endBlock = self._find_indented_block_fold_close(milestone)

        if endBlock:
            # Go!
            while block.isValid():
                userData = self.blockUserData(block)
                userData.foldedLevel -= 1
                block.setVisible(userData.foldedLevel == 0)
                if block == endBlock:
                    break
                block = block.next()

            milestone.userData().folded = False
            self.document().markContentsDirty(startBlock.position(), endBlock.position())

    # ---------- Override convert tabs <---> spaces
    def convertTabsToSpaces(self):
        match = "\t"
        self.replaceMatch(match, " " * self.tabWidth, QtGui.QTextDocument.FindFlags(), True)

    def convertSpacesToTabs(self):
        match = " " * self.tabWidth
        self.replaceMatch(match, "\t", QtGui.QTextDocument.FindFlags(), True)

    # -------------- Add select text functions
    def selectEnclosingBrackets(self, cursor = None):
        cursor = cursor or self.textCursor()
        flags = QtGui.QTextDocument.FindFlags()
        flags |= QtGui.QTextDocument.FindBackward
        foundCursors = [(self.document().find(openBrace_closeBrace[0], cursor.selectionStart(), flags), openBrace_closeBrace[1]) for openBrace_closeBrace in self.braces]
        openCursor = reduce(lambda c1, c2: (not c1[0].isNull() and c1[0].selectionEnd() > c2[0].selectionEnd()) and c1 or c2, foundCursors)
        if not openCursor[0].isNull():
            closeCursor = self.findTypingPair(openCursor[0].selectedText(), openCursor[1], openCursor[0])
            if openCursor[0].selectionEnd() <= cursor.selectionStart() <= closeCursor.selectionStart():
                # TODO New cursor at position
                cursor.setPosition(openCursor[0].selectionEnd())
                cursor.setPosition(closeCursor.selectionStart(), QtGui.QTextCursor.KeepAnchor)
                self.setTextCursor(cursor)

    def selectCurrentScope(self, cursor = None):
        cursor = cursor or self.textCursor()
        block = cursor.block()
        token = self.tokenAtPosition(cursor.position())
        cursor = self.newCursorAtPosition(block.position() + token.start, 
            block.position() + token.end)
        self.setTextCursor(cursor)

    # ---------- Bookmarks and gotos
    def toggleBookmark(self, block = None):
        block = block or self.textCursor().block()
        self.bookmarkListModel.toggleBookmark(block)

    def removeAllBookmarks(self):
        self.bookmarkListModel.removeAllBookmarks()

    def bookmarkNext(self, block = None):
        block = block or self.textCursor().block()
        block = self.bookmarkListModel.nextBookmark(block)
        if block is not None:
            self.goToBlock(block)

    def bookmarkPrevious(self, block = None):
        block = block or self.textCursor().block()
        block = self.bookmarkListModel.previousBookmark(block)
        if block is not None:
            self.goToBlock(block)

    def goToBlock(self, block):
        cursor = self.textCursor()
        cursor.setPosition(block.position())
        self.setTextCursor(cursor)
        self.centerCursor()

    def goToLine(self, lineNumber):
        cursor = self.textCursor()
        cursor.setPosition(self.document().findBlockByNumber(lineNumber - 1).position())
        self.setTextCursor(cursor)
        self.centerCursor()

    def goToColumn(self, columnNumber):
        cursor = self.textCursor()
        cursor.setPosition(cursor.block().position() + columnNumber)
        self.setTextCursor(cursor)

    def centerCursor(self, cursor = None):
        if cursor is not None:
            #Scroll to the center of cursor block number
            pageStep = self.verticalScrollBar().pageStep()
            currentValue = self.verticalScrollBar().value()
            blockNumber = cursor.block().blockNumber()
            scrollIndex = 0 if pageStep > blockNumber else blockNumber - (pageStep / 2)
            self.verticalScrollBar().setValue(scrollIndex)
        else:
            TextEditWidget.centerCursor(self)

    # ------------------- Text Indentation
    def findNoBlankBlock(self, block, direction = "down"):
        """ Return no blank block """
        block = block.next() if direction == "down" else block.previous()
        while block.isValid() and self.blockUserData(block).blank():
            block = block.next() if direction == "down" else block.previous()
        return block

    def findIndentedBlock(self, block, indent = None, direction = "down", comparison = operator.eq):
        """ Return equal indent block """
        indent = indent if indent is not None else self.blockUserData(block).indent
        block = self.findNoBlankBlock(block, direction)
        while block.isValid() and not comparison(self.blockUserData(block).indent, indent):
            block = self.findNoBlankBlock(block, direction)
        return block

    def indentBlocks(self, cursor = None):
        """Indents text, block selections."""
        cursor = QtGui.QTextCursor(cursor or self.textCursor())
        start, end = self.selectionBlockStartEnd(cursor)
        cursor.beginEditBlock()
        while True:
            cursor.setPosition(start.position())
            cursor.insertText(self.tabKeyBehavior())
            if start == end:
                break
            start = start.next()
        cursor.endEditBlock()

    def unindentBlocks(self, cursor = None):
        cursor = QtGui.QTextCursor(cursor or self.textCursor())
        start, end = self.selectionBlockStartEnd(cursor)
        cursor.beginEditBlock()
        while True:
            data = start.userData()
            if self.indentUsingSpaces:
                counter = self.tabWidth if len(data.indent) > self.tabWidth else len(data.indent)
            else:
                counter = 1 if len(data.indent) else 0
            if counter > 0:
                cursor.setPosition(start.position())
                for _ in range(counter):
                    cursor.deleteChar()
            if start == end:
                break
            start = start.next()
        cursor.endEditBlock()

    # --------------- Menus
    # Flat Popup Menu
    def showFlatPopupMenu(self, menuItems, callback, cursorPosition = True):
        menu = QtGui.QMenu(self)
        for index, item in enumerate(menuItems, 1):
            if isinstance(item, dict):
                title = "%s 	&%d" % (item["title"], index)
                icon = resources.getIcon(item["image"]) if "image" in item else QtGui.QIcon()
            elif isinstance(item,  str):
                title = "%s 	&%d" % (item, index)
                icon = QtGui.QIcon()
            elif isinstance(item,  BundleItemTreeNode):
                title = "%s 	&%d" % (item.buildMenuTextEntry(False), index)
                icon = item.icon
            menu.addAction(icon, title)

        def menu_aboutToHide():
            activeActionIndex = menu.actions().index(menu.activeAction()) if menu.activeAction() else -1
            callback(activeActionIndex)
        menu.aboutToHide.connect(menu_aboutToHide)

        point = self.viewport().mapToGlobal(self.cursorRect(self.textCursor()).bottomRight()) if cursorPosition else self.mainWindow.cursor().pos()
        menu.popup(point)

    # Default Context Menus
    def showEditorContextMenu(self, point):
        menu = self.createStandardContextMenu()
        menu.setParent(self)

        #Bundle Menu
        bundleMenu = self.application.supportManager.menuForBundle(self.syntax().bundle)
        extend_menu(menu, [ "-", bundleMenu ])

        #Se lo pasamos a los addons
        cursor = self.cursorForPosition(point)
        items = ["-"]
        for component in self.components():
            if isinstance(component, CodeEditorAddon):
                items += component.contributeToContextMenu(cursor)

        if len(items) > 1:
            actions = extend_menu(menu, items)

        menu.popup(self.mapToGlobal(point))

    # Contributes to Tab Menu
    def contributeToTabMenu(self):
        menues = []
        bundleMenu = self.application.supportManager.menuForBundle(self.syntax().bundle)
        if bundleMenu is not None:
            menues.append(bundleMenu)
            menues.append("-")
        if self.filePath:
            menues.extend([
                {   "text": "Path to clipboard",
                    "triggered": lambda ed = self: self.application.clipboard().setText(ed.filePath)  },
                {   "text": "Name to clipboard",
                    "triggered": lambda ed = self: self.application.clipboard().setText(ed.application.fileManager.basename(ed.filePath))  },
                {   "text": "Directory to clipboard",
                    "triggered": lambda ed = self: self.application.clipboard().setText(ed.application.fileManager.dirname(ed.filePath))  },
                ])
        return menues

    # Contributes to Main Menu
    @classmethod
    def contributeToMainMenu(cls):
        menu = PMXBaseEditor.contributeToMainMenu()
        menu["edit"] = [
                '-',
                {'text': '&Mode',
                 'items': [{
                        'text': 'Freehanded',
                        'sequence': resources.get_sequence("Editor", "FreehandedMode", 'Meta+Alt+E')
                    }, {
                        'text': 'Overwrite',
                        'sequence': resources.get_sequence("Editor", "OverwriteMode", 'Meta+Alt+O')
                    }, {
                        'text': 'Multiedit',
                        'sequence': resources.get_sequence("Editor", "MultieditMode", 'Meta+Alt+M')
                    }
                ]}
            ]
        menu["view"] = [
                '-',
                {'text': "Zoom in",
                  'icon': resources.get_icon("zoom-in"),
                  'sequence': resources.get_sequence("Editor", "ZoomIn"),
                  'triggered': cls.zoomIn},
                 {'text': "Zoom out",
                  'icon': resources.get_icon("zoom-out"),
                  'sequence': resources.get_sequence("Editor", "ZoomOut"),
                  'triggered': cls.zoomOut},
                '-',
                {'name': 'leftGutter',
                 'text': 'Left gutter',
                 'items': []},
                {'name': 'rightGutter',
                 'text': 'Right gutter',
                 'items': []
                }, '-',
                {'text': "Word wrap",
                 "items": [tuple([{
                        "text": "Automatic",
                        'toggled': cls.on_actionWordWrap_toggled,
                        'testChecked': lambda ed: bool(ed.getFlags() & ed.WordWrap)  and \
                            ed.wordWrapSize is None
                    }, "-" ] + [ {
                        "text": "%s" % size,
                        "toggled": lambda ed, checked, size = size: ed.on_actionWordWrap_toggled(checked, size = size),
                        'testChecked': lambda ed, size = size: bool(ed.getFlags() & ed.WordWrap) and \
                            ed.wordWrapSize == size
                    } for size in cls.STANDARD_SIZES])]
                }, 
                {'text': "Margin line",
                 "items": [tuple([{
                        "text": "None",
                        'toggled': lambda ed, checked: ed.on_actionMarginLine_toggled(not checked),
                        'testChecked': lambda ed: not bool(ed.getFlags() & ed.MarginLine)
                    }, "-" ] + [ {
                        "text": "%s" % size,
                        "toggled": lambda ed, checked, size = size: ed.on_actionMarginLine_toggled(checked, size = size),
                        'testChecked': lambda ed, size = size: bool(ed.getFlags() & ed.MarginLine) and \
                            ed.marginLineSize == size
                    } for size in cls.STANDARD_SIZES])]
                }, '-',
                {'text': "Indent guide",
                 'toggled': cls.on_actionIndentGuide_toggled,
                 'testChecked': lambda ed: bool(ed.getFlags() & ed.IndentGuide) 
                }, 
                {'text': "Highlight current line",
                 'toggled': cls.on_actionHighlightCurrentLine_toggled,
                 'testChecked': lambda ed: bool(ed.getFlags() & ed.HighlightCurrentLine) 
                },
                {'text': "Show tabs and spaces",
                 'toggled': cls.on_actionShowTabsAndSpaces_toggled,
                 'testChecked': lambda ed: bool(ed.getFlags() & ed.ShowTabsAndSpaces) },
                {'text': "Show line and paragraph",
                 'toggled': cls.on_actionShowLineAndParagraphs_toggled,
                 'testChecked': lambda ed: bool(ed.getFlags() & ed.ShowLineAndParagraphs) 
                }
            ]
        menu["text"] = {
            'before': 'bundles',
            'name': 'text',
            'text': '&Text',
            'items': [
                {'text': 'Select',
                 'items': [
                    {'text': '&Word',
                     'triggered': lambda ed: ed.selectWordCurrent(),
                     'sequence': resources.get_sequence("Editor", "SelectWord", 'Ctrl+Meta+W'),
                     },
                    {'text': '&Word under',
                     'triggered': lambda ed: ed.selectWordUnder(),
                     'sequence': resources.get_sequence("Editor", "SelectWordUnder", 'Ctrl+Meta+W'),
                     },
                    {'text': '&Line',
                     'triggered': lambda ed: ed.selectLine(),
                     'sequence': resources.get_sequence("Editor", "SelectLine", 'Ctrl+Meta+L'),
                     },
                    {'text': '&Paragraph',
                     'triggered': lambda ed: ed.selectParagraph()
                     },
                    {'text': 'Enclosing &brackets',
                     'triggered': lambda ed: ed.selectEnclosingBrackets(),
                     'sequence': resources.get_sequence("Editor", "SelectEnclosingBrackets", 'Ctrl+Meta+B'),
                     },
                    {'text': 'Current &scope',
                     'triggered': lambda ed: ed.selectCurrentScope(),
                     'sequence': resources.get_sequence("Editor", "SelectCurrentScope", 'Ctrl+Meta+S'),
                     },
                    {'text': '&All',
                     'triggered': lambda ed: ed.selectDocument(),
                     'sequence': resources.get_sequence("Editor", "SelectAll", 'Ctrl+A'),
                     }
                ]},
                {'text': 'Convert',
                 'items': [
                    {'text': 'Uppercase',
                     'sequence': resources.get_sequence("Editor", "ConvertUppercase", 'Ctrl+U'),
                     'triggered': lambda ed: ed.convertToUppercase(),
                     },
                    {'text': 'Lowercase',
                     'sequence': resources.get_sequence("Editor", "ConvertLowercase", 'Ctrl+Shift+U'),
                     'triggered': lambda ed: ed.convertToLowercase(),
                     },
                    {'text': 'Titlecase',
                     'sequence': resources.get_sequence("Editor", "ConvertTitlecase", 'Ctrl+Alt+U'),
                     'triggered': lambda ed: ed.convertToTitlecase(),
                     },
                    {'text': 'Opposite case',
                     'sequence': resources.get_sequence("Editor", "ConvertOppositeCase", 'Ctrl+G'),
                     'triggered': lambda ed: ed.convertToOppositeCase(),
                     }, '-',
                    {'text': 'Tab to spaces',
                     'triggered': lambda ed: ed.convertTabsToSpaces(),
                     },
                    {'text': 'Spaces to tabs',
                     'triggered': lambda ed: ed.convertSpacesToTabs(),
                     }, '-',
                    {'text': 'Transpose',
                     'sequence': resources.get_sequence("Editor", "ConvertTranspose", 'Ctrl+T'),
                     'triggered': lambda ed: ed.convertTranspose(),
                     }
                ]}, '-',
                {'text': 'Indentation',
                # TODO Set Indentation
                 'items': [
                    {'text': 'Indent using spaces',
                     'toggled': lambda ed, checked: ed.on_actionIndentation_toggled(checked),
                     'testChecked': lambda ed: ed.indentUsingSpaces
                     }, '-', ] + [ tuple([
                    {'text': 'Tab width: %d' % size,
                     'toggled': lambda ed, checked, size = size: ed.on_actionIndentation_toggled(ed.indentUsingSpaces, size = size),
                     'testChecked': lambda ed, size = size: (ed.indentUsingSpaces and ed.indentationWidth == size) or (not ed.indentUsingSpaces and ed.tabWidth == size)
                     } for size in range(1, 9) ]) ]
                }, 
                {'text': 'Line endings',
                 'items': [tuple(
                     [{'text': '%s' % name,
                     'toggled': lambda ed, checked, eol_chars = eol_chars: ed.setEolChars(eol_chars),
                     'testChecked': lambda ed, eol_chars = eol_chars: ed.lineSeparator() == eol_chars
                     } for eol_chars, _, name in text.EOLS])
                ]}, '-',
                {'text': 'Select bundle item',
                 'sequence': resources.get_sequence("Editor", "SelectBundleItem", 'Meta+Ctrl+T'),
                 'triggered': cls.on_actionSelectBundleItem_triggered,
                 },
                {'text': 'Execute line/selection',
                 'triggered': lambda ed: ed.executeCommand(),
                 }
            ]}
        menu["navigation"] = [
                "-",
                {'text': 'Toggle bookmark',
                 'triggered': cls.toggleBookmark,
                 'sequence': resources.get_sequence("Editor", "ToggleBookmark", 'Meta+F12'),
                 },
                {'text': 'Next bookmark',
                 'triggered': cls.bookmarkNext,
                 'sequence': resources.get_sequence("Editor", "NextBookmark", 'Meta+Alt+F12'),
                 },
                {'text': 'Previous bookmark',
                 'triggered': cls.bookmarkPrevious,
                 'sequence': resources.get_sequence("Editor", "PreviousBookmark", 'Meta+Shift+F12'),
                 },
                {'text': 'Remove all bookmarks',
                 'triggered': cls.removeAllBookmarks,
                 'sequence': resources.get_sequence("Editor", "RemoveAllBookmarks", 'Meta+Ctrl+F12'),
                 },
                "-",
                {'text': 'Go to &symbol',
                 'triggered': cls.on_actionGoToSymbol_triggered,
                 'sequence': resources.get_sequence("Editor", "GoToSymbol", 'Meta+Ctrl+Shift+O'),
                 },
                {'text': 'Go to &bookmark',
                 'triggered': cls.on_actionGoToBookmark_triggered,
                 'sequence': resources.get_sequence("Editor", "GoToBookmark", 'Meta+Ctrl+Shift+B'),
                 }
            ]
        return menu
    
    @classmethod
    def contributeToSettings(cls):
        from prymatex.gui.settings.theme import ThemeSettingsWidget
        from prymatex.gui.settings.editor import EditorSettingsWidget
        from prymatex.gui.settings.edit import EditSettingsWidget
        from prymatex.gui.settings.addons import AddonsSettingsWidgetFactory
        return [ EditorSettingsWidget, ThemeSettingsWidget, EditSettingsWidget, AddonsSettingsWidgetFactory("editor") ]
    
    def contributeToShortcuts(self):
        return [
            {'sequence': resources.get_sequence("Editor", "MoveLineUp", 'Meta+Ctrl+Up'),
             'activated': self.moveUp,
             'context': QtCore.Qt.WidgetShortcut
             },
            {'sequence': resources.get_sequence("Editor", "MoveLineDown", 'Meta+Ctrl+Down'),
             'activated': self.moveDown,
             'context': QtCore.Qt.WidgetShortcut
             },
            {'sequence': resources.get_sequence("Editor", "MoveColumnLeft", 'Meta+Ctrl+Left'),
             'activated': self.moveLeft,
             'context': QtCore.Qt.WidgetShortcut
             },
            {'sequence': resources.get_sequence("Editor", "MoveColumnRight", 'Meta+Ctrl+Right'),
             'activated': self.moveRight,
             'context': QtCore.Qt.WidgetShortcut
             }
        ]

    # ------------------ Menu Actions
    def on_actionIndentation_toggled(self, checked, size = None):
        print("Aplicando a", self)
        if size is None:
          size = self.indentationWidth if self.indentUsingSpaces else self.tabWidth
        self.indentUsingSpaces = checked
        if self.indentUsingSpaces:
            self.indentationWidth = size
        else:
            self.tabWidth = size

    def on_actionShowTabsAndSpaces_toggled(self, checked):
        if checked:
            flags = self.getFlags() | self.ShowTabsAndSpaces
        else:
            flags = self.getFlags() & ~self.ShowTabsAndSpaces
        self.setFlags(flags)

    def on_actionShowLineAndParagraphs_toggled(self, checked):
        if checked:
            flags = self.getFlags() | self.ShowLineAndParagraphs
        else:
            flags = self.getFlags() & ~self.ShowLineAndParagraphs
        self.setFlags(flags)

    def on_actionWordWrap_toggled(self, checked, size = None):
        self.wordWrapSize = size
        if checked:
            flags = self.getFlags() | self.WordWrap
        else:
            flags = self.getFlags() & ~self.WordWrap
        self.setFlags(flags)

    def on_actionHighlightCurrentLine_toggled(self, checked):
        if checked:
            flags = self.getFlags() | self.HighlightCurrentLine
        else:
            flags = self.getFlags() & ~self.HighlightCurrentLine
        self.setFlags(flags)

    def on_actionMarginLine_toggled(self, checked, size = None):
        if isinstance(size, int):
            self.marginLineSize = size
        if checked:
            flags = self.getFlags() | self.MarginLine
        else:
            flags = self.getFlags() & ~self.MarginLine
        self.setFlags(flags)

    def on_actionIndentGuide_toggled(self, checked):
        if checked:
            flags = self.getFlags() | self.IndentGuide
        else:
            flags = self.getFlags() & ~self.IndentGuide
        self.setFlags(flags)

    def on_actionSelectBundleItem_triggered(self):
        item = self.selectorDialog.select(self.bundleItemSelectableModel, title=_("Select Bundle Item"))

        # Select one?
        if item is not None:
            self.insertBundleItem(item['data'])

    def on_actionGoToSymbol_triggered(self):
        item = self.selectorDialog.select(self.symbolSelectableModel, title = _("Select Symbol"))
        if item is not None:
            self.goToBlock(item['data'])

    def on_actionGoToBookmark_triggered(self):
        item = self.selectorDialog.select(self.bookmarkSelectableModel, title=_("Select Bookmark"))
        if item is not None:
            self.goToBlock(item['data'])

    # ---------------------- Navigation API
    def restoreLocationMemento(self, memento):
        self.setTextCursor(memento)

    def on_document_undoCommandAdded(self):
        cursor = self.textCursor()

        if not (cursor.atEnd() or cursor.atStart()):
            self.saveLocationMemento(self.newCursorAtPosition(cursor.position() - 1))

    # ----------------- Drag and Drop
    def dragEnterEvent(self, event):
        self.setFocus(QtCore.Qt.MouseFocusReason)
        mimeData = event.mimeData()
        if mimeData.hasUrls() or mimeData.hasText():
            event.accept()

    def dragMoveEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        self.setTextCursor(cursor)

    def dropEvent(self, event):
        """When a url or text is dropped"""
        #mimeData = event.mimeData()
        if event.mimeData().hasUrls():
            files = [url.toLocalFile() for url in event.mimeData().urls()]
            for filePath in files:
                items = self.application.supportManager.getFileExtensionItem(filePath, self.scope())
                if items:
                    item = items[0]
                    env = {
                            #relative path of the file dropped (relative to the document directory, which is also set as the current directory).
                            'TM_DROPPED_FILE': filePath,
                            #the absolute path of the file dropped.
                            'TM_DROPPED_FILEPATH': filePath,
                            #the modifier keys which were held down when the file got dropped.
                            #This is a bitwise OR in the form: SHIFT|CONTROL|OPTION|COMMAND (in case all modifiers were down).
                            'TM_MODIFIER_FLAGS': filePath
                    }
                    self.insertBundleItem(item, environment = env)
                else:
                    self.application.openFile(filePath)
        elif event.mimeData().hasText():
            self.textCursor().insertText(event.mimeData().text())

