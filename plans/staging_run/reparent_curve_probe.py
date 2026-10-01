import json
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
n = cmds.circle(name='ctrl')[0]
cmds.setKeyframe(n, attribute='tx', time=1, value=2)
c = cmds.listConnections(n+'.tx', source=True, destination=False)[0]
print(json.dumps({'curve': c, 'type': cmds.nodeType(c), 'input_sources': cmds.listConnections(c+'.input', source=True, destination=False), 'input_plugs': cmds.listConnections(c+'.input', source=True, destination=False, plugs=True), 'input_value': cmds.getAttr(c+'.input'), 'input_connections_all': cmds.listConnections(c, connections=True, plugs=True)}, ensure_ascii=True))
