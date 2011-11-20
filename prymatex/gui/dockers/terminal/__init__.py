from prymatex.gui.dockers.base import PMXBaseDock

# TODO: Better implementation is coming :) 
from frontend import TerminalWidget 
from PyQt4 import QtGui
from prymatex.core.base import PMXObject
from prymatex.gui.dockers.terminal.tabterm import TabbedTerminal


class PMXTerminalWidget(QtGui.QDockWidget, PMXObject, PMXBaseDock):
    '''
    PyQt4 Terminal Widget (pyqtermwidget)
    by Henning Schröder (https://bitbucket.org/henning/pyqtermwidget)
    '''
    def __init__(self, parent = None):
        QtGui.QDockWidget.__init__(self, )
        PMXObject.__init__(self)
        self.setWindowTitle("Terminal")
        layout = QtGui.QVBoxLayout()
        term = TabbedTerminal(self)
        layout.addWidget(term)