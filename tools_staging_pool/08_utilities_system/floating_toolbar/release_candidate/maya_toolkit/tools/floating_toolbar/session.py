from pathlib import Path
import base64,json
from . import config_io
window=None;filters=[]
def qt():
    from . import ui
    return ui
def shelf_record(value):
    from maya import cmds
    if not isinstance(value,str) or len(value)>1024 or not cmds.shelfButton(value,exists=True):raise ValueError('Existing Maya shelfButton required')
    icon=cmds.shelfButton(value,q=True,image=True) or ''
    row={'command':cmds.shelfButton(value,q=True,command=True) or '', 'source_type':cmds.shelfButton(value,q=True,sourceType=True),'source_element':cmds.shelfButton(value,q=True,label=True) or value,'text':cmds.shelfButton(value,q=True,label=True) or value}
    # Built-in Qt resource icons are resolved only in the real Maya process.
    if icon:
        ui=qt();pixmap=ui.QtGui.QPixmap(icon)
        if pixmap.isNull():pixmap=ui.QtGui.QPixmap(':/'+icon)
        if not pixmap.isNull():row['icon_png']=encode_icon(ui.QtGui.QIcon(pixmap))
    return config_io.rows([row])[0]
def encode_icon(icon):
    ui=qt();data=ui.QtCore.QByteArray();buffer=ui.QtCore.QBuffer(data);buffer.open(ui.QtCore.QIODevice.WriteOnly)
    if not icon.pixmap(32,32).save(buffer,'PNG'):raise ValueError('Icon encoding failed')
    return base64.b64encode(bytes(data)).decode('ascii')
def apply_button(button,row):
    row=config_io.rows([row])[0];ui=qt();icon=ui.QtGui.QIcon()
    if row.get('icon_png'):
        pix=ui.QtGui.QPixmap();blob=base64.b64decode(row['icon_png'])
        if not pix.loadFromData(blob,'PNG'):raise ValueError('Icon decoding failed')
        icon=ui.QtGui.QIcon(pix)
    elif row.get('icon') and Path(row['icon']).is_file():icon=ui.QtGui.QIcon(row['icon'])
    button.command=row['command'];button.sourceElement=row['source_element'];button.source_type=row['source_type'];button.setText(row['text']);button.setIcon(icon)
def snapshot(win=None):
    win=win or window
    if win is None:raise RuntimeError('Open owned floating toolbar first')
    result=[]
    for i in range(win.toolbar_flow.count()):
        button=win.toolbar_flow.itemAt(i).widget()
        row={'command':button.command or '', 'source_element':button.sourceElement or '', 'source_type':button.source_type,'text':button.text()}
        if not button.icon().isNull():row['icon_png']=encode_icon(button.icon())
        result.append(row)
    return config_io.rows(result)
def replace_buttons(win,data):
    data=config_io.rows(data);ui=qt();buttons=[]
    try:
        for row in data:
            button=ui.ToolButton();buttons.append(button);apply_button(button,row)
    except Exception:
        for button in buttons:button.deleteLater()
        raise
    win.clear_toolbar()
    for button in buttons:win.toolbar_flow.addWidget(button)
    return len(buttons)
def execute_button(button,confirmed=False):
    if confirmed is not True:raise ValueError('Explicit command execution confirmation required')
    row=config_io.rows([{'command':button.command or '', 'source_type':button.source_type}])[0]
    if not row['command']:raise ValueError('Empty command')
    from maya_toolkit.core.context import UndoChunkContext
    from maya import cmds,mel
    with UndoChunkContext(chunk_name='Floating Toolbar Command'):
        if row['source_type']=='mel':return mel.eval(row['command'])
        import __main__
        scope=vars(__main__);scope.setdefault('cmds',cmds);scope.setdefault('mel',mel)
        exec(compile(row['command'],'<floating-toolbar-user-command>','exec'),scope,scope)
        return {'source_type':'python','executed':True}
