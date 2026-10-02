"""Retain the complete original file-manager layout, adapt its write callbacks."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/04_pipeline_io/batch_processor_v3'
PKG=UNIT/'release_candidate/maya_toolkit/tools/batch_processor_v3'
tree=ast.parse((UNIT/'文件批量执行v3.py').read_text(encoding='utf8'))
removed={'execute_script','remove_unknown_nodes','show_maya_file_manager'}
replaced={'save_button_clicked','save_as_ma','save_in_current_path','auto_execute','on_overwrite_save_changed'}
nodes=[]
for node in tree.body:
    if isinstance(node,(ast.Import,ast.ImportFrom,ast.Try)): nodes.append(node)
    elif isinstance(node,ast.FunctionDef) and node.name not in removed: nodes.append(node)
    elif isinstance(node,ast.ClassDef):
        if node.name=='MayaFileManager': node.body=[n for n in node.body if not isinstance(n,ast.FunctionDef) or n.name not in replaced]
        if node.name=='MyListWidget': node.body=[n for n in node.body if not isinstance(n,ast.FunctionDef) or n.name not in ('open_selected_files','mouseDoubleClickEvent')]
        nodes.append(node)
code='"""Original full Qt file/script lists, sort/modes and controls; writes use API."""\nimport html as _html\nfrom pathlib import Path\nfrom .tool import BatchProcessorV3Tool\n'+ '\n\n'.join(ast.unparse(n) for n in nodes)
code=code.replace('QtWidgets.QPlainTextEdit(self)','QtWidgets.QTextEdit(self)').replace('self.log_text.appendHtml(html)','self.log_text.append(html)').replace('level, message)','level, _html.escape(str(message)))')
code+='''

def open_file(path):
    if cmds.file(query=True,modified=True):
        cmds.warning('当前场景有未保存修改，请先保存。'); return
    if not Path(path).is_file(): cmds.warning('文件不存在：'+path); return
    try: cmds.file(path,open=True,force=False,executeScriptNodes=False,prompt=False)
    except Exception as exc: cmds.warning(str(exc))

def open_selected(self):
    items=self.selectedItems()
    if len(items)!=1: cmds.warning('请只选择一个文件打开。'); return
    open_file(items[0].text())

def open_double(self,event):
    item=self.itemAt(event.pos())
    if item: open_file(item.text())

MyListWidget.open_selected_files=open_selected
MyListWidget.mouseDoubleClickEvent=open_double
OriginalFileManager=MayaFileManager

class MayaFileManager(OriginalFileManager):
    def build_ui(self):
        super().build_ui()
        self.execution_mode=QtWidgets.QComboBox(self)
        self.execution_mode.addItem('隔离 mayapy（默认，保留当前场景）','isolated')
        self.execution_mode.addItem('当前 Maya（只允许干净已保存场景）','interactive')
        self.error_policy=QtWidgets.QComboBox(self)
        self.error_policy.addItem('出错跳过当前文件','skip_file'); self.error_policy.addItem('出错停止批次','stop_batch')
        self.cleanup_checkbox=QtWidgets.QCheckBox('保存前删除 unknown 节点（默认关闭）',self)
        for w in (self.execution_mode,self.error_policy,self.cleanup_checkbox): self.layout().insertWidget(1,w)
        self.overwrite_save_checkbox.setToolTip('覆盖 .ma/.mb；强制原始字节备份，文件写入不能 Maya Undo')
        self.setWindowTitle('Maya File Manager — 隔离批处理候选')
        self.busy=False

    def closeEvent(self,event):
        if self.busy: event.ignore()
        else: super().closeEvent(event)

    def on_overwrite_save_changed(self,state):
        if self.overwrite_save_checkbox.isChecked(): self.save_backup_checkbox.setChecked(True)

    def controls(self,enabled):
        self.busy=not enabled
        for w in (self.save_button,self.auto_execute_button,self.file_list_widget,self.script_list_widget,self.path_field,
                  self.save_backup_checkbox,self.save_after_checkbox,self.overwrite_save_checkbox,self.execution_mode,self.error_policy,self.cleanup_checkbox): w.setEnabled(enabled)

    def report(self,result):
        for row in (result.data or {}).get('scenes',[]):
            self.log(row['source']+': '+row['message'],'OK' if row['success'] else 'ERROR')
            for script in row.get('scripts',[]): self.log(script['path']+': '+('OK' if script['success'] else script.get('message','failed')),'OK' if script['success'] else 'ERROR')
            if row.get('backup'): self.log('原始字节备份：'+row['backup'])
            for output in row.get('outputs',[]): self.log('已保存：'+output['path'])
        self.log(result.message,'OK' if result.success else 'ERROR')
        return result

    def save_button_clicked(self):
        if self.busy: return
        if self.path_field.text().strip(): return self.save_as_ma()
        return self.save_in_current_path()

    def save_as_ma(self):
        source=cmds.file(query=True,sceneName=True); directory=self.path_field.text().strip()
        if not source or not Path(directory).is_dir(): self.log('需要已保存场景和有效保存目录','ERROR'); return
        target=str(Path(directory)/(Path(source).stem+'.ma'))
        self.controls(False)
        try: return self.report(BatchProcessorV3Tool().run(action='save_current',output=target,remove_unknown=self.cleanup_checkbox.isChecked()))
        finally: self.controls(True)

    def save_in_current_path(self):
        self.controls(False)
        try: return self.report(BatchProcessorV3Tool().run(action='save_current',overwrite=True,remove_unknown=self.cleanup_checkbox.isChecked()))
        finally: self.controls(True)

    def auto_execute(self):
        if self.busy: return
        files=[self.file_list_widget.item(i).text() for i in range(self.file_list_widget.count()) if self.execute_all_mode or self.file_list_widget.item(i).isSelected()]
        scripts=[self.script_list_widget.item(i).text() for i in range(self.script_list_widget.count())]
        if not files: self.log('文件列表为空或没有选中的文件','ERROR'); return
        params=dict(action='process',files=files,scripts=scripts,base_dir=self.path_field.text().strip() or None,
                    save_backup=self.save_backup_checkbox.isChecked(),save_after=self.save_after_checkbox.isChecked(),overwrite=self.overwrite_save_checkbox.isChecked(),
                    remove_unknown=self.cleanup_checkbox.isChecked(),execution_mode=self.execution_mode.currentData(),error_policy=self.error_policy.currentData())
        progress=QtWidgets.QProgressDialog('正在处理文件','取消',0,len(files),self)
        progress.setWindowModality(QtCore.Qt.WindowModal); progress.setMinimumDuration(0); progress.setAutoClose(False)
        tool=BatchProcessorV3Tool()
        def update(index,total,message):
            progress.setValue(index); progress.setLabelText(message); QtWidgets.QApplication.processEvents()
        tool.progress=update; tool.cancelled=progress.wasCanceled
        self.controls(False); self.log('开始批处理；脚本可操作外部文件，取消不会回滚已完成输出。')
        try: return self.report(tool.run(**params))
        finally: progress.close(); self.controls(True)

_file_manager_instance=None
def show_maya_file_manager():
    global _file_manager_instance
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    try:
        if _file_manager_instance is not None:
            _file_manager_instance.show(); _file_manager_instance.raise_(); return _file_manager_instance
    except RuntimeError: _file_manager_instance=None
    _file_manager_instance=MayaFileManager(); _file_manager_instance.show(); return _file_manager_instance
'''
ast.parse(code)
(PKG/'ui.py').write_text(code,encoding='utf8',newline='\n')
print('Full original manager layout retained with safe batch/save callbacks')
