#!/usr/bin/env python
#-*- encoding: utf-8 -*-
from PyQt4 import QtCore, QtGui

class PMXBaseEditorMode(object):
    def __init__(self, editor):
        self.editor = editor
    
    def active(self, event, scope):
        pass
    
    def isActive(self):
        return False
        
    def inactive(self):
        pass
               
    def keyPressEvent(self, event):
        pass
        
class PMXSnippetEditorMode(PMXBaseEditorMode):
    def __init__(self, editor):
        PMXBaseEditorMode.__init__(self, editor)

    def isActive(self):
        return self.editor.snippetProcessor.snippet is not None

    def inactive(self):
        self.editor.snippetProcessor.endSnippet()

    def keyPressEvent(self, event):
        cursor = self.editor.textCursor()
        if event.key() == QtCore.Qt.Key_Escape:
            return self.endSnippet(event)
        elif event.key() in [ QtCore.Qt.Key_Tab, QtCore.Qt.Key_Backtab ]:
            holder = self.editor.snippetProcessor.getHolder(cursor.selectionStart(), cursor.selectionEnd())
            if holder is None:
                return self.endSnippet(event)
            if event.key() == QtCore.Qt.Key_Tab:
                holder = self.editor.snippetProcessor.nextHolder(holder)
            else:
                holder = self.editor.snippetProcessor.previousHolder(holder)
            if holder == None:
                self.setCursorPosition(self.editor.snippetProcessor.endPosition())
            else:
                self.editor.snippetProcessor.selectHolder(holder)
        elif event.key() in [ QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete ]:
            if cursor.hasSelection():
                holder = self.editor.snippetProcessor.getHolder(cursor.selectionStart(), cursor.selectionEnd())
                if holder is None:
                    return self.endSnippet(event)
                #Posicion relativa al holder
                position = cursor.selectionStart() - holder.start
                leng = cursor.selectionEnd() - cursor.selectionStart()
                QtGui.QPlainTextEdit.keyPressEvent(self.editor, event)
                #Capture Text
                cursor.setPosition(holder.start)
                cursor.setPosition(holder.end - leng, QtGui.QTextCursor.KeepAnchor)
                holder.setContent(cursor.selectedText())
                #Prepare replace
                self.selectSlice(self.editor.snippetProcessor.startPosition(), self.editor.snippetProcessor.endPosition() - leng)
                self.editor.snippetProcessor.render()
                self.setCursorPosition(holder.start + position)
            else:
                if event.key() == QtCore.Qt.Key_Delete:
                    holder = self.editor.snippetProcessor.getHolder(cursor.position() + 1)
                else:
                    holder = self.editor.snippetProcessor.getHolder(cursor.position() - 1)
                if holder == None:
                    return self.endSnippet(event)
                #Posicion relativa al holder
                position = cursor.position() - holder.start
                leng = cursor.selectionEnd() - cursor.selectionStart()
                QtGui.QPlainTextEdit.keyPressEvent(self.editor, event)
                #Capture Text
                cursor.setPosition(holder.start)
                cursor.setPosition(holder.end - 1, QtGui.QTextCursor.KeepAnchor)
                holder.setContent(cursor.selectedText())
                #Prepare replace
                self.selectSlice(self.editor.snippetProcessor.startPosition(), self.editor.snippetProcessor.endPosition() - 1)
                self.editor.snippetProcessor.render()
                if event.key() == QtCore.Qt.Key_Delete:
                    self.setCursorPosition(holder.start + position)
                else:
                    self.setCursorPosition(holder.start + position - 1)
        elif event.text():
            if cursor.hasSelection():
                holder = self.editor.snippetProcessor.getHolder(cursor.selectionStart(), cursor.selectionEnd())
                if holder is None:
                    return self.endSnippet(event)
                #Posicion relativa al holder
                position = cursor.selectionStart() - holder.start
                leng = cursor.selectionEnd() - cursor.selectionStart()
                QtGui.QPlainTextEdit.keyPressEvent(self.editor, event)
                #Capture Text
                cursor.setPosition(holder.start)
                cursor.setPosition(holder.start + (holder.end - holder.start - leng) + 1, QtGui.QTextCursor.KeepAnchor)
                holder.setContent(cursor.selectedText())
                #Prepare replace
                self.selectSlice(self.editor.snippetProcessor.startPosition(), self.editor.snippetProcessor.endPosition() - leng + 1)
                self.editor.snippetProcessor.render()
                self.setCursorPosition(holder.start + position + 1)
            else:
                holder = self.editor.snippetProcessor.getHolder(cursor.selectionStart(), cursor.selectionEnd())
                if holder is None or holder.last:
                    return self.endSnippet(event)
                QtGui.QPlainTextEdit.keyPressEvent(self.editor, event)
                #Posicion relativa al holder
                position = cursor.position() - holder.start
                #Capture Text
                cursor.setPosition(holder.start)
                cursor.setPosition(holder.end + 1, QtGui.QTextCursor.KeepAnchor)
                holder.setContent(cursor.selectedText())
                #Prepare replace
                self.selectSlice(self.editor.snippetProcessor.startPosition(), self.editor.snippetProcessor.endPosition() + 1)
                self.editor.snippetProcessor.render()
                self.setCursorPosition(holder.start + position)

    def endSnippet(self, event = None):
        self.editor.snippetProcessor.endSnippet()
        if event is not None:
            return self.editor.keyPressEvent(event)

    def setCursorPosition(self, position):
        cursor = self.editor.textCursor()
        cursor.setPosition(position)
        self.editor.setTextCursor(cursor)
        
    def selectSlice(self, start, end):
        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
        self.editor.setTextCursor(cursor)

