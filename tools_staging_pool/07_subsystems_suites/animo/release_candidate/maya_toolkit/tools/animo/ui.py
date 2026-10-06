"""Small review panel; native resources are loaded only after explicit actions."""
_window = None


def show(tool, parent=None):
    from . import session
    session.maya_cmds()
    try:
        from PySide6 import QtWidgets, QtCore
    except ImportError:
        from PySide2 import QtWidgets, QtCore
    from maya_toolkit.core import get_maya_main_window, apply_dark_theme
    global _window
    if _window is not None:
        try:
            _window.show()
            _window.raise_()
            _window.activateWindow()
            return _window
        except RuntimeError:
            _window = None

    class ReviewWindow(QtWidgets.QDialog):
        def __init__(self):
            super(ReviewWindow, self).__init__(parent or get_maya_main_window())
            self.setObjectName('MayaToolkitAnimoReview')
            self.setWindowTitle('Animo V10.6.0 — 待人工检验')
            self.resize(1000, 760)
            self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window)
            layout = QtWidgets.QVBoxLayout(self)
            notice = QtWidgets.QLabel('候选尚未通过 Maya 检验。请在备份场景操作；安装只写全新运行目录，不覆盖已有 Animo。')
            notice.setWordWrap(True)
            layout.addWidget(notice)
            path = session.runtime_destination(session.maya_cmds())
            destination = QtWidgets.QLabel('运行目录：' + str(path))
            destination.setWordWrap(True)
            layout.addWidget(destination)
            actions = QtWidgets.QHBoxLayout()
            for text, action in (('安装运行副本', 'install_runtime'), ('打开原生工具栏', 'launch_toolbar')):
                button = QtWidgets.QPushButton(text)
                button.clicked.connect(lambda checked=False, name=action: self.run_action(name))
                actions.addWidget(button)
            layout.addLayout(actions)
            self.search = QtWidgets.QLineEdit()
            self.search.setPlaceholderText('搜索中文用途、原始功能名或 operation ID')
            self.search.textChanged.connect(self.populate)
            layout.addWidget(self.search)
            self.tree = QtWidgets.QTreeWidget()
            self.tree.setHeaderLabels(['功能', '分类', 'operation ID'])
            self.tree.setColumnWidth(0, 300)
            self.tree.setColumnWidth(1, 220)
            self.tree.itemSelectionChanged.connect(self.show_details)
            layout.addWidget(self.tree, 3)
            controls = QtWidgets.QHBoxLayout()
            preview = QtWidgets.QPushButton('预检所选')
            preview.clicked.connect(lambda: self.run_selected(True))
            execute = QtWidgets.QPushButton('执行所选（人工检验）')
            execute.clicked.connect(lambda: self.run_selected(False))
            controls.addWidget(preview)
            controls.addWidget(execute)
            layout.addLayout(controls)
            self.details = QtWidgets.QPlainTextEdit()
            self.details.setReadOnly(True)
            layout.addWidget(self.details, 2)
            apply_dark_theme(self)
            self.populate()

        def populate(self, *_):
            text = self.search.text().casefold()
            self.tree.clear()
            groups = {}
            for row in session.operations():
                if text and text not in (' '.join(str(row[k]) for k in
                        ('id', 'name', 'category', 'category_zh', 'description'))).casefold():
                    continue
                group = groups.get(row['category'])
                if group is None:
                    group = QtWidgets.QTreeWidgetItem(self.tree, [row['category_zh'], row['category'], ''])
                    groups[row['category']] = group
                item = QtWidgets.QTreeWidgetItem(group, [row['name'], row['category_zh'], row['id']])
                item.setData(0, QtCore.Qt.UserRole, row['id'])
            self.tree.expandAll()

        def selected_id(self):
            item = self.tree.currentItem()
            return item.data(0, QtCore.Qt.UserRole) if item is not None else None

        def show_details(self):
            import json
            operation_id = self.selected_id()
            if operation_id:
                self.details.setPlainText(json.dumps(session.find_operation(operation_id), ensure_ascii=False, indent=2))

        def display_result(self, result):
            self.details.setPlainText(result.to_json())
            print(result.to_json())

        def run_action(self, action):
            self.display_result(tool.run(action=action))

        def run_selected(self, dry_run):
            operation_id = self.selected_id()
            if not operation_id:
                self.details.setPlainText('请先选择一个具体功能入口。')
                return
            self.display_result(tool.run(dry_run=dry_run, action='invoke', operation_id=operation_id))

    _window = ReviewWindow()
    _window.show()
    return _window
