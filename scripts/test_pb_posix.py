from pathlib import Path
import maya.cmds as cmds
out_dir = Path(r"C:\Users\zhongweijie\.gemini\antigravity\brain\f8152522-dcb3-4911-9254-38b4c32bd26d\snapshots\mirror_anim_seq")
out_dir.mkdir(parents=True, exist_ok=True)
frame_prefix = (out_dir / "frame").as_posix()
res = cmds.playblast(startTime=1, endTime=2, format='image', compression='png', filename=frame_prefix, viewer=False, showOrnaments=False, clearCache=True, framePadding=4, percent=100, widthHeight=(640, 480), forceOverwrite=True)
print("Playblast with as_posix() succeeded:", res)
