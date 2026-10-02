"""Complete selected-reference EN, batch-row and original MEL-style forms."""
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
class ReferenceReplacementTool:

    def __init__(self):
        self.window_name = 'ReferenceReplacementTool'
        self.file_paths = []
        self.source_objects = []
        self.target_objects = []
        self.replace_rows = []

    def create_ui(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)
        cmds.window(self.window_name, title='Reference Replacement Tool', widthHeight=(400, 350))
        main_layout = cmds.columnLayout(adjustableColumn=True)
        self.main_layout=main_layout
        file_path_layout = cmds.columnLayout(adjustableColumn=True)
        cmds.text(label='文件列表:')
        self.file_path_text = cmds.textScrollList(allowMultiSelection=True, append=self.file_paths, height=150)
        button_layout = cmds.rowLayout(numberOfColumns=2, columnWidth2=[200, 66], columnAttach2=['both', 'both'], columnOffset2=[0, 5])
        add_button = cmds.button(label='添加文件', command=self.browse_files, width=200)
        delete_button = cmds.button(label='删除文件', command=self.delete_selected_files, width=66)
        cmds.setParent('..')
        add_replace_layout = cmds.columnLayout(adjustableColumn=True)
        cmds.separator(height=10, style='none')
        cmds.text(label='添加替换:')
        add_replace_button = cmds.button(label='添加替换', command=self.add_replace_fields, width=400)
        cmds.separator(height=10, style='none')
        execute_button = cmds.button(label='执行替换', command=self.execute_replacement, width=400)
        cmds.separator(height=10, style='none')
        cmds.setParent(main_layout)
        cmds.showWindow()

    def browse_files(self, *args):
        selected_files = cmds.fileDialog2(fileMode=4, dialogStyle=2, caption='选择Maya文件', fileFilter='Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)')
        if selected_files:
            for file_path in selected_files:
                if file_path not in self.file_paths:
                    self.file_paths.append(file_path)
            cmds.textScrollList(self.file_path_text, edit=True, removeAll=True)
            cmds.textScrollList(self.file_path_text, edit=True, append=self.file_paths)

    def delete_selected_files(self, *args):
        selected_items = cmds.textScrollList(self.file_path_text, query=True, selectItem=True)
        if selected_items:
            for selected_item in selected_items:
                self.file_paths.remove(selected_item)
            cmds.textScrollList(self.file_path_text, edit=True, removeAll=True)
            cmds.textScrollList(self.file_path_text, edit=True, append=self.file_paths)

    def add_replace_fields(self, *args):
        cmds.setParent(self.main_layout)
        replace_layout = cmds.rowLayout(numberOfColumns=5, columnWidth=[(1, 100), (2, 150), (3, 150), (4, 150), (5, 50)], columnAttach5=['both', 'both', 'both', 'both', 'both'], columnOffset5=[5, 5, 5, 5, 5])
        source_object_field = cmds.textField(placeholderText='原始', width=150)
        self.source_objects.append(source_object_field)
        target_object_field = cmds.textField(placeholderText='替换', width=150)
        self.target_objects.append(target_object_field)
        add_button = cmds.button(label='添加替换', command=lambda x, idx=len(self.source_objects): self.fill_target_field(target_object_field, idx), width=50)
        delete_button = cmds.button(label='删除条目', command=lambda x, layout=replace_layout: self.delete_replace_field(layout), width=50)
        cmds.setParent('..')
        self.replace_rows.append(replace_layout)

    def fill_target_field(self, target_field, index):
        selected_files = cmds.fileDialog2(fileMode=4, dialogStyle=2, caption='选择Maya文件', fileFilter='Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)')
        if selected_files:
            file_path = selected_files[0]
            cmds.textField(target_field, edit=True, text=file_path)

    def delete_replace_field(self, layout):
        if layout in self.replace_rows:
            index = self.replace_rows.index(layout)
            source_object_field = self.source_objects[index]
            target_object_field = self.target_objects[index]
            cmds.deleteUI(layout, control=True)
            self.replace_rows.remove(layout)
            self.source_objects.remove(source_object_field)
            self.target_objects.remove(target_object_field)
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
