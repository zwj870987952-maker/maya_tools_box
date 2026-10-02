from prepare_external_candidate import ROOT, put
import subprocess, sys
RC=ROOT/'tools_staging_pool/06_diagnostics_security/scene_virus_cleaner/release_candidate'
PKG=RC/'maya_toolkit/tools/scene_virus_cleaner'
put(PKG/'ascii_filter.py',r'''"""Byte-preserving MEL command lexer for generated .ma; never executes source."""
import re
PROTECTED={'sceneConfigurationScriptNode','uiConfigurationScriptNode'}
KNOWN=('vaccine_gene','breed_gene')

def commands(data):
    chunks=[]; start=0; i=0; quoted=False; escaped=False; comment=None
    while i<len(data):
        char=data[i]; nxt=data[i:i+2]
        if comment=='line':
            if char in (10,13):comment=None
        elif comment=='block':
            if nxt==b'*/':comment=None;i+=1
        elif quoted:
            if escaped:escaped=False
            elif char==92:escaped=True
            elif char==34:quoted=False
        elif nxt==b'//':comment='line';i+=1
        elif nxt==b'/*':comment='block';i+=1
        elif char==34:quoted=True
        elif char==59:
            chunks.append(data[start:i+1]);start=i+1
        i+=1
    if quoted or comment=='block':raise ValueError('Unterminated quoted string or block comment; refuse to rewrite')
    if data[start:].strip():
        tail=tokens(data[start:])
        if tail:raise ValueError('Non-comment command missing final semicolon')
    if start<len(data):chunks.append(data[start:])
    return chunks

def tokens(data):
    out=[]; i=0
    while i<len(data):
        if data[i] in b' \t\r\n;':i+=1;continue
        if data[i:i+2]==b'//':
            end=data.find(b'\n',i+2);i=len(data) if end<0 else end+1;continue
        if data[i:i+2]==b'/*':
            end=data.find(b'*/',i+2)
            if end<0:raise ValueError('Unterminated comment')
            i=end+2;continue
        if data[i]==34:
            i+=1;value=bytearray()
            while i<len(data):
                if data[i]==34:i+=1;break
                if data[i]==92 and i+1<len(data):
                    # Decode only identifier quote/backslash escapes. Script bodies remain data.
                    if data[i+1] in (34,92):value.append(data[i+1]);i+=2;continue
                value.append(data[i]);i+=1
            out.append(bytes(value).decode('utf-8',errors='surrogateescape'))
        else:
            start=i
            while i<len(data) and data[i] not in b' \t\r\n;':i+=1
            out.append(data[start:i].decode('utf-8',errors='surrogateescape'))
    return out

def clean_bytes(data, script_policy='known', script_names=None, remove_plugin_requires=False):
    if not data.lstrip().startswith(b'//Maya ASCII'):raise ValueError('Expected Maya ASCII header; binary/unknown formats refused')
    if script_policy not in ('known','all_scripts','none'):raise ValueError('Invalid script policy')
    names=set(KNOWN if script_names is None else script_names)
    chunks=commands(data); parsed=[tokens(c) for c in chunks]
    removed=set(); kept_scripts=[]; warnings=[]
    for t in parsed:
        if len(t)>=2 and t[:2]==['createNode','script']:
            if '-n' not in t:raise ValueError('Unnamed script node; ambiguous scope')
            name=t[t.index('-n')+1]
            if name in PROTECTED or script_policy=='none' or (script_policy=='known' and name not in names):kept_scripts.append(name)
            else:removed.add(name)
    def ref(name):return name.split('.',1)[0].lstrip(':') in removed
    result=[]; active=None; discarded=[]; plugin_rows=[]
    for chunk,t in zip(chunks,parsed):
        drop=False
        if not t:result.append(chunk);continue
        command=t[0]
        if command=='createNode':
            active=t[t.index('-n')+1] if '-n' in t else None
            drop=active in removed
        elif command=='select':
            selected=[v for v in t[1:] if not v.startswith('-')]
            active=selected[-1].lstrip(':') if len(selected)==1 else None
            if any(ref(v) for v in selected):
                if len(selected)>1:raise ValueError('Mixed select containing removed and kept nodes; refuse ambiguous edit')
                drop=True
        elif command in ('setAttr','addAttr','rename','lockNode') and active in removed:
            if command=='setAttr':
                attributes=[v for v in t[1:] if v.startswith('.') or ('.' in v and not v.startswith('-') and not any(c.isspace() for c in v))]
                target=attributes[0] if attributes else None
                if target is None:raise ValueError('Cannot determine removed-node setAttr target')
                drop=target.startswith('.') or ref(target)
            else:drop=True
        elif command in ('connectAttr','disconnectAttr'):
            drop=any(ref(v) for v in t[1:] if not v.startswith('-'))
        elif command=='requires' and remove_plugin_requires:
            if len(t)<3:raise ValueError('Malformed requires command')
            plugin=t[-2]
            if plugin!='maya':drop=True;plugin_rows.append({'plugin':plugin,'version':t[-1]})
        elif command=='setAttr':
            attributes=[v for v in t[1:] if v.startswith('.') or ('.' in v and not v.startswith('-') and not any(c.isspace() for c in v))]
            # Only the actual first attribute argument, never a string payload value.
            drop=bool(attributes and ref(attributes[0]))
        elif active in removed:
            # Do not discard arbitrary unrelated commands after a script block.
            active=None
        if drop:discarded.append(command)
        else:result.append(chunk)
    output=b''.join(result)
    commands(output)  # Final string/comment boundaries still valid; no MEL evaluation.
    return output,{'removed_script_nodes':sorted(removed),'retained_script_nodes':kept_scripts,
        'removed_requires':plugin_rows,'removed_command_count':len(discarded),'warnings':warnings,
        'security_claim':'Policy-driven structural filtering only; not signature-complete malware detection. Other expressions/jobs/plugins remain.'}
''')

