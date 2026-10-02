"""Retain complete original Qt layout and callbacks, route writes to Base API."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/04_pipeline_io/batch_importer_v3'
PKG=UNIT/'release_candidate/maya_toolkit/tools/batch_importer_v3'
tree=ast.parse((UNIT/'批量导入加强版v3.py').read_text(encoding='utf8'))
functions=[]; start=False; statements=[]
for node in tree.body:
    if isinstance(node,ast.FunctionDef):
        if node.name not in ('import_references','import_all_items','remove_referenced_objects'): functions.append(ast.unparse(node))
    elif isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='maya_window' for t in node.targets): start=True; statements.append(node)
    elif start: statements.append(node)
names=sorted({n.id for node in statements for n in ast.walk(node) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Store)})
body='\n'.join(ast.unparse(n) for n in statements)
body='def show_ui():\n    global '+', '.join(names)+'\n'+ '\n'.join('    '+line for line in body.splitlines())+'\n    return window\n'
header='''"""Complete original Qt UI; no module-level window creation."""
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omui
try:
    from PySide6 import QtWidgets,QtGui,QtCore
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtWidgets,QtGui,QtCore
    from shiboken2 import wrapInstance
from .tool import BatchImporterV3Tool,namespace_base
count_spinbox=None

def ui_items():
    return [{'path':list_widget.item(i).text(),'count':count_layout.itemAt(i).widget().value(),
             'namespace':name_layout.itemAt(i).widget().text()} for i in range(list_widget.count())]

def report(result):
    print(result.to_dict())
    if not result.success: cmds.warning(result.message)
    return result

def import_references(): return report(BatchImporterV3Tool().run(action='reference',items=ui_items()))
def import_all_items(): return report(BatchImporterV3Tool().run(action='import',items=ui_items()))
def remove_referenced_objects(): return report(BatchImporterV3Tool().run(action='remove_reference'))
'''
code=header+'\n'+'\n\n'.join(functions)+'\n\n'+body
code=code.replace('long(main_window_ptr)','int(main_window_ptr)').replace('file_name = os.path.basename(file).split(\'.\')[0]','file_name = namespace_base(file)').replace('file_name = os.path.basename(file_path).split(\'.\')[0]','file_name = namespace_base(file_path)').replace('setReadOnly(True)','setReadOnly(False)')
code=code.replace("folder = cmds.fileDialog2(dialogStyle=3, fileMode=3, caption='Select Folder', fileFilter=default_filter)[0]", "chosen = cmds.fileDialog2(dialogStyle=3, fileMode=3, caption='Select Folder', fileFilter=default_filter)\n    folder = chosen[0] if chosen else None")
code=code.replace("window.setWindowTitle('Import Object')","window.setWindowTitle('Import Object — namespace可编辑 / Del Ref删除整份引用')")
(PKG/'ui.py').write_text(code,encoding='utf8',newline='\n')
(PKG/'__init__.py').write_text('from .tool import BatchImporterV3Tool\n',encoding='utf8')
print('Full original Qt layout, recursive folder/count/name controls and watermark prepared')
