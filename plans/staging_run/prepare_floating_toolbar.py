"""Complete floating shelf, language-preserving scripts, portable icons and owned drag."""
import ast,json,subprocess,sys
from prepare_external_candidate import ROOT,put
UNIT=ROOT/'tools_staging_pool/08_utilities_system/floating_toolbar';RC=UNIT/'release_candidate';PKG=RC/'maya_toolkit/tools/floating_toolbar'
put(PKG/'config_io.py',r'''from pathlib import Path
import ast,base64,json
def path(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value):raise ValueError('Invalid path')
    p=Path(value)
    if not p.is_absolute() or any(q.is_symlink() for q in (p,*p.parents)):raise ValueError('Absolute non-symlink path required')
    return p
def rows(value):
    if not isinstance(value,list) or len(value)>256:raise ValueError('At most 256 button records')
    result=[]
    for row in value:
        if not isinstance(row,dict) or set(row)-{'command','source_element','text','source_type','icon','icon_png'}:raise ValueError('Unknown button fields')
        item={'command':row.get('command') or '', 'source_element':row.get('source_element') or '', 'text':row.get('text') or '', 'source_type':row.get('source_type') or ('mel' if (row.get('command') or '').rstrip().endswith(';') else 'python')}
        for k in ('command','source_element','text'):
            if not isinstance(item[k],str) or len(item[k])>(65536 if k=='command' else 1024):raise ValueError('Invalid button '+k)
        if item['source_type'] not in ('mel','python'):raise ValueError('Explicit mel/python source_type required')
        if item['source_type']=='python' and item['command']:
            try:ast.parse(item['command'])
            except SyntaxError as e:raise ValueError('Invalid Python syntax: '+str(e)) from e
        if row.get('icon_png'):
            if not isinstance(row['icon_png'],str) or len(row['icon_png'])>512*1024:raise ValueError('Icon limit')
            blob=base64.b64decode(row['icon_png'],validate=True)
            if not blob.startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('PNG icon required')
            item['icon_png']=row['icon_png']
        elif row.get('icon'):
            p=path(row['icon']);item['icon']=str(p)
        result.append(item)
    return result
def read(value):
    p=path(value)
    if not p.is_file() or p.stat().st_size>16*1024*1024:raise ValueError('Config missing or exceeds 16MiB')
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('Duplicate config key')
            result[k]=v
        return result
    return rows(json.loads(p.read_text(encoding='utf-8-sig'),object_pairs_hook=pairs))
def new_path(value):
    p=path(value)
    if p.suffix.lower()!='.json' or p.exists() or not p.parent.is_dir():raise ValueError('New JSON file and existing parent required')
    return p
def write(value,data):
    p=new_path(value);data=rows(data)
    with p.open('x',encoding='utf8') as f:json.dump(data,f,ensure_ascii=False,allow_nan=False,indent=2)
    return str(p)
''')
# Retain full primary original widget/FlowLayout, replace known broken handlers.
s=(UNIT/'floating_toolbar.py').read_text(encoding='utf8')
s=s.replace('from PySide2 import QtWidgets, QtCore, QtGui\nfrom shiboken2 import wrapInstance','try:\n    from PySide6 import QtWidgets,QtCore,QtGui\n    from shiboken6 import wrapInstance\nexcept ImportError:\n    from PySide2 import QtWidgets,QtCore,QtGui\n    from shiboken2 import wrapInstance')
s=s.replace('def __init__(self, parent=maya_main_window()):','def __init__(self, parent=None):').replace('menu.exec_(','menu.exec(').replace('dialog.exec_()','dialog.exec()')
tree=ast.parse(s);edits=[]
replacements={
('ToolButton','process_maya_shelf_button'):'''def process_maya_shelf_button(self, button_name):
    from .session import shelf_record,apply_button
    apply_button(self,shelf_record(button_name))''',
('ToolButton','mousePressEvent'):'''def mousePressEvent(self,event):
    if event.button()==QtCore.Qt.LeftButton and self.command:
        from .session import execute_button
        try:execute_button(self,True)
        except Exception as e:QtWidgets.QMessageBox.warning(self,'执行失败',str(e))
    super(ToolButton,self).mousePressEvent(event)''',
('ToolButton','dragEnterEvent'):'''def dragEnterEvent(self,event):
    from .session import drop_record
    try:drop_record(event.mimeData());event.acceptProposedAction()
    except Exception:event.ignore()''',
('ToolButton','dropEvent'):'''def dropEvent(self,event):
    from .session import drop_record,apply_button
    try:apply_button(self,drop_record(event.mimeData()));event.acceptProposedAction()
    except Exception:event.ignore()''',
('ToolButton','edit_button'):'''def edit_button(self):
    from .session import edit_button
    return edit_button(self)''',
('FloatingToolbar','clear_toolbar'):'''def clear_toolbar(self):
    while self.toolbar_flow.count():
        item=self.toolbar_flow.takeAt(0)
        widget=item.widget()
        if widget:widget.setParent(None);widget.deleteLater()''',
('FloatingToolbar','save_config'):'''def save_config(self):
    from .session import snapshot
    from .config_io import write
    value,_=QtWidgets.QFileDialog.getSaveFileName(self,'保存到新的JSON文件','','JSON (*.json)')
    if not value:return
    try:write(value,snapshot(self))
    except Exception as e:QtWidgets.QMessageBox.warning(self,'保存失败',str(e))''',
('FloatingToolbar','load_config'):'''def load_config(self):
    from .session import replace_buttons
    from .config_io import read
    value,_=QtWidgets.QFileDialog.getOpenFileName(self,'加载完整工具栏配置','','JSON (*.json)')
    if not value:return
    try:replace_buttons(self,read(value))
    except Exception as e:QtWidgets.QMessageBox.warning(self,'加载失败',str(e))'''}
