import maya.cmds as cmds
import maya.mel as mel
import os

def patch_file_dialog():
    """
    monkey patch cmds.fileDialog2，使其默认路径为当前maya文件所在目录
    """
    orig_fileDialog2 = cmds.fileDialog2
    def fileDialog2_patched(*args, **kwargs):
        cur_file = cmds.file(q=True, sn=True)
        if cur_file:
            cur_dir = os.path.dirname(cur_file)
            kwargs['startingDirectory'] = cur_dir
        return orig_fileDialog2(*args, **kwargs)
    cmds.fileDialog2 = fileDialog2_patched
    # MEL层也patch
    mel.eval('global proc string[] fileDialog2(string $args[]) { python("import maya.cmds as cmds;cmds.fileDialog2()"); }') 