#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from PyQt4 import QtGui, QtCore

from prymatex import resources
from prymatex.ui.configure.support import Ui_Support
from prymatex.gui.settings.models import PMXSettingTreeNode
from prymatex.utils.i18n import ugettext as _

class PMXSupportSettings(QtGui.QWidget, PMXSettingTreeNode, Ui_Support):
    ICON = resources.getIcon('gear')
    TITLE = "Support"
    def __init__(self, settingGroup, parent = None):
        QtGui.QWidget.__init__(self, parent)
        PMXSettingTreeNode.__init__(self, "support", settingGroup)
        self.setupUi(self)