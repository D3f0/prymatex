# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/likewise-open/SUPTRIB/dvanhaaster/Workspace/prymatex/resources/ui/configure/filters.ui'
#
# Created: Fri Jun 28 09:26:37 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_FiltersWidget(object):
    def setupUi(self, FiltersWidget):
        FiltersWidget.setObjectName(_fromUtf8("FiltersWidget"))
        FiltersWidget.resize(400, 300)
        self.horizontalLayout = QtGui.QHBoxLayout(FiltersWidget)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.listViewFilters = QtGui.QListView(FiltersWidget)
        self.listViewFilters.setObjectName(_fromUtf8("listViewFilters"))
        self.horizontalLayout.addWidget(self.listViewFilters)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.pushButtonAdd = QtGui.QPushButton(FiltersWidget)
        self.pushButtonAdd.setObjectName(_fromUtf8("pushButtonAdd"))
        self.verticalLayout.addWidget(self.pushButtonAdd)
        self.pushButtonEdit = QtGui.QPushButton(FiltersWidget)
        self.pushButtonEdit.setObjectName(_fromUtf8("pushButtonEdit"))
        self.verticalLayout.addWidget(self.pushButtonEdit)
        self.pushButtonRemove = QtGui.QPushButton(FiltersWidget)
        self.pushButtonRemove.setObjectName(_fromUtf8("pushButtonRemove"))
        self.verticalLayout.addWidget(self.pushButtonRemove)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(FiltersWidget)
        QtCore.QMetaObject.connectSlotsByName(FiltersWidget)

    def retranslateUi(self, FiltersWidget):
        FiltersWidget.setWindowTitle(QtGui.QApplication.translate("FiltersWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonAdd.setText(QtGui.QApplication.translate("FiltersWidget", "Add", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonEdit.setText(QtGui.QApplication.translate("FiltersWidget", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonRemove.setText(QtGui.QApplication.translate("FiltersWidget", "Remove", None, QtGui.QApplication.UnicodeUTF8))
