"""Self-contained eligible-reference helpers shared in behavior with batch importer."""
import hashlib
from pathlib import Path
def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def references(p):
    from maya import cmds
    nodes = p['reference_nodes']
    if nodes is None:
        objects = p['objects'] if p['objects'] is not None else cmds.ls(selection=True, long=True) or []
        if not objects:
            raise ValueError('Select referenced objects or provide exact reference nodes')
        nodes = []
        for obj in objects:
            names = cmds.ls(obj, long=True) or []
            if len(names) != 1 or not cmds.referenceQuery(names[0], isNodeReferenced=True):
                raise ValueError('Every target must belong to a reference: ' + obj)
            node = cmds.referenceQuery(names[0], referenceNode=True)
            if node not in nodes:
                nodes.append(node)
    rows = []
    for name in nodes:
        matches = cmds.ls(name, type='reference') or []
        if len(matches) != 1 or matches[0] == 'sharedReferenceNode':
            raise ValueError('Exact file reference required')
        node = matches[0]
        if cmds.referenceQuery(node, parent=True, referenceNode=True):
            raise ValueError('Nested reference removal unsupported; explicitly select a top-level file reference')
        if cmds.referenceQuery(node, child=True, referenceNode=True):
            raise ValueError('Reference contains nested child references; automatic whole-reference restoration unsupported')
        if cmds.referenceQuery(node, editStrings=True):
            raise ValueError('Edited reference cannot be restored faithfully; remove edits explicitly or use original Maya reference workflow')
        path = cmds.referenceQuery(node, filename=True, withoutCopyNumber=True)
        if not Path(path).is_file():
            raise ValueError('Reference source unavailable for Undo restore')
        namespace = cmds.referenceQuery(node, namespace=True).lstrip(':')
        if ':' in namespace:
            raise ValueError('Nested namespace reference unsupported')
        loaded = cmds.referenceQuery(node, isLoaded=True)
        rows.append({'reference_node': node, 'uuid': cmds.ls(node, uuid=True)[0], 'path': path, 'sha256': file_hash(path), 'namespace': namespace, 'loaded': loaded, 'node_locked': bool(cmds.lockNode(node, query=True, lock=True)[0]), 'nodes': cmds.referenceQuery(node, nodes=True, dagPath=True) or [] if loaded else []})
    return rows

def create_reference(row, restore=False):
    from maya import cmds
    if not Path(row['path']).is_file() or file_hash(row['path']) != row['sha256']:
        raise RuntimeError('Reference source changed/unavailable; cannot restore exact source')
    namespace = ':' + row['namespace']
    if cmds.namespace(exists=namespace):
        if cmds.namespaceInfo(namespace, listOnlyDependencyNodes=True):
            raise RuntimeError('Reference namespace contains foreign nodes')
        cmds.namespace(removeNamespace=namespace)
    previous = set(cmds.ls(type='reference') or [])
    cmds.file(row['path'], reference=True, namespace=row['namespace'], mergeNamespacesOnClash=False, executeScriptNodes=False, deferReference=not row.get('loaded', True))
    added = set(cmds.ls(type='reference') or []) - previous
    top = [n for n in added if n != 'sharedReferenceNode' and (not cmds.referenceQuery(n, parent=True, referenceNode=True))]
    if len(top) != 1:
        raise RuntimeError('Expected one top-level reference')
    node = top[0]
    if restore and node != row['reference_node']:
        if cmds.objExists(row['reference_node']):
            raise RuntimeError('Old reference node name occupied')
        cmds.lockNode(node, lock=False)
        node = cmds.rename(node, row['reference_node'])
    if restore:
        cmds.lockNode(node, lock=row.get('node_locked', True))
    return {'reference_node': node, 'uuid': cmds.ls(node, uuid=True)[0], 'path': row['path'], 'sha256': row['sha256'], 'namespace': row['namespace'], 'loaded': row.get('loaded', True), 'node_locked': bool(cmds.lockNode(node, query=True, lock=True)[0])}
