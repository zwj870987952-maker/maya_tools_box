"""Complete prototype proxy engine and explicit one-joint/one-mesh binding."""
from maya import cmds
from maya_toolkit.core.maya_utils import get_mesh_shape, get_skin_cluster


def node(value, editable=False):
    found = cmds.ls(value, long=True) or []
    if len(found) != 1 or '.' in value or not cmds.objectType(found[0], isAType='transform'):
        raise ValueError('Unique whole transform/joint required: ' + str(value))
    result = found[0]
    if len(cmds.ls(result, long=True, allPaths=True) or []) != 1:
        raise ValueError('Instanced source/target unsupported')
    if editable and (cmds.referenceQuery(result, isNodeReferenced=True) or any(cmds.lockNode(result, query=True, lock=True))):
        raise ValueError('Referenced/locked write target: ' + result)
    return result


def mesh(value):
    target = node(value, editable=True)
    shapes = cmds.listRelatives(target, shapes=True, noIntermediate=True, fullPath=True) or []
    shape = get_mesh_shape(target)
    if not shape or shapes != [shape] or cmds.polyEvaluate(shape, vertex=True) < 1:
        raise ValueError('Exactly one non-intermediate polygon mesh required')
    if cmds.referenceQuery(shape, isNodeReferenced=True) or any(cmds.lockNode(shape, query=True, lock=True)):
        raise ValueError('Referenced/locked mesh shape')
    if get_skin_cluster(target):
        raise ValueError('Existing skinCluster rejected; this tool creates new bindings')
    return target


def animation_removal_plan(target):
    curves = list(set(cmds.listConnections(target, source=True, destination=False, type='animCurve') or []))
    for curve in curves:
        if cmds.nodeType(curve) not in ('animCurveTA', 'animCurveTL', 'animCurveTU') or cmds.referenceQuery(curve, isNodeReferenced=True) or any(cmds.lockNode(curve, query=True, lock=True)):
            raise ValueError('Only writable simple source time animation can be removed')
        destinations = cmds.listConnections(curve + '.output', source=False, destination=True, plugs=True) or []
        if len(destinations) != 1 or cmds.ls(destinations[0].rsplit('.', 1)[0], long=True) != [target] or cmds.getAttr(destinations[0], lock=True):
            raise ValueError('Shared/locked source animation output rejected')
        incoming = cmds.listConnections(curve + '.input', source=True, destination=False, plugs=True) or []
        if any(cmds.nodeType(x.split('.')[0]) != 'time' for x in incoming):
            raise ValueError('Time-warped source curve rejected')
    for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'):
        if cmds.getAttr(target + '.' + attr, lock=True):
            raise ValueError('Locked source transform channel')
        for driver in cmds.listConnections(target + '.' + attr, source=True, destination=False) or []:
            if driver not in curves:
                raise ValueError('Driven/layered source channels cannot transfer to a static mesh transform')
    current = target
    while current:
        for attr in ('sx', 'sy', 'sz', 'shearXY', 'shearXZ', 'shearYZ'):
            expected = 1 if attr.startswith('s') and not attr.startswith('shear') else 0
            if abs(cmds.getAttr(current + '.' + attr) - expected) > 1e-8 or cmds.listConnections(current + '.' + attr, source=True, destination=False):
                raise ValueError('Skin transfer requires static unit scale and zero shear throughout parent chain')
        parents = cmds.listRelatives(current, parent=True, fullPath=True) or []
        current = parents[0] if parents else None
        if current:
            for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz'):
                if cmds.listConnections(current + '.' + attr, source=True, destination=False):
                    raise ValueError('Animated/driven source ancestor would double-transform the skinned proxy')
    return {'curves': curves, 'key_count': cmds.keyframe(target, query=True, keyframeCount=True) or 0, 'scope': 'ALL source transform keys, including custom channels and outside bake interval'}


