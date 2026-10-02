"""Complete folder drag/drop/list/clear/progress/cancel workflow with new output policy."""
from maya_toolkit.core.context import UndoChunkContext
from . import SceneVirusCleanerTool,normalize,clean_files
_window=None
def show_ui():
    global _window
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Interactive Maya required')
    try:
        from PySide6 import QtWidgets,QtCore
        import shiboken6 as shiboken
    except ImportError:
        from PySide2 import QtWidgets,QtCore
        import shiboken2 as shiboken
    import maya.OpenMayaUI as omui
    class FolderDrop(QtWidgets.QListWidget):
        def __init__(self):super().__init__();self.setAcceptDrops(True)
        def dragEnterEvent(self,e):
            if e.mimeData().hasUrls():e.acceptProposedAction()
        def dragMoveEvent(self,e):
            if e.mimeData().hasUrls():e.acceptProposedAction()
        def dropEvent(self,e):
            from pathlib import Path
            existing={self.item(i).text() for i in range(self.count())}
            for url in e.mimeData().urls():
                path=str(Path(url.toLocalFile()).resolve())
                if Path(path).is_dir() and path not in existing:self.addItem(path);existing.add(path)
            e.acceptProposedAction()
    class Window(QtWidgets.QMainWindow):
        def __init__(self,parent):
            super().__init__(parent);self.setWindowTitle('Maya文件清理候选');self.resize(600,500)
            main=QtWidgets.QWidget();self.setCentralWidget(main);layout=QtWidgets.QVBoxLayout(main)
            layout.addWidget(QtWidgets.QLabel('拖放多个文件夹；不改原文件。新输出目录须在输入目录外。'))
            self.paths=FolderDrop();layout.addWidget(self.paths)
            self.output=QtWidgets.QLineEdit();self.output.setPlaceholderText('全新输出目录（父目录已存在）');layout.addWidget(self.output)
            self.policy=QtWidgets.QComboBox();self.policy.addItems(['known','all_scripts','none']);layout.addWidget(self.policy)
            self.requires=QtWidgets.QCheckBox('移除非Maya requires（可能破坏合法插件）');layout.addWidget(self.requires)
            self.feedback=QtWidgets.QPlainTextEdit();self.feedback.setReadOnly(True);layout.addWidget(self.feedback)
            for label,callback in [('预检文件和变更',self.preview),('开始清理',self.clean),('清除路径',self.paths.clear)]:
                button=QtWidgets.QPushButton(label);button.clicked.connect(callback);layout.addWidget(button)
            self.busy=False
        def kwargs(self,action='clean'):
            return dict(action=action,directories=[self.paths.item(i).text() for i in range(self.paths.count())],output_dir=self.output.text().strip(),
                script_policy=self.policy.currentText(),remove_plugin_requires=self.requires.isChecked(),confirm_broad_removal=True)
        def preview(self):
            result=SceneVirusCleanerTool().run(dry_run=True,**self.kwargs());self.feedback.setPlainText(result.to_json());return result
        def clean(self):
            if self.busy:return
            preview=self.preview()
            if not preview.success:return
            text='创建过滤后的新.ma和原字节备份？'+'\n广泛策略会删除合法脚本/插件声明！' if self.policy.currentText()=='all_scripts' or self.requires.isChecked() else '创建过滤后的新.ma和原字节备份？'
            if QtWidgets.QMessageBox.question(self,'确认清理范围',text,QtWidgets.QMessageBox.StandardButton.Yes|QtWidgets.QMessageBox.StandardButton.No,QtWidgets.QMessageBox.StandardButton.No)!=QtWidgets.QMessageBox.StandardButton.Yes:return
            progress=QtWidgets.QProgressDialog('离线处理文件...','取消',0,preview.data['count'],self);progress.setMinimumDuration(0)
            progress.setWindowModality(QtCore.Qt.WindowModality.WindowModal);self.busy=True
            try:
                def update(value,total):progress.setValue(value);QtWidgets.QApplication.processEvents()
                result=clean_files(normalize(self.kwargs()),progress=update,cancel=progress.wasCanceled)
                import json
                self.feedback.setPlainText(json.dumps(result,ensure_ascii=True,indent=2))
            except Exception as e:self.feedback.setPlainText('处理失败：'+str(e))
            finally:self.busy=False;progress.close()
        def closeEvent(self,event):
            if self.busy:event.ignore()
            else:event.accept()
    if _window is not None:
        try:_window.close();_window.deleteLater()
        except RuntimeError:pass
    pointer=omui.MQtUtil.mainWindow();parent=shiboken.wrapInstance(int(pointer),QtWidgets.QWidget) if pointer else None
    _window=Window(parent);_window.show();return _window
