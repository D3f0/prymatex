#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, os, string, unicodedata
import uuid as uuidmodule

from glob import glob

from prymatex.support.bundle import PMXBundle, PMXBundleItem
from prymatex.support.macro import PMXMacro
from prymatex.support.syntax import PMXSyntax
from prymatex.support.snippet import PMXSnippet
from prymatex.support.preference import PMXPreference
from prymatex.support.command import PMXCommand, PMXDragCommand
from prymatex.support.template import PMXTemplate, PMXTemplateFile
from prymatex.support.theme import PMXTheme, PMXThemeStyle
from prymatex.support.score import PMXScoreManager
from prymatex.support.utils import ensurePath
from prymatex.support.cache import PMXSupportCache

from prymatex.utils.decorator.helpers import printtime

BUNDLEITEM_CLASSES = [ PMXSyntax, PMXSnippet, PMXMacro, PMXCommand, PMXPreference, PMXTemplate, PMXDragCommand ]

def compare(obj, keys, tests):
    if not len(keys):
        return True
    key = keys[0]
    value = getattr(obj, key, None)
    if value == None or key not in tests:
        return False
    elif isinstance(value, (str, unicode)):
        return value.find(tests[key]) != -1 and compare(obj, keys[1:], tests)
    elif isinstance(value, (int)):
        return value == tests[key] and compare(obj, keys[1:], tests)
    else:
        return value == tests[key] and compare(obj, keys[1:], tests)

