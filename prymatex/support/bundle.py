#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, shutil

from prymatex.utils import osextra

from .base import PMXManagedObject

class PMXBundle(PMXManagedObject):
    KEYS = ('name', 'deleted', 'ordering', 'mainMenu', 'contactEmailRot13',
            'description', 'contactName', 'requiredCommands', 'require' )
    FILE = 'info.plist'
    TYPE = 'bundle'
    DEFAULTS = {
        'name': 'Untitled'
    }
    def __init__(self, uuid):
        PMXManagedObject.__init__(self, uuid)
        self.__supportPath = None

    def hasSupportPath(self):
        return self.__supportPath is not None
        
    def setSupportPath(self, supportPath):
        self.__supportPath = supportPath
    
    def supportPath(self):
        return self.__supportPath
    
    def relocateSupport(self, path):
        try:
            # TODO Ver que pasa si ya existe support
            shutil.copytree(self.supportPath(), path, symlinks = True)
            self.setSupportPath(path)
        except:
            pass
    
    def __load_update(self, dataHash, initialize):
        for key in PMXBundle.KEYS:
            if key in dataHash or initialize:
                setattr(self, key, dataHash.get(key, None))

    def load(self, dataHash):
        self.__load_update(dataHash, True)
        
    def update(self, dataHash):
        self.__load_update(dataHash, False)

    def dump(self):
        dataHash = super(PMXBundle, self).dump()
        for key in PMXBundle.KEYS:
            value = getattr(self, key, None)
            if value is not None:
                dataHash[key] = value
        return dataHash

    def environmentVariables(self):
        environment = self.manager.environmentVariables()
        environment['TM_BUNDLE_PATH'] = self.currentPath()
        if self.hasSupportPath():
            environment['TM_BUNDLE_SUPPORT'] = self.supportPath()
        return environment

    def createDataFilePath(self, basePath, baseName = None):
        directory = osextra.path.ensure_not_exists(os.path.join(basePath, "%s.tmbundle"), osextra.to_valid_name(baseName or self.name))
        return os.path.join(directory, self.FILE)

    @classmethod
    def dataFilePath(cls, path):
        return os.path.join(path, cls.FILE)