from __future__ import absolute_import
from __future__ import print_function
from maya_toolkit.tools.ks_save_timer_v1_3_0 import compat_six as six
from maya_toolkit.tools.ks_save_timer_v1_3_0.qt_compat import QtCore,QtGui,QtWidgets,Signal,Property,wrapInstance
_PYSIDE_VERSION_ = 2

from configparser import ConfigParser
import os
import re

import ks_saveTimer
from ks_saveTimer.lib import Singleton


defaultConfig_user = {
    'timerOptions': {
        'timer_a_starttime': 5,
        'timer_b_starttime': 10,
        'timer_c_starttime': 15,
        'timer_flash_a_starttime': 20,
        'timer_flash_starttime': 20,
        'timer_flash_b_starttime': 20,
        'timer_flash_freq': 750,
        'timer_a_bgcolor': 'rgba(202, 155, 155, 255)',
        'timer_a_textcolor': 'rgba(68, 68, 68, 255)',
        'timer_b_bgcolor': 'rgba(202, 128, 128, 255)',
        'timer_b_textcolor': 'rgba(62, 62, 62, 255)',
        'timer_c_bgcolor': 'rgba(202, 91, 91, 255)',
        'timer_c_textcolor': 'rgba(0, 0, 0, 255)',
        'timer_flash_a_bgcolor': 'rgba(221, 174, 174, 255)',
        'timer_flash_a_textcolor': 'rgba(0, 0, 0, 255)',
        'timer_flash_b_bgcolor': 'rgba(200, 20, 20, 255)',
        'timer_flash_b_textcolor': 'rgba(0, 0, 0, 255)',
        'timer_pause_bgcolor': 'rgba(157, 157, 157, 255)',
        'timer_pause_textcolor': 'rgba(89, 89, 89, 255)',
        'timer_default_bgcolor': 'rgba(137, 137, 137, 255)',
        'timer_default_textcolor': 'rgba(89, 89, 89, 255)',
    },
    'general': {
        'timer_automute': False,
        'timer_autopause': False,
    }

}


class _configuration(QtCore.QObject):
    configUpdated = Signal()

    def __init__(self):
        super(_configuration, self).__init__()

        self._config_path = self.getConfigPath()

        self.parser = ConfigParser(interpolation=None)
        self._DICT_ = {}
        self.readConfigs()
        self.cacheToDict()

    def setCacheDictEnabled(self, state):
        self._cacheDictEnabled = state


    def getConfigPath(self):
        from maya_toolkit.tools.ks_save_timer_v1_3_0.session import data_root
        if data_root is None:raise RuntimeError("Configure state directory first")
        return str(data_root/"ksSaveTimer_config.ini")



    def readConfigs(self):
        if os.path.exists(self._config_path):
            from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import read_config
            self.readDefaultConfig()
            self.parser.read_dict({k:dict(v) for k,v in read_config(self._config_path).items() if k!="DEFAULT"})
            # print 'KS_SaveTimer - Reading config:', self._config_path
        else:
            self.readDefaultConfig()
            print('KS_SaveTimer -  No Config found.')

        self.cacheToDict()
        self.configUpdated.emit()

    def readDefaultConfig(self):
        for section in defaultConfig_user.keys():
            if not self.parser.has_section(section):
                self.parser.add_section(section)
            for key in defaultConfig_user[section].keys():
                self.parser.set(section, key, str(defaultConfig_user[section][key]))

    def writeConfig(self):
        from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import write_config
        return write_config(self._config_path,self.parser)

    def cacheToDict(self):
        config = {}
        for section in self.parser.sections():
            config[section] = {}
            for key, string in self.parser.items(section):
                    config[section][key] = self.get(section, key, useCacheDict=False)
        self._DICT_ = config

    def set(self, section, key, value=''):
        from maya_toolkit.tools.ks_save_timer_v1_3_0.storage import config_value
        config_value(section,key,value)
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        if not self._DICT_.get(section):
            self._DICT_[section] = {}

        data = value

        if type(data) == str:
            self.parser.set(section, key, data)

            if 'rgb' in data:
                qcolor = self.rgbStringToQColor(data)
                self._DICT_[section][key] = qcolor
            elif data in ['True', 'False']:
                self._DICT_[section][key] = data.lower() == 'true'
            elif data.isdigit():
                self._DICT_[section][key] = int(data)

        else:
            self._DICT_[section][key] = data

            if type(data) == QtGui.QColor:
                rgb = 'rgba'+ str(data.getRgb())
                self.parser.set(section, key, rgb)
            else:
                self.parser.set(section, key, str(data))

        self.configUpdated.emit()

    def get(self, section, key, fallback=None, useCacheDict=True):
        data = None
        if useCacheDict:
            if self._DICT_.get(section, {}).get(key):
                data = self._DICT_[section].get(key)


        if not data:
            if self.parser.has_option(section, key):
                data = self.parser.get(section, key)
            else:
                if fallback is not None:
                    self.set(section, key, value=fallback)
                    data = fallback


        if type(data) == str:
            if 'rgb' in data:
                return self.rgbStringToQColor(data)
            elif data.lower() in ['true', 'false']:
                if data == 'True':
                    return True
                else:
                    return False
            elif data.isdigit():
                return int(data)
        else:
            return data


    def rgbStringToQColor(self, data):
        if type(data) == QtGui.QColor:
            return data

        r, g, b, a = [int(x.group()) for x in re.finditer(r'\d+', data)]
        return QtGui.QColor(r, g, b, a)

    # def savePosition(self, widgetObject):
    #     geometry = widgetObject.geometry()
    #     geometryString = str(geometry)
    #     geometryString = geometryString.split('(')[1]
    #     x, y, width, height = [str(x.group()) for x in re.finditer(r'\d+', geometryString)]
    #     geometryData = '(%s, %s, %s, %s)' %(x, y, width, height)
    #     self.set(None, 'widgetPosition', __HOST_APP__, geometryData)
    #     self.writeConfig()

    # def restorePosition(self, widgetObject):
    #     geometryData = self.get(None, 'widgetPosition', __HOST_APP__)
    #     x, y, width, height = [int(x.group()) for x in re.finditer(r'\d+', geometryData)]
    #     geometry = QtCore.QRect(x, y, width, height)
    #     widgetObject.setGeometry(geometry)



_INSTANCE=None
def configuration(*args,**kwargs):
    import sys
    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import singleton
    return singleton(sys.modules[__name__],"configuration",*args,**kwargs)