def drop_record(mime):
    if mime.hasFormat('application/x-mtb-shelf-button'):
        blob=bytes(mime.data('application/x-mtb-shelf-button'))
        if len(blob)>2048:raise ValueError('Drop reference too large')
        data=json.loads(blob.decode('utf8'))
        if not isinstance(data,dict) or set(data)!={'shelf_button'}:raise ValueError('Only shelf-button references accepted')
        return shelf_record(data['shelf_button'])
    if mime.hasText():return shelf_record(mime.text())
    raise ValueError('Unsupported drag data; drop never executes code')
def edit_button(button):
    ui=qt();dialog=ui.QtWidgets.QDialog(button.parent());dialog.setWindowTitle('编辑按钮和语言');layout=ui.QtWidgets.QFormLayout(dialog)
    name=ui.QtWidgets.QLineEdit(button.sourceElement or '');code=ui.QtWidgets.QTextEdit(button.command or '');kind=ui.QtWidgets.QComboBox();kind.addItems(['python','mel']);kind.setCurrentText(button.source_type)
    layout.addRow('名称',name);layout.addRow('命令',code);layout.addRow('语言',kind);buttons=ui.QtWidgets.QDialogButtonBox(ui.QtWidgets.QDialogButtonBox.Save|ui.QtWidgets.QDialogButtonBox.Cancel);layout.addRow(buttons);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject)
    if dialog.exec()==ui.QtWidgets.QDialog.Accepted:apply_button(button,{'command':code.toPlainText(),'source_element':name.text(),'text':name.text(),'source_type':kind.currentText(),'icon_png':encode_icon(button.icon()) if not button.icon().isNull() else ''})
def show(parent=None):
    global window
    from maya import cmds
    if cmds.about(batch=True):raise RuntimeError('Real Maya GUI required')
    ui=qt();app=ui.QtWidgets.QApplication.instance()
    if app is None or ui.QtCore.QThread.currentThread()!=app.thread():raise RuntimeError('Existing Maya Qt main thread required')
    close();window=ui.FloatingToolbar(parent or ui.maya_main_window());window.setObjectName('MTB_FloatingToolbar');window.show();return window
def close():
    global window
    disable_drag()
    if window:
        try:owned=window;owned.close();owned.deleteLater()
        except RuntimeError:pass
    window=None
def make_filter(button,reference):
    ui=qt()
    class ShelfDragFilter(ui.QtCore.QObject):
        def eventFilter(self,obj,event):
            if event.type()==ui.QtCore.QEvent.MouseButtonPress and event.button()==ui.QtCore.Qt.MiddleButton and event.modifiers() & ui.QtCore.Qt.ShiftModifier:
                # Reference only. Left clicks/native shelf commands are untouched.
                drag=ui.QtGui.QDrag(button);mime=ui.QtCore.QMimeData();mime.setData('application/x-mtb-shelf-button',json.dumps({'shelf_button':reference}).encode('utf8'));drag.setMimeData(mime);drag.exec(ui.QtCore.Qt.CopyAction);return True
            return False
    return ShelfDragFilter(button)
def enable_drag():
    if filters:return {'installed':len(filters)}
    from maya import cmds,OpenMayaUI
    ui=qt()
    try:
        for shelf in cmds.layout('ShelfLayout',q=True,childArray=True) or []:
            for name in cmds.shelfLayout(shelf,q=True,childArray=True) or []:
                if not cmds.shelfButton(name,exists=True):continue
                ptr=OpenMayaUI.MQtUtil.findControl(name)
                if ptr:
                    button=ui.wrapInstance(int(ptr),ui.QtWidgets.QWidget);hook=make_filter(button,name);button.installEventFilter(hook);filters.append((button,hook))
    except Exception:disable_drag();raise
    return {'installed':len(filters),'gesture':'Shift + middle button','original_commands_changed':False}
def disable_drag():
    for button,hook in filters:
        try:button.removeEventFilter(hook);hook.deleteLater()
        except RuntimeError:pass
    filters.clear();return {'installed':0}
