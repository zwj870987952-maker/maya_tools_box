from __future__ import absolute_import
from maya_toolkit.tools.ks_save_timer_v1_3_0.qt_compat import QtCore,QtGui,QtWidgets,Signal,Property,wrapInstance
_PYSIDE_VERSION_ = 2


class SingletonMetaclass(type):
    '''Basic Singleton metaclass'''
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # print 'Init - CALL:', cls
            cls._instances[cls] = super(SingletonMetaclass, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class QtSingletonMetaclass(SingletonMetaclass, type(QtCore.QObject)):
    '''QObject-Compatible singleton metaclass'''
    pass
