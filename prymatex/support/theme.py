#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from prymatex.support.bundle import PMXManagedObject
from prymatex.support import scope
from prymatex.utils import plist

"""foreground, background, selection, invisibles, lineHighlight, caret, gutter
prymatex add gutterForeground
"""

DEFAULT_THEME_SETTINGS = {'background':         '#FFFFFF',
                          'caret':              '#000000',
                          'foreground':         '#000000',
                          'invisibles':         '#BFBFBF',
                          'lineHighlight':      '#00000012',
                          'gutter':             '#FFFFFF',
                          'gutterForeground':   '#000000',
                          'lineHighlight':      '#00000012',
                          'selection':          '#A6CBFF'}


DEFAULT_SCOPE_SELECTORS = [('Comment', 'comment'),
                           ('String', 'string'),
                           ('Number', 'constant.numeric'),
                           ('Built-in constant', 'constant.language'),
                           ('User-defined constant', 'constant.character, constant.other'),
                           ('Variable', 'variable.language, variable.other'),
                           ('Keyword', 'keyword'),
                           ('Storage', 'storage'),
                           ('Class name', 'entity.name.class'),
                           ('Inherited class', 'entity.other.inherited-class'),
                           ('Function name', 'entity.name.function'),
                           ('Function argument', 'variable.parameter'),
                           ('Tag name', 'entity.name.tag'),
                           ('Tag attribute', 'entity.other.attribute-name'),
                           ('Library function', 'support.function'),
                           ('Library constant', 'support.constant'),
                           ('Library class/type', 'support.type, support.class'),
                           ('Library variable', 'support.other.variable'),
                           ('Invalid', 'invalid')]


class PMXThemeStyle(object):
    KEYS = [ 'scope', 'name', 'settings' ]
    def __init__(self, dataHash, theme):
        self.theme = theme
        self.load(dataHash)

    def load(self, dataHash):
        for key in PMXThemeStyle.KEYS:
            value = dataHash.get(key, None)
            if key == 'scope':
                self.selector = scope.Selector(value)
            setattr(self, key, value)

    @property
    def hash(self):
        dataHash = {'name': self.name}
        if self.scope is not None:
            dataHash['scope'] = self.scope
        dataHash['settings'] = {}
        for name, setting in self.settings.items():
            if setting != None:
                dataHash['settings'][name] = setting
        return dataHash
        
    def update(self, dataHash):
        for key in list(dataHash.keys()):
            value = dataHash[key]
            if key == 'settings':
                self.settings.update(value)
                self.settings = dict([tupla for tupla in iter(self.settings.items()) if tupla[1] != None])
                continue
            elif key == 'scope':
                self.selector = scope.Selector(value)
            setattr(self, key, value)
    
class PMXTheme(PMXManagedObject):
    KEYS = [    'name', 'comment', 'author', 'settings']
    
    def __init__(self, uuid):
        super(PMXTheme, self).__init__(uuid)
        self.styles = []

    def load(self, dataHash):
        for key in PMXTheme.KEYS:
            setattr(self, key, dataHash.get(key, None))

    def setDefaultSettings(self, settings):
        self.settings = settings
        
    def update(self, dataHash):
        for key in list(dataHash.keys()):
            if key == 'settings':
                self.settings.update(dataHash[key])
                self.settings = dict([tupla for tupla in iter(self.settings.items()) if tupla[1] != None])
            else:
                setattr(self, key, dataHash[key])
    
    @property
    def hash(self):
        dataHash = super(PMXTheme, self).hash
        for key in PMXTheme.KEYS:
            value = getattr(self, key)
            if value != None:
                dataHash[key] = value
        dataHash['settings'] = [ { 'settings': self.settings } ]
        for style in self.styles:
            dataHash['settings'].append(style.hash)
        return dataHash
        
    def save(self, namespace):
        folder = os.path.dirname(self.path(namespace))
        if not os.path.exists(folder):
            os.makedirs(folder)
        plist.writePlist(self.hash, self.path(namespace))
    
    def removeThemeStyle(self, style):
        self.styles.remove(style)