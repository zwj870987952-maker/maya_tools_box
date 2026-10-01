"""Keep the complete original interface; route scene-changing callbacks through the API."""
import json
from maya import cmds
from .tool import ConstraintManagerTool
from . import engine

_window = None


def show_ui(parent=None):
    global _window
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required; no standalone QWidget creation')
    from . import native_ui as native
    QtWidgets, QtCore, QtGui = native.QtWidgets, native.QtCore, native.QtGui

    class CandidateUI(native.ConstraintTool):
        def __init__(self, parent=None):
            self.api = ConstraintManagerTool()
            super(CandidateUI, self).__init__(parent)
            button = QtWidgets.QPushButton('打开完整重建辅助面板 / JSON 快照')
            button.clicked.connect(show_rebuild_ui)
            self.layout().addWidget(button)

        def call(self, **args):
            result = self.api.run(**args)
            if not result.success:
                cmds.warning(result.message)
                return None
            return result.data

        def get_constraint_weights(self, objects):
            names = engine.discover(objects)
            attrs = []
            for n in names:
                d = engine.info(n)
                self.constraint_data[n] = {'constrained_object': d['constrained'], 'target_objects': [x['node'] for x in d['targets']]}
                attrs.extend(t['weight_plug'] for t in d['targets'])
            return attrs

        def parse_constraint_attr(self, value):
            try:
                actual, d, target = engine.weight(value.replace('[断开] ', '').replace('[反向] ', ''))
                return d['node'], target['node'], target['alias']
            except Exception:
                return None, None, None

        def get_constraint_info(self, name):
            d = engine.info(name)
            return {'type': d['type'], 'constrained_objects': [d['constrained']], 'target_objects': [x['node'] for x in d['targets']]}

        def all_items(self):
            return [self.attr_list.item(i) for i in range(self.attr_list.count()) if not self.attr_list.item(i).is_separator]

        def selected_items(self):
            return [i for i in self.attr_list.selectedItems() if not i.is_separator]

        def item_weights(self, item):
            return engine.info(item.constraint_node)['targets'] if item.constraint_node else []

        def weight_plugs(self, items):
            values = []
            for item in items:
                selected = [x['weight_plug'] for x in self.item_weights(item)] if self.btn_toggle_display.isChecked() else list(item.weight_attrs)
                for value in selected:
                    if value not in values:
                        values.append(value)
            return values

        def run_tool(self, mode):
            self.call(action='weights', selected_weights=self.weight_plugs(self.selected_items()), all_weights=self.weight_plugs(self.all_items()), mode={1: 'zero', 2: 'selected_one', 3: 'one'}[mode], keyframe=self.checkbox_set_keyframe.isChecked())
            self.attr_list.viewport().update()

        def set_custom_weight(self):
            try:
                value = float(self.input_custom_weight.text())
            except ValueError:
                cmds.warning('请输入有限数值')
                return
            self.call(action='weights', selected_weights=self.weight_plugs(self.selected_items()), mode='custom', value=value, keyframe=self.checkbox_set_keyframe.isChecked())
            self.attr_list.viewport().update()

        def selected_constraints(self):
            return list(dict.fromkeys(i.constraint_node for i in self.selected_items() if i.constraint_node))

        def action(self, action, **extras):
            data = self.call(action=action, constraints=self.selected_constraints(), **extras)
            if data is None:
                return
            if action == 'rebuild':
                mapping = {x['original']: x['new'] for x in data['results']}
                for item in self.all_items():
                    if item.constraint_node in mapping:
                        old, new = item.constraint_node, mapping[item.constraint_node]
                        item.constraint_node = new
                        item.weight_attrs = [a.replace(old+'.', new+'.', 1) for a in item.weight_attrs]
                        item.setText(item.text().replace(old, new))
            if action == 'delete':
                for item in list(self.all_items()):
                    if not cmds.objExists(item.constraint_node):
                        self.attr_list.takeItem(self.attr_list.row(item))
            else:
                for item in self.all_items():
                    if cmds.objExists(item.constraint_node):
                        d = engine.info(item.constraint_node)
                        self.constraint_data[d['node']] = {'constrained_object': d['constrained'], 'target_objects': [x['node'] for x in d['targets']]}
                        disconnected = not bool(d['outputs'])
                        item.is_disconnected = disconnected
                        original_text = item.text().replace('[断开] ', '').replace('[反向] ', '')
                        item.setText(('[反向] ' if action == 'reverse' and disconnected else '[断开] ' if disconnected else '')+original_text)
                        item.disconnected_info = {'constraint_type': d['type'], 'constrained_objects': [d['constrained']], 'target_objects': [x['node'] for x in d['targets']], 'weight_values': {x['weight_plug']: x['weight'] for x in d['targets']}, 'original_color': item.foreground().color().name()}
            self.attr_list.viewport().update()

        def disconnect_constraints(self):
            self.action('disconnect')

        def restore_constraints(self):
            self.action('restore')

        def reverse_constraints(self):
            self.action('reverse')

        def rebuild_constraints(self):
            self.action('rebuild')

        def delete_selected_constraints(self):
            self.action('delete')

        def set_rest_position(self):
            self.action('rest')

        def modify_constrained_axis(self, maintain_offset=True):
            self.action('axis', maintain_offset=maintain_offset)

        def remove_target(self, maintain_offset=False):
            self.action('remove_target', selected_weights=self.weight_plugs(self.selected_items()), maintain_offset=maintain_offset)

        def save_list(self):
            name, ok = QtWidgets.QInputDialog.getText(self, '保存列表', '输入新列表名称：')
            if ok and name:
                items = [{'text': i.text(), 'color': i.foreground().color().name(), 'constraint_node': i.constraint_node or '', 'weight_attrs': i.weight_attrs} for i in self.all_items()]
                data = self.call(action='save_list', list_name=name, items=items)
                if data:
                    self.add_saved_list_button(data['locator'])

        def load_list_from_locator(self, name):
            if not cmds.objExists(name+'.notes'):
                return
            raw = cmds.getAttr(name+'.notes') or ''
            if not raw.lstrip().startswith('{'):
                return super(CandidateUI, self).load_list_from_locator(name)
            try:
                data = json.loads(raw)
                from .tool import normalize
                normalize(action='save_list', list_name='validate_only', items=data['items'])
            except Exception as exc:
                cmds.warning('无效列表数据：'+str(exc))
                return
            self.attr_list.clear()
            for row in data['items']:
                item = native.CustomListWidgetItem(row['text'], row.get('constraint_node', ''), row.get('weight_attrs', []))
                item.setForeground(QtGui.QColor(row.get('color', '#e0e0e0')))
                self.attr_list.addItem(item)
            live = [i.constraint_node for i in self.all_items() if i.constraint_node and cmds.objExists(i.constraint_node)]
            if live:
                self.get_constraint_weights(list(dict.fromkeys(live)))

    if _window is not None:
        _window.close()
        _window.deleteLater()
    _window = CandidateUI(parent or native.maya_main_window())
    _window.show()
    return _window


