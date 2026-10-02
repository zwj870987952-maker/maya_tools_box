"""Correct candidate builder documentation to match observed plugin metadata behavior."""
from pathlib import Path
p=Path(__file__).with_name('prepare_clean_junk.py')
s=p.read_text(encoding='utf-8')
s=s.replace('remove_unknown_plugins=True才删除','remove_unknown_plugins=True+confirm_plugin_metadata_loss=True且先保存备份场景才删除（本机observed metadata不可Undo）')
s=s.replace('MDagModifier includeParents=False保父对象','MDagModifier必须解锁后排队，includeParents=False保父对象')
s=s.replace('插件用Autodesk公开undoable unknownPlugin命令同外层UndoChunk','插件虽文档称undoable，本机fixture真实Undo不能恢复，明确元数据永久移除，需要已有备份scene恢复，外层UndoChunk也不提供metadata恢复')
s=s.replace('用户可Undo。文件不保存','只有节点/回调可Undo。文件不保存')
s=s.replace("t.run(dry_run=True,action='clean',unlock_nodes=True,remove_unknown_plugins=True)","t.run(dry_run=True,action='clean',unlock_nodes=True)")
s=s.replace("t.run(action='clean',unlock_nodes=True,remove_unknown_plugins=True)","t.run(action='clean',unlock_nodes=True)")
s=s.replace('真实MA未知requires metadata delete nativeUndoRedo','真实MA requires metadata显式确认与永久移除guard')
s=s.replace('explicit移除需unused','explicit移除需unused+confirm_plugin_metadata_loss')
s=s.replace('UndoRedo恢复元数据','元数据不能依赖Undo，需用户已有备份scene恢复')
p.write_text(s,encoding='utf-8')
