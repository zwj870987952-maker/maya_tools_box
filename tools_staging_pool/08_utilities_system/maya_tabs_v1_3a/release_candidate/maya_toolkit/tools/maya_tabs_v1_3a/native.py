import os
import json
import ctypes
import logging
from maya_toolkit.tools.maya_tabs_v1_3a.qt_compat import QtCore,QtWidgets,QtGui
from maya_toolkit.tools.maya_tabs_v1_3a.qt_compat import wrapInstance,isValid
from maya_toolkit.tools.maya_tabs_v1_3a.session import cmds
from maya.OpenMayaUI import MQtUtil
from maya.api import OpenMayaUI as omui, OpenMaya as om
from uuid import getnode as get_mac
from maya_toolkit.tools.maya_tabs_v1_3a.session import versions
try:
    long
    PY = 2
except NameError:
    long = int
    PY = 3
log = logging.getLogger('MayaTabs')
mayaTabsSerialWindowName = 'MTB_mayaTabsSerial'
mayaTabsMainWindowName = 'MTB_mayaTabsMain'
from pathlib import Path
scriptPath = str(Path(__file__).parent/'resources')
scriptPath23 = os.path.expanduser('~/Documents/maya/plug-ins/Maya-Tabs_Files')

mayaTabslogo = scriptPath + '/' + 'Maya-Tabs.jpg'
mayaTabsIcon = scriptPath + '/' + 'Maya-Tabs_icon.png'
mayaTabsIconSave = scriptPath + '/' + 'icon_save.png'
mayaTabsIconOpen = scriptPath + '/' + 'icon_open.png'
mayaTabsIconAdd = scriptPath + '/' + 'icon_add.png'
mayaTabsThemesDir = scriptPath + '/' + 'Themes'
mayaTabsSerialFile = scriptPath + '/' + 'serial.cfg'
mayaTabsSerialConfigFile = scriptPath + '/' + 'mayatabs_51x56.config'
mayaTabsSettingsFile = scriptPath + '/' + 'Maya-Tabs.ini'
__ = type('This', (object,), {})()
__.callbacks = []
__.settings_fname = mayaTabsSettingsFile
__.new_tab = lambda O0OO0O0O0OOO000O0: {'name': O0OO0O0O0OOO000O0, 'fname': '', 'autosave': False, 'active': False, 'thumbnail': ''}
__.default_style = {'width': '200', 'height': '25', 'tabColor': '#707070', 'tabColorActive': '#058888', 'tabColorHasFile': '#566f6f'}
__.settings = {'version': '1.1.0', 'animated': True, 'tooltipDelay': 10, 'tabs': [__.new_tab('Tab-%d' % O00O0O00O0O0OO00O) for O00O0O00O0O0OO00O in range(8)], 'currentTabIndex': 0, 'lastSaveDir': os.path.expanduser('~'), 'style': dict(__.default_style)}
__.style = '\n\nTab {\n\tmin-width: %(width)s;\n\tmin-height: %(height)s;\n\tmargin-right: 5px;\n\tpadding: 5px;\n\tborder: 1px solid transparent;\n\tbackground: %(tabColor)s;\n}\n\nTab[hasFile=true] {\n\tbackground: %(tabColorHasFile)s;\n}\n\nTab[active=true] {\n\tbackground: %(tabColorActive)s;\n\tborder: 1px solid #666666;\n}\n\nTab[autosave=true][active=true] {\n\tbackground: #ff0000;\n\tborder: 1px solid #ff5555;\n}\n\nTab[autosave=true][active=false] {\n\tbackground: #8d1414;\n\tborder: 1px solid transparent;\n}\n\nTooltip {\n\tbackground: %(tabColorHasFile)s;\n\tpadding: 5px;\n}\n\n'

def _OOO00OO0O00000OO0():
    from maya_toolkit.tools.maya_tabs_v1_3a.session import save_settings
    return save_settings()

def _OO0O000O0OO0O000O():
    from maya_toolkit.tools.maya_tabs_v1_3a.session import read_settings
    return read_settings()
__.save = _OOO00OO0O00000OO0
__.load = _OO0O000O0OO0O000O

class Tab(QtWidgets.QPushButton):
    entered = QtCore.Signal()
    exited = QtCore.Signal()
    ctrl_clicked = QtCore.Signal()
    cleared = QtCore.Signal()
    delete = QtCore.Signal()
    open_folder = QtCore.Signal()

    def mouseReleaseEvent(O00000OOOO0O0OOO0, OO0O00OOO0O00OO0O):
        if OO0O00OOO0O00OO0O.button() == QtCore.Qt.MiddleButton:
            O00000OOOO0O0OOO0.cleared.emit()
        if OO0O00OOO0O00OO0O.button() == QtCore.Qt.LeftButton:
            if OO0O00OOO0O00OO0O.modifiers() & QtCore.Qt.ControlModifier:
                O00000OOOO0O0OOO0.ctrl_clicked.emit()
                OO0O00OOO0O00OO0O.accept()
        return super(Tab, O00000OOOO0O0OOO0).mouseReleaseEvent(OO0O00OOO0O00OO0O)

    def enterEvent(O0000O00000OOO0O0, O000O00O000OOOO00):
        O0000O00000OOO0O0.entered.emit()

    def leaveEvent(O00OOO0O0OOO0O00O, O0000O0OO0O000O0O):
        O00OOO0O0OOO0O00O.exited.emit()

    def contextMenuEvent(OO000OO00O0OO0OOO, O00OOOOO0O000OOO0):
        OOOO00O0OOO00O0OO = QtWidgets.QMenu()
        OOOOO000OO00000O0 = OOOO00O0OOO00O0OO.addAction('Delete tab')
        O0O0O0OO0OOOO00O0 = OOOO00O0OOO00O0OO.addAction('Clear tab')
        O0O0O00OOOOOO0O00 = OOOO00O0OOO00O0OO.addSeparator()
        O000OOOOOOOOO00O0 = OOOO00O0OOO00O0OO.addAction('Open Folder...')
        OOOOO000OO00000O0.triggered.connect(OO000OO00O0OO0OOO.delete.emit)
        O0O0O0OO0OOOO00O0.triggered.connect(OO000OO00O0OO0OOO.cleared.emit)
        O000OOOOOOOOO00O0.triggered.connect(OO000OO00O0OO0OOO.open_folder.emit)
        OOOO00O0OOO00O0OO.move(QtGui.QCursor.pos())
        OOOO00O0OOO00O0OO.exec()

class Tooltip(QtWidgets.QLabel):

    def __init__(OOOOO0000OOO0O000, parent=None):
        super(Tooltip, OOOOO0000OOO0O000).__init__(parent, QtCore.Qt.ToolTip)
        OOOOO0000OOO0O000.setScaledContents(True)