class PMXSupportBaseManager(object):
    ELEMENTS = ['Bundles', 'Support', 'Themes']
    VAR_PREFIX = 'PMX'
    PROTECTEDNS = 0         #El primero es el protected
    DEFAULTNS = 1           #El segundo es el default
    VALID_PATH_CARACTERS = "-_.() %s%s" % (string.ascii_letters, string.digits)
    
    SETTINGS_CACHE = {}
    
    def __init__(self):
        self.namespaces = {}
        # Te first is the name space base, and the last is de default for new bundles and items */
        self.nsorder = []
        self.environment = {}
        self.managedObjects = {}
        self.cache = PMXSupportCache()
        self.scores = PMXScoreManager()
    
    #---------------------------------------------------
    # Namespaces
    #---------------------------------------------------
    def addNamespace(self, name, path):
        self.namespaces[name] = {}
        self.nsorder.append(name)
        for element in self.ELEMENTS:
            epath = os.path.join(path, element)
            if not os.path.exists(epath):
                continue
            #Si es el primero es el protegido
            if len(self.nsorder) == 1:
                var = "_".join([ self.VAR_PREFIX, element.upper(), 'PATH' ])
            else:
                var = "_".join([ self.VAR_PREFIX, name.upper(), element.upper(), 'PATH' ])
            self.namespaces[name][element] = self.environment[var] = epath
        return name

    @property
    def protectedNamespace(self):
        return self.nsorder[self.PROTECTEDNS]
        
    @property
    def defaultNamespace(self):
        if len(self.nsorder) < 2:
            raise Exception("No default namespace")
        return self.nsorder[self.DEFAULTNS]

    def updateEnvironment(self, env):
        self.environment.update(env)

    def buildEnvironment(self):
        return self.environment.copy()
    
    def basePath(self, element, namespace):
        if namespace not in self.namespaces:
            raise Exception("The %s namespace is not registered" % namespace)
        if element in self.namespaces[namespace]:
            return self.namespaces[namespace][element]
    
    #---------------------------------------------------
    # Tools
    #---------------------------------------------------
    def uuidgen(self, uuid = None):
        # TODO: ver que el uuid generado no este entre los elementos existentes
        if uuid is None:
            return uuidmodule.uuid1()
        try:
            return uuidmodule.UUID(uuid)
        except ValueError:
            #generate
            return uuidmodule.uuid3(uuidmodule.NAMESPACE_DNS, uuid)

    def convertToValidPath(self, name):
        validPath = []
        for char in unicodedata.normalize('NFKD', unicode(name)).encode('ASCII', 'ignore'):
            char = char if char in self.VALID_PATH_CARACTERS else '-'
            validPath.append(char)
        return ''.join(validPath)

    #---------------------------------------------------
    # Message Handler
    #---------------------------------------------------
    def showMessage(self, message):
        if self.messageHandler is not None:
            self.messageHandler(message)

    #---------------------------------------------------
    # LOAD ALL SUPPORT
    #---------------------------------------------------
    def loadSupport(self, callback = None):
        # Install message handler
        self.messageHandler = callback
        for ns in self.nsorder[::-1]:
            self.loadThemes(ns)
            self.loadBundles(ns)
        for bundle in self.getAllBundles():
            if bundle.enabled:
                self.populateBundle(bundle)
        # Uninstall message handler
        self.messageHandler = None

    #---------------------------------------------------
    # LOAD THEMES
    #---------------------------------------------------
    def loadThemes(self, namespace):
        if 'Themes' in self.namespaces[namespace]:
            paths = glob(os.path.join(self.namespaces[namespace]['Themes'], '*.tmTheme'))
            for path in paths:
                PMXTheme.loadTheme(path, namespace, self)

    #---------------------------------------------------
    # LOAD BUNDLES
    #---------------------------------------------------
    def loadBundles(self, namespace):
        if 'Bundles' in self.namespaces[namespace]:
            paths = glob(os.path.join(self.namespaces[namespace]['Bundles'], '*.tmbundle'))
            for path in paths:
                PMXBundle.loadBundle(path, namespace, self)

    #---------------------------------------------------
    # POPULATE BUNDLE AND LOAD BUNDLE ITEMS
    #---------------------------------------------------
    def populateBundle(self, bundle):
        nss = bundle.namespaces[::-1]
        for namespace in nss:
            bpath = os.path.join(self.namespaces[namespace]['Bundles'], os.path.basename(bundle.path))
            # Search for support
            if bundle.support == None and os.path.exists(os.path.join(bpath, 'Support')):
                bundle.setSupport(os.path.join(bpath, 'Support'))
            self.showMessage("Loading bundle %s" % bundle.name)
            for klass in BUNDLEITEM_CLASSES:
                files = reduce(lambda x, y: x + glob(y), [ os.path.join(bpath, klass.FOLDER, file) for file in klass.PATTERNS ], [])
                for path in files:
                    klass.loadBundleItem(path, namespace, bundle, self)
        bundle.populated = True

    #---------------------------------------------------
    # RELOAD SUPPORT
    #---------------------------------------------------
    def reloadSupport(self, callback = None):
        # Install message handler
        self.messageHandler = callback
        for ns in self.nsorder[::-1]:
            self.reloadThemes(ns)
            self.reloadBundles(ns)
        for bundle in self.getAllBundles():
            if bundle.enabled:
                self.repopulateBundle(bundle)
        # Uninstall message handler
        self.messageHandler = None
    
    #---------------------------------------------------
    # RELOAD THEMES
    #---------------------------------------------------
    def reloadThemes(self, namespace):
        themes = filter(lambda theme: theme.hasNamespace(namespace), self.getAllThemes())
        if 'Themes' in self.namespaces[namespace]:
            paths = glob(os.path.join(self.namespaces[namespace]['Themes'], '*.tmTheme'))
            for path in paths:
                self.showMessage(path)
                #PMXTheme.reloadTheme(path, namespace, self)
    
    #---------------------------------------------------
    # RELOAD BUNDLES
    #---------------------------------------------------
    def reloadBundles(self, namespace):
        if 'Bundles' in self.namespaces[namespace]:
            paths = glob(os.path.join(self.namespaces[namespace]['Bundles'], '*.tmbundle'))
            for path in paths:
                self.showMessage(path)
                #PMXBundle.reloadBundle(path, namespace, self)
    
    #---------------------------------------------------
    # POPULATE BUNDLE AND LOAD BUNDLE ITEMS
    #---------------------------------------------------
    def repopulateBundle(self, bundle):
        nss = bundle.namespaces[::-1]
        for namespace in nss:
            bpath = os.path.join(self.namespaces[namespace]['Bundles'], os.path.basename(bundle.path))
            # Search for support
            if bundle.support == None and os.path.exists(os.path.join(bpath, 'Support')):
                bundle.setSupport(os.path.join(bpath, 'Support'))
            self.showMessage("Loading bundle %s" % bundle.name)
            for klass in BUNDLEITEM_CLASSES:
                files = reduce(lambda x, y: x + glob(y), [ os.path.join(bpath, klass.FOLDER, file) for file in klass.PATTERNS ], [])
                for path in files:
                    self.showMessage(path)
                    #klass.loadBundleItem(path, namespace, bundle, self)
        bundle.populated = True
        
    #---------------------------------------------------
    # MANAGED OBJECTS INTERFACE
    #---------------------------------------------------
    def setDeleted(self, uuid):
        """
        Marcar un managed object como eliminado
        """
        pass
        
    def isDeleted(self, uuid):
        """
        Retorna si un bundle item esta eliminado
        """
        return False

    def isEnabled(self, uuid):
        """
        Retorna si un bundle item esta activo
        """
        return True
    
    def setDisabled(self, uuid):
        pass
        
    def setEnabled(self, uuid):
        pass
    
    def addManagedObject(self, obj):
        obj.setManager(self)
        self.managedObjects[obj.uuid] = obj
        
    def getManagedObject(self, uuid):
        if not isinstance(uuid, uuidmodule.UUID):
            uuid = uuidmodule.UUID(uuid)
        return self.managedObjects.get(uuid, None)
    
    #---------------------------------------------------
    # BUNDLE INTERFACE
    #---------------------------------------------------
    def addBundle(self, bundle):
        return bundle
        
    def modifyBundle(self, bundle):
        """
        Llamado luego de modificar un bundle
        """
        pass

    def removeBundle(self, bundle):
        """
        Llamado luego de eliminar un bundle
        """
        pass

    def getAllBundles(self):
        return []
    
    #---------------------------------------------------
    # BUNDLE CRUD
    #---------------------------------------------------
    def findBundles(self, **attrs):
        """
        Retorna todos los bundles que cumplan con attrs
        """
        bundles = []
        for bundle in self.getAllBundles():
            if compare(bundle, attrs.keys(), attrs):
                bundles.append(bundle)
        return bundles
    
    def createBundle(self, name, namespace = None):
        """
        Crea un bundle nuevo lo agrega en los bundles y lo retorna,
        Precondiciones:
            Tenes por lo menos dos espacios de nombre el base o proteguido y uno donde generar los nuevos bundles
            El nombre tipo Title.
            El nombre no este entre los nombres ya cargados.
        Toma el ultimo espacio de nombres creado como espacio de nombre por defecto para el bundle nuevo.
        """
        namespace = namespace or self.defaultNamespace
        basePath = self.basePath("Bundles", namespace)
        path = ensurePath(os.path.join(basePath, "%s.tmbundle"), self.convertToValidPath(name))
        bundle = PMXBundle(self.uuidgen(), namespace, { 'name': name }, path)
        bundle = self.addBundle(bundle)
        self.addManagedObject(bundle)
        return bundle
    
    def readBundle(self, **attrs):
        """
        Retorna un bundle por sus atributos
        """
        bundles = self.findBundles(**attrs)
        if len(bundles) > 1:
            raise Exception("More than one bundle")
        return bundles[0]
    
    def getBundle(self, uuid):
        return self.getManagedObject(uuid)
    
    def updateBundle(self, bundle, namespace = None, **attrs):
        """
        Actualiza un bundle
        """
        if len(attrs) == 1 and "name" in attrs and attrs["name"] == bundle.name:
            #Updates que no son updates
            return bundle
        if bundle.isProtected:
            if not bundle.isSafe:
                namespace = namespace or self.defaultNamespace
                basePath = self.basePath("Bundles", namespace)
                path = os.path.join(basePath, os.path.basename(bundle.path))
                bundle.addSource(namespace, path)
        else:
            if "name" in attrs:
                path = ensurePath(os.path.join(os.path.dirname(bundle.path), "%s.tmbundle"), self.convertToValidPath(attrs["name"]))
                bundle.relocate(path)
        bundle.update(attrs)
        bundle.save()
        self.modifyBundle(bundle)
        return bundle
        
    def deleteBundle(self, bundle):
        """
        Elimina un bundle, si el bundle es del namespace proteguido no lo elimina sino que lo marca como eliminado
        """
        items = self.findBundleItems(bundle = bundle)

        #Primero los items
        for item in items:
            self.deleteBundleItem(item)
        if bundle.isProtected:
            if bundle.isSafe:
                bundle.delete()
            self.setDeleted(bundle.uuid)
        else:
            bundle.delete()
        self.removeBundle(bundle)
    
    def disableBundle(self, bundle, disabled):
        bundle.enabled = not bool(disabled)
        if not bundle.enabled:
            self.setDisabled(bundle.uuid)
        else:
            self.setEnabled(bundle.uuid)
            if not bundle.populated:
                self.populateBundle(bundle)
    
    #---------------------------------------------------
    # BUNDLEITEM INTERFACE
    #---------------------------------------------------
    def addBundleItem(self, bundleItem):
        return bundleItem
        
    def modifyBundleItem(self, bundleItem):
        pass

    def removeBundleItem(self, bundleItem):
        pass
    
    def getAllBundleItems(self):
        return []
        
    #---------------------------------------------------
    # BUNDLEITEM CRUD
    #---------------------------------------------------
    def findBundleItems(self, **attrs):
        """
        Retorna todos los items que complan las condiciones en attrs
        """
        items = []
        for item in self.getAllBundleItems():
            if compare(item, attrs.keys(), attrs):
                items.append(item)
        return items

    def createBundleItem(self, name, tipo, bundle, namespace = None):
        """
        Crea un bundle item nuevo lo agrega en los bundle items y lo retorna,
        Precondiciones:
            Tenes por lo menos dos nombres en el espacio de nombres
            El tipo tiene que ser uno de los conocidos
        Toma el ultimo espacio de nombres creado como espacio de nombre por defecto para el bundle item nuevo.
        """
        namespace = namespace or self.defaultNamespace
        if bundle.isProtected and not bundle.isSafe:
            self.updateBundle(bundle, namespace)
        klass = filter(lambda c: c.TYPE == tipo, BUNDLEITEM_CLASSES)
        if len(klass) != 1:
            raise Exception("No class type for %s" % tipo)
        klass = klass.pop()
        path = os.path.join(bundle.path, klass.FOLDER, "%s.%s" % (self.convertToValidPath(name), klass.EXTENSION))

        item = klass(self.uuidgen(), { 'name': name })
        item.setBundle(bundle)
        item = self.addBundleItem(item)
        self.addManagedObject(item)
        item.addSource(namespace, path)
        return item
    
    def readBundleItem(self, **attrs):
        """
        Retorna un bundle item por sus atributos
        """
        items = self.findBundleItems(**attrs)
        if len(items) > 1:
            raise Exception("More than one bundle item")
        return items[0]
    
    def getBundleItem(self, uuid):
        return self.getManagedObject(uuid)
    
    def updateBundleItem(self, item, namespace = None, **attrs):
        """
        Actualiza un bundle item
        """
        if len(attrs) == 1 and "name" in attrs and attrs["name"] == item.name:
            #Updates que no son updates
            return item

        #Deprecate keyEquivalent in cache
        if 'keyEquivalent' in attrs and item.keyEquivalent != attrs['keyEquivalent']:
            self.cache.deprecateValues(item.keyEquivalent, attrs['keyEquivalent'])

        #Deprecate tabTrigger in cache
        if 'tabTrigger' in attrs and item.tabTrigger != attrs['tabTrigger']:
            self.cache.deprecateValues(item.tabTrigger, attrs['tabTrigger'])

        namespace = namespace or self.defaultNamespace
        if item.bundle.isProtected and not item.bundle.isSafe:
            self.updateBundle(item.bundle, namespace)
        if item.isProtected:
            if not item.isSafe:
                path = os.path.join(item.bundle.path, item.FOLDER, os.path.basename(item.path))
                item.addSource(namespace, path)
        else:
            if "name" in attrs:
                namePattern = "%%s.%s" % item.EXTENSION if item.EXTENSION else "%s"
                path = ensurePath(os.path.join(item.bundle.path, item.FOLDER, namePattern), self.convertToValidPath(attrs["name"]))
                item.relocate(path)
        item.update(attrs)
        item.save()
        self.modifyBundleItem(item)
        return item
    
    def deleteBundleItem(self, item):
        """
        Elimina un bundle por su uuid,
        si el bundle es del namespace proteguido no lo elimina sino que lo marca como eliminado
        """
        #Si el espacio de nombres es distinto al protegido lo elimino
        if item.isProtected:
            if item.isSafe:
                item.delete()
            self.setDeleted(item.uuid)
        else:
            item.delete()
        self.removeBundleItem(item)
        
    #---------------------------------------------------
    # TEMPLATEFILE INTERFACE
    #---------------------------------------------------
    def addTemplateFile(self, file):
        return file
    
    def removeTemplateFile(self, file):
        pass
    
    #---------------------------------------------------
    # TEMPLATEFILE CRUD
    #---------------------------------------------------
    def createTemplateFile(self, name, template):
        if template.isProtected and not template.isSafe:
            self.updateBundleItem(template)
        path = ensurePath(os.path.join(template.path, "%s"), self.convertToValidPath(name))
        file = PMXTemplateFile(path, template)
        #No es la mejor forma pero es la forma de guardar el archivo
        file = self.addTemplateFile(file)
        template.files.append(file)
        file.save()
        return file

    def updateTemplateFile(self, templateFile, **attrs):
        template = templateFile.template
        if template.isProtected and not template.isSafe:
            self.updateBundleItem(template)
        if "name" in attrs:
            path = ensurePath(os.path.join(template.path, "%s"), self.convertToValidPath(attrs["name"]))
            templateFile.relocate(path)
            attrs.pop("name")
        templateFile.update(attrs)
        return templateFile

    def deleteTemplateFile(self, templateFile):
        template = templateFile.template
        if template.isProtected and not template.isSafe:
            self.deleteBundleItem(template)
        self.removeTemplateFile(templateFile)
    
    #---------------------------------------------------
    # THEME INTERFACE
    #---------------------------------------------------
    def addTheme(self, theme):
        return theme
    
    def modifyTheme(self, theme):
        pass
        
    def removeTheme(self, theme):
        pass
        
    def getAllThemes(self):
        return []
    
    #---------------------------------------------------
    # THEME CRUD
    #---------------------------------------------------
    def findThemes(self, **attrs):
        """
        Retorna todos los themes que complan las condiciones en attrs
        """
        items = []
        for item in self.getAllThemes():
            if compare(item, attrs.keys(), attrs):
                items.append(item)
        return items

    def createTheme(self, name, namespace = None):
        if len(self.nsorder) < 2:
            return None
        if namespace is None: namespace = self.defaultNamespace
        path = os.path.join(self.namespaces[namespace]['Themes'], "%s.tmTheme" % self.convertToValidPath(name))
        theme = PMXTheme(self.uuidgen(), namespace, { 'name': name }, path)
        theme = self.addTheme(theme)
        self.addManagedObject(theme)
        return theme

    def readTheme(self, **attrs):
        """
        Retorna un bundle item por sus atributos
        """
        items = self.findThemes(**attrs)
        if len(items) > 1:
            raise Exception("More than one theme")
        return items[0]
    
    def getTheme(self, uuid):
        return self.getManagedObject(uuid)
    
    def updateTheme(self, theme, **attrs):
        """
        Actualiza un themes
        """
        if theme.isProtected:
            if not theme.isSafe:
                namespace = self.defaultNamespace
                path = os.path.join(self.namespaces[namespace]['Themes'], os.path.basename(theme.path))
                theme.addSource(namespace, path)
        else:
            if "name" in attrs:
                path = ensurePath(os.path.join(os.path.dirname(theme.path), "%s.tmTheme"), self.convertToValidPath(attrs["name"]))
                theme.relocate(path)
        theme.update(attrs)
        theme.save()
        self.modifyTheme(theme)
        return theme
        
    def deleteTheme(self, theme):
        """
        Elimina un theme por su uuid
        """
        self.removeTheme(theme)
        #Si el espacio de nombres es distinto al protegido lo elimino
        if theme.isProtected:
            if theme.isSafe:
                pass #TODO: Borrar archivos en safe zones
            self.setDeleted(theme.uuid)
        else:
            theme.delete()
    
    #---------------------------------------------------
    # THEMESTYLE INTERFACE
    #---------------------------------------------------
    def addThemeStyle(self, style):
        return style
    
    def removeThemeStyle(self, style):
        pass
    
    #---------------------------------------------------
    # THEMESTYLE CRUD
    #---------------------------------------------------
    def createThemeStyle(self, name, scope, theme):
        if theme.isProtected and not theme.isSafe:
            self.updateTheme(theme)
        style = PMXThemeStyle({'name': name, 'scope': scope, 'settings': {}}, theme)
        style = self.addThemeStyle(style)
        theme.styles.append(style)
        theme.save()
        return style

    def updateThemeStyle(self, style, **attrs):
        theme = style.theme
        if theme.isProtected and not theme.isSafe:
            self.updateTheme(theme)
        style.update(attrs)
        theme.save()
        self.modifyTheme(theme)
        return style

    def deleteThemeStyle(self, style):
        theme = style.theme
        if theme.isProtected and not theme.isSafe:
            self.updateTheme(theme)
        theme.styles.remove(style)
        theme.save()
        self.removeThemeStyle(style)
        
    #---------------------------------------------------
    # PREFERENCES INTERFACE
    #---------------------------------------------------
    def getAllPreferences(self):
        """
        Return a list of all preferences bundle items
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------
    # PREFERENCES
    #---------------------------------------------------------------
    def getPreferences(self, scope):
        with_scope = []
        without_scope = []
        for preference in self.cache.setcallable("preferences", self.getAllPreferences):
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
        if not self.cache.hasSettings(scope):
            preferences = self.getPreferences(scope)
            self.cache.setSettings(scope, PMXPreference.buildSettings(preferences))
        return self.cache.getSettings(scope)
    
    #---------------------------------------------------
    # TABTRIGGERS INTERFACE
    #---------------------------------------------------
    def getAllTabTriggerItems(self):
        """
        Return a list of all tab triggers
        ['class', 'def', ...]
        """
        raise NotImplementedError
    
    def getAllBundleItemsByTabTrigger(self, tabTrigger):
        """
        Return a list of tab triggers bundle items
        """
        raise NotImplementedError
    
    #---------------------------------------------------------------
    # TABTRIGGERS
    #---------------------------------------------------------------
    @printtime
    def getTabTriggerSymbol(self, line, index):
        line = line[:index][::-1]
        tabTriggerItems = self.cache.setcallable("tabtriggers", self.getAllTabTriggerItems)
        search = map(lambda item: (item.tabTrigger, line.find(item.tabTrigger[::-1]), len(item.tabTrigger)), tabTriggerItems)
        search = filter(lambda (trigger, value, length): value == 0, search)
        if search:
            best = ("", 0)
            for trigger, value, length in search:
                if length > best[1]:
                    best = (trigger, length)
            return best[0]

    @printtime
    def getAllTabTiggerItemsByScope(self, scope):
        with_scope = []
        without_scope = []
        for item in self.cache.setcallable("tabtriggers", self.getAllTabTriggerItems):
            if item.scope == None:
                without_scope.append(item)
            else:
                score = self.scores.score(item.scope, scope)
                if score != 0:
                    with_scope.append((score, item))
        with_scope.sort(key = lambda t: t[0], reverse = True)
        with_scope = map(lambda (score, item): item, with_scope)
        return with_scope + without_scope

    @printtime
    def getTabTriggerItem(self, keyword, scope):
        with_scope = []
        without_scope = []
        for item in self.cache.setcallable(keyword, self.getAllBundleItemsByTabTrigger, keyword):
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
        """
        Return a list of key equivalent bundle items
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------
    # KEYEQUIVALENT
    #---------------------------------------------------------------
    @printtime
    def getKeyEquivalentItem(self, code, scope):
        with_scope = []
        without_scope = []
        for item in self.cache.setcallable(code, self.getAllBundleItemsByKeyEquivalent, code):
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
    # FILE EXTENSION INTERFACE
    #---------------------------------------------------
    def getAllBundleItemsByFileExtension(self, path):
        """
        Return a list of file extension bundle items
        """
        raise NotImplementedError
        
    #---------------------------------------------------------------
    # FILE EXTENSION, for drag commands
    #---------------------------------------------------------------
    @printtime
    def getFileExtensionItem(self, path, scope):
        with_scope = []
        without_scope = []
        for item in self.getAllBundleItemsByFileExtension(path):
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
    # ACTION ITEMS INTERFACE
    #---------------------------------------------------
    def getAllActionItems(self):
        """
        Return action items
        """
        raise NotImplementedError
    
    #---------------------------------------------------------------
    # ACTION ITEMS FOR SCOPE
    #---------------------------------------------------------------
    @printtime
    def getActionItems(self, scope):
        """
        Return a list of actions items for scope and without scope
        """
        with_scope = []
        without_scope = []
        for item in self.getAllActionItems():
            if item.scope == None:
                without_scope.append(item)
            else:
                score = self.scores.score(item.scope, scope)
                if score != 0:
                    with_scope.append((score, item))
        with_scope.sort(key = lambda t: t[0], reverse = True)
        with_scope = map(lambda (score, item): item, with_scope)
        return with_scope + without_scope
    
    #---------------------------------------------------
    # SYNTAXES INTERFACE
    #---------------------------------------------------
    def getAllSyntaxes(self):
        raise NotImplementedError
    
    #---------------------------------------------------------------
    # SYNTAXES
    #---------------------------------------------------------------
    def getSyntaxesAsDictionary(self):
        return dict(map(lambda syntax: (syntax.scopeName, syntax), self.getAllSyntaxes()))
    
    def getSyntaxes(self, sort = False):
        stxs = []
        for syntax in self.getAllSyntaxes():
            stxs.append(syntax)
        if sort:
            return sorted(stxs, key = lambda s: s.name)
        return stxs
    
    def getSyntaxByScopeName(self, scopeName):
        syntaxes = self.getSyntaxesAsDictionary()
        if scopeName in syntaxes:
            return syntaxes[scopeName]
        return None
        
    def findSyntaxByFirstLine(self, line):
        for syntax in self.getAllSyntaxes():
            if syntax.firstLineMatch != None and syntax.firstLineMatch.search(line):
                return syntax
    
    def findSyntaxByFileType(self, path):
        for syntax in self.getAllSyntaxes():
            if type(syntax.fileTypes) == list:
                for t in syntax.fileTypes:
                    if path.endswith(t):
                        return syntax

