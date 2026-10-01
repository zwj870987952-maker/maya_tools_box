"""Read-only scene capture and all original analysis entry points."""
import hashlib
import json
from pathlib import Path
from maya import cmds
from maya.api import OpenMaya as om
from . import graph

PKG = Path(__file__).resolve().parent
TYPES = ('pointConstraint', 'orientConstraint', 'scaleConstraint', 'parentConstraint', 'aimConstraint', 'geometryConstraint', 'normalConstraint', 'tangentConstraint', 'poleVectorConstraint', 'pointOnPolyConstraint')


def resources():
    c = json.loads((PKG/'catalog.json').read_text(encoding='utf-8'))
    for row in c['files']:
        p = PKG/row['archive']
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError('Original resource missing/changed')


def resolve(value):
    if not isinstance(value, str) or any(x in value for x in ('.', '*', '?', '[', ']', ';', '`', '\n', '\r')):
        raise ValueError('Literal whole transform/joint required')
    matches = cmds.ls(value, long=True) or []
    if len(matches) != 1 or not cmds.objectType(matches[0], isAType='transform') or cmds.nodeType(matches[0]).endswith('Constraint'):
        raise ValueError('Unique existing transform/joint required '+value)
    selection = om.MSelectionList()
    selection.add(matches[0])
    if len(om.MDagPath.getAllPathsTo(selection.getDependNode(0))) != 1:
        raise ValueError('DAG instances require explicit separate analysis')
    return matches[0]


def transform_of(value):
    matches = cmds.ls(value, long=True) or []
    if len(matches) != 1:
        raise ValueError('Ambiguous driver '+value)
    n = matches[0]
    if not cmds.objectType(n, isAType='transform'):
        selection = om.MSelectionList()
        selection.add(n)
        if len(om.MDagPath.getAllPathsTo(selection.getDependNode(0))) != 1:
            raise ValueError('Instanced geometry driver requires separate instance analysis')
        parents = cmds.listRelatives(n, parent=True, fullPath=True) or []
        if len(parents) != 1:
            raise ValueError('Shape driver has no unique parent')
        n = parents[0]
    return resolve(n)


def capture(p):
    resources()
    requested = p['objects'] if 'objects' in p else (cmds.ls(selection=True, long=True) or [])
    if not requested or len(requested) > 1000:
        raise ValueError('Select 1..1000 whole transforms/joints')
    selected = [resolve(x) for x in requested]
    if len(set(selected)) != len(selected):
        raise ValueError('Duplicate object aliases')
    all_nodes = sorted(set(cmds.ls(type='transform', long=True) or [])|set(cmds.ls(type='joint', long=True) or []))
    all_nodes = [x for x in all_nodes if not cmds.nodeType(x).endswith('Constraint')]
    if len(all_nodes) > p['max_nodes']:
        raise ValueError('Scene node budget exceeded; raise max_nodes explicitly')
    for n in all_nodes:
        resolve(n)
    direct = {n: set() for n in all_nodes}
    parent_map, constraints, warnings = {}, [], []
    edge_count = 0
    def add(a, b):
        nonlocal edge_count
        if a not in direct or b not in direct:
            raise ValueError('Constraint endpoint outside captured transform graph')
        if b not in direct[a]:
            direct[a].add(b)
            edge_count += 1
            if edge_count > p['max_edges']:
                raise ValueError('Scene edge budget exceeded')
    for n in all_nodes:
        parent = cmds.listRelatives(n, parent=True, fullPath=True) or []
        parent_map[n] = parent[0] if parent else None
        if parent and p['include_hierarchy']:
            add(resolve(parent[0]), n)
    if p['include_constraints']:
        native_constraints = sorted(set(cmds.ls(type='constraint', long=True) or []))
        if len(native_constraints) > p['max_nodes']:
            raise ValueError('Constraint capture budget exceeded')
        for n in native_constraints:
            kind = cmds.nodeType(n)
            if kind not in TYPES:
                warnings.append('Unknown constraint type skipped: '+kind+' '+n)
                continue
            parent = cmds.listRelatives(n, parent=True, fullPath=True) or []
            if len(parent) != 1:
                warnings.append('Constraint without one native child: '+n)
                continue
            child = resolve(parent[0])
            fn = getattr(cmds, kind)
            targets = fn(n, query=True, targetList=True) or []
            indices = cmds.getAttr(n+'.target', multiIndices=True) or []
            if len(targets) != len(indices):
                raise ValueError('Unresolved target indices '+n)
            drivers = []
            for target, index in zip(targets, indices):
                matrix = n+'.target['+str(index)+'].targetParentMatrix'
                upstream = cmds.listConnections(matrix, source=True, destination=False) or [] if cmds.objExists(matrix) else []
                driver = transform_of(upstream[0] if len(upstream) == 1 else target)
                drivers.append(driver)
                add(driver, child)
            constraints.append({'node': n, 'uuid': cmds.ls(n, uuid=True)[0], 'type': kind, 'constrained': child, 'drivers': drivers})
    return {'selected': selected, 'nodes': all_nodes, 'direct': direct, 'parents': parent_map, 'constraints': constraints, 'warnings': warnings, 'edge_count': edge_count}