def show_rebuild_ui(*unused):
    """All four original auxiliary actions, now callable callbacks and explicit file paths."""
    if cmds.about(batch=True):
        raise RuntimeError('Interactive Maya required')
    api = ConstraintManagerTool()
    window = 'staging_constraint_rebuild'
    if cmds.window(window, exists=True):
        cmds.deleteUI(window)
    cmds.window(window, title='重建约束：查找 / 断开 / 恢复 / 真正反向', widthHeight=(450, 300))
    cmds.columnLayout(adjustableColumn=True)
    listing = cmds.textScrollList(allowMultiSelection=True, height=120)
    def call(action, **extra):
        constraints = cmds.textScrollList(listing, query=True, selectItem=True) or cmds.textScrollList(listing, query=True, allItems=True) or []
        result = api.run(action=action, constraints=constraints, **extra)
        if not result.success:
            cmds.warning(result.message)
        return result
    def discover(*unused):
        result = api.run(action='inspect')
        if result.success:
            cmds.textScrollList(listing, edit=True, removeAll=True)
            cmds.textScrollList(listing, edit=True, append=[d['node'] for d in result.data['constraints']])
    cmds.button(label='查找约束物体（只读）', command=discover)
    cmds.button(label='断开约束输出（保留原节点）', command=lambda *x: call('disconnect'))
    cmds.button(label='恢复完整连接', command=lambda *x: call('restore'))
    cmds.button(label='反向约束（原被约束物体驱动各目标）', command=lambda *x: call('reverse'))
    def file_action(action, mode):
        paths = cmds.fileDialog2(fileMode=mode, fileFilter='JSON (*.json)') or []
        if paths:
            call(action, path=paths[0])
    cmds.button(label='导出断开/反向快照为新 JSON', command=lambda *x: file_action('export_snapshot', 0))
    cmds.button(label='载入同场景 UUID 快照', command=lambda *x: file_action('import_snapshot', 1))
    cmds.showWindow(window)
    return window
