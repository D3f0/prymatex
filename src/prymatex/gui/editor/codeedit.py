# -*- encoding: utf-8 -*-

import re, logging
from bisect import bisect
from PyQt4.QtCore import QRect, Qt, SIGNAL
from PyQt4.QtGui import QPlainTextEdit, QTextEdit, QTextFormat, QMenu, \
    QTextCursor, QAction, QFont, QPalette, QToolTip
from prymatex.bundles import PMXBundle, PMXSnippet
from prymatex.bundles.command import PMXCommand
from prymatex.bundles.syntax import PMXSyntax
from prymatex.bundles.theme import PMXTheme
from prymatex.core.base import PMXObject
from prymatex.core.config import pmxConfigPorperty
from prymatex.gui.editor.sidebar import PMXSidebar
from prymatex.gui.editor.syntax import PMXSyntaxProcessor, PMXBlockUserData

logger = logging.getLogger(__name__)

# Key press debugging 
KEY_NAMES = dict([(getattr(Qt, keyname), keyname) for keyname in dir(Qt) 
                  if keyname.startswith('Key_')])

def debug_key(key_event):
    ''' Prevents hair loss when debuging what the hell is going on '''
    key = key_event.key()
    mods = []
    modifiers = key_event.modifiers()
    if modifiers & Qt.AltModifier:
        mods.append("AltModifier")
    if modifiers & Qt.ControlModifier:
        mods.append("ControlModifier")
    if modifiers & Qt.MetaModifier:
        mods.append("MetaModifier")
    if modifiers & Qt.ShiftModifier:
        mods.append("ShiftModifier")
    
    return "%s <%s> Code: %d chr(%d) = %s" % (KEY_NAMES[key],  ", ".join(mods), 
                                              key, key, key < 255 and chr(key) 
                                              or 'N/A')

_counter = 0


