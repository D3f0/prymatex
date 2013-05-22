# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/datos/workspace/Prymatex/prymatex/resources/ui/mainwindow.ui'
#
# Created: Wed May 22 20:00:13 2013
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(801, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitTabWidget = SplitTabWidget(self.centralwidget)
        self.splitTabWidget.setObjectName(_fromUtf8("splitTabWidget"))
        self.verticalLayout.addWidget(self.splitTabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 801, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuRecentFiles = QtGui.QMenu(self.menuFile)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/document-open-recent.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuRecentFiles.setIcon(icon)
        self.menuRecentFiles.setObjectName(_fromUtf8("menuRecentFiles"))
        self.menuNew = QtGui.QMenu(self.menuFile)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/actions/document-new.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.menuNew.setIcon(icon1)
        self.menuNew.setObjectName(_fromUtf8("menuNew"))
        self.menuView = QtGui.QMenu(self.menubar)
        self.menuView.setObjectName(_fromUtf8("menuView"))
        self.menuPanels = QtGui.QMenu(self.menuView)
        self.menuPanels.setObjectName(_fromUtf8("menuPanels"))
        self.menuNavigation = QtGui.QMenu(self.menubar)
        self.menuNavigation.setObjectName(_fromUtf8("menuNavigation"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName(_fromUtf8("menuEdit"))
        self.menuBundles = QtGui.QMenu(self.menubar)
        self.menuBundles.setObjectName(_fromUtf8("menuBundles"))
        self.menuBundleEditor = QtGui.QMenu(self.menuBundles)
        self.menuBundleEditor.setObjectName(_fromUtf8("menuBundleEditor"))
        self.menuPreferences = QtGui.QMenu(self.menubar)
        self.menuPreferences.setObjectName(_fromUtf8("menuPreferences"))
        MainWindow.setMenuBar(self.menubar)
        self.actionNewEditor = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("tab-new"))
        self.actionNewEditor.setIcon(icon)
        self.actionNewEditor.setObjectName(_fromUtf8("actionNewEditor"))
        self.actionOpen = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-open"))
        self.actionOpen.setIcon(icon)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.actionSave = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-save"))
        self.actionSave.setIcon(icon)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionSaveAs = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-save-as"))
        self.actionSaveAs.setIcon(icon)
        self.actionSaveAs.setObjectName(_fromUtf8("actionSaveAs"))
        self.actionSaveAll = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-save-all"))
        self.actionSaveAll.setIcon(icon)
        self.actionSaveAll.setObjectName(_fromUtf8("actionSaveAll"))
        self.actionClose = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("tab-close"))
        self.actionClose.setIcon(icon)
        self.actionClose.setObjectName(_fromUtf8("actionClose"))
        self.actionCloseOthers = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("tab-close-other"))
        self.actionCloseOthers.setIcon(icon)
        self.actionCloseOthers.setObjectName(_fromUtf8("actionCloseOthers"))
        self.actionQuit = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("application-exit"))
        self.actionQuit.setIcon(icon)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionUndo = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-undo"))
        self.actionUndo.setIcon(icon)
        self.actionUndo.setObjectName(_fromUtf8("actionUndo"))
        self.actionRedo = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-redo"))
        self.actionRedo.setIcon(icon)
        self.actionRedo.setObjectName(_fromUtf8("actionRedo"))
        self.actionCopy = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-copy"))
        self.actionCopy.setIcon(icon)
        self.actionCopy.setObjectName(_fromUtf8("actionCopy"))
        self.actionCut = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-cut"))
        self.actionCut.setIcon(icon)
        self.actionCut.setObjectName(_fromUtf8("actionCut"))
        self.actionPaste = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-paste"))
        self.actionPaste.setIcon(icon)
        self.actionPaste.setObjectName(_fromUtf8("actionPaste"))
        self.actionSettings = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("configure"))
        self.actionSettings.setIcon(icon)
        self.actionSettings.setObjectName(_fromUtf8("actionSettings"))
        self.actionFullscreen = QtGui.QAction(MainWindow)
        self.actionFullscreen.setCheckable(True)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("view-fullscreen"))
        self.actionFullscreen.setIcon(icon)
        self.actionFullscreen.setObjectName(_fromUtf8("actionFullscreen"))
        self.actionShowMenus = QtGui.QAction(MainWindow)
        self.actionShowMenus.setCheckable(True)
        self.actionShowMenus.setObjectName(_fromUtf8("actionShowMenus"))
        self.actionNextTab = QtGui.QAction(MainWindow)
        self.actionNextTab.setObjectName(_fromUtf8("actionNextTab"))
        self.actionPreviousTab = QtGui.QAction(MainWindow)
        self.actionPreviousTab.setObjectName(_fromUtf8("actionPreviousTab"))
        self.actionReportBug = QtGui.QAction(MainWindow)
        self.actionReportBug.setObjectName(_fromUtf8("actionReportBug"))
        self.actionTranslatePrymatex = QtGui.QAction(MainWindow)
        self.actionTranslatePrymatex.setObjectName(_fromUtf8("actionTranslatePrymatex"))
        self.actionProjectHomepage = QtGui.QAction(MainWindow)
        self.actionProjectHomepage.setObjectName(_fromUtf8("actionProjectHomepage"))
        self.actionTakeScreenshot = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("ksnapshot"))
        self.actionTakeScreenshot.setIcon(icon)
        self.actionTakeScreenshot.setObjectName(_fromUtf8("actionTakeScreenshot"))
        self.actionAbout = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("help-about"))
        self.actionAbout.setIcon(icon)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionAboutQt = QtGui.QAction(MainWindow)
        self.actionAboutQt.setObjectName(_fromUtf8("actionAboutQt"))
        self.actionNewFromTemplate = QtGui.QAction(MainWindow)
        self.actionNewFromTemplate.setEnabled(True)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-new"))
        self.actionNewFromTemplate.setIcon(icon)
        self.actionNewFromTemplate.setObjectName(_fromUtf8("actionNewFromTemplate"))
        self.actionReadDocumentation = QtGui.QAction(MainWindow)
        self.actionReadDocumentation.setObjectName(_fromUtf8("actionReadDocumentation"))
        self.actionCloseAll = QtGui.QAction(MainWindow)
        self.actionCloseAll.setObjectName(_fromUtf8("actionCloseAll"))
        self.actionShowStatus = QtGui.QAction(MainWindow)
        self.actionShowStatus.setCheckable(True)
        self.actionShowStatus.setObjectName(_fromUtf8("actionShowStatus"))
        self.actionOpenAllRecentFiles = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("document-open-recent"))
        self.actionOpenAllRecentFiles.setIcon(icon)
        self.actionOpenAllRecentFiles.setObjectName(_fromUtf8("actionOpenAllRecentFiles"))
        self.actionRemoveAllRecentFiles = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-clear"))
        self.actionRemoveAllRecentFiles.setIcon(icon)
        self.actionRemoveAllRecentFiles.setObjectName(_fromUtf8("actionRemoveAllRecentFiles"))
        self.actionShowBundleEditor = QtGui.QAction(MainWindow)
        self.actionShowBundleEditor.setObjectName(_fromUtf8("actionShowBundleEditor"))
        self.actionEditCommands = QtGui.QAction(MainWindow)
        self.actionEditCommands.setObjectName(_fromUtf8("actionEditCommands"))
        self.actionEditLanguages = QtGui.QAction(MainWindow)
        self.actionEditLanguages.setObjectName(_fromUtf8("actionEditLanguages"))
        self.actionEditSnippets = QtGui.QAction(MainWindow)
        self.actionEditSnippets.setObjectName(_fromUtf8("actionEditSnippets"))
        self.actionReloadBundles = QtGui.QAction(MainWindow)
        self.actionReloadBundles.setObjectName(_fromUtf8("actionReloadBundles"))
        self.actionSelectTab = QtGui.QAction(MainWindow)
        self.actionSelectTab.setObjectName(_fromUtf8("actionSelectTab"))
        self.actionNewProject = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("project-development-new-template"))
        self.actionNewProject.setIcon(icon)
        self.actionNewProject.setObjectName(_fromUtf8("actionNewProject"))
        self.actionDelete = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("edit-delete"))
        self.actionDelete.setIcon(icon)
        self.actionDelete.setObjectName(_fromUtf8("actionDelete"))
        self.actionSwitchProfile = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("system-switch-user"))
        self.actionSwitchProfile.setIcon(icon)
        self.actionSwitchProfile.setObjectName(_fromUtf8("actionSwitchProfile"))
        self.actionImportProject = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("project-open"))
        self.actionImportProject.setIcon(icon)
        self.actionImportProject.setObjectName(_fromUtf8("actionImportProject"))
        self.actionLastEditLocation = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-first-view"))
        self.actionLastEditLocation.setIcon(icon)
        self.actionLastEditLocation.setObjectName(_fromUtf8("actionLastEditLocation"))
        self.actionLocationBack = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-previous-view"))
        self.actionLocationBack.setIcon(icon)
        self.actionLocationBack.setObjectName(_fromUtf8("actionLocationBack"))
        self.actionLocationForward = QtGui.QAction(MainWindow)
        icon = QtGui.QIcon.fromTheme(_fromUtf8("go-next-view"))
        self.actionLocationForward.setIcon(icon)
        self.actionLocationForward.setObjectName(_fromUtf8("actionLocationForward"))
        self.actionJumpToTabWindow = QtGui.QAction(MainWindow)
        self.actionJumpToTabWindow.setObjectName(_fromUtf8("actionJumpToTabWindow"))
        self.menuRecentFiles.addAction(self.actionOpenAllRecentFiles)
        self.menuRecentFiles.addAction(self.actionRemoveAllRecentFiles)
        self.menuNew.addAction(self.actionNewEditor)
        self.menuNew.addSeparator()
        self.menuNew.addAction(self.actionNewFromTemplate)
        self.menuNew.addAction(self.actionNewProject)
        self.menuFile.addAction(self.menuNew.menuAction())
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.menuRecentFiles.menuAction())
        self.menuFile.addAction(self.actionImportProject)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionSaveAll)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addAction(self.actionCloseAll)
        self.menuFile.addAction(self.actionCloseOthers)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSwitchProfile)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuView.addAction(self.menuPanels.menuAction())
        self.menuNavigation.addAction(self.actionNextTab)
        self.menuNavigation.addAction(self.actionPreviousTab)
        self.menuNavigation.addAction(self.actionSelectTab)
        self.menuNavigation.addAction(self.actionJumpToTabWindow)
        self.menuNavigation.addSeparator()
        self.menuNavigation.addAction(self.actionLastEditLocation)
        self.menuNavigation.addAction(self.actionLocationBack)
        self.menuNavigation.addAction(self.actionLocationForward)
        self.menuHelp.addAction(self.actionReportBug)
        self.menuHelp.addAction(self.actionTranslatePrymatex)
        self.menuHelp.addAction(self.actionProjectHomepage)
        self.menuHelp.addAction(self.actionReadDocumentation)
        self.menuHelp.addSeparator()
        self.menuHelp.addAction(self.actionTakeScreenshot)
        self.menuHelp.addAction(self.actionAboutQt)
        self.menuHelp.addAction(self.actionAbout)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addAction(self.actionDelete)
        self.menuBundleEditor.addAction(self.actionShowBundleEditor)
        self.menuBundleEditor.addSeparator()
        self.menuBundleEditor.addAction(self.actionEditCommands)
        self.menuBundleEditor.addAction(self.actionEditLanguages)
        self.menuBundleEditor.addAction(self.actionEditSnippets)
        self.menuBundleEditor.addSeparator()
        self.menuBundleEditor.addAction(self.actionReloadBundles)
        self.menuBundles.addAction(self.menuBundleEditor.menuAction())
        self.menuBundles.addSeparator()
        self.menuPreferences.addAction(self.actionShowMenus)
        self.menuPreferences.addAction(self.actionShowStatus)
        self.menuPreferences.addSeparator()
        self.menuPreferences.addAction(self.actionFullscreen)
        self.menuPreferences.addSeparator()
        self.menuPreferences.addAction(self.actionSettings)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuNavigation.menuAction())
        self.menubar.addAction(self.menuBundles.menuAction())
        self.menubar.addAction(self.menuPreferences.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        self.menuFile.setTitle(_translate("MainWindow", "&File", None))
        self.menuRecentFiles.setTitle(_translate("MainWindow", "&Recent Files", None))
        self.menuNew.setTitle(_translate("MainWindow", "New", None))
        self.menuView.setTitle(_translate("MainWindow", "&View", None))
        self.menuPanels.setTitle(_translate("MainWindow", "Panels", None))
        self.menuNavigation.setTitle(_translate("MainWindow", "&Navigation", None))
        self.menuHelp.setTitle(_translate("MainWindow", "&Help", None))
        self.menuEdit.setTitle(_translate("MainWindow", "&Edit", None))
        self.menuBundles.setTitle(_translate("MainWindow", "&Bundles", None))
        self.menuBundleEditor.setTitle(_translate("MainWindow", "Bundle &Editor", None))
        self.menuPreferences.setTitle(_translate("MainWindow", "&Preferences", None))
        self.actionNewEditor.setText(_translate("MainWindow", "&Editor", None))
        self.actionNewEditor.setShortcut(_translate("MainWindow", "Ctrl+N", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))
        self.actionOpen.setShortcut(_translate("MainWindow", "Ctrl+O", None))
        self.actionSave.setText(_translate("MainWindow", "Save", None))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S", None))
        self.actionSaveAs.setText(_translate("MainWindow", "Save As", None))
        self.actionSaveAs.setShortcut(_translate("MainWindow", "Ctrl+Shift+S", None))
        self.actionSaveAll.setText(_translate("MainWindow", "Save All", None))
        self.actionSaveAll.setShortcut(_translate("MainWindow", "Ctrl+Alt+S", None))
        self.actionClose.setText(_translate("MainWindow", "Close", None))
        self.actionClose.setShortcut(_translate("MainWindow", "Ctrl+W", None))
        self.actionCloseOthers.setText(_translate("MainWindow", "Close Others", None))
        self.actionCloseOthers.setShortcut(_translate("MainWindow", "Ctrl+Alt+W", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))
        self.actionUndo.setText(_translate("MainWindow", "&Undo", None))
        self.actionRedo.setText(_translate("MainWindow", "&Redo", None))
        self.actionCopy.setText(_translate("MainWindow", "&Copy", None))
        self.actionCopy.setToolTip(_translate("MainWindow", "Copy", None))
        self.actionCut.setText(_translate("MainWindow", "Cu&t", None))
        self.actionCut.setToolTip(_translate("MainWindow", "Cut", None))
        self.actionPaste.setText(_translate("MainWindow", "&Paste", None))
        self.actionPaste.setToolTip(_translate("MainWindow", "Paste", None))
        self.actionSettings.setText(_translate("MainWindow", "Settings", None))
        self.actionSettings.setShortcut(_translate("MainWindow", "Alt+P", None))
        self.actionFullscreen.setText(_translate("MainWindow", "Fullscreen", None))
        self.actionFullscreen.setShortcut(_translate("MainWindow", "F11", None))
        self.actionShowMenus.setText(_translate("MainWindow", "Show Menus", None))
        self.actionShowMenus.setShortcut(_translate("MainWindow", "Ctrl+M", None))
        self.actionNextTab.setText(_translate("MainWindow", "N&ext Tab", None))
        self.actionNextTab.setShortcut(_translate("MainWindow", "Ctrl+PgDown", None))
        self.actionPreviousTab.setText(_translate("MainWindow", "P&revious Tab", None))
        self.actionPreviousTab.setShortcut(_translate("MainWindow", "Ctrl+PgUp", None))
        self.actionReportBug.setText(_translate("MainWindow", "Report &Bug", None))
        self.actionTranslatePrymatex.setText(_translate("MainWindow", "&Translate Prymatex", None))
        self.actionProjectHomepage.setText(_translate("MainWindow", "Project &Homepage", None))
        self.actionTakeScreenshot.setText(_translate("MainWindow", "Take &Screenshot", None))
        self.actionAbout.setText(_translate("MainWindow", "&About...", None))
        self.actionAboutQt.setText(_translate("MainWindow", "About &Qt", None))
        self.actionNewFromTemplate.setText(_translate("MainWindow", "From Template", None))
        self.actionNewFromTemplate.setToolTip(_translate("MainWindow", "From Template", None))
        self.actionNewFromTemplate.setShortcut(_translate("MainWindow", "Ctrl+Shift+N", None))
        self.actionReadDocumentation.setText(_translate("MainWindow", "Read &Documentation", None))
        self.actionCloseAll.setText(_translate("MainWindow", "Close All", None))
        self.actionShowStatus.setText(_translate("MainWindow", "Show Status", None))
        self.actionOpenAllRecentFiles.setText(_translate("MainWindow", "Open All Recent Files", None))
        self.actionRemoveAllRecentFiles.setText(_translate("MainWindow", "Remove All Recent Files", None))
        self.actionShowBundleEditor.setText(_translate("MainWindow", "Show Bundle &Editor", None))
        self.actionShowBundleEditor.setShortcut(_translate("MainWindow", "Meta+Ctrl+Alt+B", None))
        self.actionEditCommands.setText(_translate("MainWindow", "Edit &Commands", None))
        self.actionEditCommands.setShortcut(_translate("MainWindow", "Meta+Ctrl+Alt+C", None))
        self.actionEditLanguages.setText(_translate("MainWindow", "Edit &Languages", None))
        self.actionEditLanguages.setShortcut(_translate("MainWindow", "Meta+Ctrl+Alt+L", None))
        self.actionEditSnippets.setText(_translate("MainWindow", "Edit &Snippets", None))
        self.actionEditSnippets.setShortcut(_translate("MainWindow", "Meta+Ctrl+Alt+S", None))
        self.actionReloadBundles.setText(_translate("MainWindow", "Reload &Bundles", None))
        self.actionSelectTab.setText(_translate("MainWindow", "&Select Tab", None))
        self.actionSelectTab.setShortcut(_translate("MainWindow", "Ctrl+E", None))
        self.actionNewProject.setText(_translate("MainWindow", "Project", None))
        self.actionNewProject.setShortcut(_translate("MainWindow", "Ctrl+Alt+N", None))
        self.actionDelete.setText(_translate("MainWindow", "Delete", None))
        self.actionSwitchProfile.setText(_translate("MainWindow", "Switch Profile", None))
        self.actionImportProject.setText(_translate("MainWindow", "Import Project", None))
        self.actionLastEditLocation.setText(_translate("MainWindow", "Last Edit Location", None))
        self.actionLastEditLocation.setShortcut(_translate("MainWindow", "Ctrl+Q", None))
        self.actionLocationBack.setText(_translate("MainWindow", "Back", None))
        self.actionLocationBack.setShortcut(_translate("MainWindow", "Alt+Left", None))
        self.actionLocationForward.setText(_translate("MainWindow", "Forward", None))
        self.actionLocationForward.setShortcut(_translate("MainWindow", "Alt+Right", None))
        self.actionJumpToTabWindow.setText(_translate("MainWindow", "Jump To Tab Window", None))
        self.actionJumpToTabWindow.setShortcut(_translate("MainWindow", "F12", None))

from prymatex.widgets.splitter import SplitTabWidget
