# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/likewise-open/SUPTRIB/dvanhaaster/Workspace/prymatex/resources/ui/dialogs/spelling.ui'
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

class Ui_SpellingDialog(object):
    def setupUi(self, SpellingDialog):
        SpellingDialog.setObjectName(_fromUtf8("SpellingDialog"))
        SpellingDialog.resize(482, 313)
        SpellingDialog.setMinimumSize(QtCore.QSize(482, 0))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/prymatex/logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SpellingDialog.setWindowIcon(icon)
        self.verticalLayout_2 = QtGui.QVBoxLayout(SpellingDialog)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lineEditNotFound = QtGui.QLineEdit(SpellingDialog)
        self.lineEditNotFound.setObjectName(_fromUtf8("lineEditNotFound"))
        self.gridLayout.addWidget(self.lineEditNotFound, 0, 0, 1, 1)
        self.label = QtGui.QLabel(SpellingDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.pushButtonChange = QtGui.QPushButton(SpellingDialog)
        self.pushButtonChange.setObjectName(_fromUtf8("pushButtonChange"))
        self.gridLayout.addWidget(self.pushButtonChange, 0, 1, 1, 1)
        self.pushButtonFindNext = QtGui.QPushButton(SpellingDialog)
        self.pushButtonFindNext.setObjectName(_fromUtf8("pushButtonFindNext"))
        self.gridLayout.addWidget(self.pushButtonFindNext, 1, 1, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.listWidgetCorrections = QtGui.QListWidget(SpellingDialog)
        self.listWidgetCorrections.setObjectName(_fromUtf8("listWidgetCorrections"))
        self.gridLayout_2.addWidget(self.listWidgetCorrections, 0, 0, 1, 1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButtonIgnore = QtGui.QPushButton(SpellingDialog)
        self.pushButtonIgnore.setObjectName(_fromUtf8("pushButtonIgnore"))
        self.verticalLayout.addWidget(self.pushButtonIgnore)
        self.pushButtonLearn = QtGui.QPushButton(SpellingDialog)
        self.pushButtonLearn.setObjectName(_fromUtf8("pushButtonLearn"))
        self.verticalLayout.addWidget(self.pushButtonLearn)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.verticalLayout, 0, 1, 1, 1)
        self.comboBoxDictionary = QtGui.QComboBox(SpellingDialog)
        self.comboBoxDictionary.setObjectName(_fromUtf8("comboBoxDictionary"))
        self.gridLayout_2.addWidget(self.comboBoxDictionary, 1, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout_2)

        self.retranslateUi(SpellingDialog)
        QtCore.QMetaObject.connectSlotsByName(SpellingDialog)

    def retranslateUi(self, SpellingDialog):
        SpellingDialog.setWindowTitle(QtGui.QApplication.translate("SpellingDialog", "Spelling", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SpellingDialog", "This word was not found in the spelling dictionary.", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonChange.setText(QtGui.QApplication.translate("SpellingDialog", "Change", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonFindNext.setText(QtGui.QApplication.translate("SpellingDialog", "Find Next", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonIgnore.setText(QtGui.QApplication.translate("SpellingDialog", "Ignore", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonLearn.setText(QtGui.QApplication.translate("SpellingDialog", "Learn", None, QtGui.QApplication.UnicodeUTF8))

