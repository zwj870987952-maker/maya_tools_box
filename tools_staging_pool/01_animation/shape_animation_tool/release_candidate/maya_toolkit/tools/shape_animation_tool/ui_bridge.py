"""Every original SAT control dispatches to the complete checked engine."""
from functools import partial
import uuid

import maya.cmds as cmds
import maya.mel as mel

from .Qt import QtCore, QtGui, QtWidgets
from .runtime import Engine, resolve
from .tool import ShapeAnimationTool

_window = None


def current(self):
    return Engine(getattr(self,'session',None))


def refresh(self,*args,rebuild=True):
    engine = current(self)
    records = engine.data['layers']
    ids = {r['id'] for r in records}
    if getattr(self,'layer_id',None) not in ids:
        self.layer_id = engine.data['current'] if records else None
    row = next((r for r in records if r['id']==self.layer_id),None)
    if row:
        try:
            engine.graph(row)
            self._last_scene_error=None
        except Exception as exc:
            if getattr(self,'_last_scene_error',None)!=str(exc):
                cmds.warning(str(exc))
                self._last_scene_error=str(exc)
    self.meshes = [r['label'] for r in records]
    self.curLayer = row['label'] if row else ''
    self.curMesh = resolve(row['mesh']) if row else ''
    self.bs_name = resolve(row['bs']) if row and row.get('bs') else ''
    self.keyFrames = sorted(p['frame'] for p in row['pairs']) if row else []
    edit = engine.data['editing']
    self.editMode = self.nowType = bool(edit)
    self.bs1 = resolve(edit['sculpt']) if edit else ''
    self.curFrame = edit['frame'] if edit else cmds.currentTime(query=True)
    if rebuild:
        blocker = QtCore.QSignalBlocker(self.geo_listWidget)
        self.geo_listWidget.clear()
        for r in records:
            item = QtWidgets.QListWidgetItem(r['label'])
            item.setData(QtCore.Qt.UserRole,r['id'])
            item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable)
            item.setFont(QtGui.QFont('Verdana',10))
            state = bool(cmds.getAttr(resolve(r['bs'])+'.envelope')) if r.get('bs') else True
            item.setCheckState(QtCore.Qt.Checked if state else QtCore.Qt.Unchecked)
            self.geo_listWidget.addItem(item)
            if r['id']==self.layer_id:
                self.geo_listWidget.setCurrentItem(item)
        del blocker
    self.sculpt_btn.blockSignals(True)
    self.sculpt_btn.setChecked(bool(edit))
    self.sculpt_btn.blockSignals(False)
    self.sculpt_btn.setStyleSheet('background-color: rgb(0,80,40)' if edit else '')
    self.geo_groupBox.setEnabled(not bool(edit))
    self.remove_btn.setEnabled(bool(row) and not bool(edit))
    self.groupBox_3.setEnabled(bool(row))
    self.groupBox_4.setEnabled(bool(row))
    for widget in (self.prevKey_btn,self.nextKey_btn,self.key_btn,self.deleteKey_btn):
        widget.setEnabled(bool(row) and not bool(edit))
    for widget in (self.brush_btn,self.points_btn,self.resetShape_btn,self.actionUse_Artisan_Tool,self.actionUse_Components,self.actionReset_Shape_to_Default):
        widget.setEnabled(bool(edit))
    available = shapes_brush_available()
    self.shapesBrush_btn.setEnabled(bool(edit) and available)
    self.actionUse_ShapesBrush_plugin.setEnabled(bool(edit) and available)
    now = cmds.currentTime(query=True)
    at = self.keyFrames.index(now)+1 if now in self.keyFrames else '-'
    self.keyData_label.setText(str(at)+' / '+str(len(self.keyFrames)))
    self.key_btn.setStyleSheet('background-color: #5f2626' if at!='-' else '')


