"""Keep both Python layouts and the original MEL form as independent UI modes."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/04_pipeline_io/replace_references'
PKG=UNIT/'release_candidate/maya_toolkit/tools/replace_references'
source=ROOT/'tools_staging_pool/04_pipeline_io/batch_importer_v3/release_candidate/maya_toolkit/tools/batch_importer_v3/tool.py'
tree=ast.parse(source.read_text(encoding='utf8'))
functions=[ast.unparse(n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('references','file_hash')]
(PKG/'reference_ops.py').write_text('import hashlib\nfrom pathlib import Path\n'+ '\n\n'.join(functions)+'\n',encoding='utf8',newline='\n')
tree=ast.parse((UNIT/'批量替换引用物体v01.py').read_text(encoding='utf8'))
cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)); cls.body=[n for n in cls.body if not isinstance(n,ast.FunctionDef) or n.name!='execute_replacement']
code='''"""Complete selected-reference EN, batch-row and original MEL-style forms."""
from maya import cmds
from .tool import ReplaceReferencesTool
tool=ReplaceReferencesTool()
def report(result):
    print(result.to_dict())
    if not result.success: cmds.warning(result.message)
    return result
def replace_references_with_new_file_ui(selected_references,new_file_path):
    return report(tool.run(action='replace',reference_nodes=selected_references,new_file=new_file_path,rename_namespace=True))
def replace_references_from_ui(*args):
    chosen=cmds.fileDialog2(fileMode=1,caption='Select the new file',fileFilter='Maya Files (*.ma *.mb)')
    if chosen: return report(tool.run(action='replace',new_file=chosen[0],rename_namespace=True))
def replace_references_in_maya(*args):
    if cmds.window('replaceReferenceWindow',exists=True): cmds.deleteUI('replaceReferenceWindow',window=True)
    window=cmds.window('replaceReferenceWindow',title='Replace Reference Files',widthHeight=(300,100)); cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='Select reference nodes or objects; whole files will be replaced.')
    cmds.button(label='Select New File and Replace References',command=replace_references_from_ui); cmds.showWindow(window); return window
'''+ast.unparse(cls)
code=code.replace('main_layout = cmds.columnLayout(adjustableColumn=True)','main_layout = cmds.columnLayout(adjustableColumn=True)\n        self.main_layout=main_layout')
code=code.replace('    def add_replace_fields(self, *args):','    def add_replace_fields(self, *args):\n        cmds.setParent(self.main_layout)')
code+='''
OriginalBatchTool=ReferenceReplacementTool
class ReferenceReplacementTool(OriginalBatchTool):
    def execute_replacement(self,*args):
        rules=[{'source_contains':cmds.textField(source,query=True,text=True),'target':cmds.textField(target,query=True,text=True)} for source,target in zip(self.source_objects,self.target_objects)]
        directory=cmds.fileDialog2(fileMode=3,caption='批量替换：选择全新结果目录（保留原scene）')
        if not directory: return
        return report(tool.run(action='batch',files=list(self.file_paths),rules=rules,output_dir=directory[0],rename_namespace=False))
def show_reference_replacement_tool(*args):
    instance=ReferenceReplacementTool(); instance.create_ui(); return instance
def replaceReferenceUI(*args):
    if cmds.window('replaceRefWindow',exists=True): cmds.deleteUI('replaceRefWindow')
    window=cmds.window('replaceRefWindow',title='Replace Reference',widthHeight=(350,100)); cmds.columnLayout(adjustableColumn=True,rowSpacing=8,columnAttach=('both',10))
    cmds.text(label='New Reference File:',align='left'); cmds.rowLayout(numberOfColumns=2,columnWidth2=(240,80),columnAttach=(1,'both',0))
    field=cmds.textField(editable=False,text='')
    def browse(*args):
        chosen=cmds.fileDialog2(fileMode=1,caption='Select New Reference File',fileFilter='Maya Files (*.ma *.mb)')
        if chosen: cmds.textField(field,edit=True,text=chosen[0])
    cmds.button(label='Browse...',command=browse); cmds.setParent('..'); cmds.separator(height=8)
    def execute(*args):
        target=cmds.textField(field,query=True,text=True)
        selected=cmds.ls(selection=True,long=True) or []
        if not selected: cmds.warning('Please select a referenced object'); return
        return report(tool.run(action='replace',objects=[selected[0]],new_file=target,rename_namespace=False))
    cmds.button(label='Execute Replace',command=execute,height=30,backgroundColor=(.6,.8,.4)); cmds.setParent('..'); cmds.showWindow(window); return window
def show_ui():
    if cmds.about(batch=True): raise RuntimeError('Interactive Maya required')
    if cmds.window('replaceReferencesModes',exists=True): cmds.deleteUI('replaceReferencesModes')
    window=cmds.window('replaceReferencesModes',title='引用替换候选',widthHeight=(360,170)); cmds.columnLayout(adjustableColumn=True)
    cmds.text(label='整引用替换；无edits/无嵌套，先用备份场景。')
    cmds.button(label='EN多选替换并改namespace',command=replace_references_in_maya)
    cmds.button(label='原MEL式单选替换（保留namespace）',command=replaceReferenceUI)
    cmds.button(label='原批量文件/替换条目（隔离新结果）',command=show_reference_replacement_tool)
    cmds.showWindow(window); return window
'''
ast.parse(code)
(PKG/'ui.py').write_text('\n'.join(line.rstrip() for line in code.splitlines())+'\n',encoding='utf8',newline='\n')
print('All three original layouts and self-contained eligible reference helpers prepared')
