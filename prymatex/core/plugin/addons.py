#!/usr/bin/env python
#-*- encoding: utf-8 -*-

from PyQt4 import QtCore, QtGui

from prymatex.core.plugin import PMXBaseAddon

#Mover cada addon a su respectivo modulo, addon editor a editor y dock addon a dock

#========================================
# BASE EDITOR ADDON
#========================================
class PMXEditorBaseAddon(PMXBaseAddon):
    def initialize(self, editor):
        PMXBaseAddon.initialize(self, editor)
        self.editor = editor

    def finalize(self):
        pass


#========================================
# BASE DOCKER ADDON
#========================================
class PMXDockBaseAddon(PMXBaseAddon):
    def initialize(self, dock):
        PMXBaseAddon.initialize(self, dock)
        self.dock = dock

    def finalize(self):
        pass
