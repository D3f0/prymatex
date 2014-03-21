#!/usr/bin/env python
#-*- encoding: utf-8 -*-

import os
import shutil

from prymatex.qt import QtCore

from prymatex.core.config import (PMX_APP_PATH,
                                  get_textmate_preferences_user_path)

from prymatex.core.settings import (TextMateSettings, SettingsGroup,
                                    ConfigurableItem, JSettingsGroup)

PRYMATEX_SETTINGS_NAME = "settings.ini"
PRYMATEX_STATE_NAME = "state.ini"
TEXTMATE_SETTINGS_NAME = "com.macromates.textmate.plist"


class PrymatexProfile(object):
    PMX_SETTING_NAME = PRYMATEX_SETTINGS_NAME
    PMX_STATE_NAME = PRYMATEX_STATE_NAME
    TM_SETTINGS_NAME = TEXTMATE_SETTINGS_NAME
    PMX_PREFERENCES_PATH = get_textmate_preferences_user_path()

    def __init__(self, name, path, default=True):
        self.PMX_PROFILE_NAME = name
        self.PMX_PROFILE_PATH = path
        self.PMX_PROFILE_DEFAULT = default
        self.PMX_TMP_PATH = os.path.join(self.PMX_PROFILE_PATH, 'tmp')
        self.PMX_LOG_PATH = os.path.join(self.PMX_PROFILE_PATH, 'log')
        self.PMX_CACHE_PATH = os.path.join(self.PMX_PROFILE_PATH, 'cache')
        self.PMX_SCREENSHOT_PATH = os.path.join(
            self.PMX_PROFILE_PATH, 'screenshot')
        self.GROUPS = {}
        self.JGROUPS = {}
        self.settings = {}
        
        self.qsettings = QtCore.QSettings(
            os.path.join(self.PMX_PROFILE_PATH, self.PMX_SETTING_NAME),
            QtCore.QSettings.IniFormat)

        self.tmsettings = TextMateSettings(
            os.path.join(self.PMX_PREFERENCES_PATH, self.TM_SETTINGS_NAME))

        self.state = QtCore.QSettings(
            os.path.join(self.PMX_PROFILE_PATH, self.PMX_STATE_NAME),
            QtCore.QSettings.IniFormat)

    # ------------------------ Setting Groups
    def __group_name(self, configurableClass):
        if hasattr(configurableClass, '_settings'):
            return configurableClass._settings.groupName()
        return configurableClass.__dict__['SETTINGS_GROUP'] \
            if 'SETTINGS_GROUP' in configurableClass.__dict__ \
            else configurableClass.__name__

    #Deprecated
    def groupByName(self, name):
        if name not in self.GROUPS:
            self.GROUPS[name] = SettingsGroup(
                name,
                self.qsettings,
                self.tmsettings)
        return self.GROUPS[name]

    def jgroupByName(self, name):
        if name not in self.JGROUPS:
            self.JGROUPS[name] = JSettingsGroup(
                name,
                self.settings.setdefault(name, {}),
                self.tmsettings)
        return self.JGROUPS[name]

    #Deprecated
    def groupByClass(self, configurableClass):
        return self.groupByName(self.__group_name(configurableClass))

    def jgroupByClass(self, configurableClass):
        return self.jgroupByName(self.__group_name(configurableClass))
        
    def registerConfigurable(self, configurableClass):
        # Prepare class group
        # TODO: Una forma de obtener y setear los valores en las settings
        # Las configurableClass tiene que tener esos metodos
        configurableClass._settings = self.groupByClass(configurableClass)
        _settings = self.jgroupByClass(configurableClass)
        # Prepare configurable attributes
        for key, value in configurableClass.__dict__.items():
            if isinstance(value, ConfigurableItem):
                if value.name is None:
                    value.name = key
                configurableClass._settings.addConfigurableItem(value)
                _settings.addConfigurableItem(value)

    def configure(self, component):
        settingsGroup = self.groupByClass(component.__class__)
        settingsGroup.addListener(component)
        settingsGroup.configure(component)
        settingsGroup = self.jgroupByClass(component.__class__)
        settingsGroup.configure(component)

    def saveState(self, component):
        self.state.setValue(component.objectName(), component.componentState())
        self.state.sync()

    def restoreState(self, component):
        state = self.state.value(component.objectName())
        if state:
            component.setComponentState(state)

    def setValue(self, name, value):
        self.qsettings.setValue(name, value)

    def value(self, name, default=None):
        if hasattr(self, name):
            return getattr(self, name)
        return self.qsettings.value(name, default)

    def clear(self):
        self.qsettings.clear()

    def sync(self):
        #Save capture values from qt
        for group in self.GROUPS.values():
            group.sync()
        self.qsettings.sync()
        for group in self.JGROUPS.values():
            group.sync()
