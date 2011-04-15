# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_files/network.ui'
#
# Created: Sat Apr  9 13:42:47 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Network(object):
    def setupUi(self, Network):
        Network.setObjectName("Network")
        Network.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/actions/resources/actions/document-open-remote.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Network.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(Network)
        self.verticalLayout.setObjectName("verticalLayout")
        self.comboProxyType = QtGui.QComboBox(Network)
        self.comboProxyType.setObjectName("comboProxyType")
        self.comboProxyType.addItem("")
        self.comboProxyType.addItem("")
        self.comboProxyType.addItem("")
        self.comboProxyType.addItem("")
        self.verticalLayout.addWidget(self.comboProxyType)
        self.groupBox_2 = QtGui.QGroupBox(Network)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label = QtGui.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.lineProxyAddress = QtGui.QLineEdit(self.groupBox_2)
        self.lineProxyAddress.setObjectName("lineProxyAddress")
        self.gridLayout_2.addWidget(self.lineProxyAddress, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineProxyPort = QtGui.QLineEdit(self.groupBox_2)
        self.lineProxyPort.setObjectName("lineProxyPort")
        self.gridLayout_2.addWidget(self.lineProxyPort, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.label_5 = QtGui.QLabel(Network)
        self.label_5.setText("")
        self.label_5.setObjectName("label_5")
        self.verticalLayout.addWidget(self.label_5)
        self.checkBox = QtGui.QCheckBox(Network)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout.addWidget(self.checkBox)
        self.groupBox = QtGui.QGroupBox(Network)
        self.groupBox.setEnabled(False)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.lineProxyUsername = QtGui.QLineEdit(self.groupBox)
        self.lineProxyUsername.setEnabled(False)
        self.lineProxyUsername.setObjectName("lineProxyUsername")
        self.gridLayout.addWidget(self.lineProxyUsername, 0, 1, 2, 1)
        self.label_3 = QtGui.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 2, 1)
        self.lineProxyPassword = QtGui.QLineEdit(self.groupBox)
        self.lineProxyPassword.setEnabled(False)
        self.lineProxyPassword.setObjectName("lineProxyPassword")
        self.gridLayout.addWidget(self.lineProxyPassword, 2, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.pushButton = QtGui.QPushButton(Network)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Network)
        QtCore.QObject.connect(self.groupBox, QtCore.SIGNAL("toggled(bool)"), self.groupBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(Network)

    def retranslateUi(self, Network):
        Network.setWindowTitle(QtGui.QApplication.translate("Network", "Network Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.comboProxyType.setItemText(0, QtGui.QApplication.translate("Network", "No Proxy", None, QtGui.QApplication.UnicodeUTF8))
        self.comboProxyType.setItemText(1, QtGui.QApplication.translate("Network", "Based on Enviroment variables", None, QtGui.QApplication.UnicodeUTF8))
        self.comboProxyType.setItemText(2, QtGui.QApplication.translate("Network", "HTTP Proxy", None, QtGui.QApplication.UnicodeUTF8))
        self.comboProxyType.setItemText(3, QtGui.QApplication.translate("Network", "Socks Proxy", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Network", "Proxy host", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Network", "Address", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Network", "Port", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setText(QtGui.QApplication.translate("Network", "Rrequires authentication", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Network", "Authentication", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("Network", "Username", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Network", "Password", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Network", "Test settings", None, QtGui.QApplication.UnicodeUTF8))

import res_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Network = QtGui.QWidget()
    ui = Ui_Network()
    ui.setupUi(Network)
    Network.show()
    sys.exit(app.exec_())
