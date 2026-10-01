"""Preserve complete installer/UI and fixed complete upstream distribution."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/tb_anim_tools'
RC = UNIT / 'release_candidate'
PKG = RC / 'maya_toolkit/tools/tb_anim_tools'


def main():
    raw = UNIT / 'tbAnimToolsInstaller.py'
    text = raw.read_text(encoding='utf-8')
    tree = ast.parse(text)
    cls = next(x for x in tree.body if isinstance(x, ast.ClassDef))
    style = next(x for x in tree.body if isinstance(x, ast.Assign) and any(isinstance(n, ast.Name) and n.id == 'styleSheet' for n in x.targets))
    methods = {m.name: ast.get_source_segment(text, m) for m in cls.body if isinstance(m, ast.FunctionDef)}
    init = methods['__init__'].replace('parent=wrapInstance(int(omUI.MQtUtil.mainWindow()), QWidget)', 'parent=None')
    init = init.replace('super(tbAnimToolsInstaller, self).__init__(parent=parent)', "if cmds.about(batch=True):\n            raise RuntimeError('Open the installer only in interactive Maya')\n        if parent is None:\n            pointer = omUI.MQtUtil.mainWindow()\n            if not pointer:\n                raise RuntimeError('Maya main window is unavailable')\n            parent = wrapInstance(int(pointer), QWidget)\n        super(tbAnimToolsInstaller, self).__init__(parent=parent)\n        from .tool import TBAnimToolsTool\n        self.adapter = TBAnimToolsTool()")
    init = init.replace("'https://github.com/tb-animator/tbAnimTools/archive/refs/heads/main.zip'", "'bundled fixed snapshot; network disabled'")
    init = init.replace('Qt.PopupFocusReason | Qt.Tool | Qt.FramelessWindowHint', 'Qt.Tool | Qt.FramelessWindowHint').replace('self.autoFillBackground = True', 'self.setAutoFillBackground(True)').replace('self.setFixedSize(400, 120)', 'self.setFixedSize(660, 290)')
    init = init.replace("QLabel('tbAnimTools installer')", "QLabel('tbAnimTools · pinned offline installer')").replace("QLabel('Welcome to tbAnimTools, click install to choose the installation directory')", "QLabel('Tom Bailey · LGPL notice / upstream GPL LICENSE · no warranty\\nChoose a NEW directory. Activation changes Maya settings and commands.')").replace("QPushButton('Install')", "QPushButton('1. Install complete files (no activation)')")
    init = init.replace('self.setLayout(self.mainLayout)', "self.registerButton = QPushButton('2. Register module (new tbAnimTools.mod only)')\n        self.launchButton = QPushButton('3. Launch original suite in this Maya session')\n        self.registerButton.clicked.connect(lambda: self.activate('register_module'))\n        self.launchButton.clicked.connect(lambda: self.activate('launch_native'))\n        self.layout.addWidget(self.registerButton)\n        self.layout.addWidget(self.launchButton)\n        self.setLayout(self.mainLayout)")
    methods['__init__'] = init
    methods['paintEvent'] = methods['paintEvent'].replace('grad.setColorAt(0, "#323232")', 'grad.setColorAt(0, QColor("#323232"))').replace('grad.setColorAt(0.1, "#373737")', 'grad.setColorAt(0.1, QColor("#373737"))').replace('grad.setColorAt(1, "#323232")', 'grad.setColorAt(1, QColor("#323232"))')
    for name in ('mousePressEvent', 'mouseMoveEvent'):
        methods[name] = methods[name].replace('event.globalPos()', '(event.globalPosition().toPoint() if hasattr(event, "globalPosition") else event.globalPos())')
    methods['pickInstallFolder'] = methods['pickInstallFolder'].replace('pm.fileDialog2', 'cmds.fileDialog2')
    methods['createVersionFile'] = '''def createVersionFile(self):
        # The unchanged upstream version/config files must stay unchanged.
        # Our separate receipt already records exact commit and file hashes.
        from .files import RECEIPT
        self.versionDataFile = os.path.join(self.installPath, RECEIPT)
        if not os.path.isfile(self.versionDataFile):
            raise RuntimeError('Installation receipt is missing')'''
    methods['installTools'] = '''def installTools(self):
        self.installPath = self.pathLineEdit.text()
        if self.download_project_files():
            self.createVersionFile()
            self.infoText.setText('Complete files installed. Module registration and suite startup are separate buttons.')'''
    methods['download_project_files'] = '''def download_project_files(self):
        result = self.adapter.run(action='install_files', destination=self.installPath)
        if not result.success:
            QMessageBox.warning(self, 'Install failed', result.message)
            return False
        return True'''
    methods['installModule'] = '''def installModule(self):
        return self.activate('register_module')'''
    extra = '''    def activate(self, action):
        self.installPath = self.pathLineEdit.text()
        message = ('Activation writes a new module file and disables automatic upstream updates. '
                   'Native startup may write preferences, runtime commands, menus, plugin state and hotkeys. '
                   'Maya Undo cannot revert these changes. Back up your Maya profile first. Continue?')
        if QMessageBox.question(self, 'Explicit suite activation', message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) != QMessageBox.Yes:
            return False
        result = self.adapter.run(action=action, destination=self.installPath, acknowledge_external_effects=True)
        if not result.success:
            QMessageBox.warning(self, 'Activation failed', result.message)
            return False
        self.infoText.setText(result.message + '\\nVerify deferred startup in Script Editor.')
        return True
'''
    header = '''# Modified staging installer, 2026-10-01: Qt6/Python3 compatibility,
# fixed offline ZIP, no overwrite, explicit registration/startup separation.
# Original copyright Tom Bailey 2020; original LGPL v3-or-later notice retained
# in upstream/tbAnimToolsInstaller.py.original. Full suite GPL LICENSE included.
import os
import maya.cmds as cmds
import maya.OpenMayaUI as omUI
qt_major = int(cmds.about(qtVersion=True).split('.')[0])
if qt_major >= 6:
    from PySide6.QtWidgets import *
    from PySide6.QtGui import *
    from PySide6.QtCore import *
    from shiboken6 import wrapInstance
elif qt_major >= 5:
    from PySide2.QtWidgets import *
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from shiboken2 import wrapInstance
else:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance
'''
    notice = next(n for n in tree.body if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and 'License and Copyright' in str(n.value.value))
    body = ast.get_source_segment(text, notice) + '\n' + header + '\n' + ast.get_source_segment(text, style) + '\n\nclass tbAnimToolsInstaller(QDialog):\n    oldPos = None\n\n'
    for name, method in methods.items():
        lines = method.splitlines()
        # get_source_segment keeps the original indentation after first line.
        if name in ('createVersionFile', 'installTools', 'download_project_files', 'installModule'):
            lines[1:] = ['    ' + line for line in lines[1:]]
        body += '    ' + lines[0] + '\n' + '\n'.join(lines[1:]) + '\n\n'
    body += extra + '''
_WINDOW = None

def show_ui(parent=None):
    global _WINDOW
    if _WINDOW is not None:
        try:
            _WINDOW.close()
        except RuntimeError:
            pass
    _WINDOW = tbAnimToolsInstaller(parent)
    _WINDOW.show()
    return _WINDOW

def onMayaDroppedPythonFile(*args):
    return show_ui()
'''
    ast.parse(body)
    (PKG / 'ui.py').write_text(body, encoding='utf-8', newline='\n')
    rows = []
    for source in [raw] + sorted((UNIT / 'Help').rglob('*')):
        if not source.is_file():
            continue
        rel = source.relative_to(UNIT)
        target = PKG / 'upstream' / (str(rel) + ('.original' if source.suffix == '.py' else ''))
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        rows.append({'path': rel.as_posix(), 'archive': target.relative_to(PKG).as_posix(), 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    archive_path = next((PKG / 'upstream').glob('tbAnimTools-*.zip'))
    with zipfile.ZipFile(archive_path) as archive:
        entries = archive.infolist()
        license_path = next(x for x in entries if x.filename.endswith('/LICENSE'))
        (PKG / 'upstream/LICENSE').write_bytes(archive.read(license_path))
    (PKG / 'catalog.json').write_text(json.dumps({'original_files': rows, 'original_ui_methods': list(methods), 'snapshot': json.loads((PKG / 'upstream/snapshot.json').read_text()), 'suite_files': [x.filename for x in entries], 'license': 'Installer header LGPL v3 or later; upstream LICENSE GPL v3, preserve both notices and exact component provenance'}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    (UNIT / '.gitattributes').write_text('*.py -text\n*.gif -text\n', encoding='utf-8')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    launch = (ROOT / 'tools_staging_pool/01_animation/root_motion_bake/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('root_motion_bake', 'tb_anim_tools').replace('RootMotionBakeTool', 'TBAnimToolsTool')
    (RC / 'launch_candidate.py').write_text(launch, encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    promotion = {'tool_id': 'tb_anim_tools', 'registration': {'module': 'tb_anim_tools', 'class_name': 'TBAnimToolsTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': [x['path'] for x in rows] + [archive_path.name, 'LICENSE', 'snapshot.json'], 'dependencies': ['Windows Maya cmds; original suite Qt/plugins/commercial optional proApps remain upstream dependencies; no PyMel required by candidate installer'], 'acceptance_required': True, 'change_summary': 'Complete original installer methods/UI/help archived and ported, plus full fixed upstream suite snapshot with source/resources. Offline hash-checked safe ZIP installation into a new directory, no overwrites, distinct module/native activation with persistent update disablement, read-only inspect/dry-run. Original entire suite is unchanged and only runs on explicit interactive activation.', 'verification_limitations': ['Maya GUI/native suite startup and individual suite tools not_run', 'Original installer LGPL notice differs from upstream GPL LICENSE; component notices preserved without relicensing claims', 'Registration writes filesystem and optionVars; native startup effects are outside Undo and may include deferred jobs, hotkeys/plugins/runtime commands', 'Snapshot is complete upstream open distribution, optional paid/pro plugin dependencies are not installed/unlocked', 'Existing installation updates deliberately rejected; source raw and vendor suite files unchanged']}
    (RC / 'promotion.json').write_text(json.dumps(promotion, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'original_files': len(rows), 'upstream_members': len(entries), 'ui_methods': len(methods)}))

if __name__ == '__main__':
    main()
