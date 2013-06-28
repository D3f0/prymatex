#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, string, unicodedata
import fnmatch

from prymatex.qt import QtCore, QtGui

from prymatex.core import PMXBaseComponent
from prymatex.core import exceptions
from prymatex.core.settings import pmxConfigPorperty
from prymatex.utils.misc import get_home_dir
from prymatex.models.lists import CheckableListModel
from prymatex.models.projects import (ProjectTreeNode, ProjectTreeModel, 
    ProjectTreeProxyModel, ProjectMenuProxyModel)

from prymatex.models.properties import PropertiesProxyModel, PropertiesTreeModel
from prymatex.core.exceptions import ProjectExistsException, FileException

from prymatex.utils.i18n import ugettext as _

class ProjectManager(QtCore.QObject, PMXBaseComponent):
    #Signals
    projectAdded = QtCore.Signal(object)
    projectRemoved = QtCore.Signal(object)
    projectClose = QtCore.Signal(object)
    projectOpen = QtCore.Signal(object)
    
    #Settings
    SETTINGS_GROUP = 'ProjectManager'
    
    workspaceDirectory  = pmxConfigPorperty(default = os.path.join(get_home_dir(), "workspace"))  #Eclipse muejejeje
    knownProjects = pmxConfigPorperty(default = [])
    
    VALID_PATH_CARACTERS = "-_.() %s%s" % (string.ascii_letters, string.digits)
    
    def __init__(self, application):
        QtCore.QObject.__init__(self)
        PMXBaseComponent.__init__(self)
        self.fileManager = application.fileManager
        self.supportManager = application.supportManager
        
        self.projectTreeModel = ProjectTreeModel(self)
        self.keywordsListModel = CheckableListModel(self)
        self.propertiesTreeModel = PropertiesTreeModel(self)
        
        self.projectTreeProxyModel = ProjectTreeProxyModel(self)
        self.projectTreeProxyModel.setSourceModel(self.projectTreeModel)

        self.projectMenuProxyModel = ProjectMenuProxyModel(self)
        self.projectMenuProxyModel.setSourceModel(self.application.supportManager.bundleProxyModel)

        self.propertiesProxyModel = PropertiesProxyModel(self)
        self.propertiesProxyModel.setSourceModel(self.propertiesTreeModel)

        self.supportManager.bundleAdded.connect(self.on_supportManager_bundleAdded)
        self.supportManager.bundleRemoved.connect(self.on_supportManager_bundleRemoved)
        self.supportManager.bundleItemAdded.connect(self.on_supportManager_bundleItemAdded)
        self.supportManager.bundleItemRemoved.connect(self.on_supportManager_bundleItemRemoved)


    @classmethod
    def contributeToSettings(cls):
        return []

    def convertToValidPath(self, name):
        #TODO: este y el del manager de bundles pasarlos a utils
        validPath = []
        for char in unicodedata.normalize('NFKD', str(name)).encode('ASCII', 'ignore'):
            char = char if char in self.VALID_PATH_CARACTERS else '-'
            validPath.append(char)
        return ''.join(validPath)

    # -------------- Signals from suppor manager
    def on_supportManager_bundleAdded(self, bundle):
        for project in self.getAllProjects():
            if bundle.hasNamespace(project.namespace) and not project.hasBundleMenu(bundle):
                self.addProjectBundleMenu(project, bundle)

    def on_supportManager_bundleRemoved(self, bundle):
        for project in self.getAllProjects():
            if bundle.hasNamespace(project.namespace) and project.hasBundleMenu(bundle):
                self.removeProjectBundleMenu(project, bundle)

    def on_supportManager_bundleItemAdded(self, bundleItem):
        if bundleItem.TYPE == "syntax":
            self.keywordsListModel.addItems(bundleItem.scopeName.split('.'))


    def on_supportManager_bundleItemRemoved(self, bundleItem):
        if bundleItem.TYPE == "syntax":
            self.keywordsListModel.removeItems(bundleItem.scopeName.split('.'))


    # -------------------- Load projects
    def loadProjects(self):
        for path in self.knownProjects[:]:
            try:
                ProjectTreeNode.loadProject(path, self)
            except exceptions.FileNotExistsException as e:
                print(e)
                self.knownProjects.remove(path)
                self.settings.setValue('knownProjects', self.knownProjects)


    def isOpen(self, project):
        return True


    def appendToKnowProjects(self, project):
        self.knownProjects.append(project.path())
        self.settings.setValue('knownProjects', self.knownProjects)


    def removeFromKnowProjects(self, project):
        self.knownProjects.remove(project.path())
        self.settings.setValue('knownProjects', self.knownProjects)


    # ------------------- Properties
    def registerPropertyWidget(self, propertyWidget):
        self.propertiesTreeModel.addConfigNode(propertyWidget)


    #---------------------------------------------------
    # Environment
    #---------------------------------------------------
    def environmentVariables(self):
        return {}


    def supportProjectEnvironment(self, project):
        return self.supportManager.projectEnvironment(project)


    #---------------------------------------------------
    # PROJECT CRUD
    #---------------------------------------------------
    def createProject(self, name, directory, overwrite = False):
        """Crea un proyecto nuevo y lo retorna"""
        project = ProjectTreeNode(directory, { "name": name })
        if not overwrite and os.path.exists(project.projectPath):
            raise exceptions.ProjectExistsException()

        project.save()
        self.addProject(project)
        self.appendToKnowProjects(project)
        return project
    
    def updateProject(self, project, **attrs):
        """Actualiza un proyecto"""
        project.update(attrs)
        project.save()
        return project

    def importProject(self, directory):
        try:
            project = ProjectTreeNode.loadProject(directory, self)
        except exceptions.FileNotExistsException:
            raise exceptions.LocationIsNotProject()
        self.appendToKnowProjects(project)

    def deleteProject(self, project, removeFiles = False):
        """Elimina un proyecto"""
        project.delete(removeFiles)
        self.removeProject(project)

    #---------------------------------------------------
    # PROJECT INTERFACE
    #---------------------------------------------------
    def addProject(self, project):
        project.setManager(self)
        # Todo proyecto define un namespace en el manager de support
        self.application.supportManager.addProjectNamespace(project)
        self.projectTreeModel.appendProject(project)
        self.projectAdded.emit(project)

    def modifyProject(self, project):
        pass

    def removeProject(self, project):
        self.removeFromKnowProjects(project)
        self.projectTreeModel.removeProject(project)

    def getAllProjects(self):
        #TODO: devolver un copia o no hace falta?
        return self.projectTreeModel.rootNode.childNodes()

    def openProject(self, project):
        # Cuando abro un proyecto agrego su namespace al support para aportar bundles y themes
        print(project.directory)

    def closeProject(self, project):
        # Cuando cierro un proyecto quito su namespace al support
        print(project.directory)

    def addProjectBundleMenu(self, project, bundle):
        project.addBundleMenu(bundle)
        project.save()

    def removeProjectBundleMenu(self, project, bundle):
        project.removeBundleMenu(bundle)
        project.save()

    def findProjectForPath(self, path):
        for project in self.getAllProjects():
            if self.application.fileManager.issubpath(path, project.path()):
                return project