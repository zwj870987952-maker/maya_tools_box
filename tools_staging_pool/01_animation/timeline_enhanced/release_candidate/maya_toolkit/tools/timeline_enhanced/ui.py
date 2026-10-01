"""Complete original layouts with a validated document bridge and local history."""
import copy
from pathlib import Path
from maya import cmds
from .native_basic import TimelineTool
from .native_enhanced import TimelineToolEnhanced
from . import model


class Bridge:
    def __init__(self, adapter):
        super().__init__()
        self.adapter = adapter
        self.window_name += '_candidate'
        self.config_file = None
        self.selected_blocks = set()
        self.clipboard = {}
        self.mode = 'drag'
        self._history, self._future = [], []
        self._shortcuts = []

    def snapshot(self):
        return model.document({'start_frame': self.start_frame, 'frame_count': self.frame_count, 'blocks': {str(k): v for k, v in self.blocks.items()}, 'selected': sorted(f for f in self.selected_blocks if f in self.blocks), 'clipboard': {str(k): v for k, v in self.clipboard.items()}})

    def restore(self, state):
        data = model.document(state)
        changed = (self.start_frame, self.frame_count) != (data['start_frame'], data['frame_count'])
        self.start_frame, self.frame_count = data['start_frame'], data['frame_count']
        self.blocks = {int(k): copy.deepcopy(v) for k, v in data['blocks'].items()}
        self.selected_blocks = set(data['selected'])
        self.clipboard = {int(k): copy.deepcopy(v) for k, v in data['clipboard'].items()}
        self.dragging_block = self.drag_source_frame = None
        cmds.intField(self.start_frame_field, edit=True, value=self.start_frame)
        cmds.intField(self.frame_count_field, edit=True, value=self.frame_count)
        if changed:
            self.refresh_timeline()
        else:
            self.update_blocks_display()
        self.update_status()

    def apply(self, action, **params):
        before = self.snapshot()
        result = self.adapter.run(action=action, state=before, **params)
        if not result.success:
            cmds.warning(result.message)
            return False
        after = result.data['state']
        if before != after:
            self._history.append(before)
            self._history = self._history[-100:]
            self._future.clear()
        self.restore(after)
        self.update_status(result.message)
        return True

    def undo_document(self):
        if self._history:
            self._future.append(self.snapshot())
            self.restore(self._history.pop())

    def redo_document(self):
        if self._future:
            self._history.append(self.snapshot())
            self.restore(self._future.pop())

    def update_status(self, message=None):
        if hasattr(self, 'status_text'):
            return TimelineToolEnhanced.update_status(self, message)
        if message:
            cmds.warning(message)

    def refresh_timeline(self):
        parent = cmds.layout(self.timeline_layout, query=True, parent=True)
        cmds.deleteUI(self.timeline_layout)
        self.timeline_layout = cmds.formLayout(parent=parent, width=self.frame_width * self.frame_count, height=self.frame_height)
        self.create_frames()
        self.update_blocks_display()

    def confirm_replace(self):
        return cmds.confirmDialog(title='替换方块', message='目标包含规划方块，是否替换？（不会移动场景关键帧）', button=['替换', '取消'], defaultButton='取消', cancelButton='取消', dismissString='取消') == '替换'

    def add_block(self, frame_num, block_data=None):
        data = block_data or model.STYLES.get(getattr(self, 'current_block_type', 'keyframe'), model.STYLES['keyframe'])
        replace = frame_num in self.blocks
        if not replace or self.confirm_replace():
            return self.apply('add', frame=frame_num, block=data, overwrite=replace)

    def add_block_at_frame(self, frame_num):
        return self.add_block(frame_num)

    def delete_block_at_frame(self, frame_num):
        return self.apply('delete', frames=[frame_num])

    def on_frame_clicked(self, frame_num):
        if self.mode == 'delete':
            return self.delete_block_at_frame(frame_num)
        if self.mode == 'add':
            return self.add_block(frame_num)
        if cmds.getModifiers() & 4:
            selected = set(self.selected_blocks)
            if frame_num in self.blocks:
                selected.symmetric_difference_update({frame_num})
            return self.apply('select', frames=sorted(selected))
        if self.mode == 'select':
            return self.apply('select', frames=[frame_num] if frame_num in self.blocks else [])
        if self.dragging_block is not None:
            return self.drop_block(frame_num)
        if frame_num in self.blocks:
            self.start_drag(frame_num)
            self.update_blocks_display()
        else:
            self.add_block(frame_num)

    def drop_block(self, target_frame):
        if self.dragging_block is not None and self.drag_source_frame is not None:
            source = self.drag_source_frame
            replace = target_frame in self.blocks and target_frame != source
            if replace and not self.confirm_replace():
                return self.cancel_drag()
            return self.apply('move', source_frame=source, frame=target_frame, overwrite=replace)

    def cancel_drag(self):
        self.dragging_block = self.drag_source_frame = None
        self.update_blocks_display()
        self.update_status('取消拖拽')

    def apply_properties(self, frame_num, label, name, color):
        return self.apply('edit', frame=frame_num, block={'label': label, 'name': name, 'color': list(color)})

    def select_block_at_frame(self, frame_num):
        return self.apply('select', frames=[frame_num] if frame_num in self.blocks else [])

    def select_all_blocks(self, *args):
        return self.apply('select', frames=sorted(self.blocks))

    def deselect_all_blocks(self, *args):
        return self.apply('select', frames=[])

    def copy_selected_blocks(self, *args):
        return self.apply('copy')

    def paste_blocks(self, *args):
        frame = cmds.intField(self.current_frame_field, query=True, value=True) if hasattr(self, 'current_frame_field') else int(cmds.currentTime(query=True))
        pending = self.adapter.validate(action='paste', state=self.snapshot(), frame=frame)
        overwrite = False
        if not pending.success:
            if 'replace' not in pending.message or not self.confirm_replace():
                return False
            overwrite = True
        return self.apply('paste', frame=frame, overwrite=overwrite)

    def delete_selected_blocks(self, *args):
        return self.apply('delete')

    def clear_all_blocks(self, *args):
        return self.apply('clear')

    def on_start_frame_changed(self, *args):
        value = cmds.intField(self.start_frame_field, query=True, value=True)
        if not self.apply('configure', start_frame=value):
            cmds.intField(self.start_frame_field, edit=True, value=self.start_frame)

    def on_frame_count_changed(self, *args):
        value = cmds.intField(self.frame_count_field, query=True, value=True)
        if not self.apply('configure', frame_count=value):
            cmds.intField(self.frame_count_field, edit=True, value=self.frame_count)

    def on_current_frame_changed(self, *args):
        return self.apply('set_current_frame', frame=cmds.intField(self.current_frame_field, query=True, value=True))

    def sync_with_maya(self, *args):
        return self.apply('sync')

    def play_timeline(self, *args):
        return self.apply('play')

    def stop_timeline(self, *args):
        return self.apply('stop')

    def save_config(self):
        if not self.config_file:
            return self.save_config_dialog()
        path = Path(self.config_file)
        overwrite = path.exists()
        if overwrite and cmds.confirmDialog(title='保存配置', message='替换现有 JSON？保留独立备份；Maya Undo 无法撤销文件写入。', button=['保存', '取消'], defaultButton='取消', cancelButton='取消', dismissString='取消') != '保存':
            return False
        return self.apply('save', path=str(path), overwrite=overwrite)

    def save_config_dialog(self, *args):
        picked = cmds.fileDialog2(fileMode=0, fileFilter='JSON (*.json)', caption='保存规划方块（文件不可 Maya Undo）')
        if picked:
            self.config_file = picked[0]
            return self.save_config()

    def load_config(self):
        # Original create_ui invokes this. No automatic package/user file read.
        if self.config_file:
            return self.apply('load', path=self.config_file)

    def load_config_dialog(self, *args):
        picked = cmds.fileDialog2(fileMode=1, fileFilter='JSON (*.json)', caption='打开规划方块配置')
        if picked:
            if self.apply('load', path=picked[0]):
                self.config_file = picked[0]

    def set_select_mode(self, *args):
        self.mode = 'select'
        self.cancel_drag()
        self.update_status('选择模式；Ctrl 多选')

    def set_add_mode(self, *args):
        self.mode = 'add'
        self.cancel_drag()
        self.update_status('添加模式')

    def set_delete_mode(self, *args):
        self.mode = 'delete'
        self.cancel_drag()
        self.update_status('删除模式')

    def fit_timeline(self, *args):
        self.frame_width = max(8, min(50, int(cmds.window(self.window_name, query=True, width=True) / self.frame_count)))
        self.refresh_timeline()
        self.update_status('缩放到适合：最小每帧8像素，可继续水平滚动')

    def reset_view(self, *args):
        self.frame_width = 25 if isinstance(self, EnhancedUI) else 20
        self.mode = 'drag'
        self.cancel_drag()
        self.refresh_timeline()

    def install_shortcuts(self):
        import maya.OpenMayaUI as omUI
        major = int(cmds.about(qtVersion=True).split('.')[0])
        if major >= 6:
            from PySide6.QtGui import QShortcut, QKeySequence
            from PySide6.QtWidgets import QWidget
            from shiboken6 import wrapInstance
        else:
            from PySide2.QtWidgets import QShortcut, QWidget
            from PySide2.QtGui import QKeySequence
            from shiboken2 import wrapInstance
        pointer = omUI.MQtUtil.findWindow(self.window_name)
        if not pointer:
            cmds.warning('Window keyboard shortcuts unavailable; use menus')
            return
        widget = wrapInstance(int(pointer), QWidget)
        for key, callback in (('Ctrl+A', self.select_all_blocks), ('Ctrl+C', self.copy_selected_blocks), ('Ctrl+V', self.paste_blocks), ('Delete', self.delete_selected_blocks), ('Escape', self.cancel_drag), ('Ctrl+Z', self.undo_document), ('Ctrl+Shift+Z', self.redo_document)):
            shortcut = QShortcut(QKeySequence(key), widget)
            shortcut.activated.connect(callback)
            self._shortcuts.append(shortcut)


class BasicUI(Bridge, TimelineTool):
    pass


class EnhancedUI(Bridge, TimelineToolEnhanced):
    pass


_WINDOWS = {}


def show_ui(adapter, variant='enhanced'):
    if cmds.about(batch=True):
        raise RuntimeError('Real interactive Maya required')
    if variant not in ('basic', 'enhanced'):
        raise ValueError('variant must be basic/enhanced')
    instance = (BasicUI if variant == 'basic' else EnhancedUI)(adapter)
    _WINDOWS[variant] = instance
    instance.create_ui()
    cmds.formLayout(instance.timeline_layout, edit=True, width=instance.frame_width * instance.frame_count, height=instance.frame_height)
    instance.install_shortcuts()
    return instance