def analyze(p):
    snap = capture(p)
    projected = graph.project(snap['direct'], snap['selected'])
    if sum(len(x) for x in projected.values()) > p['max_edges']:
        raise ValueError('Selected transitive edge budget exceeded')
    order = graph.layers(projected, snap['selected'])
    order['valid'] = order['valid'] and graph.verify(projected, order['layers'], snap['selected']) and not snap['warnings']
    hierarchy = {}
    for n in snap['selected']:
        parents, cursor = [], snap['parents'].get(n)
        while cursor:
            parents.append(cursor)
            cursor = snap['parents'].get(cursor)
        hierarchy[n] = parents
    drivers = {n: [] for n in snap['selected']}
    for constraint in snap['constraints']:
        if constraint['constrained'] in drivers:
            for driver in constraint['drivers']:
                if driver not in drivers[constraint['constrained']]:
                    drivers[constraint['constrained']].append(driver)
    warnings = list(snap['warnings'])
    if order['cycles']:
        warnings.append('Structural potential-influence cycles found; cyclic/blocked nodes are not assigned artificial layers')
    warnings.append('Structural DAG/native-constraint potential influence only; not a complete Maya DG/evaluation proof. Zero-weight targets and parent edges are included conservatively.')
    result = dict(order, objects=snap['selected'], object_uuids={n: cmds.ls(n, uuid=True)[0] for n in snap['selected']}, hierarchy=hierarchy, drivers=drivers, constraints=snap['constraints'], selected_influence={n: [x for x in snap['selected'] if x in projected[n]] for n in snap['selected']}, scene_node_count=len(snap['nodes']), scene_edge_count=snap['edge_count'], warnings=warnings, scene_write=False, file_write=False, gui_acceptance='not_run')
    if p['include_graph']:
        result['direct_graph'] = {n: sorted(snap['direct'][n]) for n in snap['nodes']}
    return result


def get_hierarchy_info(nodes):
    from .tool import normalize
    return analyze(normalize(objects=list(nodes)))['hierarchy']


def get_constraint_info(nodes):
    from .tool import normalize
    return {n: d for n, d in analyze(normalize(objects=list(nodes)))['drivers'].items() if d}


def build_global_influence_graph():
    from .tool import normalize
    nodes = [n for n in cmds.ls(type='transform', long=True) or [] if not cmds.nodeType(n).endswith('Constraint')]
    if not nodes:
        return {}
    snap = capture(normalize(objects=nodes[:1]))
    closure, count = {}, 0
    for n in snap['nodes']:
        closure[n] = graph.reachable(snap['direct'], n)
        count += len(closure[n])
        if count > 100000:
            raise ValueError('Global transitive edge budget exceeded; use selected API analysis')
    return closure


def analyze_influence_hierarchy(nodes):
    from .tool import normalize
    data = analyze(normalize(objects=list(nodes)))
    if not data['valid']:
        raise ValueError('No complete validated ordering: '+str(data['cycles'] or data['warnings']))
    return data['layers']


def topological_sort(influence_graph, nodes):
    data = graph.layers(influence_graph, list(nodes))
    if not data['valid']:
        raise ValueError('Graph contains cycles; no artificial sort')
    return [n for layer in data['layers'] for n in layer]


def verify_influence_hierarchy(influence_layers):
    from .tool import normalize
    nodes = [n for group in influence_layers for n in group]
    if not nodes or len(nodes) != len(set(nodes)):
        return False
    snap = capture(normalize(objects=nodes))
    actual_layers = [[resolve(n) for n in group] for group in influence_layers]
    return not snap['warnings'] and graph.verify(graph.project(snap['direct'], snap['selected']), actual_layers, snap['selected'])
