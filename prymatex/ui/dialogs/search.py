# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/datos/workspace/Prymatex/prymatex/resources/ui/dialogs/search.ui'
#
# Created: Tue May 14 21:59:12 2013
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

class Ui_SearchDialog(object):
    def setupUi(self, SearchDialog):
        SearchDialog.setObjectName(_fromUtf8("SearchDialog"))
        SearchDialog.resize(482, 243)
        SearchDialog.setMinimumSize(QtCore.QSize(482, 0))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/images/prymatex/logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SearchDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(SearchDialog)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(6)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(SearchDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.formLayout = QtGui.QFormLayout(self.groupBox)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.ExpandingFieldsGrow)
        self.formLayout.setMargin(6)
        self.formLayout.setSpacing(2)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label)
        self.comboBoxContainingText = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxContainingText.sizePolicy().hasHeightForWidth())
        self.comboBoxContainingText.setSizePolicy(sizePolicy)
        self.comboBoxContainingText.setEditable(True)
        self.comboBoxContainingText.setObjectName(_fromUtf8("comboBoxContainingText"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.comboBoxContainingText)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.comboBoxFilePatterns = QtGui.QComboBox(self.groupBox)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxFilePatterns.sizePolicy().hasHeightForWidth())
        self.comboBoxFilePatterns.setSizePolicy(sizePolicy)
        self.comboBoxFilePatterns.setEditable(True)
        self.comboBoxFilePatterns.setObjectName(_fromUtf8("comboBoxFilePatterns"))
        self.comboBoxFilePatterns.addItem(_fromUtf8(""))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.comboBoxFilePatterns)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setSpacing(2)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.checkBoxRecursive = QtGui.QCheckBox(self.groupBox)
        self.checkBoxRecursive.setObjectName(_fromUtf8("checkBoxRecursive"))
        self.horizontalLayout_4.addWidget(self.checkBoxRecursive)
        self.checkBoxHidden = QtGui.QCheckBox(self.groupBox)
        self.checkBoxHidden.setObjectName(_fromUtf8("checkBoxHidden"))
        self.horizontalLayout_4.addWidget(self.checkBoxHidden)
        self.checkBoxFollowLinks = QtGui.QCheckBox(self.groupBox)
        self.checkBoxFollowLinks.setObjectName(_fromUtf8("checkBoxFollowLinks"))
        self.horizontalLayout_4.addWidget(self.checkBoxFollowLinks)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.formLayout.setLayout(3, QtGui.QFormLayout.SpanningRole, self.horizontalLayout_4)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(SearchDialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setMargin(6)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.radioButtonWorkspace = QtGui.QRadioButton(self.groupBox_2)
        self.radioButtonWorkspace.setChecked(True)
        self.radioButtonWorkspace.setObjectName(_fromUtf8("radioButtonWorkspace"))
        self.verticalLayout_2.addWidget(self.radioButtonWorkspace)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.radioButtonWorkingSet = QtGui.QRadioButton(self.groupBox_2)
        self.radioButtonWorkingSet.setObjectName(_fromUtf8("radioButtonWorkingSet"))
        self.horizontalLayout.addWidget(self.radioButtonWorkingSet)
        self.comboBoxWorkingSet = QtGui.QComboBox(self.groupBox_2)
        self.comboBoxWorkingSet.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBoxWorkingSet.sizePolicy().hasHeightForWidth())
        self.comboBoxWorkingSet.setSizePolicy(sizePolicy)
        self.comboBoxWorkingSet.setEditable(True)
        self.comboBoxWorkingSet.setObjectName(_fromUtf8("comboBoxWorkingSet"))
        self.horizontalLayout.addWidget(self.comboBoxWorkingSet)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.radioButton = QtGui.QRadioButton(self.groupBox_2)
        self.radioButton.setObjectName(_fromUtf8("radioButton"))
        self.horizontalLayout_3.addWidget(self.radioButton)
        self.lineLocation = QtGui.QLineEdit(self.groupBox_2)
        self.lineLocation.setEnabled(False)
        self.lineLocation.setObjectName(_fromUtf8("lineLocation"))
        self.horizontalLayout_3.addWidget(self.lineLocation)
        self.buttonChoose = QtGui.QPushButton(self.groupBox_2)
        self.buttonChoose.setEnabled(False)
        self.buttonChoose.setObjectName(_fromUtf8("buttonChoose"))
        self.horizontalLayout_3.addWidget(self.buttonChoose)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(2)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.buttonSearch = QtGui.QPushButton(SearchDialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/edit-find.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonSearch.setIcon(icon1)
        self.buttonSearch.setObjectName(_fromUtf8("buttonSearch"))
        self.horizontalLayout_2.addWidget(self.buttonSearch)
        self.buttonCancel = QtGui.QPushButton(SearchDialog)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/dialog-cancel.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonCancel.setIcon(icon2)
        self.buttonCancel.setObjectName(_fromUtf8("buttonCancel"))
        self.horizontalLayout_2.addWidget(self.buttonCancel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.retranslateUi(SearchDialog)
        QtCore.QMetaObject.connectSlotsByName(SearchDialog)

    def retranslateUi(self, SearchDialog):
        SearchDialog.setWindowTitle(_translate("SearchDialog", "Search", None))
        self.groupBox.setTitle(_translate("SearchDialog", "Search", None))
        self.label.setText(_translate("SearchDialog", "Containing text", None))
        self.label_3.setText(_translate("SearchDialog", "File name patterns", None))
        self.comboBoxFilePatterns.setItemText(0, _translate("SearchDialog", "*.*", None))
        self.checkBoxRecursive.setText(_translate("SearchDialog", "Recursive", None))
        self.checkBoxHidden.setText(_translate("SearchDialog", "Hidden", None))
        self.checkBoxFollowLinks.setText(_translate("SearchDialog", "Follow links", None))
        self.groupBox_2.setTitle(_translate("SearchDialog", "Scope", None))
        self.radioButtonWorkspace.setText(_translate("SearchDialog", "Workspace", None))
        self.radioButtonWorkingSet.setText(_translate("SearchDialog", "Working set", None))
        self.radioButton.setText(_translate("SearchDialog", "Location", None))
        self.buttonChoose.setText(_translate("SearchDialog", "Ch&oose", None))
        self.buttonSearch.setText(_translate("SearchDialog", "&Search", None))
        self.buttonCancel.setText(_translate("SearchDialog", "C&ancel", None))

