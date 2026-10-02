from __future__ import absolute_import
from maya_toolkit.tools.ks_save_timer_v1_3_0 import compat_six as six
from maya_toolkit.tools.ks_save_timer_v1_3_0.qt_compat import QtCore,QtGui,QtWidgets,Signal,Property,wrapInstance
_PYSIDE_VERSION_ = 2

from ks_saveTimer.lib import Singleton
from ks_saveTimer.libApp import getLibApp as libApp
__LIB_APP__ = libApp.__LIB_APP__


_interval_active = 60000
_interval_idle = 2000

### FOR DEBUGGING:
# _interval_active = 5000
# _interval_idle = 1000


class _timerObject(QtCore.QObject):
    timerStop = Signal()
    timerReset = Signal()
    preSave_addHistory = Signal()
    fileSaved = Signal()

    tick = Signal(int, bool)


    def __init__(self, parent=None):
        super(_timerObject, self).__init__(parent=parent)
        self._MAINTIMER_ = QtCore.QTimer(self)
        self._MAINTIMER_.setInterval(_interval_active)
        self._MAINTIMER_.timeout.connect(self.timeTick)

        if _PYSIDE_VERSION_ == 2:
            self._MAINTIMER_.setTimerType(QtCore.Qt.VeryCoarseTimer)

        self.counter = 0
        self.counterTotal = 0
        self.counterIdle = 0
        self.counterIdleTotal = 0
        self.saveCount = 0
        self.IDLE_MODE = False


        self.idleMode_minuteCounter = 0
        self.idleMode_minuteCounter_target = _interval_active/_interval_idle

        self._applicationWindow = QtWidgets.QApplication.instance()
        self._mouseCursor = QtGui.QCursor()
        self.idleBuffer = 0
        self.idleTarget = 2
        self.mousePositionOld = None

        self.CALLBACKS = __LIB_APP__.appCallbacks()
        self.CALLBACKS.fileSaved.connect(self._fileSaved)
        self.CALLBACKS.fileOpened.connect(self.reset)


    def isActive(self):
        return self._MAINTIMER_.isActive()

    def _fileSaved(self):
        self.preSave_addHistory.emit()
        self.counter = 0
        self.saveCount += 1
        self.fileSaved.emit()


    def start(self):
        self._MAINTIMER_.start()
        self.tick.emit(self.counter, self.IDLE_MODE)


    def stop(self):
        self._MAINTIMER_.stop()
        self.timerStop.emit()


    def toggle(self):
        if self.isActive():
            self.stop()
        else:
            self.start()

    def reset(self):
        self.counter = 0
        self.timerReset.emit()

    def setTime(self, value):
        if type(value) is not int or not 0<=value<=1000000:raise ValueError("Bounded nonnegative timer minutes")
        self.counter = value
        self.tick.emit(self.counter, self.IDLE_MODE)


    def timeTick(self, countUp=True):
        # Detect a change in idle-mode.
        idleState = self.idleCheck()
        if idleState != self.IDLE_MODE:
            self.setIdleState(idleState)

        if self.IDLE_MODE:

            ### Because idleTimer runs faster than once every minute, we need to only count it when it reaches a full minute.
            self.idleMode_minuteCounter += 1
            if not self.idleMode_minuteCounter >= self.idleMode_minuteCounter_target:
                return

            if countUp is True:
                self.idleMode_minuteCounter = 0
                self.counterIdle += 1
                self.counterIdleTotal += 1
            self.tick.emit(self.counterIdle, self.IDLE_MODE)
            return

        else:
            if countUp is True:
                self.idleMode_minuteCounter = 0
                self.counterIdle = self.idleTarget
                self.counter += 1
                self.counterTotal += 1
            self.tick.emit(self.counter, self.IDLE_MODE)
            return


    def setIdleState(self, idleState):
        if idleState == True:
            self.IDLE_MODE = True

            # Subtract the idling that led up to the state-change
            self.counter = max(0,self.counter-self.idleTarget)
            self.counterTotal = max(0,self.counterTotal-self.idleTarget)

            self._MAINTIMER_.setInterval(_interval_idle)
            self.tick.emit(self.counterIdle, self.IDLE_MODE)

        else:
            self.IDLE_MODE = False
            self._MAINTIMER_.setInterval(_interval_active)
            self.tick.emit(self.counter, self.IDLE_MODE)


    def idleCheck(self):
        if self.detect_windowFocus() and self.detect_mouseActivity():
            self.idleBuffer = 0
            return False

        self.idleBuffer += 1
        if self.idleBuffer >= self.idleTarget:
            return True

        return False


    def detect_mouseActivity(self):
        #Checks if mouse has moved since last check.
        mousePos = self._mouseCursor.pos()
        if mousePos == self.mousePositionOld:
            return False
        self.mousePositionOld = mousePos
        return True

    def detect_windowFocus(self):
        # if self._applicationWindow.focusWindow():
        if self._applicationWindow.activeWindow():
            return True
        return False



_INSTANCE=None
def timerObject(*args,**kwargs):
    import sys
    from maya_toolkit.tools.ks_save_timer_v1_3_0.session import singleton
    return singleton(sys.modules[__name__],"timerObject",*args,**kwargs)
