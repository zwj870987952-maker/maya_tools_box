import os
import json
from PySide2 import QtWidgets, QtCore
import shiboken2
import maya.OpenMayaUI as omui

def get_maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return shiboken2.wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

def find_target_paths(base_path):
    anim_paths = []
    skeleton_paths = []

    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name.lower() == 'anim':
                anim_paths.append(os.path.join(root, dir_name))
        
        for file_name in files:
            if 'skeleton' in file_name.lower():
                skeleton_paths.append(os.path.join(root, file_name))

    return anim_paths, skeleton_paths

def convert_to_ue_path(windows_path):
    """Convert a Windows path to a UE relative path."""
    windows_path = windows_path.replace("\\", "/")
    content_index = windows_path.find("/Content/")
    
    if content_index != -1:
        relative_path = windows_path[content_index:]
        relative_path = "/Game" + relative_path[len("/Content"):]
        return relative_path
    return windows_path

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
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
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
        base_path = self.root_path.text().strip()
        if not base_path or not os.path.exists(base_path):
            QtWidgets.QMessageBox.warning(self, "Warning", "Please enter a valid root path.")
            return

        anim_paths, skeleton_paths = find_target_paths(base_path)

        # Clear previous entries
        self.destination_path_combo.clear()
        self.skeleton_path_combo.clear()

        # Populate destination paths
        for path in anim_paths:
            ue_path = convert_to_ue_path(path)
            self.destination_path_combo.addItem(ue_path)

        # Populate skeleton paths
        for path in skeleton_paths:
            ue_path = convert_to_ue_path(path)
            ue_path = strip_uasset_extension(ue_path)
            self.skeleton_path_combo.addItem(ue_path)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls]
        self.fbx_files_text.append("\n".join(paths))
        event.acceptProposedAction()

    def generate_config(self):
        destination_content_path = self.destination_path_combo.currentText().strip()
        skeleton_path = self.skeleton_path_combo.currentText().strip()
        fbx_files = self.fbx_files_text.toPlainText().strip().split("\n")

        if not destination_content_path or not skeleton_path or not fbx_files:
            QtWidgets.QMessageBox.warning(self, "Warning", "Please fill all fields.")
            return

        config_data = {
            "fbx_files": fbx_files,
            "destination_content_path": destination_content_path,
            "skeleton_path": skeleton_path
        }

        skeleton_name = os.path.basename(skeleton_path) + "_config.json"
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        config_dir = os.path.join(desktop_path, "FBX_Configs")

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        config_file_path = os.path.join(config_dir, skeleton_name)
        counter = 1

        while os.path.exists(config_file_path):
            config_file_path = os.path.join(config_dir, f"{os.path.splitext(skeleton_name)[0]}_{counter}.json")
            counter += 1

        try:
            with open(config_file_path, 'w', encoding='utf-8') as config_file:
                json.dump(config_data, config_file, indent=4, ensure_ascii=False)
            QtWidgets.QMessageBox.information(self, "Success", f"Config saved to {config_file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to save config: {str(e)}")

    def load_config(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Config", "", "JSON Files (*.json);;All Files (*)", options=options)
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as config_file:
                    config_data = json.load(config_file)
                    
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

show_fbx_config_generator()