class PMXMultiCursorEditorMode(PMXBaseEditorMode):
    def __init__(self, editor):
        PMXBaseEditorMode.__init__(self, editor)
        self.cursors = []
        self.scursor = self.dragPoint = self.startPoint = self.doublePoint = None
    
    def isActive(self):
        return bool(self.cursors)
    
    def inactive(self):
        self.cursors = []
        self.editor.modeChanged.emit()
    
    @property
    def isDragCursor(self):
        return self.dragPoint != None
    
    def getDragCursorRect(self):
        """Retorna un rectangulo que representa la zona del drag cursor"""
        return QtCore.QRect(self.startPoint, self.dragPoint)
    
    def mousePressPoint(self, point):
        self.startPoint = point

    def mouseDoubleClickPoint(self, point):
        self.doublePoint = point
        
    def mouseMovePoint(self, point):
        self.dragPoint = point
        self.editor.viewport().repaint(self.editor.viewport().visibleRegion())

    def mouseReleasePoint(self, endPoint):
        _, width, points = self.getPoints(self.startPoint, endPoint)
        
        emit = points and not self.isActive()
        for tupla in points:
            if tupla[0] == tupla[1]:
                cursor = self.editor.cursorForPosition(QtCore.QPoint(*tupla[0]))
                cursor = self.addMergeCursor(cursor)
                #self.editor.document().markContentsDirty(cursor.position(), cursor.position())
                continue
            #Sentido en el que queda el cursor
            if self.startPoint.x() < endPoint.x():  #izquierda a derecha
                start, end = tupla
                cursor = self.editor.cursorForPosition(QtCore.QPoint(*start))
                rect = self.editor.cursorRect(cursor)
                if rect.right() - width / 2 <= start[0] <= rect.right() + width / 2 and rect.top() <= start[1] <= rect.bottom():
                    ecursor = self.editor.cursorForPosition(QtCore.QPoint(*end))
                    rect = self.editor.cursorRect(ecursor)
                    if (rect.right() <= end[0] or rect.right() - width / 2 <= end[0] <= rect.right() + width / 2) and rect.top() <= end[1] <= rect.bottom():
                        cursor.setPosition(ecursor.position(), QtGui.QTextCursor.KeepAnchor)
                        cursor = self.addMergeCursor(cursor)
                    #self.editor.document().markContentsDirty(cursor.position(), ecursor.position())
            else: # Derecha a izquierda
                start, end = tupla
                cursor = self.editor.cursorForPosition(QtCore.QPoint(*start))
                rect = self.editor.cursorRect(cursor)
                if rect.right() - width / 2 <= start[0] <= rect.right() + width / 2 and rect.top() <= start[1] <= rect.bottom():
                    ecursor = self.editor.cursorForPosition(QtCore.QPoint(*end))
                    rect = self.editor.cursorRect(ecursor)
                    if (rect.right() <= end[0] or rect.right() - width / 2 <= end[0] <= rect.right() + width / 2) and rect.top() <= end[1] <= rect.bottom():
                        ecursor.setPosition(cursor.position(), QtGui.QTextCursor.KeepAnchor)
                        ecursor = self.addMergeCursor(ecursor)
                    #self.editor.document().markContentsDirty(cursor.position(), ecursor.position())
        
        if emit:
            #Arranco modo multicursor
            self.editor.modeChanged.emit()
        #Clean last acction
        self.scursor = self.dragPoint = self.startPoint = self.doublePoint = None
        self.editor.viewport().repaint(self.editor.viewport().visibleRegion())

    def getPoints(self, start, end):
        metrics = QtGui.QFontMetrics(self.editor.document().defaultFont())
        hight = metrics.lineSpacing()
        width = metrics.width("x")
        sx, ex = (start.x(), end.x()) if start.x() <= end.x() else (end.x(), start.x())
        sy, ey = (start.y(), end.y()) if start.y() <= end.y() else (end.y(), start.y())
        puntos = [ ( (sx, sy), (ex, sy) ) ]
        p = sy + hight
        e = ey - hight
        while p <= e:
            puntos.append( ( (sx, p), (ex, p) ) )
            p += hight
        puntos.append( ( (sx, ey), (ex, ey) ) )
        return hight, width, puntos
        
    def addMergeCursor(self, cursor):
        '''
            Only can add new cursors, if the cursor has selection then try to merge with others
        '''
        if cursor.hasSelection():
            newCursor = None
            removeCursor = None
            new_begin, new_end = cursor.selectionStart(), cursor.selectionEnd()
            for c in self.cursors:
                c_begin, c_end = c.selectionStart(), c.selectionEnd()
                if c_begin <= new_begin <= new_end <= c_end:
                    return
                elif c_begin <= new_begin <= c_end:
                    # Extiende por detras
                    newCursor = QtGui.QTextCursor(self.editor.document())
                    if c.position() > new_begin:
                        newCursor.setPosition(c_begin)
                        newCursor.setPosition(new_end, QtGui.QTextCursor.KeepAnchor)
                    else:
                        newCursor.setPosition(new_end)
                        newCursor.setPosition(c.position(), QtGui.QTextCursor.KeepAnchor)
                    removeCursor = c
                    break
                elif c_begin <= new_end <= c_end:
                    #Extiende por el frente
                    newCursor = QtGui.QTextCursor(self.editor.document())
                    if c.position() < new_end:
                        newCursor.setPosition(c_end)
                        newCursor.setPosition(new_begin, QtGui.QTextCursor.KeepAnchor)
                    else:
                        newCursor.setPosition(new_begin)
                        newCursor.setPosition(c.position(), QtGui.QTextCursor.KeepAnchor)
                    removeCursor = c
                    break
                elif new_begin <= c_begin <= c_end <= new_end:
                    #Contiene al cursor
                    newCursor = QtGui.QTextCursor(self.editor.document())
                    removeCursor = c
                    break
            if newCursor is not None:
                self.cursors.remove(removeCursor)
                self.addMergeCursor(newCursor)
            else:
                self.editor.setTextCursor(cursor)
                self.cursors.append(cursor)
        else:
            for c in self.cursors:
                begin, end = c.selectionStart(), c.selectionEnd()
                if begin <= cursor.position() <= end:
                    return
            self.editor.setTextCursor(cursor)
            self.cursors.append(cursor)

    def canMoveRight(self):
        return all(map(lambda c: not c.atEnd(), self.cursors))
    
    def canMoveLeft(self):
        return all(map(lambda c: not c.atStart(), self.cursors))
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            #Deprecated usar una lista de cursores ordenados para tomar de [0] y [-1]
            scursor = min(self.cursors, key = lambda cursor: cursor.position())
            ecursor = max(self.cursors, key = lambda cursor: cursor.position())
            self.editor.document().markContentsDirty(scursor.position(), ecursor.position())
            if ecursor.hasSelection():
                ecursor.clearSelection()
            self.editor.setTextCursor(ecursor)
            self.inactive()
            self.editor.highlightCurrentLine()
            #Se termino la joda
        elif event.modifiers() & QtCore.Qt.ControlModifier and event.key() in [ QtCore.Qt.Key_Z]:
            QtGui.QPlainTextEdit.keyPressEvent(self.editor, event)
        elif event.key() == QtCore.Qt.Key_Right:
            if self.canMoveRight():
                if event.modifiers() & QtCore.Qt.ShiftModifier:
                    for cursor in self.cursors:
                        self.editor.document().markContentsDirty(cursor.position(), cursor.position() + 1)
                        cursor.setPosition(cursor.position() + 1, QtGui.QTextCursor.KeepAnchor)
                else:
                    for cursor in self.cursors:
                        self.editor.document().markContentsDirty(cursor.position(), cursor.position() + 1)
                        cursor.setPosition(cursor.position() + 1)
                self.editor.setTextCursor(cursor)
        elif event.key() == QtCore.Qt.Key_Left:
            if self.canMoveLeft():
                if event.modifiers() & QtCore.Qt.ShiftModifier:
                    for cursor in self.cursors:
                        self.editor.document().markContentsDirty(cursor.position(), cursor.position() - 1)
                        cursor.setPosition(cursor.position() - 1, QtGui.QTextCursor.KeepAnchor)
                else:
                    for cursor in self.cursors:
                        self.editor.document().markContentsDirty(cursor.position(), cursor.position() - 1)
                        cursor.setPosition(cursor.position() - 1)
                self.editor.setTextCursor(cursor)
        elif event.key() in [ QtCore.Qt.Key_Up, QtCore.Qt.Key_Down, QtCore.Qt.Key_PageUp, QtCore.Qt.Key_PageDown, QtCore.Qt.Key_End, QtCore.Qt.Key_Home]:
            #Desactivados por ahora
            pass
        elif event.key() in [QtCore.Qt.Key_Insert]:
            self.editor.setOverwriteMode(not self.editor.overwriteMode())
        elif event.text():
            cursor = self.editor.textCursor()
            cursor.beginEditBlock()
            for cursor in self.cursors:
                self.editor.setTextCursor(cursor)
                QtGui.QPlainTextEdit.keyPressEvent(self.editor, event)
            cursor.endEditBlock()
    
    def __iter__(self):
        return iter(self.cursors)
        
