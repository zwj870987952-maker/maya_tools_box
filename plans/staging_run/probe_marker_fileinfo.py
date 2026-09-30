import os
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('isolated only')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
import json
cmds.file(new=True, force=True)
cmds.undoInfo(state=True)
payload = json.dumps({'frames':[1], 'colors':[[0,255,0]], 'comments':['quote " slash \\ newline\n中文']},ensure_ascii=False)
cmds.fileInfo('timelineMarkers', payload)
print('ENCODED', repr(payload), 'QUERY', repr(cmds.fileInfo('timelineMarkers',query=True)[0]))
cmds.flushUndo()
cmds.undoInfo(openChunk=True, chunkName='marker_probe')
cmds.fileInfo('timelineMarkers', 'after')
cmds.undoInfo(closeChunk=True)
print('BEFORE_UNDO', cmds.fileInfo('timelineMarkers', query=True), cmds.undoInfo(query=True, undoQueueEmpty=True))
try:
    cmds.undo()
except RuntimeError as error:
    print('NON_UNDOABLE', str(error))
print('AFTER_UNDO', cmds.fileInfo('timelineMarkers', query=True))
maya.standalone.uninitialize()
