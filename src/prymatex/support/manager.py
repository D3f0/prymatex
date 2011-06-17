#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, string, unicodedata
from os.path import join, basename, dirname, exists, normpath

from glob import glob
from prymatex.support.bundle import PMXBundle, PMXBundleItem
from prymatex.support.macro import PMXMacro
from prymatex.support.syntax import PMXSyntax
from prymatex.support.snippet import PMXSnippet
from prymatex.support.preference import PMXPreference
from prymatex.support.command import PMXCommand, PMXDragCommand
from prymatex.support.template import PMXTemplate
from prymatex.support.theme import PMXTheme
from prymatex.support.score import PMXScoreManager
from prymatex.support.utils import sh, ensurePath

BUNDLEITEM_CLASSES = [ PMXSyntax, PMXSnippet, PMXMacro, PMXCommand, PMXPreference, PMXTemplate, PMXDragCommand ]

def compare(object, attrs, tests):
    if not attrs:
        return True
    attr = getattr(object, attrs[0], None)
    if attr == None or attrs[0] not in tests:
        return True and compare(object, attrs[1:], tests)
    elif isinstance(attr, (str, unicode)):
        return attr.find(tests[attrs[0]]) != -1 and compare(object, attrs[1:], tests)
    elif isinstance(attr, (int)):
        return attr == tests[attrs[0]] and compare(object, attrs[1:], tests)
    else:
        return attr == tests[attrs[0]] and compare(object, attrs[1:], tests)

