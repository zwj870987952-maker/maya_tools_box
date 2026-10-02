import os
import json
try:
    from PySide6 import QtWidgets, QtCore
    import shiboken6 as shiboken2
except ImportError:
    from PySide2 import QtWidgets, QtCore
    import shiboken2
from engine_toolkit.tools.ue_fbx_auto_import import config as config_api
import maya.OpenMayaUI as omui

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def find_target_paths(base_path):
    return config_api.find_target_paths(base_path)

def convert_to_ue_path(windows_path):
    return config_api.convert_to_ue_path(windows_path)

def strip_uasset_extension(path):
    """Remove the .uasset extension if present."""
    if path.endswith(".uasset"):
        return path[:-len(".uasset")]
    return path

class FBXConfigGenerator(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(FBXConfigGenerator, self).__init__(parent)
        self.setWindowTitle("FBX Config Generator")
        self.setGeometry(300, 300, 450, 400)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.Window)
        self.setup_ui()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Root Path for Intelligent Detection
        self.root_path = QtWidgets.QLineEdit(self)
        self.detect_button = QtWidgets.QPushButton("Detect Paths", self)
        self.detect_button.clicked.connect(self.detect_paths)
        root_layout = QtWidgets.QHBoxLayout()
        root_layout.addWidget(QtWidgets.QLabel("Root Path:", self))
        root_layout.addWidget(self.root_path)
        root_layout.addWidget(self.detect_button)

        # Load Button
        self.load_button = QtWidgets.QPushButton("Load Config", self)
        self.load_button.clicked.connect(self.load_config)

        # Destination Path ComboBox
        self.destination_path_combo = QtWidgets.QComboBox(self)
        self.destination_path_combo.setEditable(True)
        destination_layout = QtWidgets.QHBoxLayout()
        destination_layout.addWidget(QtWidgets.QLabel("Destination Path:", self))
        destination_layout.addWidget(self.destination_path_combo)

        # Skeleton Path ComboBox
        self.skeleton_path_combo = QtWidgets.QComboBox(self)
        self.skeleton_path_combo.setEditable(True)
        skeleton_layout = QtWidgets.QHBoxLayout()
        skeleton_layout.addWidget(QtWidgets.QLabel("Skeleton Path:", self))
        skeleton_layout.addWidget(self.skeleton_path_combo)

        # FBX Files
        self.fbx_files_text = QtWidgets.QTextEdit(self)
        self.fbx_files_text.setAcceptDrops(True)
        self.fbx_files_text.setPlaceholderText("Drag and drop FBX files here or paste paths...")

        self.fbx_files_text.dragEnterEvent = self.dragEnterEvent
        self.fbx_files_text.dropEvent = self.dropEvent

        # Generate Button
        self.generate_button = QtWidgets.QPushButton("Generate Config", self)
        self.generate_button.clicked.connect(self.generate_config)

        layout.addLayout(root_layout)
        layout.addWidget(self.load_button)  # Add load button to layout
        layout.addLayout(destination_layout)
        layout.addLayout(skeleton_layout)
        layout.addWidget(self.fbx_files_text)
        layout.addWidget(self.generate_button)

    def detect_paths(self):
        try:
            base = self.root_path.text().strip()
            anim, skeleton = config_api.find_target_paths(base)
            content = config_api.content_root(base)
            anim = [config_api.convert_to_ue_path(p, content) for p in anim]
            skeleton = [config_api.convert_to_ue_path(p, content) for p in skeleton]
            self.destination_path_combo.clear(); self.skeleton_path_combo.clear()
            self.destination_path_combo.addItems(anim); self.skeleton_path_combo.addItems(skeleton)
        except Exception as error:
            QtWidgets.QMessageBox.warning(self, 'Warning', str(error))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]
        self.fbx_files_text.append("\n".join(paths))
        event.acceptProposedAction()

    def generate_config(self):
        data = {'destination_content_path': self.destination_path_combo.currentText().strip(),
                'skeleton_path': self.skeleton_path_combo.currentText().strip(),
                'fbx_files': [p.strip() for p in self.fbx_files_text.toPlainText().splitlines() if p.strip()]}
        try:
            result = config_api.generate_config(data, os.path.join(os.path.expanduser('~'), 'Desktop', 'FBX_Configs'))
            QtWidgets.QMessageBox.information(self, 'Success', 'Config saved to ' + result['output'])
        except Exception as error:
            QtWidgets.QMessageBox.critical(self, 'Error', str(error))

    def load_config(self):
        options = QtWidgets.QFileDialog.Option(0)
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Config", "", "JSON Files (*.json);;All Files (*)", options=options)

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as config_file:
                    config_data = config_api.check_config(json.load(config_file))["config"]

                # Fill in the fields
                self.fbx_files_text.clear()
                self.destination_path_combo.clear()
                self.skeleton_path_combo.clear()

                self.destination_path_combo.addItem(config_data.get("destination_content_path", ""))
                self.skeleton_path_combo.addItem(config_data.get("skeleton_path", ""))
                self.fbx_files_text.setPlainText("\n".join(config_data.get("fbx_files", [])))

                # Removed success message
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"Failed to load config: {str(e)}")

def show_fbx_config_generator():
    global fbx_config_window
    try:
        if fbx_config_window and fbx_config_window.isVisible():
            fbx_config_window.raise_()
            return
    except NameError:
        pass

    fbx_config_window = FBXConfigGenerator(get_maya_main_window())
    fbx_config_window.show()
    return fbx_config_window