class MayaTabs(QtWidgets.QToolBar):
    instance = None

    def __init__(OOOOOO00OOO0O000O, parent=None):
        super(MayaTabs, OOOOOO00OOO0O000O).__init__(parent)
        OOOOOO00OOO0O000O.setAttribute(QtCore.Qt.WA_StyledBackground)
        OOOOOO00OOO0O000O.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        OOOOOO00OOO0O000O.setWindowTitle('Maya Tabs')
        OOOO0OO0O0O0000OO = OOOOOO00OOO0O000O.addAction(QtGui.QIcon(mayaTabsIcon), 'Maya Tabs')
        O00O0OOOOO00OO000 = OOOOOO00OOO0O000O.addAction(QtGui.QIcon(mayaTabsIconOpen), 'Load')
        OOOO000OOOOO0O000 = OOOOOO00OOO0O000O.addAction(QtGui.QIcon(mayaTabsIconSave), 'Save')
        OO00O0O00000O0000 = OOOOOO00OOO0O000O.addAction(QtGui.QIcon(mayaTabsIconAdd), '+')
        OOOO0OO0O0O0000OO.triggered.connect(OOOOOO00OOO0O000O.on_logo_session)
        O00O0OOOOO00OO000.triggered.connect(OOOOOO00OOO0O000O.on_load_session)
        OOOO000OOOOO0O000.triggered.connect(OOOOOO00OOO0O000O.on_save_session)
        OO00O0O00000O0000.triggered.connect(OOOOOO00OOO0O000O.on_new_tab)
        O00O0OOOOO00OO000.setToolTip('Load a Maya Tabs session from disk')
        OOOO000OOOOO0O000.setToolTip('Save a Maya Tabs session to disk')
        OO00O0O00000O0000.setToolTip('Add a new tab')
        MayaTabs.instance = OOOOOO00OOO0O000O
        O0OOOO0O000000O0O = Tooltip(OOOOOO00OOO0O000O)
        O0OOOO0O000000O0O.hide()
        OOOOOO00OOO0O000O._tooltip = O0OOOO0O000000O0O
        OOOOOO00OOO0O000O._slots = []
        OOOOOO00OOO0O000O._current_slot = None
        O000OO0O0OO0O00O0 = QtCore.QPropertyAnimation(O0OOOO0O000000O0O, b'pos')
        O000OO0O0OO0O00O0.setDuration(200)
        O000OO0O0OO0O00O0.setEasingCurve(QtCore.QEasingCurve.OutQuart)
        OOOOOO00OOO0O000O._tooltip_anim = O000OO0O0OO0O00O0
        OOOOOO00OOO0O000O._tooltip_anim_firsttime = True
        OOOOOO00OOO0O000O.load_settings()
        OOOOOO00OOO0O000O.refresh()

    def closeEvent(self,event):
        from maya_toolkit.tools.maya_tabs_v1_3a import session
        if session.window is self:session.close()
        super().closeEvent(event)

    def on_new_tab(O0000000O00000O00):
        O00OOOO0000O0OOO0 = __.new_tab('New Tab')
        __.settings['tabs'] += [O00OOOO0000O0OOO0]
        O0000000O00000O00.save_settings()
        O0000000O00000O00.load_settings()

    def on_logo_session(O0O000OO0OOO0000O):
        guiMayaTabs()

    def on_load_session(OO00OOOOOO0OO0000):
        O00O0000O00O00O00, O000OO0000O000O0O = QtWidgets.QFileDialog.getOpenFileName(OO00OOOOOO0OO0000, 'Open Maya Tabs session', __.settings['lastSaveDir'], 'Session files (*.tabs-session)')
        if not O00O0000O00O00O00:
            return log.warning('Cancelled')
        try:
            O000OO00O00OO0O00 = open(O00O0000O00O00O00)
            OO00O000O0OO00000 = json.load(O000OO00O00OO0O00)
        except Exception:
            import traceback
            traceback.print_exc()
            return log.warning("Couldn't load %s, ensure it is a valid Maya Tabs session" % O00O0000O00O00O00)
        finally:
            O000OO00O00OO0O00.close()
        __.settings['lastSaveDir'] = os.path.dirname(O00O0000O00O00O00)
        __.settings['tabs'] = OO00O000O0OO00000
        __.save()
        OO00OOOOOO0OO0000.load_settings()
        for O0O00000O0000O0OO in OO00O000O0OO00000:
            log.info('Saving tab %s' % O0O00000O0000O0OO['fname'])
        log.info('Successfully loaded Maya Tabs session from %s' % O00O0000O00O00O00)

    def on_save_session(O0O000OOOO0OO0O0O):
        OO00000OO00O0OO00, O00O0000O00OO00O0 = QtWidgets.QFileDialog.getSaveFileName(O0O000OOOO0OO0O0O, 'Save Maya Tabs session', __.settings['lastSaveDir'], 'Session files (*.tabs-session)')
        if OO00000OO00O0OO00:
            OO0OO0O0OO0O0OOOO = __.settings['tabs']
            with open(OO00000OO00O0OO00, 'w') as OOO00OOO000O0000O:
                json.dump(OO0OO0O0OO0O0OOOO, OOO00OOO000O0000O, indent=4, sort_keys=True)
            for OOOO0O00O0OOOOOO0 in OO0OO0O0OO0O0OOOO:
                log.info('Saving tab %s' % OOOO0O00O0OOOOOO0['name'])
            log.info('Successfully saved Maya Tabs session to %s' % OO00000OO00O0OO00)
        else:
            print('No file selected')

    def on_slot_entered(OO00OOOO0O0000000):
        """"""
        O0O00OO00000O0O0O = OO00OOOO0O0000000.sender()
        OO00OOOO0O0000000._tooltip.hide()
        OOOOO00000OOOO00O = O0O00OO00000O0O0O.property('thumbnail')
        if not O0O00OO00000O0O0O.property('active') and OOOOO00000OOOO00O:
            OO00OOOO0O0000000._tooltip.setPixmap(OOOOO00000OOOO00O)
            OO00000000O0O0O0O = float(OOOOO00000OOOO00O.height()) / OOOOO00000OOOO00O.width()
            O0OO0O00O000OO00O = QtCore.QSize(O0O00OO00000O0O0O.width(), int(round(O0O00OO00000O0O0O.width() * OO00000000O0O0O0O)))
            OO000O0O0O00000OO = O0O00OO00000O0O0O.mapToGlobal(QtCore.QPoint(0, 0))
            OO000O0O0O00000OO -= QtCore.QPoint(0, O0OO0O00O000OO00O.height())
            OO000O0O0O00000OO -= QtCore.QPoint(0, 5)
            if OO00OOOO0O0000000._tooltip_anim_firsttime:
                OO00OOOO0O0000000._tooltip.move(OO000O0O0O00000OO + QtCore.QPoint(0, 100))
                OO00OOOO0O0000000._tooltip_anim_firsttime = False
            if __.settings.get('animated'):
                OO00OOOO0O0000000._tooltip_anim.setEndValue(OO000O0O0O00000OO)
                OO00OOOO0O0000000._tooltip_anim.start()
            else:
                OO00OOOO0O0000000._tooltip.move(OO000O0O0O00000OO)
            OO00OOOO0O0000000._tooltip.resize(O0OO0O00O000OO00O)
            _owned_single_shot(__.settings.get('tooltipDelay', 10), OO00OOOO0O0000000._tooltip.show)

    def on_slot_exited(O0O00O0O0OO0O00OO):
        """"""
        O0O00O0O0OO0O00OO._tooltip.hide()

    def refresh(O00O0000000OO0O00):
        O00O0000000OO0O00._tooltip.hide()
        for OOOOO000OO0OOO0OO in O00O0000000OO0O00._slots:
            OOO00OOO0OO0O000O = OOOOO000OO0OOO0OO.property('fname')
            O00OOO00O00O0OOO0 = os.path.basename(str(OOO00OOO0OO0O000O))
            O00OOO00O00O0OOO0 = O00OOO00O00O0OOO0.replace('.mb', '')
            OOOOO000OO0OOO0OO.setText(O00OOO00O00O0OOO0 or OOOOO000OO0OOO0OO.property('name'))
            OOOOO000OO0OOO0OO.setToolTip(OOO00OOO0OO0O000O)
            OOOOO000OO0OOO0OO.setProperty('active', OOOOO000OO0OOO0OO == O00O0000000OO0O00._current_slot)
            OOOOO000OO0OOO0OO.setProperty('autosave', OOOOO000OO0OOO0OO.property('autosave'))
            OOOOO000OO0OOO0OO.setProperty('hasFile', OOO00OOO0OO0O000O != '')
        OOOOO000O00O00OOO = __.style % __.settings.get('style', __.default_style)
        O00O0000000OO0O00.setStyleSheet(OOOOO000O00O00OOO)

    def _save(O00000O00O0000O0O):
        if not O00000O00O0000O0O.has_current_slot():
            return
        O00O0000O00OOOO0O = O00000O00O0000O0O._current_slot.property('fname')
        if not O00O0000O00OOOO0O:
            O00OO00OOOO000OOO = 'Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb);;All Files (*.*)'
            O00O0000O00OOOO0O = cmds.fileDialog2(fileFilter=O00OO00OOOO000OOO, dialogStyle=2)
            if O00O0000O00OOOO0O:
                O00O0000O00OOOO0O = O00O0000O00OOOO0O[0]
            else:
                return log.warning('Cancelled')
        cmds.file(rename=O00O0000O00OOOO0O)
        cmds.file(save=True, force=True)
        return True

    def on_clear_clicked(O0OO0O00O0OOOOO00):
        OO0000OO0OOO0O000 = O0OO0O00O0OOOOO00.sender()
        if not OO0000OO0OOO0O000.property('fname'):
            O0OO0O00O0OOOOO00.on_delete_clicked()
            return
        OOO0O00OOOO0OOO00 = QtWidgets.QMessageBox(O0OO0O00O0OOOOO00)
        OOO0O00OOOO0OOO00.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        OOO0O00OOOO0OOO00.setWindowTitle('Clear')
        OOO0O00OOOO0OOO00.setText('Clear tab %s' % (OO0000OO0OOO0O000.property('index') + 1))
        if OOO0O00OOOO0OOO00.exec() == QtWidgets.QMessageBox.Cancel:
            return log.warning('Cancelled')
        log.info('Clearing %s' % OO0000OO0OOO0O000.property('name'))
        OO0000OO0OOO0O000.setProperty('fname', '')
        OO0000OO0OOO0O000.setProperty('thumbnail', '')
        OO0000OO0OOO0O000.setProperty('autosave', False)
        if OO0000OO0OOO0O000 == O0OO0O00O0OOOOO00._current_slot:
            cmds.file(new=True, force=True)
        O0OO0O00O0OOOOO00.save_settings()
        O0OO0O00O0OOOOO00.refresh()

    def on_ctrl_open_clicked(OO0OOOOOO0OOO0O00):
        O0O0OO0OO0OO00O0O = QtWidgets.QMessageBox(OO0OOOOOO0OOO0O00)
        O0O0OO0OO0OO00O0O.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        O0O0OO0OO0OO00O0O.setWindowTitle('Maya Tabs Auto-Save')
        O00000O0O00OO0000 = OO0OOOOOO0OOO0O00.sender()
        if O00000O0O00OO0000.property('autosave'):
            O0O0OO0OO0OO00O0O.setText('Disable auto-save?')
        else:
            O0O0OO0OO0OO00O0O.setText('Enable auto-save?')
        if O0O0OO0OO0OO00O0O.exec() == QtWidgets.QMessageBox.Ok:
            O00000O0O00OO0000.setProperty('autosave', not O00000O0O00OO0000.property('autosave'))
            OO0OOOOOO0OOO0O00.save_settings()
            OO0OOOOOO0OOO0O00.on_open_clicked()
        else:
            log.info('Cancelled')
        OO0OOOOOO0OOO0O00.refresh()

    def has_current_slot(OOOO00OOOO0OOOOOO):
        return OOOO00OOOO0OOOOOO._current_slot is not None and isValid(OOOO00OOOO0OOOOOO._current_slot)

    def on_open_clicked(OOOO0O00O0O0000O0):
        O000O0OOO0O000O0O = OOOO0O00O0O0000O0.sender()
        if O000O0OOO0O000O0O == OOOO0O00O0O0000O0._current_slot:
            return
        O000OOOOOOO000O00 = O000O0OOO0O000O0O.property('fname')
        OO0O00OOO00O00OO0 = O000O0OOO0O000O0O.property('index')
        OOOO0O0OO000OOOOO = cmds.file(query=True, modified=True)
        if OOOO0O0OO000OOOOO and OOOO0O00O0O0000O0.has_current_slot():
            if OOOO0O00O0O0000O0._current_slot.property('autosave'):
                if not OOOO0O00O0O0000O0._save():
                    return
            else:
                OOOOOO0000OO0O0O0 = QtWidgets.QMessageBox(OOOO0O00O0O0000O0)
                OOOOOO0000OO0O0O0.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
                O0OO0O000OOO00O00 = OOOO0O00O0O0000O0._current_slot.property('fname')
                OOOOOO0000OO0O0O0.setWindowTitle('Warning: Scene not saved')
                OOOOOO0000OO0O0O0.setText('Save changes to %s?' % (O0OO0O000OOO00O00 or 'untitled scene'))
                OO0OO0O0O00O0000O = OOOOOO0000OO0O0O0.exec()
                if OO0OO0O0O00O0000O == QtWidgets.QMessageBox.Save:
                    if not OOOO0O00O0O0000O0._save():
                        return
                elif OO0OO0O0O00O0000O == QtWidgets.QMessageBox.Cancel:
                    return log.warning('Cancelled')
        if O000OOOOOOO000O00:
            log.info('Opening %s..' % O000OOOOOOO000O00)
            cmds.file(O000OOOOOOO000O00, open=True, force=True, ignoreVersion=True)
        else:
            log.info('Starting new scene @ slot %d' % (OO0O00OOO00O00OO0 + 1))
            cmds.file(new=True, force=True)
        OOOO0O00O0O0000O0._current_slot = O000O0OOO0O000O0O
        OOOO0O00O0O0000O0.refresh()

    def on_new(O0O0OO000OOO00OOO):
        if not O0O0OO000OOO00OOO.has_current_slot():
            return
        log.info('New tab')
        O0O0OO000OOO00OOO._current_slot.setProperty('fname', '')
        O0O0OO000OOO00OOO._current_slot.setProperty('thumbnail', '')
        O0O0OO000OOO00OOO.save_settings()
        O0O0OO000OOO00OOO.refresh()

    def on_open(OOOOOO00O0OOOO000, O0OO00O0OO0O0O000):
        if not OOOOOO00O0OOOO000.has_current_slot():
            return
        log.info('Opening tab %s' % O0OO00O0OO0O0O000)
        OOOOOO00O0OOOO000._current_slot.setProperty('fname', O0OO00O0OO0O0O000)
        OOO0000O00OO0O0O0 = OOOOOO00O0OOOO000._view_to_pixmap()
        OOOOOO00O0OOOO000._current_slot.setProperty('thumbnail', OOO0000O00OO0O0O0)
        OOOOOO00O0OOOO000.save_settings()
        OOOOOO00O0OOOO000.refresh()

    def on_save(O0O0OOO0OOOOO0OOO, O0000OO00O000O0O0):
        if not O0O0OOO0OOOOO0OOO.has_current_slot():
            return
        log.info('Saving tab %s' % O0000OO00O000O0O0)
        O0O0OOO0OOOOO0OOO._current_slot.setProperty('fname', O0000OO00O000O0O0)
        O0000OOO0OO0O00O0 = O0O0OOO0OOOOO0OOO._view_to_pixmap()
        O0O0OOO0OOOOO0OOO._current_slot.setProperty('thumbnail', O0000OOO0OO0O00O0)
        O0O0OOO0OOOOO0OOO.save_settings()
        O0O0OOO0OOOOO0OOO.refresh()

    def on_delete_clicked(O00O00O0O000000OO):
        O0OOO00O00O00OO00 = O00O00O0O000000OO.sender()
        OO00OOOOO0O0OOOO0 = 'Nothing'
        for OO0OOO0O000O00O0O in list(O00O00O0O000000OO._slots):
            if OO0OOO0O000O00O0O != O0OOO00O00O00OO00:
                continue
            OO0000O0OOOO0O000 = OO0OOO0O000O00O0O.property('index')
            OO00000O0O0O0O00O = __.settings['tabs'].pop(OO0000O0OOOO0O000)
            OO00OOOOO0O0OOOO0 = O0OOO00O00O00OO00.property('fname')
            O00O00O0O000000OO._slots.remove(O0OOO00O00O00OO00)
            log.info('Deleted %s' % OO00000O0O0O0O00O['fname'])
            if O0OOO00O00O00OO00 == O00O00O0O000000OO._current_slot:
                O00O00O0O000000OO._current_slot = None
            O0OOO00O00O00OO00.deleteLater()
        O00O00O0O000000OO.save_settings()
        O00O00O0O000000OO.load_settings()

    def on_open_folder(O00OO0OOOOOOO00O0):
        O000OO0O00000O000 = O00OO0OOOOOOO00O0.sender()
        O0O0OOOOO000OO0OO = O000OO0O00000O000.property('fname')
        OO0O0O0OOO000O0OO = os.path.dirname(O0O0OOOOO000OO0OO)
        if OO0O0O0OOO000O0OO:
            os.startfile(OO0O0O0OOO000O0OO)

    def load_settings(OO0OOOO0OO0O0O0OO):
        """"""
        __.load()
        for O00O0OO0OO0O0000O in OO0OOOO0OO0O0O0OO._slots:
            O00O0OO0OO0O0000O.deleteLater()
        OO0OOOO0OO0O0O0OO._slots[:] = []
        O0OOOOO000000000O = cmds.file(query=True, sceneName=True)
        for O0O0OO0O00O0OO0OO, OOOOOOOOO0OO00OOO in enumerate(__.settings['tabs']):
            O00O0OO0OO0O0000O = Tab()
            O00O0OO0OO0O0000O.setProperty('name', OOOOOOOOO0OO00OOO['name'])
            O00O0OO0OO0O0000O.setProperty('index', O0O0OO0O00O0OO0OO)
            O00O0OO0OO0O0000O.clicked.connect(OO0OOOO0OO0O0O0OO.on_open_clicked)
            O00O0OO0OO0O0000O.cleared.connect(OO0OOOO0OO0O0O0OO.on_clear_clicked)
            O00O0OO0OO0O0000O.open_folder.connect(OO0OOOO0OO0O0O0OO.on_open_folder)
            O00O0OO0OO0O0000O.ctrl_clicked.connect(OO0OOOO0OO0O0O0OO.on_ctrl_open_clicked)
            O00O0OO0OO0O0000O.delete.connect(OO0OOOO0OO0O0O0OO.on_delete_clicked)
            O00O0OO0OO0O0000O.entered.connect(OO0OOOO0OO0O0O0OO.on_slot_entered)
            O00O0OO0OO0O0000O.exited.connect(OO0OOOO0OO0O0O0OO.on_slot_exited)
            OO0OOOO0OO0O0O0OO.addWidget(O00O0OO0OO0O0000O)
            OO0OOOO0OO0O0O0OO._slots.append(O00O0OO0OO0O0000O)
            O0000O000O0O0OO00 = os.path.basename(OOOOOOOOO0OO00OOO['fname']) or OOOOOOOOO0OO00OOO['name']
            O00O0OO0OO0O0000O.setText(O0000O000O0O0OO00)
            O00O0OO0OO0O0000O.setProperty('fname', OOOOOOOOO0OO00OOO['fname'])
            O00O0OO0OO0O0000O.setProperty('hasFile', OOOOOOOOO0OO00OOO['fname'] != '')
            O00O0OO0OO0O0000O.setProperty('autosave', OOOOOOOOO0OO00OOO['autosave'])
            O00O0OO0OO0O0000O.setProperty('active', all([OOOOOOOOO0OO00OOO['fname'] == O0OOOOO000000000O, O0OOOOO000000000O]))
            if OOOOOOOOO0OO00OOO['fname'] != '' and 'thumbnail' in OOOOOOOOO0OO00OOO and OOOOOOOOO0OO00OOO['thumbnail']:
                try:
                    O0OOO000O0000OOO0 = OOOOOOOOO0OO00OOO['thumbnail'].encode()
                    O0O0000O0O00O0000 = QtCore.QByteArray.fromBase64(O0OOO000O0000OOO0)
                    O0O00OO000000OOOO = QtGui.QPixmap()
                    O0O00OO000000OOOO.loadFromData(O0O0000O0O00O0000)
                    O00O0OO0OO0O0000O.setProperty('thumbnail', O0O00OO000000OOOO)
                except Exception:
                    import traceback
                    traceback.print_exc()
                    log.info('Unable to load thumbnail for %s' % OOOOOOOOO0OO00OOO['fname'])
            if O00O0OO0OO0O0000O.property('active'):
                OO0OOOO0OO0O0O0OO._current_slot = O00O0OO0OO0O0000O
        OO0OOOO0OO0O0O0OO.refresh()

    def save_settings(OOO0OOO0000OO0O00):
        """"""
        for OOOO00OOO000OO0OO, O0O0O00OOO0OOO0OO in enumerate(OOO0OOO0000OO0O00._slots):
            O0OO000OO0O00OOO0 = __.settings['tabs'][OOOO00OOO000OO0OO]
            O0OO000OO0O00OOO0['fname'] = O0O0O00OOO0OOO0OO.property('fname')
            O0OO000OO0O00OOO0['autosave'] = O0O0O00OOO0OOO0OO.property('autosave')
            OOO00OO0000O0OOOO = O0O0O00OOO0OOO0OO.property('thumbnail')
            if OOO00OO0000O0OOOO:
                O0OO000OO0O00OOO0['thumbnail'] = OOO0OOO0000OO0O00._serialise_thumnail(OOO00OO0000O0OOOO)
        if OOO0OOO0000OO0O00.has_current_slot():
            O000OOO00OOOO00OO = OOO0OOO0000OO0O00._current_slot.property('index')
            __.settings['currentTabIndex'] = O000OOO00OOOO00OO
        __.save()

    def _serialise_thumnail(O000O00O0O0O00O0O, OOO0O00OOO00OO0OO):
        """"""
        O00O0OOO0000OOO00 = QtCore.QByteArray()
        OOOOOOO0OOOOO0O00 = QtCore.QBuffer(O00O0OOO0000OOO00)
        OOOOOOO0OOOOO0O00.open(QtCore.QIODevice.WriteOnly)
        OOO0O00OOO00OO0OO.save(OOOOOOO0OOOOO0O00, 'png')
        if PY == 2:
            return str(O00O0OOO0000OOO00.toBase64())
        else:
            return str(O00O0OOO0000OOO00.toBase64(), 'utf-8')

    def _view_to_pixmap(O0OO0OOOO0OOO0O00):
        """"""
        O0O000O000OO0O0OO = om.MImage()
        O00O00O0000O0OO0O = omui.M3dView.active3dView()
        O00O00O0000O0OO0O.readColorBuffer(O0O000O000OO0O0OO, True)
        O0O000O000OO0O0OO.verticalFlip()
        O00O00O000O0000OO = O0O000O000OO0O0OO.getSize()
        OOOO000O00O000O0O = ctypes.c_ubyte * (O00O00O000O0000OO[0] * O00O00O000O0000OO[1] * 4)
        OOOO000O00O000O0O = OOOO000O00O000O0O.from_address(long(O0O000O000OO0O0OO.pixels()))
        O00OOO0OO0OOO0000 = QtGui.QImage(OOOO000O00O000O0O, O00O00O000O0000OO[0], O00O00O000O0000OO[1], QtGui.QImage.Format_RGB32).rgbSwapped()
        return QtGui.QPixmap.fromImage(O00OOO0OO0OOO0000).scaled(512, 256, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

def m2mLoadSettings(setting='', settingsFile='settings'):
    OO00O00O0OO0000OO = ''
    if settingsFile == 'settings':
        OO00O00O0OO0000OO = m2mSettingsFile
    if settingsFile == 'ser':
        OO00O00O0OO0000OO = m2mSerialFile
    try:
        with open(OO00O00O0OO0000OO, 'r') as O0O00O00O0OO00O0O:
            OO0OO0000OO0O000O = O0O00O00O0OO00O0O.readlines()
            for OOOO00O000OO0O0O0 in OO0OO0000OO0O000O:
                if setting in OOOO00O000OO0O0O0:
                    O000OO0O0OOOOOO00 = OOOO00O000OO0O0O0.split('=')
                    return O000OO0O0OOOOOO00[1].rstrip('\n')
    except:
        print('error loading settings')
srl = None
# serial read only by explicit session.load

def addToClipBoard(value):
    QtWidgets.QApplication.clipboard().setText(value.strip())

def chkSrl(OO0000O0O000O0OOO):
    O000O0OO0O000O0OO = get_mac()
    OO0O0O00OO00OO000 = str(O000O0OO0O000O0OO)[2:4]
    O0O0OO00OOOOO0O0O = str(O000O0OO0O000O0OO)[6:8]
    OO00OOOOO00000OO0 = str(O000O0OO0O000O0OO)[1:3]
    OO0OOOOOO0000O0O0 = OO0000O0O000O0OOO[3:5]
    O0O00OO0OOO00O00O = OO0000O0O000O0OOO[6:8]
    OOOOOO00OOO0000O0 = OO0000O0O000O0OOO[10:12]
    OOO00OOOOOOOO00O0 = 'xxx'
    OOO00OO0OO0OO0O0O = 'x'
    O00OOOO00O000000O = 'xx'
    O000000OO0O0O00O0 = 'xxx' + OO00OOOOO00000OO0 + 'x' + OO0O0O00OO00OO000 + 'xx' + O0O0OO00OOOOO0O0O
    if OO0OOOOOO0000O0O0 == OO00OOOOO00000OO0 and O0O00OO0OOO00O00O == OO0O0O00OO00OO000 and (OOOOOO00OOO0000O0 == O0O0OO00OOOOO0O0O):
        return True
    else:
        return False

def versionCheck():
    print('Version check...')
    O0O0000O0O00OOOOO = str(versions.current())
    print(O0O0000O0O00OOOOO)
    O0OOO0OOOOOO00O0O = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2022']
    for OO0OOOOOO0OO0OO00 in O0OOO0OOOOOO00O0O:
        if OO0OOOOOO0OO0OO00 in O0O0000O0O00OOOOO:
            print('Maya Tabs: Supported Version')
            return True
    O00O0OO0OOOO00000 = 'Maya Version not Supported. Please visit www.3DtoAll.com'
    cmds.confirmDialog(title='Maya Tabs', message=O00O0OO0OOOO00000, button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')
    return False

def guiSerial():

    def OO0OO0OO0O00O0000():
        OOOOOO00O0OO0O00O = get_mac()
        OO0O0O00OO000O00O = str(OOOOOO00O0OO0O00O)[2:4]
        O0OOOOO00O0O000OO = str(OOOOOO00O0OO0O00O)[6:8]
        O0O0OOOO0O0O0O00O = str(OOOOOO00O0OO0O00O)[1:3]
        O0OOOOO00OOOO0OOO = 'MTB'
        O00000OOO000O00OO = 'V1Y'
        OOO000OO00O0000O0 = 'TAB'
        O0OOOOO0O0OO0OO00 = '09H'
        OO000O0OOO000O000 = O0OOOOO00OOOO0OOO + OO0O0O00OO000O00O + O00000OOO000O00OO + O0OOOOO00O0O000OO + OOO000OO00O0000O0 + O0O0OOOO0O0O0O00O
        return OO000O0OOO000O000

    def OOO0O0OO0OO00O00O():
        O0O0000O000OO0OOO = cmds.textField('MTB_txtFieldCode', query=True, text=True)
        addToClipBoard(O0O0000O000OO0OOO)

    def OOO0OO000OO000OOO():
        cmds.launch(web='http://www.3dtoall.com/register')

    def O0OO00OOO0OO0OO00():
        O0O00OO0O00OO0O00 = cmds.textField(O0000OO000O0O0000, q=True, tx=True)
        O0O00OO0O00OO0O00 = O0O00OO0O00OO0O00.replace(' ', '')
        if chkSrl(O0O00OO0O00OO0O00) == True:
            with open(mayaTabsSerialFile, 'w') as OO00OO000OOO0000O:
                OO00OO000OOO0000O.write('Serial=' + O0O00OO0O00OO0O00 + '\n')
            with open(mayaTabsSerialConfigFile, 'w') as OO00OO000OOO0000O:
                OO00OO000OOO0000O.write('Serial=' + O0O00OO0O00OO0O00 + '\n')
            print('- Maya Tabs Activated -')
            try:
                cmds.deleteUI(mayaTabsSerialWindowName)
            except:
                pass
            install_toolbar()
            install_callbacks()
        else:
            cmds.confirmDialog(title='Maya Tabs', message='Activation Problem. Please try again or contact support.', button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')
    try:
        O0OO000O0OO0O0000 = cmds.window('mayatabsSerial', query=True, title=True)
    except:
        pass
    try:
        cmds.deleteUI(mainWindowName)
    except Exception as OO0OOOOO0O00O00O0:
        pass
    try:
        cmds.deleteUI(mayaTabsSerialWindowName)
    except Exception as OO0OOOOO0O00O00O0:
        pass
    O0O0OOO000000O00O = cmds.window(mayaTabsSerialWindowName, toolbox=True, maximizeButton=False, minimizeButton=False, sizeable=False, title='Maya Tabs', widthHeight=(343, 310))
    OOO00OOO0000OOOO0 = cmds.formLayout(numberOfDivisions=100)
    OO00000O0O0OO0000 = cmds.image(image=mayaTabslogo, backgroundColor=(0.392157, 0.862745, 1), w=343, h=88)
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(OO00000O0O0OO0000, 'top', 0), (OO00000O0O0OO0000, 'left', 0)])
    OO00000O0O0OO0000 = cmds.text(label='Your Code:', w=115, h=21)
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(OO00000O0O0OO0000, 'top', 90), (OO00000O0O0OO0000, 'left', 115)])
    OOOOO00O000OOOO00 = cmds.textField('MTB_txtFieldCode', tx=OO0OO0OO0O00O0000(), font='boldLabelFont', editable=False, width=150)
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(OOOOO00O000OOOO00, 'top', 115), (OOOOO00O000OOOO00, 'left', 50)])
    OO00000O00O0O0OO0 = cmds.button(label='Copy to Clipboard', width=120, c=lambda *O00O0O0OOOO0000O0: OOO0O0OO0OO00O00O(), height=20)
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(OO00000O00O0O0OO0, 'top', 115), (OO00000O00O0O0OO0, 'left', 175)])
    OO000OOO00000OO0O = cmds.button(label='Get Activation Serial', width=260, c=lambda *OO00OO00OO00OO0OO: OOO0OO000OO000OOO(), height=25)
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(OO000OOO00000OO0O, 'top', 142), (OO000OOO00000OO0O, 'left', 45)])
    OO00000O0O0OO0000 = cmds.separator(style='in', w=325, h=6)
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(OO00000O0O0OO0000, 'top', 175), (OO00000O0O0OO0000, 'left', 10)])
    O00OO0O0O0O0OOO0O = cmds.text(label='Enter your Maya Tabs serial here:')
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(O00OO0O0O0O0OOO0O, 'top', 188), (O00OO0O0O0O0OOO0O, 'left', 85)])
    O0000OO000O0O0000 = cmds.textField('txtFieldSerialEnter', tx='', width=210)
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(O0000OO000O0O0000, 'top', 206), (O0000OO000O0O0000, 'left', 70)])
    OO00O0O0O000O0000 = cmds.button(label='ACTIVATE', command=lambda *OO00O0OO0000O00O0: O0OO00OOO0OO0OO00(), height=40, width=210)
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(OO00O0O0O000O0000, 'top', 232), (OO00O0O0O000O0000, 'left', 70)])
    OO00000O0O0OO0000 = cmds.separator(style='in', w=325, h=6)
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(OO00000O0O0OO0000, 'top', 280), (OO00000O0O0OO0000, 'left', 10)])
    OO0O00O0OOO00O0O0 = cmds.text(label='(c) 2022 3DtoAll. All Rights Reserved.')
    cmds.formLayout(OOO00OOO0000OOOO0, edit=True, attachForm=[(OO0O00O0OOO00O0O0, 'top', 290), (OO0O00O0OOO00O0O0, 'left', 85)])
    cmds.showWindow(O0O0OOO000000O00O)
    cmds.window(O0O0OOO000000O00O, e=True, width=335, height=312)

