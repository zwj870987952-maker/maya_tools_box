import maya.cmds as cmds
import os


class ReferenceReplacementTool:
    def __init__(self):
        self.window_name = "ReferenceReplacementTool"
        self.file_paths = []
        self.source_objects = []
        self.target_objects = []
        self.replace_rows = []

    def create_ui(self):
        if cmds.window(self.window_name, exists=True):
            cmds.deleteUI(self.window_name)

        cmds.window(self.window_name, title="Reference Replacement Tool", widthHeight=(400, 350))
        main_layout = cmds.columnLayout(adjustableColumn=True)

        # 文件路径布局
        file_path_layout = cmds.columnLayout(adjustableColumn=True)
        # 文件列表名字
        cmds.text(label="文件列表:")
        self.file_path_text = cmds.textScrollList(allowMultiSelection=True, append=self.file_paths, height=150)

        button_layout = cmds.rowLayout(numberOfColumns=2, columnWidth2=[200, 66], columnAttach2=["both", "both"], columnOffset2=[0, 5])
        add_button = cmds.button(label="添加文件", command=self.browse_files, width=200)
        delete_button = cmds.button(label="删除文件", command=self.delete_selected_files, width=66)
        cmds.setParent('..')

        # 添加替换布局
        add_replace_layout = cmds.columnLayout(adjustableColumn=True)
        cmds.separator(height=10, style="none")
        cmds.text(label="添加替换:")
        add_replace_button = cmds.button(label="添加替换", command=self.add_replace_fields, width=400)
        cmds.separator(height=10, style="none")

        # 执行按钮
        execute_button = cmds.button(label="执行替换", command=self.execute_replacement, width=400)
        cmds.separator(height=10, style="none")

        cmds.setParent(main_layout)
        cmds.showWindow()

    def browse_files(self, *args):
        selected_files = cmds.fileDialog2(fileMode=4, dialogStyle=2, caption="选择Maya文件", fileFilter="Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)")
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
        # 创建并列布局
        replace_layout = cmds.rowLayout(numberOfColumns=5, columnWidth=[(1, 100), (2, 150), (3, 150), (4, 150), (5, 50)], columnAttach5=["both", "both", "both", "both", "both"],
                                        columnOffset5=[5, 5, 5, 5, 5])

        # 创建原始物体框
        source_object_field = cmds.textField(placeholderText="原始", width=150)
        self.source_objects.append(source_object_field)

        # 创建替换物体框
        target_object_field = cmds.textField(placeholderText="替换", width=150)
        self.target_objects.append(target_object_field)

        # 创建添加按钮
        add_button = cmds.button(label="添加替换", command=lambda x, idx=len(self.source_objects): self.fill_target_field(target_object_field, idx), width=50)

        # 创建删除按钮
        delete_button = cmds.button(label="删除条目", command=lambda x, layout=replace_layout: self.delete_replace_field(layout), width=50)

        # 将控件添加到布局中
        cmds.setParent('..')
        self.replace_rows.append(replace_layout)

    def fill_target_field(self, target_field, index):
        selected_files = cmds.fileDialog2(fileMode=4, dialogStyle=2, caption="选择Maya文件", fileFilter="Maya Files (*.ma *.mb);;Maya ASCII (*.ma);;Maya Binary (*.mb)")
        if selected_files:
            file_path = selected_files[0]
            cmds.textField(target_field, edit=True, text=file_path)

    def delete_replace_field(self, layout):
        if layout in self.replace_rows:
            # 获取点击删除按钮所在的布局
            index = self.replace_rows.index(layout)

            # 获取原始物体框和替换物体框
            source_object_field = self.source_objects[index]
            target_object_field = self.target_objects[index]

            # 删除对应的原始物体框和替换物体框，并更新列表
            cmds.deleteUI(layout, control=True)
            self.replace_rows.remove(layout)
            self.source_objects.remove(source_object_field)
            self.target_objects.remove(target_object_field)

    def execute_replacement(self, *args):
        for file_path in self.file_paths:
            cmds.file(file_path, open=True, force=True)

            for i in range(len(self.source_objects)):
                source_name = cmds.textField(self.source_objects[i], query=True, text=True)
                target_path = cmds.textField(self.target_objects[i], query=True, text=True)

                references = cmds.ls(type='reference')
                for ref_node in references:
                    ref_path = cmds.referenceQuery(ref_node, filename=True)
                    if "sharedReferenceNode" not in ref_path and source_name in ref_path:
                        cmds.file(target_path, loadReference=ref_node, type="mayaBinary" if ref_path.endswith(".mb") else "mayaAscii", options="v=0")

        cmds.warning("替换完成！")


def show_reference_replacement_tool():
    tool = ReferenceReplacementTool()
    tool.create_ui()


# 运行脚本
show_reference_replacement_tool()
