#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.qt import QtGui
from prymatex.support.processor import PMXCommandProcessor

class PMXCommandProcessor(PMXCommandProcessor):
    def __init__(self, editor):
        super(PMXCommandProcessor, self).__init__()
        self.editor = editor

    def startCommand(self, command):
        self.command = command
        self.__env = None

    def endCommand(self, command):
        self.command = None
        
    def environmentVariables(self):
        if self.__env is None:
            # TODO No es mejor que tambien el editor saque de la mainwindow para 
            # preservar la composision?
            self.__env = {}
            envs = [ self.command.environmentVariables(),
                self.editor.mainWindow.environmentVariables(),
                self.editor.environmentVariables(),
                self.baseEnvironment ]
            for env in envs:
                self.__env.update(env)
        return self.__env
        
    def configure(self, settings):
        # TODO El cursor :)
        self.asynchronous = settings.get("asynchronous", True)
        self.tabTriggered = settings.get("tabTriggered", False)
        self.disableIndent = settings.get("disableIndent", False)
        self.baseEnvironment = settings.get("environment", {})
        self.errorCommand = settings.get("errorCommand", False)

    def formatAsXml(self, text, firstBlock, lastBlock, startIndex, endIndex):
        result = []
        block = firstBlock
        for line in text.splitlines(True):
            userData = self.editor.blockUserData(block) 
            if block == firstBlock and block == lastBlock:
                ranges = userData.ranges(start = startIndex, end = endIndex)
            elif block == firstBlock:
                ranges = userData.ranges(start = startIndex)
            elif block == lastBlock:
                ranges = userData.ranges(end = endIndex)
            else:
                ranges = userData.ranges()
            lineXML = ""
            start = ranges.pop(0)
            token = userData.tokenAtPosition(start)
            for index in ranges:
                lineXML += token.scope.to_xml(line[start:index])
                token = userData.tokenAtPosition(index)
                start = index
            # TODO Ver si esta bien esto del replace
            result.append(lineXML.replace('\n', ''))
            if block == lastBlock:
                break
            block = block.next()
        return "\n".join(result)

    # --------------------- Inputs
    def document(self, inputFormat = None):
        text = self.editor.document().toPlainText()
        if inputFormat == "xml":
            firstBlock = self.editor.document().firstBlock()
            lastBlock = self.editor.document().lastBlock()
            return self.formatAsXml(text, firstBlock, lastBlock, firstBlock.position(), lastBlock.position() + lastBlock.length())
        else:
            return text
        
    def line(self, inputFormat = None):
        return self.editor.textCursor().block().text()
        
    def character(self, inputFormat = None):
        cursor = self.editor.textCursor()
        return cursor.document().characterAt(cursor.position())
        
    def scope(self, inputFormat = None):
        cursor = self.editor.textCursor()
        block = cursor.block()
        token = self.editor.blockUserData(block).tokenAtPosition(
            cursor.positionInBlock())
        return token.chunk

    def selection(self, inputFormat = None):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = self.editor.selectedTextWithEol(cursor)
            if inputFormat == "xml":
                firstBlock, lastBlock = self.editor.selectionBlockStartEnd()
                return self.formatAsXml(text, firstBlock, lastBlock, cursor.selectionStart() - firstBlock.position(), cursor.selectionEnd() - lastBlock.position())
            else:
                return text
        
    def selectedText(self, inputFormat = None):
        return self.selection(inputFormat)

    def word(self, inputFormat = None):
        word, start, end = self.editor.currentWord()
        return word

    # ----------------- Before Running Command
    def saveModifiedFiles(self):
        ret = True
        for editor in self.editor.mainWindow.editors():
            if editor.isModified():
                self.editor.mainWindow.saveEditor(editor = editor)
                ret = ret and not editor.isModified()
            if ret == False:
                break
        return ret
    
    def saveActiveFile(self):
        self.editor.mainWindow.saveEditor(editor = self.editor)
        return not (self.editor.isModified() or self.editor.isNew())
    
    # ----------------- Delete From Editor
    def deleteWord(self):
        _, start, end = self.editor.currentWord()
        cursor = self.editor.textCursor()
        cursor.setPosition(start)
        cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        
    def deleteSelection(self):
        cursor = self.editor.textCursor()
        cursor.removeSelectedText()

    def deleteLine(self):
        cursor = self.editor.textCursor()
        block = cursor.block()
        cursor.setPosition(block.position())
        cursor.setPosition(block.position() + block.length() - 1, QtGui.QTextCursor.KeepAnchor)
        cursor.removeSelectedText()
        
    def deleteCharacter(self):
        cursor = self.editor.textCursor()
        cursor.deleteChar()
    
    def deleteDocument(self):
        self.editor.document().clear()
       
    # ------------------- Outpus function
    def error(self, context, outputFormat = None):
        if self.errorCommand:
            raise Exception(context.errorValue)
        else:
            self.editor.mainWindow.showErrorInBrowser(
                context.description(),
                context.errorValue,
                context.outputType,
                errorCommand = True
            )

    def discard(self, context, outputFormat = None):
        pass
        
    def replaceSelectedText(self, context, outputFormat = None):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            position = cursor.selectionStart()
            cursor.insertText(context.outputValue)
            cursor.setPosition(position, position + len(context.outputValue))
        else:
            cursor.insertText(context.outputValue)
        self.editor.setTextCursor(cursor)
        
    def replaceDocument(self, context, outputFormat = None):
        self.editor.updatePlainText(context.outputValue)
        
    def replaceSelection(self, context, outputFormat = None):
        print("replaceSelection")

    # ------------ Version 2
    def replaceInput(self, context, outputFormat = None):
        if outputFormat == "text":
            self.editor.textCursor().insertText(context.outputValue)
        elif outputFormat == "html":
            self.editor.textCursor().appendHtml(context.outputValue)
        elif outputFormat == "snippet":
            self.insertAsSnippet(context)

    def insertText(self, context, outputFormat = None):
        cursor = self.editor.textCursor()
        cursor.insertText(context.outputValue)
    
    def atCaret(self, context, outputFormat = None):
        print("atCaret")

    def afterInput(self, context, outputFormat = None):
        print("afterInput")

    def afterSelectedText(self, context, outputFormat = None):
        cursor = self.editor.textCursor()
        cursor.setPosition(cursor.selectionEnd())
        cursor.insertText(context.outputValue)
        
    def insertAsSnippet(self, context, outputFormat = None):
        snippet = self.editor.application.supportManager.buildAdHocSnippet(context.outputValue, context.bundleItem.bundle, tabTrigger = context.bundleItem.tabTrigger)
        self.editor.insertBundleItem(snippet, tabTriggered = self.tabTriggered, disableIndent = self.disableIndent)
            
    def showAsHTML(self, context, outputFormat = None):
        self.editor.browserDock.setRunningContext(context)

    def showAsTooltip(self, context, outputFormat = None):
        message = context.outputValue.strip()
        timeout = len(message) * 20
        if timeout > 2000:
            timeout = 2000
        
        point = self.editor.cursorRect(self.editor.textCursor()).bottomRight()
        point = self.editor.mapToGlobal(point)
        callbacks = {
            'copy': lambda s = message: QtGui.qApp.instance().clipboard().setText(s)
        }
        
        self.editor.mainWindow.showMessage(message, 
            frmt = outputFormat or "text", timeout = timeout, point = point,
            linkMap = callbacks)
        
    def toolTip(self, context, outputFormat = None):
        self.showAsTooltip(context, outputFormat)

    def createNewDocument(self, context, outputFormat = None):
        editor= self.editor.mainWindow.addEmptyEditor()
        editor.setPlainText(context.outputValue)
        
    def newWindow(self, context, outputFormat = None):
        if outputFormat == "html":
            self.editor.browserDock.newRunningContext(context)
        elif outputFormat == "text":
            # TODO: Quiza una mejor forma de crear documentos con texto
            editor = self.editor.mainWindow.addEmptyEditor()
            editor.setPlainText(context.outputValue)

    def openAsNewDocument(self, context, outputFormat = None):
        editor = self.editor.mainWindow.addEmptyEditor()
        editor.setPlainText(context.outputValue)
