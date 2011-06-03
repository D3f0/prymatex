# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui

from prymatex.core.base import PMXObject
from prymatex.gui.bundles.ui_editor import Ui_bundleEditor
from prymatex.gui.bundles.models import PMXBundleTreeProxyModel, PMXBundleTreeModel
from prymatex.gui.bundles.widgets import PMXSnippetWidget, PMXCommandWidget, PMXDragCommandWidget
from prymatex.gui.bundles.widgets import PMXBundleWidget,PMXTemplateFileWidget, PMXTemplateWidget
from prymatex.gui.bundles.widgets import PMXPreferenceWidget, PMXLanguageWidget, PMXEditorBaseWidget

class PMXBundleEditor(Ui_bundleEditor, QtGui.QWidget, PMXObject):
    '''
        Prymatex Bundle Editor
    '''
    def __init__(self, manager = None):
        super(PMXBundleEditor, self).__init__()
        self.setupUi(self)
        self.configEditorWidgets()
        self.configSelectTop()
        self.configTreeView(manager)
        self.configActivation()

    def selectTopChange(self, index):
        value = self.comboBoxItemFilter.itemData(index).toString()
        self.proxyTreeModel.setFilterRegExp(value)
        
    def configSelectTop(self):
        self.comboBoxItemFilter.addItem("Show all", QtCore.QVariant(""))
        self.comboBoxItemFilter.addItem("Syntaxs", QtCore.QVariant("syntax"))
        self.comboBoxItemFilter.addItem("Snippets", QtCore.QVariant("snippet"))
        self.comboBoxItemFilter.addItem("Macros", QtCore.QVariant("macro"))
        self.comboBoxItemFilter.addItem("Commands", QtCore.QVariant("command"))
        self.comboBoxItemFilter.addItem("DragCommands", QtCore.QVariant("dragcommand"))
        self.comboBoxItemFilter.addItem("Preferences", QtCore.QVariant("preference"))
        self.comboBoxItemFilter.addItem("Templates", QtCore.QVariant("template*"))
        self.comboBoxItemFilter.currentIndexChanged[int].connect(self.selectTopChange)
        
    def configTreeView(self, manager = None):
        if manager is None:
            self.treeModel = self.pmxApp.supportManager.bundleTreeModel
        else:
            self.treeModel = PMXBundleTreeModel(manager)
            self.treeModel.populateFromManager()
        self.proxyTreeModel = PMXBundleTreeProxyModel()
        self.proxyTreeModel.setSourceModel(self.treeModel)
        self.proxyTreeModel.sort(0)
        self.treeView.setModel(self.proxyTreeModel)
        self.treeView.setHeaderHidden(True)
        self.treeView.setAnimated(True)
        self.treeView.activated.connect(self.treeViewItemActivated)
        
    def configEditorWidgets(self):
        self.stackLayout = QtGui.QStackedLayout()
        self.container.setLayout(self.stackLayout)
        self.indexes = {}
        self.editors = [ PMXSnippetWidget(),
                         PMXCommandWidget(),
                         PMXDragCommandWidget(),
                         PMXBundleWidget(),
                         PMXTemplateFileWidget(),
                         PMXTemplateWidget(),
                         PMXPreferenceWidget(),
                         PMXLanguageWidget(),
                         PMXEditorBaseWidget() ]
        for editor in self.editors:
            self.indexes[editor.TYPE] = self.stackLayout.addWidget(editor)
        self.noneWidgetIndex = len(self.editors)
        #self.stackLayout.currentChanged.connect(self.currentEditorWidgetChanged)
        self.stackLayout.setCurrentIndex(self.noneWidgetIndex)
    
    def configActivation(self):
        self.comboBoxActivation.addItem("Key Equivalent", QtCore.QVariant("keyEquivalent"))
        self.comboBoxActivation.addItem("Tab Trigger", QtCore.QVariant("tabTrigger"))
    
    def currentEditorWidgetChanged(self, index):
        widget = self.stackLayout.currentWidget()
        self.labelTitle.setText(widget.title())
        scope = widget.scope
        tabTrigger = widget.tabTrigger
        keyEquivalent = widget.keyEquivalent
        self.lineEditScope.setEnabled(scope != None)
        self.lineEditActivation.setEnabled(tabTrigger != None or keyEquivalent != None)
        self.comboBoxActivation.setEnabled(tabTrigger != None or keyEquivalent != None)
        if scope != None:
            self.lineEditScope.setText(scope)
        if keyEquivalent != None:
            self.lineEditActivation.setText(keyEquivalent)
            self.comboBoxActivation.setCurrentIndex(0)
        if tabTrigger != None:
            self.lineEditActivation.setText(tabTrigger)
            self.comboBoxActivation.setCurrentIndex(1)
        
    def treeViewItemActivated(self, index):
        treeItem = self.proxyTreeModel.mapToSource(index).internalPointer()
        if treeItem.tipo in self.indexes: 
            index = self.indexes[treeItem.tipo]
            editor = self.editors[index]
            editor.edit(treeItem.data)
            #TODO: ver si tengo que cuardar el current editor
            print self.container.layout().currentWidget()
            self.container.layout().setCurrentIndex(index)
            self.currentEditorWidgetChanged(index)
            #title = self.container.layout().currentWidget().windowTitle()
            #self.labelTitle.setText( title )
            