class PMXCodeEdit(QPlainTextEdit, PMXObject):
    '''
    The GUI element which holds the editor.
    This class acts as a buffer for text, it does not know anything about
    the underlying filesystem.
    
    It holds the highlighter and the folding
    
    '''
    
    WHITESPACE = re.compile(r'^(?P<whitespace>\s+)', re.UNICODE)
    SPLITWORDS = re.compile(r'\s', re.UNICODE)
    WORD = re.compile(r'\w+', re.UNICODE)

    #=======================================================================
    # Settings, config and init
    #=======================================================================
    default_syntax = pmxConfigPorperty(default = 'text.plain')
    soft_tabs = pmxConfigPorperty(default = True)
    tab_size = pmxConfigPorperty(default = 4)
    font = pmxConfigPorperty(default = QFont('Monospace', 10))
    
    @pmxConfigPorperty(default = 'Twilight')
    def theme(self, name):
        theme = PMXTheme.getThemeByName(name)
        self.processor.formatter = theme
        style = theme.getStyle()
        foreground = style.getQColor('foreground')
        background = style.getQColor('background')
        selection = style.getQColor('selection')
        invisibles = style.getQColor('invisibles')
        palette = self.palette()
        palette.setColor(QPalette.Active, QPalette.Text, foreground)
        palette.setColor(QPalette.Active, QPalette.Base, background)
        palette.setColor(QPalette.Inactive, QPalette.Base, background)
        palette.setColor(QPalette.Active, QPalette.Highlight, selection)
        palette.setColor(QPalette.Active, QPalette.AlternateBase, invisibles)
        self.setPalette(palette)
        self.line_highlight = style.getQColor('lineHighlight')
        self.highlightCurrentLine()
    
    class Meta(object):
        settings = 'editor'
    
    @property
    def tabKeyBehavior(self):
        return self.soft_tabs and u' ' * self.tab_size or u'\t'
    
    def __init__(self, parent = None):
        super(PMXCodeEdit, self).__init__(parent)
        self.sidebar = PMXSidebar(self)
        self.processor = PMXSyntaxProcessor(self)
        self.bookmarks = []
        self.folded = []
        self.snippet = None
        
        # Actions performed when a key is pressed
        self.setupUi()
        self.setupActions()
        self.connectSignals()
        self.declareEvents()
        self.configure()
        
        #Set default syntax
        syntax = PMXSyntax.getSyntaxByScope(self.default_syntax)
        if syntax != None:
            self.setSyntax(syntax)

    #=======================================================================
    # Connect Signals and Declare Events
    #=======================================================================
    def setupUi(self):
        #self.updateLineNumberAreaWidth(0)
        self.setWindowTitle(self.__class__.__name__)
        
    def connectSignals(self):
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.sendCursorPosChange)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
    def declareEvents(self):
        self.declareEvent('editorCursorPositionChangedEvent()')
        self.declareEvent('editorSetSyntaxEvent()')

    def setupActions(self):
        self.actionIndent = QAction(self.trUtf8("Increase indentation"), self )
        self.connect(self.actionIndent, SIGNAL("triggered()"), self.indent)
        self.actionUnindent = QAction(self.trUtf8("Decrease indentation"), self )
        self.connect(self.actionUnindent, SIGNAL("triggered()"), self.unindent)
        self.actionFind = QAction(self.trUtf8("Find"), self)

    def getCurrentScope(self):
        cursor = self.textCursor()
        block = cursor.block()
        user_data = block.userData()
        if user_data == None:
            return ""
        if not bool(user_data) and block.userState() == self.processor.MULTI_LINE:
            while not bool(block.userData()):
                block = block.previous()
            return block.userData().getLastScope()
        return user_data.getScopeAtPosition(cursor.columnNumber())
        
    def sendCursorPosChange(self):
        c = self.textCursor()
        line  = c.blockNumber()
        col = c.columnNumber()
        self.editorCursorPositionChangedEvent(line, col)
        
    def setSyntax(self, syntax):
        self.processor.syntax = syntax
        self.editorSetSyntaxEvent(syntax)
    
    @property
    def syntax(self):
        return self.processor.syntax
        
    @property
    def index(self):
        tab_widget = self.parent()
        return tab_widget.indexOf(self)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        
        menu.addAction(self.actionIndent)
        menu.addAction(self.actionUnindent)
        self.actionUnindent.setEnabled(self.can_unindent())

        menu.exec_(event.globalPos());
        del menu
        
    def lineNumberAreaWidth(self):
        # si tiene folding tengo que sumar mas 10
        return 3 + self.fontMetrics().width('9') * len(str(self.blockCount())) + self.sidebar.bookmarkArea + self.sidebar.foldArea 
        
    def updateLineNumberAreaWidth(self, newBlockCount):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.sidebar.scroll(0, dy);
        else:
            self.sidebar.update(0, rect.y(), self.sidebar.width(), rect.height());
        if (rect.contains(self.viewport().rect())):
            self.updateLineNumberAreaWidth(0)
    
    def resizeEvent(self, event):
        super(PMXCodeEdit, self).resizeEvent(event)
        cr = self.contentsRect()
        self.sidebar.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
        
    def highlightCurrentLine(self):
        extraSelections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(self.line_highlight);
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        self.setExtraSelections(extraSelections)
    
    def selectionBlockStart(self):
        '''
        Returns the block where the slection starts
        '''
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return -1
        return self.document().findBlock( cursor.selectionStart() ).blockNumber()
        
    def selectionBlockEnd(self):
        '''
        Returns the block number where the selection ends
        '''
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return -1
        return self.document().findBlock( cursor.selectionEnd() ).blockNumber()
    
    #=======================================================================
    # Mouse Events
    #=======================================================================
    
    def mousePressEvent(self, mouse_event):
        #self.inserSpacesUpToPoint(mouse_event.pos())
        super(PMXCodeEdit, self).mousePressEvent(mouse_event)

    def mouseMoveEvent(self, event):
        #position = event.pos()
        #QToolTip.showText(self.mapToGlobal(position), "Cacho", self)
        super(PMXCodeEdit, self).mouseMoveEvent(event)

    def inserSpacesUpToPoint(self, point, spacing_character = ' '):
        '''
        Inserts whitespace up to a point
        '''
        cursor = self.cursorForPosition(point)
        block = cursor.block()
        if not block.isValid():
            return
        text = block.text()
        self.fontMetrics()
        font_width = self.fontMetrics().width(' ')
        line_width = font_width * text.length()
        # Cast to int if Py > 3.x
        char_number = int(point.x() / font_width)
        char_number_delta = char_number - text.length()
        if char_number_delta > 0:
            # Insert some empty characters
            cursor.beginEditBlock()
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor, 1)
            #print "Inserting", char_number_delta
            cursor.insertText(spacing_character * char_number_delta)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor, 1)
            cursor.endEditBlock()
            self.setTextCursor(cursor)
            
        #print block.blockNumber(), ":", text, line_width, "px"
        #print char_number, text.length()
    
    #=======================================================================
    # Keyboard Events
    #=======================================================================
    
    def keyPressEvent(self, key_event):
        '''
        This method is called whenever a key is pressed. The key code is stored in key_event.key()
        '''
        
        #Check for snippet
        if self.snippet != None and self.keyPressSnippetEvent(key_event):
            return
        
        key = key_event.key()
        if key == Qt.Key_Tab:
            for handler in [self.keyTabPressBundleItemEvent, self.keyTabPressIndentEvent]:
                if handler(key_event):
                    return
        elif key == Qt.Key_Backtab:
            for handler in [self.keyBacktabPressUnindentEvent]:
                if handler(key_event):
                    return
        elif key == Qt.Key_Backspace:
            for handler in [self.keyBackspacePressSmartTypingEvent]:
                if handler(key_event):
                    return
        elif key == Qt.Key_Return:
            for handler in [self.keyReturnPressSyntaxEvent, self.keyReturnPressIndentEvent]:
                if handler(key_event):
                    return
        else:
            for handler in [self.keyOtherPressBundleItemEvent, self.keyOtherPressIndentEvent, self.keyOtherPressSmartTypingEvent]:
                if handler(key_event):
                    return
        super(PMXCodeEdit, self).keyPressEvent(key_event)

    def keyPressSnippetEvent(self, key_event):
        key = key_event.key()
        cursor = self.textCursor()
        
        if key == Qt.Key_Tab or key == Qt.Key_Backtab:
            (index, holder) = self.snippet.setDefaultHolder(cursor.position())
            if holder == None:
                self.snippet = None
                return False
            if key == Qt.Key_Tab:
                holder = self.snippet.next()
            else:
                holder = self.snippet.previous()
            if holder == None:
                cursor.setPosition(self.snippet.ends)
            else:
                index = holder.position()
                cursor.setPosition(index)
                cursor.setPosition(index + len(holder), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        elif key == Qt.Key_Backspace or key == Qt.Key_Delete:
            starts = self.snippet.starts
            ends = self.snippet.ends
            if cursor.hasSelection():
                (index, holder) = self.snippet.setDefaultHolder(cursor.selectionStart(), cursor.selectionEnd())
                if holder == None:
                    self.snippet = None
                    return False
                holder.remove(cursor.selectionStart() - index, cursor.selectionEnd() - index)
                position = cursor.selectionStart()
            else:
                if key == Qt.Key_Delete:
                    (index, holder) = self.snippet.setDefaultHolder(cursor.position() + 1)
                else:
                    (index, holder) = self.snippet.setDefaultHolder(cursor.position())
                if holder == None:
                    self.snippet = None
                    return False
                if key == Qt.Key_Delete:
                    holder.remove(cursor.position() - index, cursor.position() - index + 1)
                    position = cursor.position()
                else:
                    holder.remove(cursor.position() - index - 1, cursor.position() - index)
                    position = cursor.position() - 1
            #Ajuste
            position += (holder.position() - index)
            cursor.setPosition(starts)
            cursor.setPosition(ends, QTextCursor.KeepAnchor)
            cursor.insertText(str(self.snippet))
            self.snippet.ends = cursor.position()
            cursor.setPosition(position)
            self.setTextCursor(cursor)
        elif 0x20 <= key <= 0x7E: #Para latin poner otra cosa
            starts = self.snippet.starts
            ends = self.snippet.ends
            if cursor.hasSelection():
                (index, holder) = self.snippet.setDefaultHolder(cursor.selectionStart(), cursor.selectionEnd())
                if holder == None or holder.last:
                    self.snippet = None
                    return key_event
                holder.remove(cursor.selectionStart() - index, cursor.selectionEnd() - index)
                position = cursor.selectionStart()
            else:
                (index, holder) = self.snippet.setDefaultHolder(cursor.position())
                if holder == None or holder.last:
                    self.snippet = None
                    return False
                position = cursor.position()
            holder.insert(unicode(key_event.text()), position - index)
            position += holder.position() - index + 1
            cursor.setPosition(starts)
            cursor.setPosition(ends, QTextCursor.KeepAnchor)
            cursor.insertText(str(self.snippet))
            self.snippet.ends = cursor.position()
            cursor.setPosition(position)
            self.setTextCursor(cursor)
        else:
            return False
        return True
    
    #=======================================================================
    # Tab Keyboard Events
    #=======================================================================
    
    def keyTabPressBundleItemEvent(self, key_event):
        cursor = self.textCursor()
        line = unicode(cursor.block().text())
        scope = self.getCurrentScope()
        words = self.SPLITWORDS.split(line[:cursor.columnNumber()])
        word = words and words[-1] or ""
        if scope or word:
            snippets = PMXBundle.getTabTriggerItem(word, scope)
            if len(snippets) > 1:
                self.selectBundleItem(snippets, tabTrigger = True)
                return True
            elif snippets:
                self.insertBundleItem(snippets[0], tabTrigger = True)
                return True
        return False
    
    def keyTabPressIndentEvent(self, key_event):
        cursor = self.textCursor()
        if cursor.hasSelection():
            self.indent(self.tabKeyBehavior)
        else:
            cursor.insertText(self.tabKeyBehavior)
        return True
    
    #=======================================================================
    # Backtab Keyboard Events
    #=======================================================================
    
    def keyBacktabPressUnindentEvent(self, key_event):
        self.unindent()
        return True
    
    #=======================================================================
    # Backspace Keyboard Events
    #=======================================================================
    def keyBackspacePressSmartTypingEvent(self, key_event):
        cursor = self.textCursor()
        if cursor.hasSelection():
            return False
        doc = self.document()
        scope = self.getCurrentScope()
        preferences = PMXBundle.getPreferenceSettings(scope)
        if preferences.smartTypingPairs:
            character = doc.characterAt(cursor.position() - 1).toAscii()
            pairs = filter(lambda pair: pair[0] == character or pair[1] == character, preferences.smartTypingPairs)
            if pairs and pairs[0][0] == character and doc.characterAt(cursor.position()).toAscii() == pairs[0][1]:
                cursor.deleteChar()
            elif pairs and pairs[0][1] == character and doc.characterAt(cursor.position() - 2).toAscii() == pairs[0][0]:
                cursor.deletePreviousChar()
        return False
    
    #=======================================================================
    # Return Keyboard Events
    #=======================================================================
    
    def keyReturnPressSyntaxEvent(self, key_event):
        line = unicode(self.textCursor().block().text())
        if self.document().blockCount() == 1:
            syntax = PMXSyntax.findSyntaxByFirstLine(line)
            if syntax != None:
                self.setSyntax(syntax)
        return False
    
    def keyReturnPressIndentEvent(self, key_event):
        line = unicode(self.textCursor().block().text())
        scope = self.getCurrentScope()
        settings = PMXBundle.getPreferenceSettings(scope)
        acction = settings.indent(line)
        indentation = self.indentationWhitespace(line)
        if acction == settings.INDENT_INCREASE:
            print "increase"
            super(PMXCodeEdit, self).keyPressEvent(key_event)
            self.increaseIndent(indentation)
        elif acction == settings.INDENT_NEXTLINE:
            print "increasenext"
            super(PMXCodeEdit, self).keyPressEvent(key_event)
            self.increaseIndent(indentation)
        else:
            super(PMXCodeEdit, self).keyPressEvent(key_event)
            self.indent(indentation)
        return True
    
    #=======================================================================
    # Other Keyboard Events
    #=======================================================================
    
    def keyOtherPressBundleItemEvent(self, key_event):
        return False
    
    def keyOtherPressIndentEvent(self, key_event):
        key = key_event.key()
        if key > 256:
            return False
        character = chr(key)
        cursor = self.textCursor()
        current_line = unicode(cursor.block().text()) + character
        scope = self.getCurrentScope()
        settings = PMXBundle.getPreferenceSettings(scope)
        acction = settings.indent(current_line)
        if acction == settings.INDENT_DECREASE:
            previous_block = cursor.block().previous()
            if previous_block:
                current_indentation = self.indentationWhitespace(current_line)
                previous_indentation = self.indentationWhitespace(previous_block.text())
                if current_indentation == previous_indentation:
                    self.unindent()
                    return True
        elif acction == settings.UNINDENT:
            print "unident"
        return False
    
    def keyOtherPressSmartTypingEvent(self, key_event):
        cursor = self.textCursor()
        character = unicode(key_event.text())
        scope = self.getCurrentScope()
        preferences = PMXBundle.getPreferenceSettings(scope)
        pairs = filter(lambda pair: pair[0] == character or pair[1] == character, preferences.smartTypingPairs)
        if pairs:
            if cursor.hasSelection():
                position = cursor.selectionStart()
                text = pairs[0][0] + cursor.selectedText() + pairs[0][1]
                cursor.insertText(text)
                cursor.setPosition(position)
                cursor.setPosition(position + len(text), QTextCursor.KeepAnchor)
            else:
                position = cursor.position()
                if pairs[0][0] == character:
                    super(PMXCodeEdit, self).keyPressEvent(key_event)
                    cursor.insertText(pairs[0][1])
                elif pairs[0][1] == character:
                    cursor.insertText(pairs[0][0])
                    super(PMXCodeEdit, self).keyPressEvent(key_event)
                cursor.setPosition(position + 1)
            self.setTextCursor(cursor)
            return True
        else:
            return False

    #==========================================================================
    # BundleItems
    #==========================================================================

    def insertBundleItem(self, item, tabTrigger = False, indent = True):
        ''' Inserta un bundle item, por ahora un snippet, debe resolver el item antes de insertarlo
        '''
        cursor = self.textCursor()
        line = unicode(cursor.block().text())
        indentation = indent and self.indentationWhitespace(line) or ""
        if tabTrigger and item.tabTrigger != None:
            for _ in range(len(item.tabTrigger)):
                cursor.deletePreviousChar()
        if isinstance(item, PMXSnippet):
            #Snippet Item needs compile and clone
            if not item.ready:
                item.compile()
            item = item.clone()
            item.resolve(indentation = indentation, tabreplacement = self.tabKeyBehavior, environment = self.buildEnvironment(item))
            #Set starts
            if cursor.hasSelection():
                item.starts = cursor.selectionStart()
            else:
                item.starts = cursor.position()
            #Insert Snippet
            #TODO: que no sea por str sino un un render o algo de eso
            cursor.insertText(str(item))
            #Set end
            item.ends = cursor.position()
            holder = item.next()
            if holder != None:
                index = holder.position()
                cursor.setPosition(index)
                cursor.setPosition(index + len(holder), QTextCursor.KeepAnchor)
                self.snippet = item
            else:
                cursor.setPosition(item.ends)
            self.setTextCursor(cursor)
        elif isinstance(item, PMXCommand):
            char = line and line[cursor.columnNumber() - 1] or ""
            item.resolve(unicode(self.toPlainText()), char, environment = self.buildEnvironment(item))
            functions = {
                         'replaceSelectedText': self.replaceSelectedText,
                         'replaceDocument': self.replaceDocument,
                         'insertText': self.insertText,
                         'afterSelectedText': self.afterSelectedText,
                         'insertAsSnippet': self.insertSnippet,
                         'showAsHTML': self.mainwindow.showHtml,
                         'showAsTooltip': self.mainwindow.showTooltip,
                         'createNewDocument': self.mainwindow.createNewDocument
                         }
            item.execute(functions)
        elif isinstance(item, PMXSyntax):
            self.setSyntax(item)

    def selectBundleItem(self, items, tabTrigger = False):
        syntax = any(map(lambda item: isinstance(item, PMXSyntax), items))
        menu = QMenu()
        for index, item in enumerate(items):
            action = menu.addAction(item.buildMenuTextEntry("&" + str(index + 1)))
            receiver = lambda item = item: self.insertBundleItem(item, tabTrigger = tabTrigger)
            self.connect(action, SIGNAL('triggered()'), receiver)
        if syntax:
            point = self.mainwindow.cursor().pos()
        else:
            point = self.viewport().mapToGlobal(self.cursorRect(self.textCursor()).bottomRight())
        menu.exec_(point)
    
    def buildEnvironment(self, item):
        cursor = self.textCursor()
        line = unicode(cursor.block().text())
        scope = self.getCurrentScope()
        preferences = PMXBundle.getPreferenceSettings(scope)
        try:
            match = filter(lambda m: m.start() <= cursor.columnNumber() <= m.end(), self.WORD.finditer(line)).pop()
            current_word = line[match.start():match.end()]
        except IndexError:
            current_word = ""
        env = item.buildEnvironment()
        env.update({
                'TM_CURRENT_LINE': line,
                'TM_LINE_INDEX': cursor.columnNumber(), 
                'TM_LINE_NUMBER': cursor.block().blockNumber() + 1, 
                'TM_SCOPE': scope,
                'TM_SOFT_TABS': self.soft_tabs and u'YES' or u'NO',
                'TM_TAB_SIZE': self.tab_size,
        });
        if current_word != "":
            env['TM_CURRENT_WORD'] = current_word
        if self.syntax != None:
            env['TM_MODE'] = self.syntax.name
        if self.parent().file.path != None:
            env['TM_FILEPATH'] = self.parent().file.path
            env['TM_FILENAME'] = self.parent().file.filename
            env['TM_DIRECTORY'] = self.parent().file.directory
        if cursor.hasSelection():
            env['TM_SELECTED_TEXT'] = cursor.selectedText().replace(u'\u2029', '\n')
        #env.update(self._meta.settings['static_variables'])
        env.update(preferences.shellVariables)
        return env

    #==========================================================================
    # Commands
    #==========================================================================
    
    def replaceSelectedText(self, string, **kwargs):
        if 'input' in kwargs and kwargs['input'] == 'document':
            self.replaceDocument(string, **kwargs)
        else:
            cursor = self.textCursor()
            position = cursor.selectionStart()
            cursor.insertText(string)
            cursor.setPosition(position, position + len(string))
            self.setTextCursor(cursor)
        
    def replaceDocument(self, string, **kwargs):
        self.document().setPlainText(string)
        
    def insertText(self, string, **kwargs):
        cursor = self.textCursor()
        cursor.insertText(string)
    
    def afterSelectedText(self, string, **kwargs):
        cursor = self.textCursor()
        position = cursor.selectionEnd()
        cursor.setPosition(position)
        cursor.insertText(string)
    
    def insertSnippet(self, snippet, **kwargs):
        '''Create a new snippet and insert'''
        cursor = self.textCursor()
        if 'input' in kwargs:
            print kwargs['input']
            if kwargs['input'] == 'selection':
                position = cursor.selectionStart()
                cursor.removeSelectedText()
                cursor.setPosition(position)
                self.setTextCursor(cursor)
            elif kwargs['input'] == 'word':
                line = unicode(cursor.block().text())
                match = filter(lambda m: m.start() <= cursor.columnNumber() <= m.end(), self.WORD.finditer(line)).pop()
                current_word = line[match.start():match.end()]
                index = cursor.columnNumber() - len(current_word)
                index = index >= 0 and index or 0
                index = line.find(current_word, index)
                cursor.setPosition(cursor.block().position() + index)
                self.setTextCursor(cursor)
                for _ in range(len(current_word)):
                    cursor.deleteChar()
        self.insertBundleItem(snippet, indent = False)

    #==========================================================================
    # Folding
    #==========================================================================
    
    def codeFoldingEvent(self, line_number):
        if line_number in self.folded:
            self._unfold(line_number)
        else:
            self._fold(line_number)
        self.update()
        self.sidebar.update()
    
    def _fold(self, line_number):
        startBlock = self.document().findBlockByNumber(line_number - 1)
        endBlock = self._find_block_fold_closing(startBlock)

        block = startBlock
        while block.isValid() and block != endBlock:
            block = block.next()
            user_data = block.userData()
            user_data.folding += 1
            block.setVisible(user_data.folding == PMXBlockUserData.FOLDING_NONE)
            block = block.next()
        
        self.folded.append(line_number)
        self.document().markContentsDirty(startBlock.position(), endBlock.position())

    def _unfold(self, line_number):
        '''startBlock = self.document().findBlockByNumber(line_number - 1)
        endPos = self._find_block_fold_closing(startBlock)
        endBlock = self.document().findBlockByNumber(endPos)

        block = startBlock.next()
        while block.isValid() and block != endBlock:
            block.setVisible(True)
            block.setLineCount(block.layout().lineCount())
            endPos = block.position() + block.length()
            if block.blockNumber() in self.folded:
                close = self._find_fold_closing(block)
                block = self.document().findBlockByNumber(close)
            else:
                block = block.next()
        '''
        self.folded.remove(line_number)
        #self.document().markContentsDirty(startBlock.position(), endPos)

    def _find_block_fold_closing(self, start):
        end = start
        if start.userData().folding == PMXBlockUserData.FOLDING_START:
            #Find Next
            start_counter = 0
            while end.userData().folding != PMXBlockUserData.FOLDING_STOP or (end.userData().folding == PMXBlockUserData.FOLDING_STOP and start_counter != 0):
                end = end.next()
                if end.userDate().folding == PMXBlockUserData.FOLDING_START:
                    start_counter += 1
                elif end.userDate().folding == PMXBlockUserData.FOLDING_STOP:
                    start_counter -= 1
        else:
            #Find Previous
            end_counter = 0
            while end.userData().folding != PMXBlockUserData.FOLDING_START or (end.userData().folding == PMXBlockUserData.FOLDING_START and end_counter != 0):
                end = end.previous()
                if end.userDate().folding == PMXBlockUserData.FOLDING_STOP:
                    end_counter += 1
                elif end.userDate().folding == PMXBlockUserData.FOLDING_START:
                    end_counter -= 1
        return end
    #==========================================================================
    # Bookmarks
    #==========================================================================
    
    def toggleBookmark(self, line_number):
        if line_number in self.bookmarks:
            self.bookmarks.remove(line_number)
        else:
            index = bisect(self.bookmarks, line_number)
            self.bookmarks.insert(index, line_number)
        self.sidebar.update()
    
    def removeBookmarks(self):
        self.bookmarks = []
        self.sidebar.update()
    
    def bookmarkNext(self, line_number):
        index = bisect(self.bookmarks, line_number)
        if index < len(self.bookmarks):
            self.goToLine(self.bookmarks[index])
        else:
            self.goToLine(self.bookmarks[0])
    
    def bookmarkPrevious(self, line_number):
        if line_number in self.bookmarks:
            index = self.bookmarks.index(line_number)
        else:
            index = bisect(self.bookmarks, line_number)
        if index < len(self.bookmarks):
            self.goToLine(self.bookmarks[index - 1])
    
    def goToLine(self, lineno):
        cursor = self.textCursor()
        cursor.setPosition(self.document().findBlockByNumber(lineno - 1).position())
        self.setTextCursor(cursor)
    
    def goToColumn(self, column):
        cursor = self.textCursor()
        cursor.setPosition(cursor.block().position() + column)
        self.setTextCursor(cursor)
    
    #===========================================================================
    # Text Indentation
    #===========================================================================
    
    @classmethod
    def indentationWhitespace(cls, text):
        '''
        Gets text whitespace
        @param text: Text, QTextCursor o QTextBlock instance
        @return: The text whitespace
        '''
        match = cls.WHITESPACE.match(text)
        try:
            ws = match.group('whitespace')
            return ws
        except AttributeError:
            return ''
    
    def increaseIndent(self, indentation):
        self.indent(indentation + (self.tabKeyBehavior))
    
    def decreaseIndent(self, indentation):
        self.unindent()
        
    # TODO: Word wrapping fix
    # TODO: Correct whitespace mix
    def indent(self, indentation):
        '''
        Indents text, it take cares of block selections.
        '''
        block_count = self.selectionBlockEnd() - self.selectionBlockStart() + 1
        cursor = self.textCursor()
        cursor.beginEditBlock()
        new_cursor = QTextCursor(cursor)
        new_cursor.movePosition(QTextCursor.PreviousBlock, QTextCursor.MoveAnchor, block_count - 1)
        new_cursor.movePosition(QTextCursor.StartOfBlock)
        for _i in range(block_count):
            new_cursor.insertText(indentation)
            new_cursor.movePosition(QTextCursor.NextBlock)
        self.setTextCursor(cursor)
        cursor.endEditBlock()

    def can_unindent(self):
        '''
        Check if un-indetation is possible
        @returns True if indentation is possible, false otherwise
        '''
        block_count = self.selectionBlockEnd() - self.selectionBlockStart() + 1
        new_cursor = QTextCursor( self.textCursor() )
        new_cursor.movePosition(QTextCursor.PreviousBlock, QTextCursor.MoveAnchor, block_count -1)
        new_cursor.movePosition(QTextCursor.StartOfBlock)
        for i in range(block_count):
            if not new_cursor.block().text().startsWith(self.tabKeyBehavior):
                new_cursor.movePosition(QTextCursor.PreviousBlock, QTextCursor.MoveAnchor, i)
                return False
        del new_cursor
        return True
    
    def unindent(self):
        '''
        Unindents text, fails if can_unindent() returns False
        '''
        if not self.can_unindent():
            return
        block_count = self.selectionBlockEnd() - self.selectionBlockStart() + 1
        cursor = self.textCursor()
        cursor.beginEditBlock()
        new_cursor = QTextCursor(cursor)
        new_cursor.movePosition(QTextCursor.PreviousBlock, QTextCursor.MoveAnchor, block_count -1)
        new_cursor.movePosition(QTextCursor.StartOfBlock)

        for _i in range(block_count):
            if self.soft_tabs:
                for _j in range(self.tab_size):
                    new_cursor.deleteChar()
            else:
                new_cursor.deleteChar()
                    
            new_cursor.movePosition(QTextCursor.NextBlock)
            
            self.setTextCursor(cursor)
        cursor.endEditBlock()

    MAX_FONT_POINT_SIZE = 32
    MIN_FONT_POINT_SIZE = 6
    
    @property
    def font_size(self):
        font = self.font()
        pt_size = font.pointSize()
        return pt_size

    @font_size.setter
    def font_size(self, value):
        font = self.font()
        font.setPointSize(value)
        self.setFont(font)
        
