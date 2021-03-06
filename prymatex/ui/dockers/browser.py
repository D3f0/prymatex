# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/likewise-open/SUPTRIB/dvanhaaster/Workspace/prymatex/resources/ui/dockers/browser.ui'
#
# Created: Tue Jul 30 11:12:00 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_BrowserDock(object):
    def setupUi(self, BrowserDock):
        BrowserDock.setObjectName(_fromUtf8("BrowserDock"))
        BrowserDock.resize(520, 54)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.buttonBack = QtGui.QPushButton(self.dockWidgetContents)
        self.buttonBack.setMaximumSize(QtCore.QSize(24, 24))
        self.buttonBack.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-previous"))
        self.buttonBack.setIcon(icon)
        self.buttonBack.setFlat(True)
        self.buttonBack.setObjectName(_fromUtf8("buttonBack"))
        self.horizontalLayout.addWidget(self.buttonBack)
        self.buttonNext = QtGui.QPushButton(self.dockWidgetContents)
        self.buttonNext.setEnabled(True)
        self.buttonNext.setMaximumSize(QtCore.QSize(24, 24))
        self.buttonNext.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.buttonNext.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-next"))
        self.buttonNext.setIcon(icon)
        self.buttonNext.setFlat(True)
        self.buttonNext.setObjectName(_fromUtf8("buttonNext"))
        self.horizontalLayout.addWidget(self.buttonNext)
        self.buttonReload = QtGui.QPushButton(self.dockWidgetContents)
        self.buttonReload.setMaximumSize(QtCore.QSize(24, 24))
        self.buttonReload.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("view-refresh"))
        self.buttonReload.setIcon(icon)
        self.buttonReload.setFlat(True)
        self.buttonReload.setObjectName(_fromUtf8("buttonReload"))
        self.horizontalLayout.addWidget(self.buttonReload)
        self.lineUrl = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineUrl.setObjectName(_fromUtf8("lineUrl"))
        self.horizontalLayout.addWidget(self.lineUrl)
        self.buttonStop = QtGui.QPushButton(self.dockWidgetContents)
        self.buttonStop.setMaximumSize(QtCore.QSize(24, 24))
        self.buttonStop.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("dialog-close"))
        self.buttonStop.setIcon(icon)
        self.buttonStop.setFlat(True)
        self.buttonStop.setObjectName(_fromUtf8("buttonStop"))
        self.horizontalLayout.addWidget(self.buttonStop)
        self.line = QtGui.QFrame(self.dockWidgetContents)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.toolButtonOptions = QtGui.QToolButton(self.dockWidgetContents)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("configure"))
        self.toolButtonOptions.setIcon(icon)
        self.toolButtonOptions.setPopupMode(QtGui.QToolButton.MenuButtonPopup)
        self.toolButtonOptions.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolButtonOptions.setAutoRaise(True)
        self.toolButtonOptions.setArrowType(QtCore.Qt.NoArrow)
        self.toolButtonOptions.setObjectName(_fromUtf8("toolButtonOptions"))
        self.horizontalLayout.addWidget(self.toolButtonOptions)
        self.verticalLayout.addLayout(self.horizontalLayout)
        BrowserDock.setWidget(self.dockWidgetContents)
        self.actionSyncEditor = QtGui.QAction(BrowserDock)
        self.actionSyncEditor.setCheckable(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/system-switch-user.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSyncEditor.setIcon(icon)
        self.actionSyncEditor.setObjectName(_fromUtf8("actionSyncEditor"))
        self.actionConnectEditor = QtGui.QAction(BrowserDock)
        self.actionConnectEditor.setCheckable(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/network-connect.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionConnectEditor.setIcon(icon1)
        self.actionConnectEditor.setObjectName(_fromUtf8("actionConnectEditor"))

        self.retranslateUi(BrowserDock)
        QtCore.QMetaObject.connectSlotsByName(BrowserDock)

    def retranslateUi(self, BrowserDock):
        BrowserDock.setWindowTitle(QtGui.QApplication.translate("BrowserDock", "Web Browser", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonBack.setToolTip(QtGui.QApplication.translate("BrowserDock", "Back", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonNext.setToolTip(QtGui.QApplication.translate("BrowserDock", "Next", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonReload.setToolTip(QtGui.QApplication.translate("BrowserDock", "Reload", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonStop.setToolTip(QtGui.QApplication.translate("BrowserDock", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSyncEditor.setText(QtGui.QApplication.translate("BrowserDock", "Sync Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSyncEditor.setToolTip(QtGui.QApplication.translate("BrowserDock", "Sync browser with current editor content", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConnectEditor.setText(QtGui.QApplication.translate("BrowserDock", "Connect Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.actionConnectEditor.setToolTip(QtGui.QApplication.translate("BrowserDock", "Connect browser with current editor", None, QtGui.QApplication.UnicodeUTF8))

