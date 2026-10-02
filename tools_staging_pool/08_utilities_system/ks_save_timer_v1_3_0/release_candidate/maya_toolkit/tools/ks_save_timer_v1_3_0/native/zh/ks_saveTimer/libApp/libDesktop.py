from __future__ import absolute_import
from __future__ import print_function
from maya_toolkit.tools.ks_save_timer_v1_3_0 import compat_six as six
from maya_toolkit.tools.ks_save_timer_v1_3_0.qt_compat import QtCore,QtGui,QtWidgets,Signal,Property,wrapInstance
_PYSIDE_VERSION_ = 2

import os
from ks_saveTimer.lib import Singleton

def QT_getMainWindow():
    return None

def getUserConfigLocation():
    return os.path.expanduser("~")

def displayWarningMessage(message):
    print(message)

def displayStatusMessage(message):
    print(message)


##
## ------------------ Callbacks ------------------
##



class _appCallbacks(QtCore.QObject):
    fileSaved = Signal()
    fileOpened = Signal()

    currentWatchFolder = ''
    currentWatchFile = ''
    currentFileExt = ''

    dirContent = []

    def __init__(cls):
        super(_appCallbacks, cls).__init__()

        cls.systemWatcher = QtCore.QFileSystemWatcher(cls)
        cls.systemWatcher.directoryChanged.connect(cls.checkNewFiles)
        cls.systemWatcher.fileChanged.connect(cls.emitSaveSignal)


    def emitSaveSignal(cls,*args):
        from maya_toolkit.tools.ks_save_timer_v1_3_0 import session
        if args and isinstance(args[0],str) and os.path.isfile(args[0]):session.watched_file=args[0]
        cls.fileSaved.emit()
        cls.signalPrint()

    def checkNewFiles(cls,*args):
        files = cls.listDirectory(cls.currentWatchFolder)
        newFiles = list(set(files) - set(cls.dirContent))
        if newFiles:
            for file in newFiles:
                from maya_toolkit.tools.ks_save_timer_v1_3_0 import session
                session.watched_file=os.path.normpath(os.path.join(cls.currentWatchFolder,file))
                print('newFile:', file)
                cls.systemWatcher.addPath(os.path.normpath(os.path.join(cls.currentWatchFolder, file)))
            cls.emitSaveSignal()
        print('nowWatching - Files:', cls.systemWatcher.files())
        print('nowWatching - Dirs:', cls.systemWatcher.directories())

        cls.dirContent = files



    def setWatchFile(cls, path):
        try:
            cls.systemWatcher.removePaths(cls.systemWatcher.files())
            cls.systemWatcher.removePaths(cls.systemWatcher.directories())
        except:
            print('Failed removing files from systemWatcher!')


        fileExt = os.path.splitext(path)[1]
        cls.currentFileExt = fileExt

        dirPath, fileName = os.path.split(path)
        print('dirPath:', dirPath)
        print('fileName:', fileName)
        cls.currentWatchFolder = dirPath

        files = cls.listDirectory(dirPath)
        print('dir files:', files)
        cls.dirContent = files

        cls.systemWatcher.addPath(dirPath)
        cls.systemWatcher.addPath(path)

        print('Now Watching:', path)

    def listDirectory(cls, path):
        files = []
        for item in os.listdir(path):
            if item.endswith(cls.currentFileExt):
                files.append(item)
        return files

    def signalPrint(cls):
        print('signal has been triggered!', cls.fileSaved)

_INSTANCE=None
def appCallbacks(*args,**kwargs):
    import sys
    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import singleton
    return singleton(sys.modules[__name__],"appCallbacks",*args,**kwargs)

def get_filePath():
    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import current_file
    return current_file()
