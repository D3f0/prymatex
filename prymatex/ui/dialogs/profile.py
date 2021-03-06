# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/likewise-open/SUPTRIB/dvanhaaster/Workspace/prymatex/resources/ui/dialogs/profile.ui'
#
# Created: Tue Jul 30 11:11:59 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ProfileDialog(object):
    def setupUi(self, ProfileDialog):
        ProfileDialog.setObjectName(_fromUtf8("ProfileDialog"))
        ProfileDialog.resize(400, 250)
        ProfileDialog.setMinimumSize(QtCore.QSize(400, 0))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/prymatex/logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ProfileDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(ProfileDialog)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(ProfileDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.buttonCreate = QtGui.QPushButton(ProfileDialog)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("list-add-user"))
        self.buttonCreate.setIcon(icon)
        self.buttonCreate.setObjectName(_fromUtf8("buttonCreate"))
        self.verticalLayout_2.addWidget(self.buttonCreate)
        self.buttonRename = QtGui.QPushButton(ProfileDialog)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("user-properties"))
        self.buttonRename.setIcon(icon)
        self.buttonRename.setObjectName(_fromUtf8("buttonRename"))
        self.verticalLayout_2.addWidget(self.buttonRename)
        self.buttonDelete = QtGui.QPushButton(ProfileDialog)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("list-remove-user"))
        self.buttonDelete.setIcon(icon)
        self.buttonDelete.setObjectName(_fromUtf8("buttonDelete"))
        self.verticalLayout_2.addWidget(self.buttonDelete)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setSpacing(2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.listViewProfiles = QtGui.QListView(ProfileDialog)
        self.listViewProfiles.setObjectName(_fromUtf8("listViewProfiles"))
        self.verticalLayout_3.addWidget(self.listViewProfiles)
        self.checkDontAsk = QtGui.QCheckBox(ProfileDialog)
        self.checkDontAsk.setObjectName(_fromUtf8("checkDontAsk"))
        self.verticalLayout_3.addWidget(self.checkDontAsk)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.buttonExit = QtGui.QPushButton(ProfileDialog)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("application-exit"))
        self.buttonExit.setIcon(icon)
        self.buttonExit.setObjectName(_fromUtf8("buttonExit"))
        self.horizontalLayout_2.addWidget(self.buttonExit)
        self.buttonStartPrymatex = QtGui.QPushButton(ProfileDialog)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("system-run"))
        self.buttonStartPrymatex.setIcon(icon)
        self.buttonStartPrymatex.setObjectName(_fromUtf8("buttonStartPrymatex"))
        self.horizontalLayout_2.addWidget(self.buttonStartPrymatex)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(ProfileDialog)
        QtCore.QMetaObject.connectSlotsByName(ProfileDialog)

    def retranslateUi(self, ProfileDialog):
        ProfileDialog.setWindowTitle(QtGui.QApplication.translate("ProfileDialog", "Prymatex Choose User Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ProfileDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Sans Serif\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Prymatex stores information about your settings, preferences and other items in your user profile.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonCreate.setText(QtGui.QApplication.translate("ProfileDialog", "&Create Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonRename.setText(QtGui.QApplication.translate("ProfileDialog", "&Rename Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonDelete.setText(QtGui.QApplication.translate("ProfileDialog", "&Delete Profile", None, QtGui.QApplication.UnicodeUTF8))
        self.checkDontAsk.setText(QtGui.QApplication.translate("ProfileDialog", "Don\'t a&sk at startup", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonExit.setText(QtGui.QApplication.translate("ProfileDialog", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonStartPrymatex.setText(QtGui.QApplication.translate("ProfileDialog", "Start Prymatex", None, QtGui.QApplication.UnicodeUTF8))