def preflight(p):
    if not cmds.undoInfo(query=True, state=True):
        raise ValueError('Enable Undo before binding/proxy creation')
    plan = dict(p, scene_write=True, file_write=False, gui_acceptance='not_run')
    if p['action'] == 'bind':
        pairs = []
        for item in p['pairs']:
            joint = node(item['joint'], editable=True)
            if cmds.nodeType(joint) != 'joint':
                raise ValueError('Each influence must be an existing joint')
            target = mesh(item['mesh'])
            if joint == target or joint.startswith(target + '|'):
                raise ValueError('Influence cannot be the mesh or its descendant')
            pairs.append({'joint': joint, 'mesh': target})
        targets = [x['mesh'] for x in pairs]
        if len(set(targets)) != len(targets):
            raise ValueError('Duplicate mesh aliases')
        plan['pairs'] = pairs
    else:
        values = p.get('objects', cmds.ls(selection=True, long=True) or [])
        if not values:
            raise ValueError('Select or supply whole source transforms')
        targets = [mesh(v) if p['skinning'] else node(v) for v in values]
        if len(targets) != len(set(targets)):
            raise ValueError('Duplicate source aliases')
        plan['objects'] = targets
        if p['skinning']:
            start = p.get('start_frame', cmds.playbackOptions(query=True, min=True))
            end = p.get('end_frame', cmds.playbackOptions(query=True, max=True))
            if not 0 <= end - start <= 10000:
                raise ValueError('Bounded ordered inclusive bake range required')
            plan.update(start_frame=start, end_frame=end, source_animation_removal={x: animation_removal_plan(x) for x in targets})
    if (p['action'] == 'bind' or p['skinning']) and any(a.startswith(b + '|') for a in targets for b in targets if a != b):
        raise ValueError('Skinned meshes cannot be parents/children of one another')
    return plan


class Capture:
    def __init__(self):
        self.created = {'joints': [], 'locators': [], 'cubes': [], 'constraints': [], 'sets': [], 'skin_clusters': []}
        self.constraint_ids = set()

    def __getattr__(self, name):
        function = getattr(cmds, name)
        category = {'joint': 'joints', 'spaceLocator': 'locators', 'polyCube': 'cubes', 'parentConstraint': 'constraints', 'sets': 'sets', 'skinCluster': 'skin_clusters'}.get(name)
        if not category:
            return function
        def invoke(*args, **kwargs):
            result = function(*args, **kwargs)
            names = result if isinstance(result, list) else [result]
            for n in names[:1] if name == 'polyCube' else names:
                self.created[category].append(n)
                if category == 'constraints':
                    self.constraint_ids.add(cmds.ls(n, uuid=True)[0])
            return result
        return invoke

    def delete(self, target):
        if cmds.ls(target, uuid=True)[0] not in self.constraint_ids:
            raise RuntimeError('Refusing to delete an unrelated scene constraint')
        cmds.delete(target)


def execute(p):
    from . import engine
    plan = preflight(p)
    state = {'time': cmds.currentTime(query=True), 'selection': cmds.ls(selection=True, long=True) or [], 'autokey': cmds.autoKeyframe(query=True, state=True), 'namespace': cmds.namespaceInfo(currentNamespace=True)}
    tracker = Capture()
    original = engine.cmds
    try:
        cmds.autoKeyframe(state=False)
        cmds.namespace(setNamespace=':')
        if p['action'] == 'bind':
            bindings = []
            for pair in plan['pairs']:
                cluster = tracker.skinCluster(pair['joint'], pair['mesh'], toSelectedBones=True)[0]
                bindings.append(dict(pair, skin_cluster=cluster))
            return dict(plan, bindings=bindings)
        engine.cmds = tracker
        if p['skinning']:
            cmds.currentTime(plan['start_frame'])
        if p['proxy_type'] == 'joint':
            created = engine.create_joint_and_parent_constraint(plan['objects'], skinning_enabled=p['skinning'], frame_range=(plan.get('start_frame'), plan.get('end_frame')))
        elif p['proxy_type'] == 'locator':
            created = engine.create_locator_and_parent_constraint(plan['objects'])
        else:
            created = engine.create_cube_and_parent_constraint(plan['objects'])
        rows = [{'source': source, 'proxy': proxy, 'proxy_uuid': cmds.ls(proxy, uuid=True)[0]} for source, proxy in zip(plan['objects'], created)]
        live = {k: [n for n in values if cmds.objExists(n)] for k, values in tracker.created.items()}
        return dict(plan, mappings=rows, created=live, proxy_constraints_retained=not p['skinning'])
    finally:
        engine.cmds = original
        cmds.namespace(setNamespace=state['namespace'])
        cmds.currentTime(state['time'])
        cmds.autoKeyframe(state=state['autokey'])
        if state['selection']:
            cmds.select(state['selection'], replace=True)
        else:
            cmds.select(clear=True)