class PMXSupportBaseManager(object):
    ELEMENTS = ['Bundles', 'Support', 'Themes']
    VAR_PREFIX = 'PMX'
    PROTECTEDNS = 0
    DEFAULTNS = -1
    TABTRIGGERSPLITS = (re.compile(r"\s+", re.UNICODE), re.compile(r"\w+", re.UNICODE), re.compile(r"\W+", re.UNICODE), re.compile(r"\W", re.UNICODE))
    VALID_PATH_CARACTERS = "-_.() %s%s" % (string.ascii_letters, string.digits)
    #FIXME: Dudo de la cache en este lugar
    SETTINGS_CACHE = {}
    
    def __init__(self, disabledBundles = [], deletedBundles = []):
        self.namespaces = {}
        # Te first is the name space base, and the last is de default for new bundles and items */
        self.nsorder = []
        self.environment = {}
        self.disabledBundles = disabledBundles
        self.deletedBundles = deletedBundles
        self.scores = PMXScoreManager()
    
    def addNamespace(self, name, path):
        self.namespaces[name] = {}
        self.nsorder.append(name)
        for element in self.ELEMENTS:
            epath = join(path, element)
            if not exists(epath):
                continue
            #Si es el primero es el protegido
            if len(self.nsorder) == 1:
                var = "_".join([ self.VAR_PREFIX, element.upper(), 'PATH' ])
            else:
                var = "_".join([ self.VAR_PREFIX, name.upper(), element.upper(), 'PATH' ])
            self.namespaces[name][element] = self.environment[var] = epath

    def uuidgen(self):
        # TODO: ver que el uuid generado no este entre los elementos existentes
        return sh("uuidgen").strip()
        
    def convertToValidPath(self, name):
        # TODO: ver que el uuid generado no este entre los elementos existentes
        validPath = []
        for char in unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore'):
            char = char if char in self.VALID_PATH_CARACTERS else '-'
            validPath.append(char)
        return ''.join(validPath)

    def updateEnvironment(self, env):
        self.environment.update(env)

    def buildEnvironment(self):
        return self.environment

    #---------------------------------------------------
    # LOAD ALL SUPPORT
    #---------------------------------------------------
    def loadSupport(self, callback = None):
        cache = {}
        for ns in self.nsorder[::-1]:
            self.loadThemes(ns, cache)
            self.loadBundles(ns, cache)
        for bundle in self.getAllBundles():
            self.populateBundle(bundle, cache)

    #---------------------------------------------------
    # LOAD THEMES
    #---------------------------------------------------
    def loadThemes(self, namespace, cache = {}):
        if 'Themes' in self.namespaces[namespace]:
            paths = glob(join(self.namespaces[namespace]['Themes'], '*.tmTheme'))
            for path in paths:
                theme = PMXTheme.loadTheme(path, namespace)
                if theme == None:
                    continue
                if theme.uuid not in cache:
                    theme.setManager(self)
                    self.addTheme(theme)
                    cache[theme.uuid] = theme
                else:
                    cache[theme.uuid].addNamespace(namespace)

    #---------------------------------------------------
    # LOAD BUNDLES
    #---------------------------------------------------
    def loadBundles(self, namespace, cache = {}):
        if 'Bundles' in self.namespaces[namespace]:
            paths = glob(join(self.namespaces[namespace]['Bundles'], '*.tmbundle'))
            for path in paths:
                bundle = PMXBundle.loadBundle(path, namespace)
                if bundle == None:
                    continue
                bundle.disabled = bundle.uuid in self.disabledBundles
                if bundle.uuid not in self.deletedBundles and bundle.uuid not in cache:
                    bundle.setManager(self)
                    self.addBundle(bundle)
                    cache[bundle.uuid] = bundle
                elif bundle.uuid in cache:
                    cache[bundle.uuid].addNamespace(namespace)

    #---------------------------------------------------
    # POPULATE BUNDLE AND LOAD BUNDLE ITEMS
    #---------------------------------------------------
    def populateBundle(self, bundle, cache = {}):
        nss = bundle.namespaces[::-1]
        for ns in nss:
            bpath = join(self.namespaces[ns]['Bundles'], basename(bundle.path))
            # Search for support
            if bundle.support == None and exists(join(bpath, 'Support')):
                bundle.setSupport(join(bpath, 'Support'))
            for klass in BUNDLEITEM_CLASSES:
                files = reduce(lambda x, y: x + glob(y), [ join(bpath, klass.FOLDER, file) for file in klass.PATTERNS ], [])
                for sf in files:
                    item = klass.loadBundleItem(sf, ns)
                    if item == None:
                        continue
                    if bundle.uuid not in self.deletedBundles and item.uuid not in cache:
                        item.setManager(self)
                        item.setBundle(bundle)
                        self.addBundleItem(item)
                        cache[item.uuid] = item
                    elif item.uuid in cache:
                        cache[item.uuid].addNamespace(ns)

    #---------------------------------------------------
    # BUNDLE INTERFACE
    #---------------------------------------------------
    def addBundle(self, bundle):
        return bundle
        
    def getBundle(self, uuid):
        pass

    def modifyBundle(self, bundle):
        '''
            Llamado luego de modificar un bundle
        '''
        pass

    def removeBundle(self, bundle):
        '''
            Llamado antes de eliminar un bundle
        '''
        pass

    def setDeletedBundle(self, uuid):
        '''
            Marcar un bundle como eliminado
        '''
        pass
        
    def hasBundle(self, uuid):
        pass

    def getAllBundles(self):
        pass
    
    #---------------------------------------------------
    # BUNDLE CRUD
    #---------------------------------------------------
    def findBundles(self, **attrs):
        '''
            Retorna todos los bundles que cumplan con attrs
        '''
        bundles = []
        keys = PMXBundle.KEYS
        keys.extend([key for key in attrs.keys() if key not in keys])
        for bundle in self.getAllBundles():
            if compare(bundle, keys, attrs):
                bundles.append(bundle)
        return bundles
    
    def createBundle(self, name, namespace = None):
        '''
            Crea un bundle nuevo lo agrega en los bundles y lo retorna,
            Precondiciones:
                Tenes por lo menos dos espacios de nombre el base o proteguido y uno donde generar los nuevos bundles
                El nombre tipo Title.
                El nombre no este entre los nombres ya cargados.
            Toma el ultimo espacio de nombres creado como espacio de nombre por defecto para el bundle nuevo.
        '''
        if len(self.nsorder) < 2:
            return None
        namespace = self.nsorder[self.DEFAULTNS] if namespace == None else namespace
        hash = {    'uuid': self.uuidgen(),
                    'name': name }
        path = join(self.namespaces[namespace]['Bundles'], "%s.tmbundle" % self.convertToValidPath(name))
        bundle = PMXBundle(namespace, hash, path)
        return self.addBundle(bundle)
    
    def readBundle(self, **attrs):
        '''
            Retorna un bundle por sus atributos
        '''
        bundles = self.findBundles(**attrs)
        if len(bundles) > 1:
            raise Exception("More than one bundle")
        return bundles[0]
        
    def updateBundle(self, bundle, **attrs):
        '''
            Actualiza un bundle
        '''
        if len(self.nsorder) < 2:
            return None
        if len(attrs) == 1 and "name" in attrs and attrs["name"] == bundle.name:
            #Updates que no son updates
            return bundle
        if bundle.namespaces[-1] == self.nsorder[self.PROTECTEDNS]:
            #Cambiar de namespace y de path al por defecto para proteger el base
            newns = self.nsorder[self.DEFAULTNS]
            attrs["path"] = join(self.namespaces[newns]['Bundles'], basename(bundle.path))
            bundle.update(attrs)
            bundle.save()
            bundle.addNamespace(newns)
        else:
            if "name" in attrs and self.nsorder[self.PROTECTEDNS] not in bundle.namespaces:
                attrs["path"] = ensurePath(join(dirname(bundle.path), "%s.tmbundle"), self.convertToValidPath(attrs["name"]))
                bundle.relocate(attrs["path"])
            bundle.update(attrs)
            bundle.save()
        self.modifyBundle(bundle)
        return bundle
        
    def deleteBundle(self, bundle):
        '''
            Elimina un bundle,
            si el bundle es del namespace proteguido no lo elimina sino que lo marca como eliminado
        '''
        self.removeBundle(bundle)
        items = self.findBundleItems(bundle = bundle)
        #Primero los items
        for item in items:
            self.deleteBundleItem(item)
        if bundle.namespace == self.nsorder[0]:
            self.setDeletedBundle(bundle.uuid)
        else:
            bundle.delete()
        
    #---------------------------------------------------
    # BUNDLEITEM INTERFACE
    #---------------------------------------------------
    def addBundleItem(self, bundleItem):
        return bundleItem
        
    def getBundleItem(self, uuid):
        pass

    def modifyBundleItem(self, bundleItem):
        pass

    def removeBundleItem(self, bundleItem):
        pass
    
    def setDeletedBundleItem(self, uuid):
        '''
            Marcar un bundle item como eliminado
        '''
        pass
        
    def hasBundleItem(self, uuid):
        '''
        @return: True if PMXBundleItem exists
        '''
        pass

    def getAllBundleItems(self):
        pass
        
    #---------------------------------------------------
    # BUNDLEITEM CRUD
    #---------------------------------------------------
    def findBundleItems(self, **attrs):
        '''
            Retorna todos los items que complan las condiciones en attrs
        '''
        items = []
        keys = PMXBundleItem.KEYS
        keys.extend([key for key in attrs.keys() if key not in keys])
        for item in self.getAllBundleItems():
            if compare(item, keys, attrs):
                items.append(item)
        return items

    def createBundleItem(self, name, tipo, bundle, namespace = None):
        '''
            Crea un bundle item nuevo lo agrega en los bundle items y lo retorna,
            Precondiciones:
                Tenes por lo menos dos nombres en el espacio de nombres
                El tipo tiene que ser uno de los conocidos
            Toma el ultimo espacio de nombres creado como espacio de nombre por defecto para el bundle item nuevo.
        '''
        if len(self.nsorder) < 2:
            return None
        namespace = self.nsorder[self.DEFAULTNS] if namespace == None else namespace
        hash = {    'uuid': self.uuidgen(),
                    'name': name }
        klass = filter(lambda c: c.TYPE == tipo, BUNDLEITEM_CLASSES)
        if len(klass) != 1:
            raise Exception("No class type for %s" % tipo)
        klass = klass.pop()
        path = join(bundle.path, klass.FOLDER, "%s.%s" % (self.convertToValidPath(name), klass.EXTENSION))

        item = klass(namespace, hash, path)
        item.setBundle(bundle)
        return self.addBundleItem(item)
    
    def readBundleItem(self, **attrs):
        '''
            Retorna un bundle item por sus atributos
        '''
        items = self.findBundleItems(**attrs)
        if len(items) > 1:
            raise Exception("More than one bundle item")
        return items[0]
    
    def updateBundleItem(self, item, **attrs):
        '''
            Actualiza un bundle item
        '''
        if len(self.nsorder) < 2:
            return None
        if len(attrs) == 1 and "name" in attrs and attrs["name"] == item.name:
            #Updates que no son updates
            return item
        if item.bundle.namespaces[-1] == self.nsorder[self.PROTECTEDNS]:
            self.updateBundle(item.bundle)
        if item.namespaces[-1] == self.nsorder[self.PROTECTEDNS]:
            #Cambiar de namespace y de path al por defecto para proteger el base
            newns = self.nsorder[self.DEFAULTNS]
            attrs["path"] = join(item.bundle.path, item.FOLDER, basename(item.path))
            item.update(attrs)
            item.save()
            item.addNamespace(newns)
        else:
            if "name" in attrs and self.nsorder[self.PROTECTEDNS] not in item.namespaces:
                attrs["path"] = ensurePath(join(item.bundle.path, item.FOLDER, "%%s.%s" % item.EXTENSION), self.convertToValidPath(attrs["name"]))
                item.relocate(attrs["path"])
            item.update(attrs)
            item.save()
        self.modifyBundleItem(item)
        return item
    
    def deleteBundleItem(self, item):
        '''
            Elimina un bundle por su uuid,
            si el bundle es del namespace proteguido no lo elimina sino que lo marca como eliminado
        '''
        self.removeBundleItem(item)
        #Si el espacio de nombres es distinto al protegido lo elimino
        if item.namespace == self.nsorder[self.PROTECTEDNS]:
            self.setDeletedBundleItem(item.uuid)
        else:
            item.delete()

    #---------------------------------------------------
    # THEME INTERFACE
    #---------------------------------------------------
    def addTheme(self, theme):
        pass
        
    def getTheme(self, uuid):
        pass

    def modifyTheme(self, theme):
        pass
        
    def removeTheme(self, theme):
        pass
        
    def setDeletedTheme(self, uuid):
        pass
        
    def hasTheme(self, uuid):
        pass

    def getAllThemes(self):
        pass
    
    #---------------------------------------------------
    # THEME CRUD
    #---------------------------------------------------
    def findThemes(self, **attrs):
        '''
            Retorna todos los themes que complan las condiciones en attrs
        '''
        items = []
        keys = PMXTheme.KEYS
        keys.extend([key for key in attrs.keys() if key not in keys])
        for item in self.getAllThemes():
            if compare(item, keys, attrs):
                items.append(item)
        return items

    def createTheme(self, name, namespace = None):
        '''
            
        '''
        namespace = self.nsorder[self.DEFAULTNS] if namespace == None else namespace
        hash = {    'uuid': self.uuidgen(),
                    'name': name }
        path = join(self.namespaces[namespace]['Themes'], "%s.tmTheme" % self.convertToValidPath(name))
        theme = PMXTheme(namespace, hash, path)
        self.addTheme(theme)
        return theme
    
    def readTheme(self, **attrs):
        '''
            Retorna un bundle item por sus atributos
        '''
        items = self.findThemes(**attrs)
        if len(items) > 1:
            raise Exception("More than one theme")
        return items[0]
        
    def updateTheme(self, theme, **attrs):
        '''
            Actualiza un themes
        '''
        if theme.namespaces[-1] == self.nsorder[self.PROTECTEDNS]:
            #Cambiar de namespace y de path al por defecto para proteger el base
            newns = self.nsorder[-1]
            attrs["namespace"] = newns
            name = "%s.tmTheme" % self.convertToValidPath(attrs["name"]) if "name" in attrs else basename(theme.path)
            attrs["path"] = join(self.namespaces[newns]['Themes'], name)
            theme.update(attrs)
            theme.save()
            theme.addNamespace(newns)
        else:
            theme.update(attrs)
            theme.save()
        self.modifyTheme(theme)
        return theme
        
    def deleteTheme(self, theme):
        '''
            Elimina un theme por su uuid
        '''
        self.removeTheme(theme)
        #Si el espacio de nombres es distinto al protegido lo elimino
        if theme.namespace == self.nsorder[self.PROTECTEDNS]:
            self.setDeletedTheme(theme.uuid)
        else:
            theme.delete()
    
    #---------------------------------------------------
    # PREFERENCES INTERFACE
    #---------------------------------------------------
    def getAllPreferences(self):
        '''
            Return a list of preferences bundle items
        '''
        pass
        
    #---------------------------------------------------------------
    # PREFERENCES
    #---------------------------------------------------------------
    def getPreferences(self, scope):
        with_scope = []
        without_scope = []
        for preference in self.getAllPreferences():
            if preference.scope == None:
                without_scope.append(preference)
            else:
                score = self.scores.score(preference.scope, scope)
                if score != 0:
                    with_scope.append((score, preference))
        with_scope.sort(key = lambda t: t[0], reverse = True)
        preferences = map(lambda (score, item): item, with_scope)
        with_scope = []
        for p in preferences:
            with_scope.append(p)
        return with_scope + without_scope

    def getPreferenceSettings(self, scope):
        if scope not in self.SETTINGS_CACHE:
            preferences = self.getPreferences(scope)
            self.SETTINGS_CACHE[scope] = PMXPreference.buildSettings(preferences)
        return self.SETTINGS_CACHE[scope]
    
    #---------------------------------------------------
    # TABTRIGGERS INTERFACE
    #---------------------------------------------------
    def getAllTabTriggersMnemonics(self):
        '''
            Return a list of tab triggers
            ['class', 'def', ...]
        '''
        pass
    
    def getAllBundleItemsByTabTrigger(self, tabTrigger):
        '''
            Return a list of tab triggers bundle items
        '''
        pass
    
    #---------------------------------------------------------------
    # TABTRIGGERS
    #---------------------------------------------------------------
    def getTabTriggerSymbol(self, line, index):
        line = line[:index]
        tiggers = self.getAllTabTriggersMnemonics()
        for tabSplit in self.TABTRIGGERSPLITS:
            matchs = filter(lambda m: m.start() <= index <= m.end(), tabSplit.finditer(line))
            if matchs:
                match = matchs.pop()
                word = line[match.start():match.end()]
                if word in tiggers:
                    return word
    
    def getTabTriggerItem(self, keyword, scope):
        with_scope = []
        without_scope = []
        for item in self.getAllBundleItemsByTabTrigger(keyword):
            if item.scope == None:
                without_scope.append(item)
            else:
                score = self.scores.score(item.scope, scope)
                if score != 0:
                    with_scope.append((score, item))
        with_scope.sort(key = lambda t: t[0], reverse = True)
        with_scope = map(lambda (score, item): item, with_scope)
        return with_scope and with_scope or without_scope
    
    #---------------------------------------------------
    # KEYEQUIVALENT INTERFACE
    #---------------------------------------------------
    def getAllBundleItemsByKeyEquivalent(self, keyEquivalent):
        '''
            Return a list of key equivalent bundle items
        '''
        pass
        
    #---------------------------------------------------------------
    # KEYEQUIVALENT
    #---------------------------------------------------------------
    def getKeyEquivalentItem(self, code, scope):
        with_scope = []
        without_scope = []
        for item in self.getAllBundleItemsByKeyEquivalent(code):
            if item.scope == None:
                without_scope.append(item)
            else:
                score = self.scores.score(item.scope, scope)
                if score != 0:
                    with_scope.append((score, item))
        with_scope.sort(key = lambda t: t[0], reverse = True)
        with_scope = map(lambda (score, item): item, with_scope)
        return with_scope and with_scope or without_scope
        
    #---------------------------------------------------------------
    # SYNTAXES
    #---------------------------------------------------------------
    def getSyntaxes(self, sort = False):
        stxs = []
        for syntax in self.SYNTAXES.values():
            stxs.append(syntax)
        if sort:
            return sorted(stxs, key = lambda s: s.name)
        return stxs
    
    def getSyntaxByScopeName(self, scope):
        if scope in self.SYNTAXES:
            return self.SYNTAXES[scope]
        return None
        
    def findSyntaxByFirstLine(self, line):
        for syntax in self.SYNTAXES.values():
            if syntax.firstLineMatch != None and syntax.firstLineMatch.search(line):
                return syntax
    
    def findSyntaxByFileType(self, path):
        for syntax in self.SYNTAXES.values():
            if type(syntax.fileTypes) == list:
                for t in syntax.fileTypes:
                    if path.endswith(t):
                        return syntax

        