class PMXCompleterEditorMode(QtGui.QCompleter, PMXBaseEditorMode):
    def __init__(self, editor):
        QtGui.QCompleter.__init__(self, editor)
        PMXBaseEditorMode.__init__(self, editor)
        self.setWidget(self.editor)
        self.popupView = QtGui.QListView()
        self.popupView.setAlternatingRowColors(True)
        self.popupView.setWordWrap(False)
        self.setPopup(self.popupView)
        self.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.activated[str].connect(self.insertCompletion)
        self.completions = []

    def active(self, event, scope):
        if event.key() == QtCore.Qt.Key_Space and event.modifiers() == QtCore.Qt.ControlModifier:
            preferences = self.editor.getPreference(scope)
            self.completions = preferences.completions

    def isActive(self):
        return self.popup().isVisible()
        
    def inactive(self):
        self.completions = []

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return, QtCore.Qt.Key_Tab, QtCore.Qt.Key_Escape, QtCore.Qt.Key_Backtab):
            self.inactive()
            event.ignore()
        elif self.completions:
            self.editor.showCompleter(self.completions)
        else:
            QtGui.QPlainTextEdit.self.keyPressEvent(self.editor, event)
    
    def insertCompletion(self, insert):
        self.editor.textCursor().insertText(insert[len(self.completionPrefix()):])

    def complete(self, rect):
        self.popup().setCurrentIndex(self.completionModel().index(0, 0))
        rect.setWidth(self.popup().sizeHintForColumn(0) + self.popup().verticalScrollBar().sizeHint().width() + 20)
        QtGui.QCompleter.complete(self, rect)