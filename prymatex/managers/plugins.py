#!/usr/bin/env python
# -*- coding: utf-8 -*-

import traceback
import os, sys
from glob import glob
import collections

try:
    import json
except ImportError:
    import simplejson as json

from prymatex.qt import QtGui, QtCore
from prymatex import resources
from prymatex.utils import osextra
from prymatex.core import config
from prymatex.core import PrymatexComponent, PrymatexEditor
from prymatex.utils.importlib import import_module, import_from_directories

from prymatex.gui.main import PrymatexMainWindow

class ResourceProvider():
    def __init__(self, resources):
        self.resources = resources

    def get_image(self, index, size = None, default = None):
        if index in self.resources:
            return QtGui.QPixmap(self.resources[index])
        return resources.get_image(index, size, default)
        
    def get_icon(self, index, size = None, default = None):
        if index in self.resources:
            return QtGui.QIcon(self.resources[index])
        return resources.get_icon(index, size, default)

class PluginDescriptor(object):
    name = ""
    description = ""
    icon = None
    def __init__(self, entry):
        for key, value in entry.items():
            setattr(self, key, value)
        
class PluginManager(PrymatexComponent, QtCore.QObject):
    
    #=========================================================
    # Settings
    #=========================================================
    SETTINGS_GROUP = 'PluginManager'
    
    def __init__(self, **kwargs):
        super(PluginManager, self).__init__(**kwargs)

        self.namespaces = {}
        
        self.currentPluginDescriptor = None
        self.plugins = {}
        
        self.components = {}
        self.defaultComponent = QtGui.QPlainTextEdit
        
    @classmethod
    def contributeToSettings(cls):
        from prymatex.gui.settings.plugins import PluginsSettingsWidget
        return [ PluginsSettingsWidget ]

    def addNamespace(self, name, base_path):
        #TODO Validar que existe el base_path + PMX_PLUGINS_NAME
        self.namespaces[name] = os.path.join(base_path, config.PMX_PLUGINS_NAME)

    # ------------- Cargando clases
    def registerComponent(self, componentClass, componentBase = PrymatexMainWindow, default = False):
        self.application.populateComponentClass(componentClass)
        componentClass.plugin = self.currentPluginDescriptor
        self.components.setdefault(componentBase, []).append(componentClass)
        if default:
            self.defaultComponent = componentClass
    
    # ------------ Handle component classes
    def findComponentsForClass(self, klass):
        return self.components.get(klass, [])
    
    def componentHierarchyForClass(self, klass):
        hierarchy = [ ]
        while klass != PrymatexMainWindow:
            hierarchy.append(klass)
            parent = [p_children for p_children in iter(self.components.items()) if klass in p_children[1]]
            if len(parent) != 1:
                break
            klass = parent.pop()[0]
        hierarchy.reverse()
        return hierarchy
        
    # ------------ Handle editor classes
    def findEditorClassByName(self, name):
        editors = (cmp for cmp in self.components.get(PrymatexMainWindow, []) if issubclass(cmp, PrymatexEditor))
        for klass in editors:
            if name == klass.__name__:
                return klass

    def findEditorClassForFile(self, filepath):
        mimetype = self.application.fileManager.mimeType(filepath)
        editors = (cmp for cmp in self.components.get(PrymatexMainWindow, []) if issubclass(cmp, PrymatexEditor))
        for klass in editors:
            if klass.acceptFile(filepath, mimetype):
                return klass
    
    def defaultEditor(self):
        return self.defaultComponent

    # ---------- Load plugins
    def loadResources(self, pluginDirectory, pluginEntry):
        if "icon" in pluginEntry:
            iconPath = os.path.join(pluginDirectory, pluginEntry["icon"])
            pluginEntry["icon"] = QtGui.QIcon(iconPath)
        if "share" in pluginEntry:
            pluginEntry["share"] = os.path.join(pluginDirectory, pluginEntry["share"])
            res = resources.loadResources(pluginEntry["share"])
            pluginEntry["resources"] = ResourceProvider(res)
        else:
            # Global resources
            pluginEntry["resources"] = resources
        
    def loadPlugin(self, pluginEntry):
        pluginId = pluginEntry.get("id")
        packageName = pluginEntry.get("package")
        registerFunction = pluginEntry.get("register", "registerPlugin")
        pluginDirectories = pluginEntry.get("paths")
        pluginDirectory = pluginEntry.get("path")
        self.loadResources(pluginDirectory, pluginEntry)
        try:
            pluginEntry["module"] = import_from_directories(pluginDirectories, packageName)
            registerPluginFunction = getattr(pluginEntry["module"], registerFunction)
            if isinstance(registerPluginFunction, collections.Callable):
                self.currentPluginDescriptor = self.plugins[pluginId] = PluginDescriptor(pluginEntry)
                registerPluginFunction(self, self.currentPluginDescriptor)
        except Exception as reason:
            # On exception remove entry
            if pluginId in self.plugins:
                del self.plugins[pluginId]
            traceback.print_exc()
        self.currentPluginDescriptor = None
    
    def loadCoreModule(self, moduleName, pluginId):
        pluginEntry = {"id": pluginId,
                       "resources": resources}
        try:
            pluginEntry["module"] = import_module(moduleName)
            registerPluginFunction = getattr(pluginEntry["module"], "registerPlugin")
            if isinstance(registerPluginFunction, collections.Callable):
                self.currentPluginDescriptor = self.plugins[pluginId] = PluginDescriptor(pluginEntry)
                registerPluginFunction(self, self.currentPluginDescriptor)
        except (ImportError, AttributeError) as reason:
            # On exception remove entry
            if pluginId in self.plugins:
                del self.plugins[pluginId]
            traceback.print_exc()
        self.currentPluginDescriptor = None
        
    def hasDependenciesResolved(self, pluginEntry):
        return all([dep in self.plugins for dep in pluginEntry.get("depends", [])])
    
    def loadPlugins(self):
        self.loadCoreModule('prymatex.gui.codeeditor', 'org.prymatex.codeeditor')
        self.loadCoreModule('prymatex.gui.dockers', 'org.prymatex.dockers')
        self.loadCoreModule('prymatex.gui.dialogs', 'org.prymatex.dialogs')
        loadLaterEntries = []
        for name, directory in self.namespaces.items():
            if not os.path.isdir(directory):
                continue
            for pluginPath in glob(os.path.join(directory, config.PMX_PLUGIN_GLOB)):
                pluginDescriptorPath = os.path.join(pluginPath, config.PMX_DESCRIPTOR_NAME)
                if os.path.isdir(pluginPath) and os.path.isfile(pluginDescriptorPath):
                    descriptorFile = open(pluginDescriptorPath, 'r')
                    pluginEntry = json.load(descriptorFile)
                    descriptorFile.close()
                    # Load paths
                    pluginEntry["path"] = pluginPath
                    paths = [ pluginPath ]
                    for path in pluginEntry.get("paths", []):
                        if not os.path.isabs(path):
                            path = os.path.abspath(os.path.join(pluginPath, path))
                        paths.append(path)
                    pluginEntry["paths"] = paths
                    if self.hasDependenciesResolved(pluginEntry):
                        self.loadPlugin(pluginEntry)
                    else:
                        loadLaterEntries.append(pluginEntry)
        #Cargar las que quedaron bloqueadas por dependencias hasta consumirlas
        # dependencias circulares? son ridiculas pero por lo menos detectarlas
        unsolvedCount = len(loadLaterEntries)
        while True:
            loadLater = []
            for pluginEntry in loadLaterEntries:
                if self.hasDependenciesResolved(pluginEntry):
                    self.loadPlugin(pluginEntry)
                else:
                    loadLater.append(pluginEntry)
            if not loadLater or unsolvedCount == len(loadLater):
                break
            else:
                loadLaterEntries = loadLater
                unsolvedCount = len(loadLaterEntries)
        #Si me quedan plugins tendira que avisar o mostrar algo es que no se cumplieron todas las dependencias
