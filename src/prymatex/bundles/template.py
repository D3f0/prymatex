#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Template's module
    http://manual.macromates.com/en/templates
'''

import os, plistlib
from subprocess import Popen
from prymatex.bundles.utils import ensureShellScript, makeExecutableTempFile,\
    ensureEnvironment, deleteFile
# for run as main
if __name__ == "__main__":
    import sys
    sys.path.append(os.path.abspath('../..'))
from prymatex.bundles.base import PMXBundleItem

class PMXTemplate(PMXBundleItem):
    KEYS = [    'command', 'extension']
    TYPE = 'template'
    FOLDER = 'Templates'
    FILES = [ '*' ]
    bundle_collection = 'templates'
    def __init__(self, namespace, hash = None, path = None):
        super(PMXTemplate, self).__init__(namespace, hash, path)
    
    def load(self, hash):
        super(PMXTemplate, self).load(hash)
        for key in PMXTemplate.KEYS:
            setattr(self, key, hash.get(key, None))
    
    @property
    def hash(self):
        hash = super(PMXTemplate, self).hash
        for key in PMXTemplate.KEYS:
            value = getattr(self, key)
            if value != None:
                hash[key] = value
        return hash
    
    def buildEnvironment(self, directory = "", name = ""):
        env = super(PMXTemplate, self).buildEnvironment()
        env['TM_NEW_FILE'] = os.path.join(directory, name + '.' + self.extension)
        env['TM_NEW_FILE_BASENAME'] = name
        env['TM_NEW_FILE_DIRECTORY'] = directory
        return env
    
    def resolve(self, environment = {}):
        origWD = os.getcwd() # remember our original working directory
        os.chdir(self.path)
        
        command = ensureShellScript(self.command)
        temp_file = makeExecutableTempFile(command)  
        process = Popen([ temp_file ], env = ensureEnvironment(environment))
        process.wait()
        
        deleteFile(temp_file)
        os.chdir(origWD) # get back to our original working directory
        
    @classmethod
    def loadBundleItem(cls, path, name_space = 'prymatex'):
        info_file = os.path.join(path, 'info.plist')
        try:
            data = plistlib.readPlist(info_file)
            template = cls(name_space, data, path)
        except Exception, e:
            print "Error in bundle %s (%s)" % (info_file, e)
            return None
        return template