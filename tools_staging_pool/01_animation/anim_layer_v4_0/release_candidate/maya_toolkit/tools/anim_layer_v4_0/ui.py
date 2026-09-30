"""Suite gateway: explicit edition load, typed API actions and original help asset."""
import json
import maya.cmds as cmds
from .contracts import CATALOG, PACKAGE


class SuiteUI:
    WINDOW = 'MayaToolkitAnimLayerV4Gateway'

    def __init__(self, tool):
        self.tool = tool

    def show(self):
        if cmds.window(self.WINDOW, exists=True):
            cmds.deleteUI(self.WINDOW)
        cmds.window(self.WINDOW, title='Anim Layer v4.0 套件入口', widthHeight=(720, 700), sizeable=True)
        cmds.scrollLayout(childResizable=True)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=6)
        cmds.text(label='保留原第三方套件；加载会改变 Maya 进程 MEL/UI，不能由场景 Undo 撤回。', align='left')
        self.edition = cmds.optionMenu(label='版本', changeCommand=self.refresh)
        cmds.menuItem(label='no_ui')
        cmds.menuItem(label='full')
        self.procedure = cmds.optionMenu(label='global 过程', changeCommand=self.show_signature)
        self.signature = cmds.scrollField(editable=False, height=80)
        self.arguments = cmds.scrollField(text='{}', height=90)
        cmds.button(label='查看过程签名与资源（不加载）', command=lambda *_: self.dispatch('inventory', True))
        cmds.button(label='预检此调用（不加载、不执行）', command=lambda *_: self.dispatch('invoke', True))
        cmds.button(label='加载所选版本并调用此过程', command=lambda *_: self.dispatch('invoke', False))
        cmds.button(label='打开原始工具菜单（完整版同时重建层编辑器）', command=lambda *_: self.dispatch('open_ui', False))
        cmds.button(label='只加载所选原始版本', command=lambda *_: self.dispatch('load', False))
        cmds.button(label='显示原帮助图', command=self.help)
        self.status = cmds.scrollField(editable=False, height=170)
        self.refresh()
        cmds.showWindow(self.WINDOW)
        return self

    def refresh(self, *_):
        items = cmds.optionMenu(self.procedure, query=True, itemListLong=True) or []
        for item in items:
            cmds.deleteUI(item)
        edition = cmds.optionMenu(self.edition, query=True, value=True)
        for name in sorted(CATALOG['editions'][edition]['procedures']):
            cmds.menuItem(label=name, parent=self.procedure)
        self.show_signature()

    def show_signature(self, *_):
        edition = cmds.optionMenu(self.edition, query=True, value=True)
        name = cmds.optionMenu(self.procedure, query=True, value=True)
        info = CATALOG['editions'][edition]['procedures'][name]
        cmds.scrollField(self.signature, edit=True, text=json.dumps(info, ensure_ascii=False, indent=2))
        # Keep user arguments; signatures guide edits rather than silently rewriting input.

    def dispatch(self, action, dry_run):
        try:
            edition = cmds.optionMenu(self.edition, query=True, value=True)
            name = cmds.optionMenu(self.procedure, query=True, value=True)
            args = dict(action=action, edition=edition)
            if action in ('inventory', 'invoke'):
                args['procedure'] = name
            if action == 'invoke':
                args['arguments'] = json.loads(cmds.scrollField(self.arguments, query=True, text=True))
            result = self.tool.run(dry_run=dry_run, **args)
            text = result.to_json()
        except Exception as error:
            text = str(error)
        cmds.scrollField(self.status, edit=True, text=text)
        print(text)

    def help(self, *_):
        name = self.WINDOW + 'Help'
        if cmds.window(name, exists=True):
            cmds.deleteUI(name)
        cmds.window(name, title='原套件帮助图', widthHeight=(800, 500))
        cmds.columnLayout(adjustableColumn=True)
        cmds.image(image=str(PACKAGE / 'upstream/anim_layer_help.jpg'), width=780, height=480)
        cmds.showWindow(name)


def show_ui(tool):
    if cmds.about(batch=True):
        raise RuntimeError('Open the suite gateway in interactive Maya')
    return SuiteUI(tool).show()
