# encoding: utf-8

"""This module contains the main window status bar definition and widgets."""

from prymatex.qt import QtGui

class PrymatexMainStatusBar(QtGui.QStatusBar):
    def __init__(self, mainWindow):
        QtGui.QStatusBar.__init__(self, mainWindow)
        mainWindow.currentEditorChanged.connect(self.on_currentEditorChanged)
        self.statusBars = []

    def addPermanentWidget(self, widget):
        self.statusBars.append(widget)
        QtGui.QStatusBar.addPermanentWidget(self, widget, 1)

    def on_currentEditorChanged(self, editor):
        for bar in self.statusBars:
            bar.setCurrentEditor(editor)
            bar.setVisible(bar.acceptEditor(editor))
        self.show()
