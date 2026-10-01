"""Full original algorithms with explicit options and owned mark/pose state."""
from contextlib import contextmanager
import json
import math
from pathlib import Path
from maya import cmds
from maya.api import OpenMaya as om
from .original_logic import RelationshipTool

OWNER = 'stagingRelationshipOwner'
ROLE = 'stagingRelationshipRole'
SOURCE = 'stagingRelationshipSource'
CACHE = {}


def nodes(values, writable=False, channels=()):
    result = []
    for value in values:
        found = cmds.ls(value, long=True) or []
        if len(found) != 1 or '.' in value or not cmds.objectType(found[0], isAType='transform'):
            raise ValueError('Unique whole transform/joint required')
        node = found[0]
        sel = om.MSelectionList()
        sel.add(node)
        if len(om.MDagPath.getAllPathsTo(sel.getDependNode(0))) != 1:
            raise ValueError('Instanced inputs unsupported')
        if writable and (cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True))):
            raise ValueError('Locked/referenced target')
        for attr in channels if writable else ():
            plug = node + '.' + attr
            if cmds.getAttr(plug, lock=True):
                raise ValueError('Locked target channel: ' + plug)
            drivers = cmds.listConnections(plug, source=True, destination=False) or []
            if any(not cmds.nodeType(n).startswith('animCurve') for n in drivers):
                raise ValueError('Constraint/layer/complex driver rejected: ' + plug)
            for curve in drivers:
                destinations = cmds.listConnections(curve + '.output', source=False, destination=True, plugs=True) or []
                if len(destinations) != 1 or cmds.referenceQuery(curve, isNodeReferenced=True) or any(cmds.lockNode(curve, query=True, lock=True)):
                    raise ValueError('Shared/locked/referenced animation curve')
                inputs = cmds.listConnections(curve + '.input', source=True, destination=False) or []
                if any(cmds.nodeType(n) != 'time' for n in inputs):
                    raise ValueError('Driven/non-time animation input rejected')
        if node in result:
            raise ValueError('Duplicate node aliases')
        result.append(node)
    return result


def identifier(node):
    return cmds.ls(node, uuid=True)[0]


def owned():
    result = []
    for plug in cmds.ls('*.' + OWNER, recursive=True) or []:
        if cmds.getAttr(plug) == 'relationship_tools_v19':
            result.append(plug.rsplit('.', 1)[0])
    return sorted(set(cmds.ls(result, long=True) or [])) if result else []


def role(node):
    return cmds.getAttr(node + '.' + ROLE) if cmds.objExists(node + '.' + ROLE) else 'helper'


def mark_metadata(node, kind='helper', source=None):
    for name, value in ((OWNER, 'relationship_tools_v19'), (ROLE, kind)):
        if not cmds.objExists(node + '.' + name):
            cmds.addAttr(node, longName=name, dataType='string')
        cmds.setAttr(node + '.' + name, value, type='string')
    if source:
        cmds.addAttr(node, longName=SOURCE, attributeType='message')
        cmds.connectAttr(source + '.message', node + '.' + SOURCE)


def mark_map():
    mapping = {}
    for node in owned():
        if role(node) != 'tag':
            continue
        source = cmds.listConnections(node + '.' + SOURCE, source=True, destination=False) or []
        if len(source) == 1:
            path = nodes(source)[0]
            if path in mapping:
                raise ValueError('Multiple owned tags for same source')
            mapping[path] = node
    return mapping


def cleanup_plan():
    targets = owned()
    members = {identifier(n) for n in targets}
    for node in targets:
        if cmds.referenceQuery(node, isNodeReferenced=True) or any(cmds.lockNode(node, query=True, lock=True)):
            raise ValueError('Owned mark is locked/referenced')
        children = cmds.listRelatives(node, allDescendents=True, fullPath=True) or []
        for child in children:
            if cmds.objectType(child, isAType='transform') and identifier(child) not in members:
                raise ValueError('Foreign child under owned mark; deletion rejected')
        for destination in cmds.listConnections(node, source=False, destination=True) or []:
            if identifier(destination) not in members:
                raise ValueError('Owned mark drives foreign node; deletion rejected')
    return targets


