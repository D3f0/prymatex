#!/usr/bin/env python
# -*- coding: utf-8 -*-

from prymatex.core.components.base import PrymatexComponentWidget

# TODO: separar estos dialogos de los que se pueden generar desde el servidor remoto?
class PrymatexDialog(PrymatexComponentWidget):
    def __init__(self, **kwargs):
        super(PrymatexDialog, self).__init__(**kwargs)
        
    def initialize(self, parent = None, **kwargs):
        super(PrymatexDialog, self).initialize(**kwargs)
        self.mainWindow = parent
        
    def setParameters(self, parameters):
        pass

    def waitForInput(self, callback):
        pass
    
    def execModal(self):
        pass
        
PMXBaseDialog = PrymatexDialog