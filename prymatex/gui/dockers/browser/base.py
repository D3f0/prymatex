#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import os
import codecs
import mimetypes
from subprocess import Popen, PIPE, STDOUT

from prymatex.qt import QtCore, QtGui, QtWebKit
from prymatex.core import PMXBaseDock

from prymatex import resources
from prymatex.qt.helpers import create_menu
from prymatex.ui.dockers.browser import Ui_BrowserDock
from prymatex.core.settings import pmxConfigPorperty
from prymatex.support.utils import prepareShellScript, deleteFile
from .tabwebview import TabbedWebView
from .network import setGlobalApplicationProxy

#=======================================================================
# Browser Dock
#=======================================================================
class BrowserDock(QtGui.QDockWidget, Ui_BrowserDock, PMXBaseDock):
    SHORTCUT = "F9"
    ICON = resources.getIcon("internet-web-browser")
    PREFERED_AREA = QtCore.Qt.BottomDockWidgetArea
    
    # ------------------ Web Settings
    DeveloperExtrasEnabled = 1<<0
    PluginsEnabled = 1<<1
    PrivateBrowsingEnabled = 1<<2
    JavaEnabled = 1<<3
    AutoLoadImages = 1<<4
    JavascriptEnabled = 1<<5
    
    # ----------------- Proxy type
    NoProxy = 1<<0
    SystemProxy = 1<<1
    ManualProxy = 1<<2
    
    # -------------- Settings
    SETTINGS_GROUP = "Browser"
    
    updateInterval = pmxConfigPorperty(default = 3000)
    homePage = pmxConfigPorperty(default = "http://www.prymatex.org")
    
    @pmxConfigPorperty(default = NoProxy)
    def proxyType(self, value):
        if value == self.NoProxy:
            setGlobalApplicationProxy()
        elif value == self.SystemProxy:
            setGlobalApplicationProxy(os.environ.get('http_proxy'))
    
    @pmxConfigPorperty(default = os.environ.get('http_proxy', ''))
    def proxyAddress(self, value):
        if self.proxyType == self.ManualProxy:
            setGlobalApplicationProxy(value)

    @pmxConfigPorperty(default = DeveloperExtrasEnabled | PluginsEnabled | JavascriptEnabled | AutoLoadImages)
    def defaultWebSettings(self, flags):
        QtWebKit.QWebSettings.globalSettings().setAttribute(
            QtWebKit.QWebSettings.DeveloperExtrasEnabled,
            flags & self.DeveloperExtrasEnabled)
        QtWebKit.QWebSettings.globalSettings().setAttribute(
            QtWebKit.QWebSettings.PluginsEnabled,
            flags & self.PluginsEnabled)
        QtWebKit.QWebSettings.globalSettings().setAttribute(
            QtWebKit.QWebSettings.PrivateBrowsingEnabled,
            flags & self.PrivateBrowsingEnabled)
        QtWebKit.QWebSettings.globalSettings().setAttribute(
            QtWebKit.QWebSettings.JavaEnabled,
            flags & self.JavaEnabled)
        QtWebKit.QWebSettings.globalSettings().setAttribute(
            QtWebKit.QWebSettings.AutoLoadImages,
            flags & self.AutoLoadImages)
        QtWebKit.QWebSettings.globalSettings().setAttribute(
            QtWebKit.QWebSettings.JavascriptEnabled,
            flags & self.JavascriptEnabled)

    def __init__(self, parent):
        QtGui.QDockWidget.__init__(self, parent)
        PMXBaseDock.__init__(self)
        self.setupUi(self)
        self.setupToolBar()
        
        # Tab web view
        self.tabWebView = TabbedWebView(self)
        self.tabWebView.currentWebViewChanged.connect(self.on_tabWebView_currentWebViewChanged)
        self.tabWebView.empty.connect(self.on_tabWebView_empty)
        self.verticalLayout.addWidget(self.tabWebView)
        
        #Settings mover a un lugar de configuracion :)
        QtWebKit.QWebSettings.globalSettings().setIconDatabasePath(self.application.currentProfile.value('PMX_TMP_PATH'))

        self.scrollValues = (False, 0, 0)   #(<restore scroll values>, <horizontalValue>, <verticalValue>)
        
        #Capturar editor y webView
        self.currentEditor = None
        
        #Sync Timer
        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(self.updateHtmlCurrentEditorContent)
    
    def initialize(self, mainWindow):
        PMXBaseDock.initialize(self, mainWindow)
        self.on_tabWebView_empty()

    @classmethod
    def contributeToSettings(cls):
        from prymatex.gui.settings.browser import NetworkSettingsWidget
        from prymatex.gui.settings.addons import AddonsSettingsWidgetFactory
        return [ NetworkSettingsWidget, AddonsSettingsWidgetFactory("browser") ]
        
    def setupToolBar(self):
        #Setup Context Menu
        optionsMenu = { 
            "text": "Browser Options",
            "items": [ self.actionSyncEditor, self.actionConnectEditor ]
        }

        self.browserOptionsMenu, _ = create_menu(self, optionsMenu)
        self.toolButtonOptions.setMenu(self.browserOptionsMenu)


    def showEvent(self, event):
        self.setFocus()


    def event(self, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Escape:
                self.close()
                self.mainWindow.currentEditor().setFocus()
                return True
            elif event.key() == QtCore.Qt.Key_L and event.modifiers() == QtCore.Qt.ControlModifier:
                self.lineUrl.setFocus()
                self.lineUrl.selectAll()
                return True
        return QtGui.QDockWidget.event(self, event)

    # -------------------- Browser main methods
    def setHtml(self, string, url = None):
        if not self.isVisible():
            self.show()
        self.raise_()
        self.tabWebView.currentWebView().setHtml(string, url)
    
    def setRunningContext(self, context):
        if not self.isVisible():
            self.show()
        self.raise_()
        self.tabWebView.currentWebView().setRunningContext(context)
    
    
    def on_tabWebView_empty(self):
        webView = self.tabWebView.createWebView()
        #Connect signals
        webView.urlChanged.connect(self.on_webView_urlChanged)
        webView.loadProgress.connect(self.on_webView_loadProgress)
        
        # Set the default home page
        #self.lineUrl.setText(self.homePage)
        webView.setUrl(QtCore.QUrl(self.homePage))
    
    # TabbedWebView signals
    def on_tabWebView_currentWebViewChanged(self, webView):
        history = webView.page().history()
        self.buttonBack.setEnabled(history.canGoBack())
        self.buttonNext.setEnabled(history.canGoForward())
        self.lineUrl.setText(webView.url().toString())
    
    # ------------ Browser Signals handlers
    def on_manager_commandUrlRequested(self, url):
        self.application.handleUrlCommand(url)

    def on_lineUrl_returnPressed(self):
        """Url have been changed by user"""
        webView = self.tabWebView.currentWebView()
        
        history = webView.page().history()
        self.buttonBack.setEnabled(history.canGoBack())
        self.buttonNext.setEnabled(history.canGoForward())

        webView.setUrl(QtCore.QUrl.fromUserInput(self.lineUrl.text()))

    def on_buttonStop_clicked(self):
        """Stop loading the page"""
        self.tabWebView.currentWebView().stop()

    def on_buttonReload_clicked(self):
        """Reload the web page"""
        self.tabWebView.currentWebView().reload()

    def on_buttonBack_clicked(self):
        """Back button clicked, go one page back"""
        page = self.tabWebView.currentWebView().page()
        history = page.history()
        history.back()
        self.buttonBack.setEnabled(history.canGoBack())
    
    def on_buttonNext_clicked(self):
        """Next button clicked, go to next page"""
        page = self.tabWebView.currentWebView().page()
        history = page.history()
        history.forward()
        self.buttonNext.setEnabled(history.canGoForward())
    
    # ----------- QWebView Signals handlers
    def on_webView_linkClicked(self, link):
        #Terminar el timer y navegar hasta esa Url
        #TODO: validar que el link este bien
        self.stopTimer()
        map(lambda action: action.setChecked(False), [ self.actionSyncEditor, self.actionConnectEditor ])
        self.tabWebView.currentWebView().load(link)

    def on_webView_urlChanged(self, url):
        """Update the URL if a link on a web page is clicked"""
        #History
        webView = self.tabWebView.currentWebView()
        history = webView.page().history()
        self.buttonBack.setEnabled(history.canGoBack())
        self.buttonNext.setEnabled(history.canGoForward())
        
        #Line Location
        self.lineUrl.setText(url.toString())
        
    def on_webView_loadProgress(self, load):
        """Page load progress"""
        self.buttonStop.setEnabled(load != 100)
    
    #=======================================================================
    # Browser Auto update for current Editor
    #=======================================================================
    def updateHtmlCurrentEditorContent(self):
        # TODO Resolver url, asegurar que sea html para no hacer cochinadas
        editor = self.currentEditor if self.currentEditor is not None else self.mainWindow.currentEditor()
        content = editor.toPlainText()
        url = QtCore.QUrl.fromUserInput(editor.filePath)
        
        self.tabWebView.currentWebView().settings().clearMemoryCaches()
        
        self.tabWebView.currentWebView().setHtml(content, url)
    
    def stopTimer(self):
        self.updateTimer.stop()
        self.tabWebView.currentWebView().page().setLinkDelegationPolicy(QtWebKit.QWebPage.DontDelegateLinks)

    def startTimer(self):
        self.updateTimer.start(self.updateInterval)
        self.tabWebView.currentWebView().page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)

    def connectCurrentEditor(self):
        self.currentEditor = self.mainWindow.currentEditor()
        self.connect(self.currentEditor, QtCore.SIGNAL("close()"), self.disconnectCurrentEditor)
        
    def disconnectCurrentEditor(self):
        if self.currentEditor is not None:
            self.disconnect(self.currentEditor, QtCore.SIGNAL("close()"), self.disconnectCurrentEditor)
            self.currentEditor = None

    @QtCore.pyqtSlot(bool)
    def on_actionSyncEditor_toggled(self, checked):
        if checked:
            #Quitar otro check
            self.actionConnectEditor.setChecked(False)
            #Desconectar editor
            self.disconnectCurrentEditor()
            self.startTimer()
        else:
            self.stopTimer()

    @QtCore.pyqtSlot(bool)
    def on_actionConnectEditor_toggled(self, checked):
        # TODO Capturar el current editor y usarlo para el update
        if checked:
            #Quitar otro check
            self.actionSyncEditor.setChecked(False)
            #Capturar editor
            self.connectCurrentEditor()
            self.startTimer()
        else:
            self.stopTimer()
            self.disconnectCurrentEditor()