for cls in tree.body:
    if isinstance(cls,ast.ClassDef):
        for fn in cls.body:
            if isinstance(fn,ast.FunctionDef) and (cls.name,fn.name) in replacements:
                text=replacements[(cls.name,fn.name)];edits.append((fn.lineno-1,fn.end_lineno,'\n'.join('    '+line for line in text.splitlines())))
for fn in tree.body:
    if isinstance(fn,ast.FunctionDef) and fn.name in ('install_tool_draggers','show_floating_toolbar'):
        name='enable_drag' if fn.name=='install_tool_draggers' else 'show'
        edits.append((fn.lineno-1,fn.end_lineno,f'def {fn.name}():\n    from .session import {name}\n    return {name}()'))
lines=s.splitlines()
for start,end,value in sorted(edits,reverse=True):lines[start:end]=value.splitlines()
s='\n'.join(lines)+'\n';s=s.replace('        self.sourceElement = None','        self.sourceElement = None\n        self.source_type = "python"',1)
s=s.replace('    def mouseMoveEvent(self, event):','    def closeEvent(self,event):\n        from . import session\n        if session.window is self:session.disable_drag();session.window=None\n        super(FloatingToolbar,self).closeEvent(event)\n\n    def mouseMoveEvent(self, event):',1)
put(PKG/'ui.py',s)
put(PKG/'session.py',r'''from pathlib import Path
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
''')
put(PKG/'__init__.py',r'''from maya_toolkit.framework import BaseMayaTool,ToolResult
from . import config_io
class FloatingToolbarTool(BaseMayaTool):
    tool_id='floating_toolbar';tool_name='浮动工具栏';category='pipeline_io';version='1.0.0'
    description='Full editable draggable floating Maya shelf with explicit Python/MEL language, flow layout and portable icon JSON'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{'action':{'type':'string','enum':['inspect','show_ui','close_ui','enable_drag','disable_drag','load_config','save_config','set_buttons','get_buttons','execute_button','clear'],'default':'inspect'},'path':{'type':'string'},'buttons':{'type':'array','maxItems':256,'items':{'type':'object'}},'index':{'type':'integer','minimum':0,'maximum':255},'confirm_execute':{'type':'boolean','default':False}}}
    def validate(self,action='inspect',**kw):
        try:
            if action not in self.parameters_schema['properties']['action']['enum'] or set(kw)-set(self.parameters_schema['properties']):raise ValueError('Unknown action/arguments')
            if action=='load_config':config_io.read(kw.get('path'))
            if action=='save_config':config_io.new_path(kw.get('path'))
            if action=='set_buttons':config_io.rows(kw.get('buttons'))
            if action=='execute_button':
                if type(kw.get('index')) is not int or not 0<=kw['index']<256 or kw.get('confirm_execute') is not True:raise ValueError('Explicit index and confirm_execute=True required')
            return ToolResult.ok(message='无副作用预检；未执行按钮命令/启动窗口/修改原shelf')
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)])
    def execute(self,action='inspect',**kw):
        if action=='inspect':return ToolResult.ok(data={'features':['flow_layout','add_edit_delete','shelf_drag','save_load','portable_png','explicit_python_mel'],'gui_acceptance':'not_run'})
        from . import session
        if action=='show_ui':session.show();return ToolResult.ok()
        if action=='close_ui':session.close();return ToolResult.ok()
        if action in ('enable_drag','disable_drag'):return ToolResult.ok(data=getattr(session,action)())
        if session.window is None:raise RuntimeError('Open this floating toolbar first')
        if action=='load_config':return ToolResult.ok(data={'count':session.replace_buttons(session.window,config_io.read(kw['path']))})
        if action=='save_config':return ToolResult.ok(data={'path':config_io.write(kw['path'],session.snapshot()),'undo':'External config is not Maya Undo'})
        if action=='set_buttons':return ToolResult.ok(data={'count':session.replace_buttons(session.window,kw['buttons'])})
        if action=='get_buttons':return ToolResult.ok(data={'buttons':session.snapshot()})
        if action=='clear':session.window.clear_toolbar();return ToolResult.ok()
        if kw['index']>=session.window.toolbar_flow.count():raise ValueError('Button index out of range')
        value=session.execute_button(session.window.toolbar_flow.itemAt(kw['index']).widget(),True);return ToolResult.ok(data={'result':value})
    def show_ui(self,parent=None):
        from .session import show
        return show(parent)
''')
put(RC/'tests/test_floating_toolbar.py',r'''import importlib.util,sys,tempfile,unittest
from pathlib import Path
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').exists():
    spec=importlib.util.spec_from_file_location('launch_ft',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    from maya_toolkit.tools.floating_toolbar import FloatingToolbarTool
    tool=FloatingToolbarTool()
from maya_toolkit.tools.floating_toolbar import config_io
class Checks(unittest.TestCase):
    def test_preflight_full_python_and_config_no_overwrite(self):
        self.assertTrue(tool.validate().success);self.assertNotIn('maya_toolkit.tools.floating_toolbar.ui',sys.modules)
        data=[{'command':'x=1\nx+=2','source_type':'python','text':'Code'}]
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'new.json');config_io.write(p,data);self.assertEqual(config_io.read(p)[0]['command'],'x=1\nx+=2')
            with self.assertRaises(ValueError):config_io.write(p,data)
        self.assertFalse(tool.validate(action='execute_button',index=0).success)
        self.assertFalse(tool.validate(action='set_buttons',buttons=[{'command':'if','source_type':'python'}]).success)
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_floating_toolbar_qt.py',r'''import importlib.util,os,tempfile,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable Qt process; do not initialize Maya')
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_ft',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from PySide6 import QtCore,QtGui,QtWidgets
app=QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
from maya_toolkit.tools.floating_toolbar import session,ui,config_io
class QtChecks(unittest.TestCase):
    def test_full_flow_buttons_png_config_and_clear(self):
        win=ui.FloatingToolbar();self.assertEqual(win.toolbar_flow.count(),10);data=[{'command':'x=1\nx+=2','source_type':'python','text':'Code'}];session.replace_buttons(win,data);self.assertEqual(win.toolbar_flow.count(),1)
        button=win.toolbar_flow.itemAt(0).widget();pix=QtGui.QPixmap(32,32);pix.fill(QtGui.QColor('red'));button.setIcon(QtGui.QIcon(pix));records=session.snapshot(win);self.assertTrue(records[0]['icon_png'])
        with tempfile.TemporaryDirectory() as td:
            p=str(Path(td)/'new.json');config_io.write(p,records);session.replace_buttons(win,config_io.read(p));self.assertFalse(win.toolbar_flow.itemAt(0).widget().icon().isNull())
        before=win.toolbar_flow.count()
        with self.assertRaises(ValueError):session.replace_buttons(win,[{'command':'if','source_type':'python'}])
        self.assertEqual(win.toolbar_flow.count(),before);win.clear_toolbar();self.assertEqual(win.toolbar_flow.count(),0);win.deleteLater()
    def test_left_click_filter_does_not_consume(self):
        button=QtWidgets.QToolButton();hook=session.make_filter(button,'reference');event=QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress,QtCore.QPointF(1,1),QtCore.Qt.LeftButton,QtCore.Qt.LeftButton,QtCore.Qt.NoModifier);self.assertFalse(hook.eventFilter(button,event));hook.deleteLater();button.deleteLater()
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_floating_toolbar_maya.py',r'''import importlib.util,os,unittest
from pathlib import Path
if os.environ.get('STAGING_ISOLATED_MAYAPY')!='1':raise RuntimeError('Disposable mayapy only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch_ft',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
from maya_toolkit.tools.floating_toolbar import session
class Checks(unittest.TestCase):
    def test_python_statements_mel_language_and_explicit_execution(self):
        cmds.file(new=True,force=True);node=cmds.createNode('transform',name='control');cmds.setAttr(node+'.tx',7)
        class Button:command="import maya.cmds as cmds\nvalue=9\ncmds.setAttr('control.tx',value)";source_type='python'
        with self.assertRaises(ValueError):session.execute_button(Button())
        self.assertEqual(cmds.getAttr(node+'.tx'),7);cmds.flushUndo();session.execute_button(Button(),True);self.assertEqual(cmds.getAttr(node+'.tx'),9);cmds.undo();self.assertEqual(cmds.getAttr(node+'.tx'),7)
        button=Button();button.source_type='mel';button.command='setAttr control.tx 13';cmds.flushUndo();session.execute_button(button,True);self.assertEqual(cmds.getAttr(node+'.tx'),13);cmds.undo();self.assertEqual(cmds.getAttr(node+'.tx'),7)
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/floating_toolbar.md','''# 浮动工具栏完整候选

2原版本SHA归档，完整ToolButton/FlowLayout/可拖无边框窗口/增删编辑/clear/save/load保留，统一superset行为。原PySide2单版本/构造参数eager Maya主窗/清空只deleteLater未移layout/重复安装mousePress monkey/右键拖回调仅print/闭包button复用/用末尾分号猜语言及Python eval语句失败等确定问题已改：Qt6/5、parent晚绑定、takeAt清布局、全配置验证及图标解码成功后再替换按钮，明确source_type。

Base/Schema/ToolResult默认inspect/dry不导入Qt、开窗、改shelf或运行用户command。完整UI与actions：show/close、enable/disable_drag、set/get_buttons/load/save/clear/execute_button。按钮左键属于明确运行用户脚本，API须confirm_execute=True；Python compile exec完整多行与语句，在Maya __main__按shelf语义执行，MEL用真实mel.eval，不靠分号猜。命令可以产生场景/文件/UI任意原脚本影响，scene UndoChunk分组不能撤文件或全局UI；候选不声称任意用户脚本可由预检证明安全。JSON命令和drop仅载入数据，直到明确点击不执行；Python只AST语法检，MEL真实runtime再验。

原shelf拖入查询真实sourceType/command/label/icon，不改原command/sourceType/dragCallback/mousePress；显式安装每shelf QWidget自有eventFilter，Shift+中键发MIME仅shelfButton引用，左键等native事件不拦，drop再查询现存按钮；close移自有filter，不重复叠加/碰外来hook。用户从Maya原拖入text/plain也只接受现存shelfButton名字；拒绝旧未经核验raw命令MIME。图标解析文件或Maya Qt资源，PNG32x32内嵌base64到JSON，不再生成/覆盖icon_0.png，跨目录配置保持图标。

配置最大16MiB/256按钮/64KiB命令/严格fields和language，重复key/非法Python/坏PNG/非绝对symlink配置拒绝；新已有parent的JSONexclusive保存，不覆盖原文件/不mkdir。旧配置可读取icon绝对路径和原末尾分号判断的语言默认，编辑器可改成正确Python/MEL，保存后显式语言+内嵌PNG；旧外部icon不存在就保留文字fallback。导入/编辑不得先清空再发现坏末项。外部config保存不能Maya Undo。

离线完整Python语句AST/new配置不覆盖、完整未来registry/domain/panel检查；独立Qt无Maya初始化实测全FlowLayout/10空按钮/事务替换/PNG保存回读/坏配置保持原按钮/clear立即归零/左键filter不吞。真实Maya shelf拖入、Shift中键QDrag、Python/MEL按钮运行、Qt资源图标/窗体交互/跨版本not_run；用户确认真实通过后才晋级。
''')
put(RC/'acceptance.md','''# 浮动工具栏真实Maya验收 not_run

1. 原完整无边框可拖窗口、FlowLayout换行、10空按钮、编辑名称/完整多行Python/MEL语言、删除/clear。show不自动改shelf，enable/disable重复安装自有filter，Shift中键拖入与原Maya原生拖入现存名字；原left click/command/sourceType/dragCallback/mousePress无变化。close撤filter，不触其他工具。
2. 拖入Python import语句、多行与末尾分号、MEL无末尾分号均尊重源language；drop/load不执行，明确按钮或API confirm_execute才run，scene一次Undo但文件/UI影响另记。任意外部用户脚本先自己审阅，不在整理过程中运行真实shelf命令。
3. 图标Maya Qt资源/自选PNG保存内嵌JSON跨目录读取；不生成覆盖icon_i文件。坏最后按钮/坏PNG/非法Python不清原配置，新JSON已有文件拒绝覆盖，既有raw配置读兼容语言需显式检查。
4. 当前仅离线/Qt，真实MayaGUI/shelf/drag与实际command/cross-version实测逐项记；candidate_sha256/accepted_by/maya_version/date/passed=true后再promotion。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','08_utilities_system/floating_toolbar','--class-name','FloatingToolbarTool','--summary','Complete floating toolbar with explicit script languages, portable icon JSON, transactional load and reversible shelf drag filters','--dependencies','Maya cmds/MEL/Qt shelf widgets','PySide6/PySide2','--limitations','Real Maya GUI/native shelf drag/Python-MEL execution/cross-version acceptance not_run'],check=True)