put(PKG/'__init__.py',r'''"""Offline Maya ASCII filtering with exact original backup and entirely new outputs."""
from pathlib import Path
import hashlib
import json
import os
from maya_toolkit.framework import BaseMayaTool,ToolResult
from .ascii_filter import clean_bytes,KNOWN

def normalize(kwargs):
    allowed={'action','files','directories','output_dir','script_policy','script_names','remove_plugin_requires','confirm_broad_removal'}
    if set(kwargs)-allowed:raise ValueError('Unknown parameters')
    p=dict(action='scan',files=[],directories=[],output_dir=None,script_policy='known',script_names=list(KNOWN),remove_plugin_requires=False,confirm_broad_removal=False);p.update(kwargs)
    if p['action'] not in ('scan','clean') or p['script_policy'] not in ('known','all_scripts','none'):raise ValueError('Invalid action/script_policy')
    for key in ('remove_plugin_requires','confirm_broad_removal'):
        if not isinstance(p[key],bool):raise ValueError('Boolean required')
    for key in ('files','directories','script_names'):
        if not isinstance(p[key],list) or len(p[key])>10000 or any(not isinstance(v,str) or not v for v in p[key]):raise ValueError('String list required: '+key)
    if (p['script_policy']=='all_scripts' or p['remove_plugin_requires']) and not p['confirm_broad_removal']:
        raise ValueError('Broad removal can break legitimate scripts/plugins: confirm_broad_removal=True required')
    return p

def plan(p):
    paths=set(); roots=[]
    for value in p['files']:
        path=Path(value).resolve()
        if not path.is_file() or path.suffix.lower()!='.ma':raise ValueError('Existing .ma file required: '+value)
        paths.add(path)
    for value in p['directories']:
        root=Path(value).resolve()
        if not root.is_dir():raise ValueError('Input directory missing: '+value)
        roots.append(root)
        for directory,dirs,files in os.walk(root,followlinks=False):
            dirs[:]=sorted(n for n in dirs if n.casefold() not in ('history','release_candidate','__pycache__','.git') and not (Path(directory)/n).is_symlink())
            for name in files:
                if Path(name).suffix.lower()=='.ma':paths.add((Path(directory)/name).resolve())
            if len(paths)>10000:raise ValueError('More than 10000 input files')
    if not paths:raise ValueError('No .ma files found')
    out=None
    if p['action']=='clean':
        if not isinstance(p['output_dir'],str) or not p['output_dir']:raise ValueError('clean requires explicit new output_dir')
        out=Path(p['output_dir']).resolve()
        if out.exists() or not out.parent.is_dir():raise ValueError('output_dir must be new, with an existing parent')
        for root in roots:
            if out==root or root in out.parents:raise ValueError('Output must be outside recursively scanned input directories')
    rows=[]
    for path in sorted(paths):
        if path.stat().st_size>128*1024*1024:raise ValueError('Source exceeds bounded 128 MB lexer input: '+str(path))
        data=path.read_bytes(); cleaned,changes=clean_bytes(data,p['script_policy'],p['script_names'],p['remove_plugin_requires'])
        key=hashlib.sha256(str(path).encode()).hexdigest()[:12];filename=path.stem+'_'+key+'.ma'
        rows.append({'source':str(path),'source_sha256':hashlib.sha256(data).hexdigest(),'output_sha256':hashlib.sha256(cleaned).hexdigest(),
            'size':len(data),'output_size':len(cleaned),'changes':changes,
            'output':str(out/filename) if out else None,'backup':str(out/'history'/filename) if out else None})
    return {'rows':rows,'count':len(rows),'output_dir':str(out) if out else None,'options':p,
        'impact':'New filtered .ma and byte-exact original backups + report only. Original files/current scene untouched. External writes cannot Maya Undo. Does not guarantee virus-free.'}

def clean_files(p,progress=None,cancel=None):
    report=plan(p);root=Path(report['output_dir']);root.mkdir();(root/'history').mkdir()
    result=dict(report,completed=[],failures=[],cancelled=False)
    for index,row in enumerate(report['rows']):
        if cancel and cancel():result['cancelled']=True;break
        backup,output=Path(row['backup']),Path(row['output']);owned_output=False;owned_backup=False;backup_complete=False
        try:
            data=Path(row['source']).read_bytes()
            if hashlib.sha256(data).hexdigest()!=row['source_sha256']:raise ValueError('Source changed after preflight')
            filtered,changes=clean_bytes(data,p['script_policy'],p['script_names'],p['remove_plugin_requires'])
            if hashlib.sha256(filtered).hexdigest()!=row['output_sha256']:raise ValueError('Filter changed after preflight')
            with backup.open('xb') as stream:owned_backup=True;stream.write(data)
            backup_complete=hashlib.sha256(backup.read_bytes()).hexdigest()==row['source_sha256']
            if not backup_complete:raise ValueError('Backup SHA mismatch')
            with output.open('xb') as stream:owned_output=True;stream.write(filtered)
            result['completed'].append(row)
        except Exception as error:
            if owned_output:output.unlink(missing_ok=True)
            if owned_backup and not backup_complete:backup.unlink(missing_ok=True)
            result['failures'].append({'source':row['source'],'error':str(error),'backup_retained':backup_complete})
            break
        if progress:progress(index+1,len(report['rows']))
    try:
        with (root/'report.json').open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=True,indent=2)
    except Exception as error:result['failures'].append({'source':'report.json','error':str(error),'backup_retained':False})
    return result

class SceneVirusCleanerTool(BaseMayaTool):
    tool_id='scene_virus_cleaner';tool_name='Maya ASCII 脚本与声明清理';category='scene_hygiene'
    description='离线字节保留.ma策略过滤与新文件/原备份；不是完整杀毒，不执行待检查脚本'
    parameters_schema={'type':'object','additionalProperties':False,'properties':{
        'action':{'type':'string','enum':['scan','clean'],'default':'scan'},'files':{'type':'array','items':{'type':'string'},'maxItems':10000},
        'directories':{'type':'array','items':{'type':'string'},'maxItems':10000},'output_dir':{'type':'string'},
        'script_policy':{'type':'string','enum':['known','all_scripts','none'],'default':'known'},
        'script_names':{'type':'array','items':{'type':'string'},'default':list(KNOWN)},
        'remove_plugin_requires':{'type':'boolean','default':False},'confirm_broad_removal':{'type':'boolean','default':False}}}
    def validate(self,**kwargs):
        try:return ToolResult.ok(message='离线文件/清理策略预检通过，未执行MEL/未写文件',data=plan(normalize(kwargs)),dry_run=True)
        except Exception as e:return ToolResult.fail(message=str(e),errors=[str(e)],dry_run=True)
    def execute(self,**kwargs):
        p=normalize(kwargs);data=clean_files(p) if p['action']=='clean' else plan(p)
        if data.get('failures'):return ToolResult.fail(message='部分文件处理失败，原文件未改，查看新输出报告',data=data,errors=[r['error'] for r in data['failures']])
        return ToolResult.ok(message='策略过滤完成，不宣称病毒已全部清除',data=data)
    def show_ui(self):
        from .ui import show_ui
        return show_ui()
''')
put(PKG/'ui.py',r'''"""Complete folder drag/drop/list/clear/progress/cancel workflow with new output policy."""
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
''')
put(RC/'tests/test_scene_virus_cleaner.py',r'''from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest
rc=Path(__file__).resolve().parents[1]
if (rc/'launch_candidate.py').is_file():
    spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
else:
    sys.path.insert(0,str(rc));from maya_toolkit.tools.scene_virus_cleaner import SceneVirusCleanerTool;tool=SceneVirusCleanerTool()
from maya_toolkit.tools.scene_virus_cleaner import ascii_filter as a,normalize,clean_files
DATA=b'//Maya ASCII 2025 scene\r\nrequires maya "2025";\r\nrequires "legalPlugin" "1.0";\r\ncurrentUnit -l centimeter;\r\ncreateNode transform -n "cube";\r\nsetAttr ".tx" 4;\r\ncreateNode script -n "vaccine_gene";\r\nsetAttr ".b" -type "string" "python(\\"a; //payload\\");\\nfoo";\r\ncreateNode script -n "myLegitScript";\r\nsetAttr ".b" -type "string" "keep; // quoted";\r\ncreateNode script -n "sceneConfigurationScriptNode";\r\nsetAttr ".st" 6;\r\nconnectAttr "vaccine_gene.message" "cube.message";\r\n// tail \xff\r\n'
class Tests(unittest.TestCase):
    def test_quoted_multiline_payload_and_legacy_bytes_preserved(self):
        out,report=a.clean_bytes(DATA)
        self.assertNotIn(b'vaccine_gene',out);self.assertNotIn(b'//payload',out)
        self.assertIn(b'legalPlugin',out);self.assertIn(b'myLegitScript',out);self.assertIn(b'keep; // quoted',out);self.assertIn(b'// tail \xff\r\n',out)
        self.assertEqual(report['removed_script_nodes'],['vaccine_gene'])
        extra=b'createNode network -n "validData";setAttr ".notes" -type "string" "vaccine_gene.message";'
        kept,_=a.clean_bytes(DATA+extra);self.assertIn(extra,kept)
        broad,report=a.clean_bytes(DATA,'all_scripts',remove_plugin_requires=True)
        self.assertNotIn(b'myLegitScript',broad);self.assertNotIn(b'legalPlugin',broad);self.assertIn(b'sceneConfigurationScriptNode',broad)
        with self.assertRaises(ValueError):a.clean_bytes(DATA+b'setAttr ".b" "unterminated')
    def test_fresh_output_exact_backup_and_invalid_last_preflight(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source.ma';source.write_bytes(DATA);out=root/'new'
            kwargs=dict(action='clean',files=[str(source)],output_dir=str(out))
            self.assertTrue(tool.validate(**kwargs).success);self.assertFalse(out.exists())
            result=clean_files(normalize(kwargs));row=result['completed'][0]
            self.assertEqual(Path(row['backup']).read_bytes(),DATA);self.assertEqual(source.read_bytes(),DATA);self.assertNotIn(b'vaccine_gene',Path(row['output']).read_bytes())
            self.assertFalse(tool.validate(**kwargs).success)
            bad=root/'bad.ma';bad.write_bytes(DATA+b'incompleteCommand');another=root/'another'
            self.assertFalse(tool.validate(action='clean',files=[str(source),str(bad)],output_dir=str(another)).success);self.assertFalse(another.exists())
    def test_cancel_partial_report_and_broad_guard(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);first=root/'a.ma';second=root/'b.ma';first.write_bytes(DATA);second.write_bytes(DATA);calls=[]
            p=normalize(dict(action='clean',files=[str(first),str(second)],output_dir=str(root/'output')))
            result=clean_files(p,progress=lambda *a:calls.append(a),cancel=lambda:bool(calls))
            self.assertTrue(result['cancelled']);self.assertEqual(len(result['completed']),1);self.assertTrue((root/'output/report.json').is_file());self.assertEqual(second.read_bytes(),DATA)
        with self.assertRaises(ValueError):normalize({'script_policy':'all_scripts'})
if __name__=='__main__':unittest.main()
''')
put(RC/'tests/test_scene_virus_cleaner_maya.py',r'''from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
rc=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('launch',rc/'launch_candidate.py');launch=importlib.util.module_from_spec(spec);spec.loader.exec_module(launch);tool=launch.load_tool()
class Tests(unittest.TestCase):
    def test_actual_saved_ma_filtered_and_reopened_without_scene_mutation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);cmds.file(new=True,force=True);cube=cmds.polyCube(name='ReviewCube')[0];cmds.setAttr(cube+'.tx',7)
            cmds.scriptNode(name='vaccine_gene',beforeScript='print("fixture; not run")',scriptType=0,sourceType='python')
            cmds.scriptNode(name='legalScript',beforeScript='print("preserve; text")',scriptType=0,sourceType='python')
            source=root/'source.ma';cmds.file(rename=str(source));cmds.file(save=True,type='mayaAscii',force=True);original=source.read_bytes()
            cmds.setAttr(cube+'.ty',9);cmds.select(cube);before=(cmds.ls(),cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True),cmds.getAttr(cube+'.ty'))
            result=tool.run(action='clean',files=[str(source)],output_dir=str(root/'new'));self.assertTrue(result.success,result)
            self.assertEqual((cmds.ls(),cmds.file(q=True,modified=True),cmds.undoInfo(q=True,undoName=True),cmds.getAttr(cube+'.ty')),before);self.assertEqual(source.read_bytes(),original)
            row=result.data['completed'][0];self.assertEqual(Path(row['backup']).read_bytes(),original)
            cmds.file(row['output'],open=True,force=True,executeScriptNodes=False)
            self.assertTrue(cmds.objExists(cube));self.assertEqual(cmds.getAttr(cube+'.tx'),7);self.assertFalse(cmds.objExists('vaccine_gene'));self.assertTrue(cmds.objExists('legalScript'))
if __name__=='__main__':unittest.main()
''')
put(RC/'docs/tools/scene_virus_cleaner.md','''# Maya ASCII 脚本/声明过滤候选

原批量目录递归、拖放多目录列表/清除/反馈/进度/取消、备份/过滤.ma功能全部保留。原文件SHA归档。原直接覆盖输入/errors=ignore/固定_backup覆盖改为完全新output_dir内过滤MA、history字节原副本与report.json，不改源或当前Maya场景，无自动import/UI。不能把结构过滤称为完整杀毒；自定义表达式/scriptJob/插件代码/恶意MEL外部命令/其它节点可能仍存在。

Base/Schema/ToolResult/scene_hygiene；scan默认纯文件读取，不执行任何源MEL/脚本，不在Maya打开源。files/directories（递归排history/release_candidate/.git与symlink目录）最多10000；MA header和128MB每file界限；output_dir clean必须显式不存在且父目录存在，不得在递归输入根内，全部预检后mkdir独占。原路径哈希后缀防跨目录同名输出碰撞；SHA/size/changes/目标/备份一览。取消或中途失败保留已生成files/backup/report，不称整批事务，文件不Undo。源在写前SHA复核，失败不覆已有，自己的partial output删除、原备份保留。

默认known只按准确script_names=[vaccine_gene,breed_gene]删除节点，名字匹配只是用户约定而非病毒证明。script_policy none不删，all_scripts+confirm_broad_removal=True保留原广泛过滤能力，会删除合法其他脚本；sceneConfigurationScriptNode/uiConfigurationScriptNode两默认保留（原仅scene保留，额外ui保留明确改变）。remove_plugin_requires=False保全部插件，True+confirm_broad_removal仅移除非maya requires单条；仍有该插件节点会无法正确加载，禁止当成通用加速操作。与原行为相比默认范围缩小，广泛模式明确可选。

自有bytes MEL命令lexer识别双引号/escape/行注释/block注释/分号，脚本内容嵌分号/createNode不冒充外部命令；不decode/reencode整文件，保UTF8/ANSI未知字节/换行。移除节点create与setAttr/addAttr/rename/lockBlock，后续显式select与指向该节点的connect/disconnect/setAttr一并处理，避免留下裸引用。混select/语法引号或block不闭/非comment尾缺分号/不明确attribute拒绝改写。限定Maya生成ASCII常规命令；手工复杂MEL/未知全名/间接script依赖仍须Maya读回审查，不宣称完整MEL语义解析。

```python
from maya_toolkit.tools.scene_virus_cleaner import SceneVirusCleanerTool
t=SceneVirusCleanerTool()
t.run(dry_run=True,action='clean',directories=[r'D:/ReviewScenes'],output_dir=r'D:/CleanCandidate')
t.run(action='clean',directories=[r'D:/ReviewScenes'],output_dir=r'D:/CleanCandidate')
```

UI保完整路径drag/list/clear与进度取消，补output/policy/requires/preview、broad确认，处理时拒绝close或重复start。Qt5/6与真实Maya parent，未创建额外QApplication。取消仅文件间，不打断单file lexer/IO；结果显示真实已完成/失败/取消，不像原返回失败仍“全部完毕”。共用框架协议，纯字节解析/文件IO不适合正式core下沉；所有代码自包含、知识/tests/晋级注册预制。

3离线真实bytes/backup/cancel/坏后file预检+1隔离Maya2025真实保存/过滤/ScriptNodes=False读回模型属性与合法script仍存，临时布局/注册/panel通过仅离线证据；真实GUI/复杂生产MA/插件/node-data semantics/跨版本not_run。原场景健康清理/未知节点工具不是这个磁盘范围；输出仍需用户复核和真实Maya验收，不覆盖原scene。
''')
put(RC/'acceptance.md','''# Maya文件过滤直验 not_run

仅备份的临时.ma；绝不执行原清理入口，不打开不可信脚本允许执行。新output在输入目录外。真实UI多目录拖拽/去重/clear/preview策略/defaultknown/broad告警/Progress cancel/失败统计正常；dry不建目录，不改源。用known名节点、合法脚本、插件requires、中文/ANSI/CRLF、带引号/分号/注释/多行脚本字符串、create/select/连接验证目标删除范围和byte-exact history。existing output/坏最后文件/引号未闭/混select/超限与非ma拒绝且源不改。过滤结果在隔离备份Maya中executeScriptNodes=False打开、模型/动画/引用/材质保持、合法script与requires保持，broad删除合法功能必须人工接受；未知命令/真实生产节点需专项复核。Maya读回不报丢节点/无效连接，不能宣称病毒已清完；外部备份/output/report不受Undo。GUI/跨版本未验收，通过后记录当前SHA/版本/操作者/日期再晋级。
''')
subprocess.run([sys.executable,str(ROOT/'plans/staging_run/prepare_small_candidate.py'),'--tool','06_diagnostics_security/scene_virus_cleaner','--class-name','SceneVirusCleanerTool','--summary','Complete folder batch Maya ASCII policy cleaner with byte-preserving lexer, new exclusive cleaned files, exact source backups, GUI progress/cancel and no malware-free guarantee','--limitations','Real GUI, complex production MA/plugin semantics and cross-version Maya acceptance not_run'],check=True)