class PMXSupportManager(PMXSupportBaseManager):
    BUNDLES = {}
    BUNDLE_ITEMS = {}
    THEMES = {}
    SYNTAXES = {}
    TAB_TRIGGERS = {}
    KEY_EQUIVALENTS = {}
    DRAGS = []
    PREFERENCES = []
    TEMPLATES = []
    
    def __init__(self, disabledBundles = [], deletedBundles = []):
        super(PMXSupportManager, self).__init__(disabledBundles, deletedBundles)
    
    #---------------------------------------------------
    # BUNDLE INTERFACE
    #---------------------------------------------------
    def addBundle(self, bundle):
        '''
        @param bundle: PMXBundle instance
        '''
        self.BUNDLES[bundle.uuid] = bundle

    def getBundle(self, uuid):
        '''
        @return: PMXBundle by UUID
        '''
        return self.BUNDLES[uuid]

    def modifyBundle(self, bundle):
        pass

    def removeBundle(self, bundle):
        '''
        @param bundle: PMXBundle instance
        '''
        self.BUNDLES.pop(bundle.uuid)

    def addDeletedBundle(self, uuid):
        '''
            Perform logical delete
        '''
        self.deletedBundles.append(uuid)
        
    def hasBundle(self, uuid):
        '''
        @return: True if bundle exists
        '''
        return uuid in self.BUNDLES

    def getAllBundles(self):
        '''
        @return: list of PMXBundle instances
        '''
        return self.BUNDLES.values()
    
    #---------------------------------------------------
    # BUNDLEITEM INTERFACE
    #---------------------------------------------------
    def addBundleItem(self, item):
        self.BUNDLE_ITEMS[item.uuid] = item
        if item.bundle.mainMenu != None:
            item.bundle.mainMenu[item.uuid] = item
        if item.tabTrigger != None:
            self.TAB_TRIGGERS.setdefault(item.tabTrigger, []).append(item)
        if item.keyEquivalent != None:
            self.KEY_EQUIVALENTS.setdefault(item.keyEquivalent, []).append(item)
        if item.TYPE == 'preference':
            self.PREFERENCES.append(item)
        elif item.TYPE == 'template':
            self.TEMPLATES.append(item)
        elif item.TYPE == 'syntax':
            self.SYNTAXES[item.scopeName] = item

    def getBundleItem(self, uuid):
        return self.BUNDLE_ITEMS[uuid]

    def modifyBundleItem(self, item):
        pass

    def removeBundleItem(self, item):
        self.BUNDLE_ITEMS.pop(item.uuid)
    
    def hasBundleItem(self, uuid):
        '''
        @return: True if PMXBundleItem exists
        '''
        return uuid in self.BUNDLE_ITEMS

    def getAllBundleItems(self):
        return self.BUNDLE_ITEMS.values()
        
    #---------------------------------------------------
    # THEME INTERFACE
    #---------------------------------------------------
    def addTheme(self, theme):
        self.THEMES[theme.uuid] = theme
        
    def getTheme(self, uuid):
        return self.THEMES[uuid]

    def modifyTheme(self, theme):
        pass
        
    def removeTheme(self, theme):
        self.THEMES.pop(theme.uuid)

    def hasTheme(self, uuid):
        return uuid in self.THEMES

    def getAllThemes(self):
        return self.THEMES.values()
    
    #---------------------------------------------------
    # PREFERENCES INTERFACE
    #---------------------------------------------------
    def getAllPreferences(self):
        '''
            Return all preferences
        '''
        return self.PREFERENCES
    
    #---------------------------------------------------
    # TABTRIGGERS INTERFACE
    #---------------------------------------------------
    def getAllTabTriggersMnemonics(self):
        '''
            Return a list of tab triggers
            ['class', 'def', ...]
        '''
        return self.TAB_TRIGGERS.keys()
    
    def getAllBundleItemsByTabTrigger(self, tabTrigger):
        '''
            Return a list of tab triggers bundle items
        '''
        if tabTrigger not in self.TAB_TRIGGERS:
            return []
        return self.TAB_TRIGGERS[tabTrigger]
    
    #---------------------------------------------------
    # KEYEQUIVALENT INTERFACE
    #---------------------------------------------------
    def getAllBundleItemsByKeyEquivalent(self, keyEquivalent):
        '''
            Return a list of key equivalent bundle items
        '''
        if keyEquivalent not in self.KEY_EQUIVALENTS:
            return [] 
        return self.KEY_EQUIVALENTS[keyEquivalent]
    
    #---------------------------------------------------------------
    # SYNTAXES
    #---------------------------------------------------------------
    def getSyntaxes(self, sort = False):
        stxs = []
        for syntax in self.SYNTAXES.values():
            stxs.append(syntax)
        if sort:
            return sorted(stxs, key = lambda s: s.name)
        return stxs
    
    def getSyntaxByScopeName(self, scope):
        if scope in self.SYNTAXES:
            return self.SYNTAXES[scope]
        return None
        
    def findSyntaxByFirstLine(self, line):
        for syntax in self.SYNTAXES.values():
            if syntax.firstLineMatch != None and syntax.firstLineMatch.search(line):
                return syntax
    
    def findSyntaxByFileType(self, path):
        for syntax in self.SYNTAXES.values():
            if type(syntax.fileTypes) == list:
                for t in syntax.fileTypes:
                    if path.endswith(t):
                        return syntax