#===================================================
# PYTHON MANAGER
#===================================================
class PMXSupportPythonManager(PMXSupportBaseManager):
    BUNDLES = {}
    BUNDLE_ITEMS = {}
    THEMES = {}
    SYNTAXES = {}
    TAB_TRIGGERS = {}
    KEY_EQUIVALENTS = {}
    DRAGS = []
    PREFERENCES = []
    TEMPLATES = []
    
    def __init__(self):
        super(PMXSupportPythonManager, self).__init__()
    
    #---------------------------------------------------
    # BUNDLE INTERFACE
    #---------------------------------------------------
    def addBundle(self, bundle):
        '''
        @param bundle: PMXBundle instance
        '''
        self.BUNDLES[bundle.uuid] = bundle
        return bundle

    def modifyBundle(self, bundle):
        pass

    def removeBundle(self, bundle):
        '''
        @param bundle: PMXBundle instance
        '''
        self.BUNDLES.pop(bundle.uuid)

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
        return item

    def modifyBundleItem(self, item):
        pass

    def removeBundleItem(self, item):
        self.BUNDLE_ITEMS.pop(item.uuid)
    
    def getAllBundleItems(self):
        return self.BUNDLE_ITEMS.values()
        
    #---------------------------------------------------
    # THEME INTERFACE
    #---------------------------------------------------
    def addTheme(self, theme):
        self.THEMES[theme.uuid] = theme
        return theme
        
    def modifyTheme(self, theme):
        pass
        
    def removeTheme(self, theme):
        self.THEMES.pop(theme.uuid)

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
        """
        Return a list of tab triggers
        ['class', 'def', ...]
        """
        return self.TAB_TRIGGERS.keys()
    
    def getAllBundleItemsByTabTrigger(self, tabTrigger):
        """
        Return a list of tab triggers bundle items
        """
        if tabTrigger not in self.TAB_TRIGGERS:
            return []
        return self.TAB_TRIGGERS[tabTrigger]
    
    #---------------------------------------------------
    # KEYEQUIVALENT INTERFACE
    #---------------------------------------------------
    def getAllBundleItemsByKeyEquivalent(self, keyEquivalent):
        """
        Return a list of key equivalent bundle items
        """
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

    def findSyntaxByFileType(self, suffix):
        for syntax in self.SYNTAXES.values():
            if type(syntax.fileTypes) == list:
                for t in syntax.fileTypes:
                    if suffix.endswith(t):
                        return syntax