def guiMayaTabs():

    def O00OOOOO00OO0OOO0(OOOO00OOO00O000O0):
        OO000000000O0O0OO = []
        for O00O0O0OOO000OOO0 in (0, 2, 4):
            O0000000O000O0O00 = int(OOOO00OOO00O000O0[O00O0O0OOO000OOO0:O00O0O0OOO000OOO0 + 2], 16)
            OO000000000O0O0OO.append(O0000000O000O0O00)
        return tuple(OO000000000O0O0OO)

    def O0OO0OOO0O000O000(OOOO0O0000O00O000):
        OO00OO000OOO0OO00 = int(OOOO0O0000O00O000[0] * 255)
        OOO000000OO0O0O0O = int(OOOO0O0000O00O000[1] * 255)
        O0OO0O000OO0O000O = int(OOOO0O0000O00O000[2] * 255)
        print('--------------')
        return '#%02x%02x%02x' % (OO00OO000OOO0OO00, OOO000000OO0O0O0O, O0OO0O000OO0O000O)

    def OOOO0OO0OO00O0000():
        import json
        O0000OOO000000000 = open(mayaTabsSettingsFile, 'r')
        OO0OO000OO00OO0O0 = json.loads(O0000OOO000000000.read())
        O00OO0OO00O0O0OO0 = OO0OO000OO00OO0O0['style']['height']
        O0000000O0O0O0O0O = OO0OO000OO00OO0O0['style']['width']
        if O00OO0OO00O0O0OO0 == '20':
            cmds.optionMenu('MTB_menuTabsHeight', e=True, sl=1)
        if O00OO0OO00O0O0OO0 == '35':
            cmds.optionMenu('MTB_menuTabsHeight', e=True, sl=2)
        if O00OO0OO00O0O0OO0 == '60':
            cmds.optionMenu('MTB_menuTabsHeight', e=True, sl=3)
        if O0000000O0O0O0O0O == '10':
            cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=1)
        if O0000000O0O0O0O0O == '50':
            cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=2)
        if O0000000O0O0O0O0O == '100':
            cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=3)
        if O0000000O0O0O0O0O == '150':
            cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=4)
        if O0000000O0O0O0O0O == '200':
            cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=5)
        O000000OOO0OO0O00 = OO0OO000OO00OO0O0['style']['tabColorActive']
        O0OOO0OOOO0OOOOO0 = O00OOOOO00OO0OOO0(O000000OOO0OO0O00.lstrip('#'))
        cmds.button(OOOO000OOO0000OOO, edit=True, bgc=[O0OOO0OOOO0OOOOO0[0] / 255, O0OOO0OOOO0OOOOO0[1] / 255, O0OOO0OOOO0OOOOO0[2] / 255])
        O000000OOO0OO0O00 = OO0OO000OO00OO0O0['style']['tabColorHasFile']
        O0OOO0OOOO0OOOOO0 = O00OOOOO00OO0OOO0(O000000OOO0OO0O00.lstrip('#'))
        cmds.button(O00OOOOOO0OO0OO00, edit=True, bgc=[O0OOO0OOOO0OOOOO0[0] / 255, O0OOO0OOOO0OOOOO0[1] / 255, O0OOO0OOOO0OOOOO0[2] / 255])
        O000000OOO0OO0O00 = OO0OO000OO00OO0O0['style']['tabColor']
        O0OOO0OOOO0OOOOO0 = O00OOOOO00OO0OOO0(O000000OOO0OO0O00.lstrip('#'))
        cmds.button(O0OOOOO00OOO0O000, edit=True, bgc=[O0OOO0OOOO0OOOOO0[0] / 255, O0OOO0OOOO0OOOOO0[1] / 255, O0OOO0OOOO0OOOOO0[2] / 255])
        O0000OOO000000000.close()

    def O00000000OO0000O0():
        O0OOO00000O000000 = open(mayaTabsSettingsFile, 'r')
        OO0OOOOO0O00O0000 = json.load(O0OOO00000O000000)
        O0OOO00000O000000.close()
        OOO00OOOO00OOOOOO = cmds.optionMenu(O0000O000O0O00O0O, query=True, value=True)
        O0O0OOO00OO0000OO = cmds.optionMenu(O0O0OO00OOO000OOO, query=True, value=True)
        O00O0O000OOOO0000 = O0OO0OOO0O000O000(cmds.button(OOOO000OOO0000OOO, query=True, bgc=True))
        O00OO0O0O0OO00OOO = O0OO0OOO0O000O000(cmds.button(O00OOOOOO0OO0OO00, query=True, bgc=True))
        O000O000000000OOO = O0OO0OOO0O000O000(cmds.button(O0OOOOO00OOO0O000, query=True, bgc=True))
        OO0OOOOO0O00O0000['style']['height'] = OOO00OOOO00OOOOOO
        OO0OOOOO0O00O0000['style']['width'] = O0O0OOO00OO0000OO
        OO0OOOOO0O00O0000['style']['tabColorActive'] = O00O0O000OOOO0000
        OO0OOOOO0O00O0000['style']['tabColorHasFile'] = O00OO0O0O0OO00OOO
        OO0OOOOO0O00O0000['style']['tabColor'] = O000O000000000OOO
        O0OOO00000O000000 = open(mayaTabsSettingsFile, 'w+')
        O0OOO00000O000000.write(json.dumps(OO0OOOOO0O00O0000))
        O0OOO00000O000000.close()
        uninstall_toolbar()
        install_toolbar()

    def OOO0OO00OOO0OO000():
        O0OOOO000OO0O000O = cmds.button(OOOO000OOO0000OOO, query=True, bgc=True)
        cmds.colorEditor(rgbValue=[O0OOOO000OO0O000O[0], O0OOOO000OO0O000O[1], O0OOOO000OO0O000O[2]])
        if cmds.colorEditor(query=True, result=True):
            OO00OOOO0O000O00O = cmds.colorEditor(query=True, rgb=True)
            cmds.button(OOOO000OOO0000OOO, edit=True, bgc=[OO00OOOO0O000O00O[0], OO00OOOO0O000O00O[1], OO00OOOO0O000O00O[2]])
            O00000000OO0000O0()
        else:
            print('Editor was dismissed')

    def O0O000O0O00O0O0OO():
        OOOOOO00000OO0O0O = cmds.button(O00OOOOOO0OO0OO00, query=True, bgc=True)
        cmds.colorEditor(rgbValue=[OOOOOO00000OO0O0O[0], OOOOOO00000OO0O0O[1], OOOOOO00000OO0O0O[2]])
        if cmds.colorEditor(query=True, result=True):
            O0000O00O0000000O = cmds.colorEditor(query=True, rgb=True)
            cmds.button(O00OOOOOO0OO0OO00, edit=True, bgc=[O0000O00O0000000O[0], O0000O00O0000000O[1], O0000O00O0000000O[2]])
            O00000000OO0000O0()
        else:
            print('Editor was dismissed')

    def O0OO00O00O0O00O00():
        OO00O00OOO0OO0000 = cmds.button(O0OOOOO00OOO0O000, query=True, bgc=True)
        cmds.colorEditor(rgbValue=[OO00O00OOO0OO0000[0], OO00O00OOO0OO0000[1], OO00O00OOO0OO0000[2]])
        if cmds.colorEditor(query=True, result=True):
            O0O0OOO0OOO0O000O = cmds.colorEditor(query=True, rgb=True)
            cmds.button(O0OOOOO00OOO0O000, edit=True, bgc=[O0O0OOO0OOO0O000O[0], O0O0OOO0OOO0O000O[1], O0O0OOO0OOO0O000O[2]])
            O00000000OO0000O0()
        else:
            print('Editor was dismissed')

    def O0OOO000000O0OO00():
        O0O000O0O0O0O0O0O = cmds.button(btnTabBorderColor, query=True, bgc=True)
        cmds.colorEditor(rgbValue=[O0O000O0O0O0O0O0O[0], O0O000O0O0O0O0O0O[1], O0O000O0O0O0O0O0O[2]])
        if cmds.colorEditor(query=True, result=True):
            OO0O0OOO0OOOOOOO0 = cmds.colorEditor(query=True, rgb=True)
            cmds.button(btnTabBorderColor, edit=True, bgc=[OO0O0OOO0OOOOOOO0[0], OO0O0OOO0OOOOOOO0[1], OO0O0OOO0OOOOOOO0[2]])
            O00000000OO0000O0()
        else:
            print('Editor was dismissed')

    def O0OO0O0O00OO0O00O():
        OO0OO0O0O0O0OOO0O = None
        OO0O0OO0OOO00O00O, O0O000OOO000OO00O = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Maya Tabs Theme', mayaTabsThemesDir, 'Theme (*.mttheme)')
        if OO0O0OO0OOO00O00O:
            try:
                O00O0OOOO00O000O0 = O0OO0OOO0O000O000(cmds.button(OOOO000OOO0000OOO, query=True, bgc=True))
                O00OO0000OO0000OO = O0OO0OOO0O000O000(cmds.button(O00OOOOOO0OO0OO00, query=True, bgc=True))
                OOOO0000O0O000000 = O0OO0OOO0O000O000(cmds.button(O0OOOOO00OOO0O000, query=True, bgc=True))
                O00OOOO0OO0000OO0 = {}
                OOO0OO0O00O000OOO = '100'
                if cmds.optionMenu('MTB_menuTabsWidth', query=True, sl=True) == 1:
                    OOO0OO0O00O000OOO = '10'
                if cmds.optionMenu('MTB_menuTabsWidth', query=True, sl=True) == 2:
                    OOO0OO0O00O000OOO = '50'
                if cmds.optionMenu('MTB_menuTabsWidth', query=True, sl=True) == 3:
                    OOO0OO0O00O000OOO = '100'
                if cmds.optionMenu('MTB_menuTabsWidth', query=True, sl=True) == 4:
                    OOO0OO0O00O000OOO = '150'
                if cmds.optionMenu('MTB_menuTabsWidth', query=True, sl=True) == 5:
                    OOO0OO0O00O000OOO = '200'
                O000O00O00O0OO00O = '20'
                if cmds.optionMenu('MTB_menuTabsHeight', query=True, sl=True) == 1:
                    O000O00O00O0OO00O = '20'
                if cmds.optionMenu('MTB_menuTabsHeight', query=True, sl=True) == 2:
                    O000O00O00O0OO00O = '35'
                if cmds.optionMenu('MTB_menuTabsHeight', query=True, sl=True) == 3:
                    O000O00O00O0OO00O = '60'
                O00OOOO0OO0000OO0['size'] = {'height': O000O00O00O0OO00O, 'width': OOO0OO0O00O000OOO}
                O00OOOO0OO0000OO0['style'] = {'active': O00O0OOOO00O000O0, 'inactive': O00OO0000OO0000OO, 'empty': OOOO0000O0O000000}
                with open(OO0O0OO0OOO00O00O, 'w') as O000000OO00O0O0OO:
                    json.dump(O00OOOO0OO0000OO0, O000000OO00O0O0OO)
            except:
                print('Error saving Theme File')

    def OO0OO00OOOOO0O0OO():
        OOOOOO0O0000O0OO0, O0000O0OOOO00OOOO = QtWidgets.QFileDialog.getOpenFileName(None, 'Load Maya Tabs Theme', mayaTabsThemesDir, 'Theme (*.mttheme)')
        if OOOOOO0O0000O0OO0:
            try:
                O0000OOOO000O00O0 = open(OOOOOO0O0000O0OO0)
                O0OO000O0OO0OO00O = json.load(O0000OOOO000O00O0)
                O00OO0O00OOO0O000 = O0OO000O0OO0OO00O['size']['height']
                OOO0OO0O0OO0O000O = O0OO000O0OO0OO00O['size']['width']
                O0000OOOO000O00O0.close()
                print('==' * 50)
                print('readTabHeight', O00OO0O00OOO0O000)
                print('readTabWidth', OOO0OO0O0OO0O000O)
                print('==' * 50)
                if O00OO0O00OOO0O000 == '20':
                    cmds.optionMenu('MTB_menuTabsHeight', e=True, sl=1)
                if O00OO0O00OOO0O000 == '35':
                    cmds.optionMenu('MTB_menuTabsHeight', e=True, sl=2)
                if O00OO0O00OOO0O000 == '60':
                    cmds.optionMenu('MTB_menuTabsHeight', e=True, sl=3)
                if OOO0OO0O0OO0O000O == '10':
                    cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=1)
                if OOO0OO0O0OO0O000O == '50':
                    cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=2)
                if OOO0OO0O0OO0O000O == '100':
                    cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=3)
                if OOO0OO0O0OO0O000O == '150':
                    cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=4)
                if OOO0OO0O0OO0O000O == '200':
                    cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=5)
                OO000O0O0OO000000 = O0OO000O0OO0OO00O['style']['active']
                OO00OO0O0O00O000O = O00OOOOO00OO0OOO0(OO000O0O0OO000000.lstrip('#'))
                cmds.button(OOOO000OOO0000OOO, edit=True, bgc=[OO00OO0O0O00O000O[0] / 255, OO00OO0O0O00O000O[1] / 255, OO00OO0O0O00O000O[2] / 255])
                OO000O0O0OO000000 = O0OO000O0OO0OO00O['style']['inactive']
                OO00OO0O0O00O000O = O00OOOOO00OO0OOO0(OO000O0O0OO000000.lstrip('#'))
                cmds.button(O00OOOOOO0OO0OO00, edit=True, bgc=[OO00OO0O0O00O000O[0] / 255, OO00OO0O0O00O000O[1] / 255, OO00OO0O0O00O000O[2] / 255])
                OO000O0O0OO000000 = O0OO000O0OO0OO00O['style']['empty']
                OO00OO0O0O00O000O = O00OOOOO00OO0OOO0(OO000O0O0OO000000.lstrip('#'))
                cmds.button(O0OOOOO00OOO0O000, edit=True, bgc=[OO00OO0O0O00O000O[0] / 255, OO00OO0O0O00O000O[1] / 255, OO00OO0O0O00O000O[2] / 255])
                O00000000OO0000O0()
                print('finished')
            except:
                print('Error reading Theme File')

    def OOO0O0O00OOO0OO00():
        try:
            OO00O0OO0O000OO00 = '#4c8758'
            O0OO0O00000OOO000 = O00OOOOO00OO0OOO0(OO00O0OO0O000OO00.lstrip('#'))
            cmds.button(OOOO000OOO0000OOO, edit=True, bgc=[O0OO0O00000OOO000[0] / 255, O0OO0O00000OOO000[1] / 255, O0OO0O00000OOO000[2] / 255])
            OO00O0OO0O000OO00 = '#3e6170'
            O0OO0O00000OOO000 = O00OOOOO00OO0OOO0(OO00O0OO0O000OO00.lstrip('#'))
            cmds.button(O00OOOOOO0OO0OO00, edit=True, bgc=[O0OO0O00000OOO000[0] / 255, O0OO0O00000OOO000[1] / 255, O0OO0O00000OOO000[2] / 255])
            OO00O0OO0O000OO00 = '#212324'
            O0OO0O00000OOO000 = O00OOOOO00OO0OOO0(OO00O0OO0O000OO00.lstrip('#'))
            cmds.button(O0OOOOO00OOO0O000, edit=True, bgc=[O0OO0O00000OOO000[0] / 255, O0OO0O00000OOO000[1] / 255, O0OO0O00000OOO000[2] / 255])
            cmds.optionMenu('MTB_menuTabsHeight', e=True, sl=1)
            cmds.optionMenu('MTB_menuTabsWidth', e=True, sl=4)
            O00000000OO0000O0()
        except:
            print("Can't load Defaults")

    def O000O000OO0OOO00O(O0000OOO0OO000O00):
        O00000000OO0000O0()

    def O0000O0OOOO000OOO():
        cmds.launch(web='http://www.3dtoall.com')

    def OO000OO00OO00OOOO():
        try:
            cmds.deleteUI(mayaTabsMainWindowName)
        except:
            print("can't close")
    try:
        O0OOOOOOOOOO0O0OO = cmds.window('mayatabsMain', query=True, title=True)
    except:
        pass
    try:
        cmds.deleteUI(mainWindowName)
    except Exception as OO0O0OO0O00O0O0O0:
        pass
    try:
        cmds.deleteUI(mayaTabsMainWindowName)
    except Exception as OO0O0OO0O00O0O0O0:
        pass
    O0O000O000OOOO000 = cmds.window(mayaTabsMainWindowName, toolbox=True, maximizeButton=False, minimizeButton=False, sizeable=False, title='Maya Tabs', widthHeight=(343, 340))
    OOO0O0000O0O00000 = cmds.formLayout(numberOfDivisions=100)
    O000O0OOOO00O0OOO = cmds.image(image=mayaTabslogo, backgroundColor=(0.392157, 0.862745, 1), w=343, h=88)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(O000O0OOOO00O0OOO, 'top', 0), (O000O0OOOO00O0OOO, 'left', 0)])
    OO0O0OOO0OOOO00O0 = cmds.text(label='Theme Editor:')
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(OO0O0OOO0OOOO00O0, 'top', 100), (OO0O0OOO0OOOO00O0, 'left', 25)])
    O000O0OOOO00O0OOO = cmds.separator(style='in', w=220, h=6)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(O000O0OOOO00O0OOO, 'top', 105), (O000O0OOOO00O0OOO, 'left', 105)])
    OO000OOOO0000OO00 = 20
    OOOO00OOO00OO0OOO = 5
    OOOO000OOO0000OOO = cmds.button(label='Active', width=60, c=lambda *OOOOO0000O00OO0OO: OOO0OO00OOO0OO000(), height=25)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(OOOO000OOO0000OOO, 'top', 120 + OOOO00OOO00OO0OOO), (OOOO000OOO0000OOO, 'left', 162 + OO000OOOO0000OO00)])
    O00OOOOOO0OO0OO00 = cmds.button(label='Inactive', width=60, c=lambda *OO0000O0O0OO000O0: O0O000O0O00O0O0OO(), height=25)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(O00OOOOOO0OO0OO00, 'top', 120 + OOOO00OOO00OO0OOO), (O00OOOOOO0OO0OO00, 'left', 226 + OO000OOOO0000OO00)])
    O0OOOOO00OOO0O000 = cmds.button(label='Empty', width=124, c=lambda *O0OO0OO0000O0OOO0: O0OO00O00O0O00O00(), height=25)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(O0OOOOO00OOO0O000, 'top', 149 + OOOO00OOO00OO0OOO), (O0OOOOO00OOO0O000, 'left', 162 + OO000OOOO0000OO00)])
    O0O0OO00OOO000OOO = cmds.optionMenu('MTB_menuTabsWidth', w=120, label='Tabs Width: ', changeCommand=O000O000OO0OOO00O)
    cmds.menuItem(O0O0OO00OOO000OOO, label='10')
    cmds.menuItem(O0O0OO00OOO000OOO, label='50')
    cmds.menuItem(O0O0OO00OOO000OOO, label='100')
    cmds.menuItem(O0O0OO00OOO000OOO, label='150')
    cmds.menuItem(O0O0OO00OOO000OOO, label='200')
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(O0O0OO00OOO000OOO, 'top', 121 + OOOO00OOO00OO0OOO), (O0O0OO00OOO000OOO, 'left', 20 + OO000OOOO0000OO00)])
    O0000O000O0O00O0O = cmds.optionMenu('MTB_menuTabsHeight', w=120, label='Tabs Height:', changeCommand=O000O000OO0OOO00O)
    cmds.menuItem(O0O0OO00OOO000OOO, label='20')
    cmds.menuItem(O0O0OO00OOO000OOO, label='35')
    cmds.menuItem(O0O0OO00OOO000OOO, label='60')
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(O0000O000O0O00O0O, 'top', 150 + OOOO00OOO00OO0OOO), (O0000O000O0O00O0O, 'left', 20 + OO000OOOO0000OO00)])
    OOOO00OOO00OO0OOO = -60
    OO00O000OO0OOO00O = cmds.button(label='Load Theme...', width=90, c=lambda *O0O0OOOO000O0OO00: OO0OO00OOOOO0O0OO(), height=25)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(OO00O000OO0OOO00O, 'top', 256 + OOOO00OOO00OO0OOO), (OO00O000OO0OOO00O, 'left', 27)])
    OO00000OOO00OO000 = cmds.button(label='Save Theme...', width=90, c=lambda *O000OOO0OOOO000OO: O0OO0O0O00OO0O00O(), height=25)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(OO00000OOO00OO000, 'top', 256 + OOOO00OOO00OO0OOO), (OO00000OOO00OO000, 'left', 123)])
    OO0OOOO000O000O00 = cmds.button(label='Reset', width=85, c=lambda *O0O0O0O00OO00O000: OOO0O0O00OOO0OO00(), height=25)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(OO0OOOO000O000O00, 'top', 256 + OOOO00OOO00OO0OOO), (OO0OOOO000O000O00, 'left', 219)])
    O000O0OOOO00O0OOO = cmds.separator(style='in', w=315, h=6)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(O000O0OOOO00O0OOO, 'top', 288 + OOOO00OOO00OO0OOO), (O000O0OOOO00O0OOO, 'left', 10)])
    OO0O00OO00O0O000O = cmds.button(label='Ok', command=lambda *OO0000O0OOO00O00O: OO000OO00OO00OOOO(), height=40, width=146)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(OO0O00OO00O0O000O, 'top', 305 + OOOO00OOO00OO0OOO), (OO0O00OO00O0O000O, 'left', 176 - 5)])
    OOOO0O0000O00O0O0 = cmds.button(label='Visit 3dtoall.com...', command=lambda *O00OOO00O000OO0O0: O0000O0OOOO000OOO(), height=40, width=146)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(OOOO0O0000O00O0O0, 'top', 305 + OOOO00OOO00OO0OOO), (OOOO0O0000O00O0O0, 'left', 24 - 5)])
    O000O0OOOO00O0OOO = cmds.separator(style='in', w=315, h=6)
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(O000O0OOOO00O0OOO, 'top', 353 + OOOO00OOO00OO0OOO), (O000O0OOOO00O0OOO, 'left', 10)])
    O0OOOO0O00OOO00O0 = cmds.text(label='(c) 2021 3DtoAll. All Rights Reserved.')
    cmds.formLayout(OOO0O0000O0O00000, edit=True, attachForm=[(O0OOOO0O00OOO00O0, 'top', 366 + OOOO00OOO00OO0OOO), (O0OOOO0O00OOO00O0, 'left', 85)])
    cmds.showWindow(O0O000O000OOOO000)
    cmds.window(O0O000O000OOOO000, e=True, width=335, height=330)
    print('START FORM!')
    OOOO0OO0OO00O0000()

