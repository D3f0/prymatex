# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/likewise-open/SUPTRIB/dvanhaaster/Workspace/prymatex/resources/ui/configure/mainwindow.ui'
#
# Created: Fri Jun 28 09:26:36 2013
#      by: PyQt4 UI code generator 4.9.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(451, 333)
        self.verticalLayout = QtGui.QVBoxLayout(MainWindow)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox_2 = QtGui.QGroupBox(MainWindow)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox_2)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout_2.setMargin(6)
        self.formLayout_2.setSpacing(2)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.comboBoxTabTemplate = QtGui.QComboBox(self.groupBox_2)
        self.comboBoxTabTemplate.setEditable(True)
        self.comboBoxTabTemplate.setObjectName(_fromUtf8("comboBoxTabTemplate"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.comboBoxTabTemplate)
        self.labelTabVisibility = QtGui.QLabel(self.groupBox_2)
        self.labelTabVisibility.setObjectName(_fromUtf8("labelTabVisibility"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.LabelRole, self.labelTabVisibility)
        self.comboBoxTabVisibility = QtGui.QComboBox(self.groupBox_2)
        self.comboBoxTabVisibility.setObjectName(_fromUtf8("comboBoxTabVisibility"))
        self.formLayout_2.setWidget(3, QtGui.QFormLayout.FieldRole, self.comboBoxTabVisibility)
        self.verticalLayout.addWidget(self.groupBox_2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "General", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("MainWindow", "Interface", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Title template:", None, QtGui.QApplication.UnicodeUTF8))
        self.labelTabVisibility.setText(QtGui.QApplication.translate("MainWindow", "Tab visibilty:", None, QtGui.QApplication.UnicodeUTF8))
