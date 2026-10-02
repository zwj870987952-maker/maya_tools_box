"""Disposable mayapy-only readout of native Undo queue formatting."""
import json
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
from maya.api import OpenMaya as om
cmds.file(new=True,force=True)
cmds.polyCube()
cmds.undoInfo(openChunk=True,chunkName='mtbCheckpoint_PROBE')
cmds.createNode('network',name='testMarkerProbe')
cmds.undoInfo(closeChunk=True)
cmds.setAttr('testMarkerProbe.caching',True)
messages=[]
handle=om.MCommandMessage.addCommandOutputCallback(lambda message,kind,data:messages.append(message))
try: result=cmds.undoInfo(query=True,printQueue=True)
finally: om.MMessage.removeCallback(handle)
print(json.dumps({'result':result,'messages':messages,'top':cmds.undoInfo(query=True,undoName=True)},ensure_ascii=True))
