# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/datos/workspace/Prymatex/prymatex/resources/ui/configure/resource.ui'
#
# Created: Wed May 22 20:00:31 2013
#      by: PyQt4 UI code generator snapshot-4.10.2-6f54723ef2ba
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_ResouceWidget(object):
    def setupUi(self, ResouceWidget):
        ResouceWidget.setObjectName(_fromUtf8("ResouceWidget"))
        ResouceWidget.resize(574, 392)
        self.verticalLayout = QtGui.QVBoxLayout(ResouceWidget)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setSpacing(2)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.labelPath = QtGui.QLabel(ResouceWidget)
        self.labelPath.setObjectName(_fromUtf8("labelPath"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.labelPath)
        self.labelType = QtGui.QLabel(ResouceWidget)
        self.labelType.setObjectName(_fromUtf8("labelType"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.labelType)
        self.labelLocation = QtGui.QLabel(ResouceWidget)
        self.labelLocation.setObjectName(_fromUtf8("labelLocation"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.labelLocation)
        self.labelLastModified = QtGui.QLabel(ResouceWidget)
        self.labelLastModified.setObjectName(_fromUtf8("labelLastModified"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.labelLastModified)
        self.textLabelPath = QtGui.QLabel(ResouceWidget)
        self.textLabelPath.setText(_fromUtf8(""))
        self.textLabelPath.setObjectName(_fromUtf8("textLabelPath"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.textLabelPath)
        self.textLabelType = QtGui.QLabel(ResouceWidget)
        self.textLabelType.setText(_fromUtf8(""))
        self.textLabelType.setObjectName(_fromUtf8("textLabelType"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.textLabelType)
        self.textLabelLocation = QtGui.QLabel(ResouceWidget)
        self.textLabelLocation.setText(_fromUtf8(""))
        self.textLabelLocation.setObjectName(_fromUtf8("textLabelLocation"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.textLabelLocation)
        self.textLabelLastModified = QtGui.QLabel(ResouceWidget)
        self.textLabelLastModified.setText(_fromUtf8(""))
        self.textLabelLastModified.setObjectName(_fromUtf8("textLabelLastModified"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.FieldRole, self.textLabelLastModified)
        self.labelSize = QtGui.QLabel(ResouceWidget)
        self.labelSize.setObjectName(_fromUtf8("labelSize"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.labelSize)
        self.textLabelSize = QtGui.QLabel(ResouceWidget)
        self.textLabelSize.setText(_fromUtf8(""))
        self.textLabelSize.setObjectName(_fromUtf8("textLabelSize"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.textLabelSize)
        self.verticalLayout.addLayout(self.formLayout)
        self.line = QtGui.QFrame(ResouceWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout.addWidget(self.line)
        self.groupBox_3 = QtGui.QGroupBox(ResouceWidget)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.tableWidgetPermissions = QtGui.QTableWidget(self.groupBox_3)
        self.tableWidgetPermissions.setObjectName(_fromUtf8("tableWidgetPermissions"))
        self.tableWidgetPermissions.setColumnCount(3)
        self.tableWidgetPermissions.setRowCount(3)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetPermissions.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetPermissions.setVerticalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetPermissions.setVerticalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetPermissions.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetPermissions.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidgetPermissions.setHorizontalHeaderItem(2, item)
        item = QtGui.QTableWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidgetPermissions.setItem(0, 0, item)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidgetPermissions.setItem(0, 1, item)
        item = QtGui.QTableWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidgetPermissions.setItem(0, 2, item)
        item = QtGui.QTableWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidgetPermissions.setItem(1, 0, item)
        item = QtGui.QTableWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidgetPermissions.setItem(1, 1, item)
        item = QtGui.QTableWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidgetPermissions.setItem(1, 2, item)
        item = QtGui.QTableWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidgetPermissions.setItem(2, 0, item)
        item = QtGui.QTableWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidgetPermissions.setItem(2, 1, item)
        item = QtGui.QTableWidgetItem()
        item.setCheckState(QtCore.Qt.Checked)
        self.tableWidgetPermissions.setItem(2, 2, item)
        self.verticalLayout_2.addWidget(self.tableWidgetPermissions)
        self.label = QtGui.QLabel(self.groupBox_3)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox = QtGui.QGroupBox(ResouceWidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout_2 = QtGui.QFormLayout(self.groupBox)
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout_2.setMargin(6)
        self.formLayout_2.setSpacing(2)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.radioButton = QtGui.QRadioButton(self.groupBox)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.SpanningRole, self.radioButton)
        self.radioButton_2 = QtGui.QRadioButton(self.groupBox)
        self.radioButton_2.setObjectName(_fromUtf8("radioButton_2"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.radioButton_2)
        self.comboBoxEncoding = QtGui.QComboBox(self.groupBox)
        self.comboBoxEncoding.setEnabled(False)
        self.comboBoxEncoding.setObjectName(_fromUtf8("comboBoxEncoding"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.comboBoxEncoding)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(ResouceWidget)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.formLayout_3 = QtGui.QFormLayout(self.groupBox_2)
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout_3.setMargin(6)
        self.formLayout_3.setSpacing(2)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.comboBoxEndOfLine_2 = QtGui.QComboBox(self.groupBox_2)
        self.comboBoxEndOfLine_2.setEnabled(False)
        self.comboBoxEndOfLine_2.setObjectName(_fromUtf8("comboBoxEndOfLine_2"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.FieldRole, self.comboBoxEndOfLine_2)
        self.radioButton_4 = QtGui.QRadioButton(self.groupBox_2)
        self.radioButton_4.setObjectName(_fromUtf8("radioButton_4"))
        self.formLayout_3.setWidget(1, QtGui.QFormLayout.LabelRole, self.radioButton_4)
        self.radioButton_3 = QtGui.QRadioButton(self.groupBox_2)
        self.radioButton_3.setChecked(True)
        self.radioButton_3.setObjectName(_fromUtf8("radioButton_3"))
        self.formLayout_3.setWidget(0, QtGui.QFormLayout.SpanningRole, self.radioButton_3)
        self.verticalLayout.addWidget(self.groupBox_2)
        spacerItem = QtGui.QSpacerItem(20, 30, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(ResouceWidget)
        QtCore.QMetaObject.connectSlotsByName(ResouceWidget)

    def retranslateUi(self, ResouceWidget):
        ResouceWidget.setWindowTitle(_translate("ResouceWidget", "Resource", None))
        self.labelPath.setText(_translate("ResouceWidget", "Path:", None))
        self.labelType.setText(_translate("ResouceWidget", "Type:", None))
        self.labelLocation.setText(_translate("ResouceWidget", "Location:", None))
        self.labelLastModified.setText(_translate("ResouceWidget", "Last modified:", None))
        self.labelSize.setText(_translate("ResouceWidget", "Size:", None))
        self.groupBox_3.setTitle(_translate("ResouceWidget", "Permissions", None))
        item = self.tableWidgetPermissions.verticalHeaderItem(0)
        item.setText(_translate("ResouceWidget", "Owner", None))
        item = self.tableWidgetPermissions.verticalHeaderItem(1)
        item.setText(_translate("ResouceWidget", "Group", None))
        item = self.tableWidgetPermissions.verticalHeaderItem(2)
        item.setText(_translate("ResouceWidget", "Other", None))
        item = self.tableWidgetPermissions.horizontalHeaderItem(0)
        item.setText(_translate("ResouceWidget", "Read", None))
        item = self.tableWidgetPermissions.horizontalHeaderItem(1)
        item.setText(_translate("ResouceWidget", "Write", None))
        item = self.tableWidgetPermissions.horizontalHeaderItem(2)
        item.setText(_translate("ResouceWidget", "Execute", None))
        __sortingEnabled = self.tableWidgetPermissions.isSortingEnabled()
        self.tableWidgetPermissions.setSortingEnabled(False)
        self.tableWidgetPermissions.setSortingEnabled(__sortingEnabled)
        self.label.setText(_translate("ResouceWidget", "<html><head/><body><p><span style=\" font-weight:600;\">Note:</span> Removing de executable flag on a folder will cause its children to become unreadable</p></body></html>", None))
        self.groupBox.setTitle(_translate("ResouceWidget", "Text file encoding", None))
        self.radioButton.setText(_translate("ResouceWidget", "Inherited", None))
        self.radioButton_2.setText(_translate("ResouceWidget", "Other:", None))
        self.groupBox_2.setTitle(_translate("ResouceWidget", "Text file end of line", None))
        self.radioButton_4.setText(_translate("ResouceWidget", "Other", None))
        self.radioButton_3.setText(_translate("ResouceWidget", "Inherited", None))

