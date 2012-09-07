# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources/ui/dockers/projects.ui'
#
# Created: Fri Sep  7 14:19:37 2012
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from prymatex.utils.i18n import ugettext as _
from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ProjectsDock(object):
    def setupUi(self, ProjectsDock):
        ProjectsDock.setObjectName(_fromUtf8("ProjectsDock"))
        ProjectsDock.resize(330, 484)
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.buttonsLayout = QtGui.QHBoxLayout()
        self.buttonsLayout.setSpacing(2)
        self.buttonsLayout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        self.buttonsLayout.setObjectName(_fromUtf8("buttonsLayout"))
        spacerItem = QtGui.QSpacerItem(10, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.buttonsLayout.addItem(spacerItem)
        self.pushButtonSync = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButtonSync.setMaximumSize(QtCore.QSize(24, 24))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("folder-sync"))
        self.pushButtonSync.setIcon(icon)
        self.pushButtonSync.setCheckable(True)
        self.pushButtonSync.setFlat(True)
        self.pushButtonSync.setObjectName(_fromUtf8("pushButtonSync"))
        self.buttonsLayout.addWidget(self.pushButtonSync)
        self.pushButtonCollapseAll = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButtonCollapseAll.setMaximumSize(QtCore.QSize(24, 24))
        self.pushButtonCollapseAll.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("view-list-tree"))
        self.pushButtonCollapseAll.setIcon(icon)
        self.pushButtonCollapseAll.setFlat(True)
        self.pushButtonCollapseAll.setObjectName(_fromUtf8("pushButtonCollapseAll"))
        self.buttonsLayout.addWidget(self.pushButtonCollapseAll)
        self.pushButtonCustomFilters = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButtonCustomFilters.setMaximumSize(QtCore.QSize(24, 24))
        self.pushButtonCustomFilters.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("view-filter"))
        self.pushButtonCustomFilters.setIcon(icon)
        self.pushButtonCustomFilters.setFlat(True)
        self.pushButtonCustomFilters.setObjectName(_fromUtf8("pushButtonCustomFilters"))
        self.buttonsLayout.addWidget(self.pushButtonCustomFilters)
        self.pushButtonOptions = QtGui.QPushButton(self.dockWidgetContents)
        self.pushButtonOptions.setMaximumSize(QtCore.QSize(45, 24))
        self.pushButtonOptions.setText(_fromUtf8(""))
        icon = QtGui.QIcon.fromTheme(_fromUtf8("configure"))
        self.pushButtonOptions.setIcon(icon)
        self.pushButtonOptions.setFlat(True)
        self.pushButtonOptions.setObjectName(_fromUtf8("pushButtonOptions"))
        self.buttonsLayout.addWidget(self.pushButtonOptions)
        self.verticalLayout.addLayout(self.buttonsLayout)
        self.treeViewProjects = QtGui.QTreeView(self.dockWidgetContents)
        self.treeViewProjects.setUniformRowHeights(True)
        self.treeViewProjects.setHeaderHidden(True)
        self.treeViewProjects.setObjectName(_fromUtf8("treeViewProjects"))
        self.verticalLayout.addWidget(self.treeViewProjects)
        ProjectsDock.setWidget(self.dockWidgetContents)
        self.actionNewFile = QtGui.QAction(ProjectsDock)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/document-new.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewFile.setIcon(icon)
        self.actionNewFile.setObjectName(_fromUtf8("actionNewFile"))
        self.actionNewFolder = QtGui.QAction(ProjectsDock)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/folder-new.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewFolder.setIcon(icon1)
        self.actionNewFolder.setObjectName(_fromUtf8("actionNewFolder"))
        self.actionNewFromTemplate = QtGui.QAction(ProjectsDock)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/run-build-file.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewFromTemplate.setIcon(icon2)
        self.actionNewFromTemplate.setObjectName(_fromUtf8("actionNewFromTemplate"))
        self.actionDelete = QtGui.QAction(ProjectsDock)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/edit-delete.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDelete.setIcon(icon3)
        self.actionDelete.setObjectName(_fromUtf8("actionDelete"))
        self.actionNewProject = QtGui.QAction(ProjectsDock)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/project-development-new-template.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNewProject.setIcon(icon4)
        self.actionNewProject.setObjectName(_fromUtf8("actionNewProject"))
        self.actionCloseProject = QtGui.QAction(ProjectsDock)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/project-development-close.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCloseProject.setIcon(icon5)
        self.actionCloseProject.setObjectName(_fromUtf8("actionCloseProject"))
        self.actionOpenProject = QtGui.QAction(ProjectsDock)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/project-open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpenProject.setIcon(icon6)
        self.actionOpenProject.setObjectName(_fromUtf8("actionOpenProject"))
        self.actionProperties = QtGui.QAction(ProjectsDock)
        self.actionProperties.setObjectName(_fromUtf8("actionProperties"))
        self.actionRefresh = QtGui.QAction(ProjectsDock)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/view-refresh.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRefresh.setIcon(icon7)
        self.actionRefresh.setObjectName(_fromUtf8("actionRefresh"))
        self.actionOpen = QtGui.QAction(ProjectsDock)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/document-open.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen.setIcon(icon8)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionOpenSystemEditor = QtGui.QAction(ProjectsDock)
        self.actionOpenSystemEditor.setObjectName(_fromUtf8("actionOpenSystemEditor"))
        self.actionRename = QtGui.QAction(ProjectsDock)
        icon9 = QtGui.QIcon()
        icon9.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/edit-rename.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionRename.setIcon(icon9)
        self.actionRename.setObjectName(_fromUtf8("actionRename"))
        self.actionOrderByName = QtGui.QAction(ProjectsDock)
        self.actionOrderByName.setCheckable(True)
        self.actionOrderByName.setObjectName(_fromUtf8("actionOrderByName"))
        self.actionOrderBySize = QtGui.QAction(ProjectsDock)
        self.actionOrderBySize.setCheckable(True)
        self.actionOrderBySize.setObjectName(_fromUtf8("actionOrderBySize"))
        self.actionOrderByDate = QtGui.QAction(ProjectsDock)
        self.actionOrderByDate.setCheckable(True)
        self.actionOrderByDate.setObjectName(_fromUtf8("actionOrderByDate"))
        self.actionOrderByType = QtGui.QAction(ProjectsDock)
        self.actionOrderByType.setCheckable(True)
        self.actionOrderByType.setObjectName(_fromUtf8("actionOrderByType"))
        self.actionOrderDescending = QtGui.QAction(ProjectsDock)
        self.actionOrderDescending.setCheckable(True)
        self.actionOrderDescending.setObjectName(_fromUtf8("actionOrderDescending"))
        self.actionOrderFoldersFirst = QtGui.QAction(ProjectsDock)
        self.actionOrderFoldersFirst.setCheckable(True)
        self.actionOrderFoldersFirst.setObjectName(_fromUtf8("actionOrderFoldersFirst"))
        self.actionSetInTerminal = QtGui.QAction(ProjectsDock)
        icon10 = QtGui.QIcon()
        icon10.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/apps/utilities-terminal.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSetInTerminal.setIcon(icon10)
        self.actionSetInTerminal.setObjectName(_fromUtf8("actionSetInTerminal"))
        self.actionRemove = QtGui.QAction(ProjectsDock)
        self.actionRemove.setObjectName(_fromUtf8("actionRemove"))
        self.actionBundleEditor = QtGui.QAction(ProjectsDock)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/bundles/bundle.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionBundleEditor.setIcon(icon11)
        self.actionBundleEditor.setObjectName(_fromUtf8("actionBundleEditor"))
        self.actionBashInit = QtGui.QAction(ProjectsDock)
        self.actionBashInit.setObjectName(_fromUtf8("actionBashInit"))
        self.actionCopy = QtGui.QAction(ProjectsDock)
        icon12 = QtGui.QIcon()
        icon12.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/edit-copy.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCopy.setIcon(icon12)
        self.actionCopy.setObjectName(_fromUtf8("actionCopy"))
        self.actionCut = QtGui.QAction(ProjectsDock)
        icon13 = QtGui.QIcon()
        icon13.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/edit-cut.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionCut.setIcon(icon13)
        self.actionCut.setObjectName(_fromUtf8("actionCut"))
        self.actionPaste = QtGui.QAction(ProjectsDock)
        icon14 = QtGui.QIcon()
        icon14.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/edit-paste.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPaste.setIcon(icon14)
        self.actionPaste.setObjectName(_fromUtf8("actionPaste"))

        self.retranslateUi(ProjectsDock)
        QtCore.QMetaObject.connectSlotsByName(ProjectsDock)

    def retranslateUi(self, ProjectsDock):
        ProjectsDock.setWindowTitle(_('Projects'))
        self.pushButtonSync.setToolTip(_('Sync folder with current editor file path'))
        self.actionNewFile.setText(_('File'))
        self.actionNewFolder.setText(_('Folder'))
        self.actionNewFromTemplate.setText(_('File From Template'))
        self.actionNewFromTemplate.setToolTip(_('File From Template'))
        self.actionDelete.setText(_('Delete'))
        self.actionNewProject.setText(_('Project'))
        self.actionCloseProject.setText(_('Close'))
        self.actionOpenProject.setText(_('Open'))
        self.actionProperties.setText(_('Properties'))
        self.actionRefresh.setText(_('Refresh'))
        self.actionRefresh.setShortcut(_('F5'))
        self.actionOpen.setText(_('Open'))
        self.actionOpenSystemEditor.setText(_('System Editor'))
        self.actionRename.setText(_('Rename'))
        self.actionRename.setToolTip(_('Rename'))
        self.actionRename.setShortcut(_('F2'))
        self.actionOrderByName.setText(_('By Name'))
        self.actionOrderBySize.setText(_('By Size'))
        self.actionOrderByDate.setText(_('By Date'))
        self.actionOrderByType.setText(_('By Type'))
        self.actionOrderDescending.setText(_('Descending'))
        self.actionOrderFoldersFirst.setText(_('Folders First'))
        self.actionSetInTerminal.setText(_('Set In Terminal'))
        self.actionRemove.setText(_('Remove'))
        self.actionBundleEditor.setText(_('Bundle Editor'))
        self.actionBashInit.setText(_('Bash Init'))
        self.actionCopy.setText(_('&Copy'))
        self.actionCopy.setShortcut(_('Ctrl+C'))
        self.actionCut.setText(_('Cu&t'))
        self.actionCut.setShortcut(_('Ctrl+X'))
        self.actionPaste.setText(_('&Paste'))
        self.actionPaste.setShortcut(_('Ctrl+V'))