def install():

    def O0OOO0O0OO0O0O00O():
        O0OO00000OOO0OO0O = str(versions.current())
        OO000000OO0OO000O = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2022', '2023']
        for O00O000O00OO000OO in OO000000OO0OO000O:
            if O00O000O00OO000OO in O0OO00000OOO0OO0O:
                return True
        OO0OO0OOO00O00O00 = 'Maya Version not Supported. Please visit www.3DtoAll.com'
        cmds.confirmDialog(title='Maya-Tabs', message=OO0OO0OOO00O00O00, button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')
        return False
    if O0OOO0O0OO0O0O00O() == True:
        if os.path.exists(mayaTabsSerialConfigFile) == True:
            install_toolbar()
            install_callbacks()
        else:
            if srl != None and O0OOO0O0OO0O0O00O() == True:
                if chkSrl(srl) == True:
                    install_toolbar()
                    install_callbacks()
                else:
                    guiSerial()
            if srl == None or chkSrl == False:
                guiSerial()

def uninstall():
    uninstall_callbacks()
    uninstall_toolbar()

def install_toolbar():
    from maya_toolkit.tools.maya_tabs_v1_3a.session import install_toolbar
    return install_toolbar()

def uninstall_toolbar():
    from maya_toolkit.tools.maya_tabs_v1_3a.session import close
    return close()

def _O00OO0OO0O0O00OOO(*O0O0OO0000O0O0000):
    O0OO0000OO0000O00 = MayaTabs.instance
    O0OO0000OO0000O00.on_new()

def _O000000OOO0O0O000(*O00O00O0000OO0OOO):
    OOOOOOO0OOOO00O0O = MayaTabs.instance
    OO00O000OO00O0O0O = cmds.file(query=True, sceneName=True)
    OOOOOOO0OOOO00O0O.on_save(OO00O000OO00O0O0O)

def _O0O0OOO0O0OO0O000(*OOO0OOO0OOO0OOO0O):
    OOO0OO000000O00OO = MayaTabs.instance
    O0O0O0000O0O0OOOO = cmds.file(query=True, sceneName=True)
    OOO0OO000000O00OO.on_open(O0O0O0000O0O0OOOO)

def install_callbacks():
    from maya_toolkit.tools.maya_tabs_v1_3a.session import install_callbacks
    return install_callbacks()

def uninstall_callbacks():
    from maya_toolkit.tools.maya_tabs_v1_3a.session import close
    return close()

def initializePlugin(O0O0000OO0O0O0O00):
    install()

def uninitializePlugin(O00O0OO0O0OO00OOO):
    uninstall()

from maya_toolkit.tools.maya_tabs_v1_3a.session import native_open as open, later as _owned_single_shot, Dialogs
import types as _types
QtWidgets=_types.SimpleNamespace(**vars(QtWidgets));QtWidgets.QFileDialog=Dialogs