def frames(p, objects):
    if p.get('frame_range') is None:
        return [cmds.currentTime(query=True)]
    start, end = p['frame_range']
    if p['bake']:
        selected = list(range(start, end, p['step']))
        if end - 1 not in selected:
            selected.append(end - 1)
        return selected
    selected = sorted({float(frame) for node in objects for attr in channels(p) for frame in cmds.keyframe(node, attribute=attr, query=True, timeChange=True) or [] if start <= frame < end})
    return selected  # Empty key-only range is a genuine no-op, never dense bake.


def channels(p):
    return (['translateX', 'translateY', 'translateZ'] if p['translate'] else []) + (['rotateX', 'rotateY', 'rotateZ'] if p['rotate'] else [])


def pose_cache():
    result = {}
    for uuid, value in CACHE.items():
        found = cmds.ls(uuid, long=True) or []
        if len(found) == 1:
            result[found[0]] = dict(value)
    return result


class SafeRelationship(RelationshipTool):
    def __init__(self, p):
        self.settings = p
        self.DEFAULT_MAX_ATTEMPTS = 6
        self.DEFAULT_FULL_CHECK_ATTEMPTS = 6
        self.world_transform_data = pose_cache()
        self.world_coordinate_mode = p['world_coords']
        self.created_layer = None

    def option(self, name):
        return self.settings[name]

    def get_time_range(self):
        return tuple(self.settings['frame_range'])

    def get_frame_step(self):
        return self.settings['step']

    def get_attribute_options(self):
        return self.settings['translate'], self.settings['rotate'], channels(self.settings)

    def cleanup_scene(self):
        targets = cleanup_plan()
        if targets:
            cmds.delete(targets)

    def with_performance_optimization(self, func, *args, **kwargs):
        evaluation = cmds.evaluationManager(query=True, mode=True)[0]
        suspended = cmds.refresh(query=True, suspend=True)
        try:
            cmds.evaluationManager(mode='off')
            cmds.refresh(suspend=True)
            return func(*args, **kwargs)
        finally:
            cmds.refresh(suspend=suspended)
            cmds.evaluationManager(mode=evaluation)

    def optimize_keyframes(self, objects, start_frame, end_frame):
        # Frames are sampled at the requested step before writing. Never cut
        # existing keys on objects, disabled TR channels, scale or custom attrs.
        return None

    def get_objects_and_locators(self, selection):
        mapping = mark_map()
        selected = nodes(selection) if selection else list(mapping)
        return selected, {n: mapping[n] for n in selected}

    def create_mark(self, source, kind, parent=None):
        leaf = source.rsplit('|', 1)[-1] if source else 'foot'
        name = leaf + ('_locatorTag' if kind == 'tag' else '_locatorPar')
        if cmds.objExists(name):
            raise ValueError('Existing mark-like name protected: ' + name)
        node = cmds.spaceLocator(name=name)[0]
        mark_metadata(node, kind, source)
        if source:
            cmds.matchTransform(node, source, pos=True, rot=True)
        if parent:
            node = cmds.parent(node, parent)[0]
        return node

    def create_locator_system(self, parent_obj, child_objs):
        parent = self.create_mark(parent_obj, 'par')
        constraint = cmds.parentConstraint(parent_obj, parent, maintainOffset=False)[0]
        mark_metadata(constraint)
        children = [self.create_mark(n, 'tag', parent) for n in child_objs]
        return parent, children

    def mark_action(self, *args):
        selection = cmds.ls(selection=True, long=True) or []
        self.cleanup_scene()
        parent, children = self.create_locator_system(selection[-1], selection[:-1])
        self.lock_and_hide([parent] + children)

    def mark_foot_action(self, *args):
        selection = cmds.ls(selection=True, long=True) or []
        self.cleanup_scene()
        parent = self.create_mark(None, 'par')
        children = [self.create_mark(n, 'tag', parent) for n in selection]
        self.lock_and_hide([parent] + children)

    def mark_ani_action(self, *args):
        selection = cmds.ls(selection=True, long=True) or []
        self.cleanup_scene()
        parent, children = self.create_locator_system(selection[-1], selection[:-1])
        chosen = frames(self.settings, selection)
        def sample():
            for frame in chosen:
                cmds.currentTime(frame)
                for tag, source in zip(children, selection[:-1]):
                    self.match_locator_to_object(tag, source)
                    cmds.setKeyframe(tag, attribute=channels(self.settings))
        self.with_performance_optimization(sample)
        self.lock_and_hide([parent] + children)

    def copy_world_transform(self):
        selected = cmds.ls(selection=True, long=True) or []
        CACHE.clear()
        for node in selected:
            CACHE[identifier(node)] = {'pos': cmds.xform(node, query=True, worldSpace=True, translation=True), 'rot': cmds.xform(node, query=True, worldSpace=True, rotation=True), 'short_name': node.rsplit('|', 1)[-1]}
        self.world_transform_data = pose_cache()

    def load_world_transform_data(self):
        self.world_transform_data = pose_cache()
        return bool(self.world_transform_data)

    def process_step_operation(self, is_more_step=False):
        selection = nodes(cmds.ls(selection=True, long=True) or [])
        selected = self.sort_objects_by_hierarchy(selection)
        chosen = frames(self.settings, selected) if is_more_step else [cmds.currentTime(query=True)]
        mapping = mark_map() if not self.settings['world_coords'] else {}
        poses = pose_cache()
        def operate():
            for frame in chosen:
                cmds.currentTime(frame)
                if self.settings['world_coords']:
                    self._paste_world_transform_to_objects(selected, {n: poses[n] for n in selected}, *self.get_attribute_options())
                else:
                    self.perform_single_step_operation(selected, {n: mapping[n] for n in selected})
                for target in selected:
                    expected = poses[target] if self.settings['world_coords'] else {'pos': cmds.xform(mapping[target], query=True, worldSpace=True, translation=True), 'rot': cmds.xform(mapping[target], query=True, worldSpace=True, rotation=True)}
                    if self.settings['translate'] and not self.is_close(cmds.xform(target, query=True, worldSpace=True, translation=True), expected['pos']):
                        raise RuntimeError('World translation did not converge')
                    if self.settings['rotate'] and not self.angle_close(cmds.xform(target, query=True, worldSpace=True, rotation=True), expected['rot']):
                        raise RuntimeError('World rotation did not converge')
        self.use_anim_layer_if_enabled(selected, operate)
        if self.settings['advance']:
            cmds.currentTime(self.settings['_original_time'] + 1)

    def align_objects_action(self, *args):
        selected = nodes(cmds.ls(selection=True, long=True) or [])
        sources, target = selected[:-1], selected[-1]
        chosen = frames(self.settings, selected)
        def operate():
            if self.settings['frame_range'] is None:
                self._perform_single_frame_align(target, self.sort_objects_by_hierarchy(sources), self.settings['translate'], self.settings['rotate'])
            else:
                self._perform_multi_frame_align(target, sources, chosen, *self.get_attribute_options())
        self.use_anim_layer_if_enabled(sources, operate)

    def create_anim_layer(self, objects, layer_name=None):
        layer = cmds.animLayer(layer_name or 'RTL_Layer', override=True)
        for obj in objects:
            for attr in channels(self.settings):
                cmds.animLayer(layer, edit=True, attribute=obj + '.' + attr)
        self.created_layer = layer
        return layer

    def use_anim_layer_if_enabled(self, objects, func, *args, **kwargs):
        if not self.settings['layer'] or self.created_layer:
            return func(*args, **kwargs)
        layer = self.create_anim_layer(objects)
        previous = {n: {'preferred': cmds.animLayer(n, query=True, preferred=True), 'selected': cmds.animLayer(n, query=True, selected=True)} for n in cmds.ls(type='animLayer') or [] if n != layer}
        try:
            cmds.animLayer(layer, edit=True, preferred=True, selected=True)
            return func(*args, **kwargs)
        finally:
            cmds.animLayer(layer, edit=True, preferred=False, selected=False)
            for n, state in previous.items():
                cmds.animLayer(n, edit=True, preferred=state['preferred'], selected=state['selected'])