def invoke(self,action,**kwargs):
    options = {'action':action,**kwargs}
    if getattr(self,'session',None):
        options['session']=self.session
    if action not in ('status','add_mesh','remove_all','inspect_legacy','adopt_legacy') and getattr(self,'layer_id',None):
        options['layer_id']=self.layer_id
    result = ShapeAnimationTool().run(**options)
    if result.success:
        self.session = result.data.get('session')
        self.layer_id = result.data.get('added_layer',getattr(self,'layer_id',None))
        refresh(self)
    else:
        cmds.warning('Shape Animation Tool: '+result.message)
        QtWidgets.QMessageBox.warning(self,'修型操作未完成',result.message+'\n操作失败时请检查 Script Editor，并使用 Maya Undo 恢复。')
    return result


def start(self):
    self.session = None
    self.layer_id = None
    self._job = None
    self._pick_context = 'mtkSATPick_'+uuid.uuid4().hex[:12]
    self._before_pick_context = None
    engine = current(self)
    self.session = engine.sid
    refresh(self)
    self._job = cmds.scriptJob(event=['timeChanged',partial(time_changed,self)],protected=False)
    # Do not replace the user's Maya timeline press/release callbacks.
    legacy = cmds.ls('sat',type='network') or []
    if legacy and not engine.data['layers']:
        cmds.warning('发现旧 SAT 数据。候选不会自动接管；可先用 inspect_legacy 预检，再显式 adopt_legacy。')


def time_changed(self):
    if not self.isVisible():
        return
    try:
        engine = current(self)
        edit = engine.data['editing']
        if edit and cmds.currentTime(query=True)!=edit['frame']:
            # Time/Undo callbacks remain read-only. The original setChecked(False)
            # did not call its clicked slot and left an inconsistent sculpt state.
            if not getattr(self,'_warned_pending_frame',False):
                cmds.warning('雕刻仍处于待完成状态；返回原帧或点击 Edit 完成，再操作其他修型。')
                self._warned_pending_frame=True
        else:
            self._warned_pending_frame=False
        refresh(self)
    except Exception as exc:
        cmds.warning(str(exc))


def choose(self,item,previous=None):
    if item is not None:
        self.layer_id = item.data(QtCore.Qt.UserRole)
        refresh(self,rebuild=False)


def toggle(self,item=None):
    if item is None:
        item = self.geo_listWidget.currentItem()
    if item is not None:
        self.layer_id = item.data(QtCore.Qt.UserRole)
        invoke(self,'set_enabled',enabled=item.checkState()==QtCore.Qt.Checked)


def sculpt(self,*args):
    result = invoke(self,'end_sculpt' if current(self).data['editing'] else 'begin_sculpt')
    if result.success and self.editMode:
        try:
            panel = cmds.getPanel(withFocus=True)
            if cmds.getPanel(typeOf=panel)=='modelPanel' and cmds.isolateSelect(panel,query=True,state=True):
                cmds.isolateSelect(panel,addSelected=True)
            if self.brushMode==1:
                brush(self)
            elif self.brushMode==2:
                shapes_brush(self)
            else:
                components(self,True)
        except RuntimeError as exc:
            cmds.warning('雕刻网格已准备；笔刷初始化需在 Maya 中检查：'+str(exc))


def components(self,component=False):
    edit = current(self).data['editing']
    if not edit:
        return
    node = resolve(edit['sculpt'])
    cmds.select(node,replace=True)
    if component:
        cmds.selectMode(component=True)
        cmds.selectType(vertex=True)
        cmds.hilite(node,replace=True)
        cmds.setToolTo('moveSuperContext')
    else:
        cmds.selectMode(object=True)
        cmds.hilite(node,unHilite=True)
        cmds.setToolTo('selectSuperContext')


def brush(self,*args):
    self.brushMode = 1
    components(self,False)
    if current(self).data['editing']:
        cmds.SculptGeometryTool()


def shapes_brush_available():
    try:
        return bool(cmds.pluginInfo('SHAPESBrush',query=True,loaded=True)) and bool(mel.eval('exists "SHAPESBrush"'))
    except RuntimeError:
        return False


def shapes_brush(self,*args):
    if not shapes_brush_available():
        cmds.warning('SHAPESBrush 插件/MEL 未安装或未加载；请自行安装后重新打开窗口')
        return
    self.brushMode = 2
    components(self,False)
    if current(self).data['editing']:
        mel.eval('SHAPESBrush')


def points(self,*args):
    self.brushMode = 3
    components(self,True)


def close(self,event):
    try:
        if current(self).data['editing']:
            result = invoke(self,'end_sculpt')
            if not result.success:
                event.ignore()
                return
        if self._job is not None and cmds.scriptJob(exists=self._job):
            cmds.scriptJob(kill=self._job,force=True)
        if cmds.draggerContext(self._pick_context,exists=True):
            if cmds.currentCtx()==self._pick_context and self._before_pick_context:
                cmds.setToolTo(self._before_pick_context)
            cmds.deleteUI(self._pick_context)
        event.accept()
    except Exception as exc:
        cmds.warning(str(exc))
        event.ignore()


def install(klass):
    # All 33 MainWindow methods remain in native.py, with original algorithms
    # archived and an explicit checked dispatch for every scene-changing control.
    klass.start=start
    klass.updateFrame=lambda self,*a: time_changed(self)
    klass.updateUI=lambda self,*a: refresh(self)
    klass.fillGeoList=lambda self,*a: refresh(self)
    klass.selectMeshInList=choose
    klass.onOffBs=toggle
    klass.addMesh=lambda self,*a: invoke(self,'add_mesh')
    klass.removeMesh=lambda self,*a: invoke(self,'remove_mesh')
    klass.removeAllMeshes=lambda self,*a: invoke(self,'remove_all')
    klass.setKey=lambda self,*a: invoke(self,'set_key')
    klass.deleteKey=lambda self,*a: invoke(self,'delete_key')
    klass.deleteAllKeys=lambda self,*a: invoke(self,'delete_all_keys')
    klass.getKeytimes=lambda self,*a: refresh(self)
    klass.saveData=lambda self,*a: refresh(self)  # Scene mutations save in the checked engine.
    klass.loadData=lambda self,*a: refresh(self)
    klass.sculpt=sculpt
    klass.scultpMenuOn=sculpt  # One click dispatches; no disconnected setChecked toggle.
    klass.setSelectionMode=components
    klass.brush=brush
    klass.shapesBrush=shapes_brush
    klass.points=points
    klass.resetShape=lambda self,*a: invoke(self,'reset_shape')
    klass.stepKey=lambda self,direction,*a: invoke(self,'step_key',direction=direction)
    klass.returnName=lambda self,name: name.rsplit('|',1)[-1].rsplit(':',1)[-1]
    def helper_only(self,node):
        from .runtime import owned,shape
        owned(node,current(self).sid,'temporary_mesh')
        return shape(node)
    klass.removeIntermediateShape=helper_only
    klass.fixShapeName=helper_only  # Actual shape paths are queried, never guessed by name.
    klass.closeEvent=close
    original_picker=klass.pickMesh
    def pick(self,*args):
        if current(self).data['editing']:
            cmds.warning('完成当前雕刻后再拾取另一个网格')
            return
        if cmds.currentCtx()!=self._pick_context:
            self._before_pick_context=cmds.currentCtx()
        return original_picker(self)
    klass.pickMesh=pick


def show_ui(parent=None):
    global _window
    if cmds.about(batch=True) or QtWidgets.QApplication.instance() is None:
        raise RuntimeError('Open this UI inside a running interactive Maya, never standalone mayapy')
    if _window is not None:
        _window.close()
        if _window.isVisible():
            return _window
    from .native import MainWindow
    candidate = MainWindow(parent)
    candidate.setObjectName('mtkSATCandidateWindow')
    try:
        candidate.start()
        candidate.connectSignals()
        candidate.show()
    except Exception:
        if getattr(candidate,'_job',None) is not None and cmds.scriptJob(exists=candidate._job):
            cmds.scriptJob(kill=candidate._job,force=True)
        candidate.deleteLater()
        raise
    _window = candidate
    return candidate
