# -*- coding: utf-8 -*-
"""Original pivot actions, with UUID resolution and parent restoration."""
from __future__ import absolute_import, division, print_function

from contextlib import contextmanager

ACTIONS = ("center", "origin", "parent", "reset_axes", "world", "joint", "complete")
HIERARCHY_ACTIONS = ("reset_axes", "world", "joint", "complete")


def maya_commands():
    import maya.cmds as cmds
    return cmds


def resolve(cmds, node_id):
    paths = cmds.ls(node_id, long=True) or []
    if len(paths) != 1:
        raise ValueError("Node must resolve to one DAG path: {}".format(node_id))
    return paths[0]


@contextmanager
def world_parent(cmds, node_id):
    node = resolve(cmds, node_id)
    parents = cmds.listRelatives(node, parent=True, fullPath=True) or []
    parent_id = (cmds.ls(parents[0], uuid=True) or [None])[0] if parents else None
    try:
        if parent_id:
            cmds.parent(node, world=True)
        yield
    finally:
        if parent_id:
            cmds.parent(resolve(cmds, node_id), resolve(cmds, parent_id))


def apply_action(cmds, action, node_id, joint_orientation=None):
    node = resolve(cmds, node_id)
    if action in ("center", "origin", "parent"):
        rotation = cmds.xform(node, query=True, rotation=True)
        if action == "center":
            # Preserve Maya centerPivots semantics; do not replace with a bbox algorithm.
            cmds.xform(node, centerPivots=True)
        elif action == "origin":
            cmds.xform(node, worldSpace=True, pivots=[0, 0, 0])
        else:
            parent = cmds.listRelatives(node, parent=True, fullPath=True)[0]
            pivot = cmds.xform(parent, query=True, worldSpace=True, pivots=True)[:3]
            cmds.xform(node, worldSpace=True, pivots=pivot)
        cmds.xform(node, rotation=rotation)
        return resolve(cmds, node_id)

    position = cmds.xform(node, query=True, worldSpace=True, translation=True)
    scale = cmds.xform(node, query=True, worldSpace=True, scale=True)
    pivot = cmds.xform(node, query=True, worldSpace=True, pivots=True)[:3]
    with world_parent(cmds, node_id):
        node = resolve(cmds, node_id)
        if action in ("reset_axes", "complete"):
            cmds.makeIdentity(node, apply=True, rotate=True)
        if action == "complete":
            cmds.xform(node, centerPivots=True)
        if action in ("world", "complete", "joint"):
            cmds.xform(node, worldSpace=True, rotation=joint_orientation if action == "joint" else [0, 0, 0])
        cmds.xform(node, worldSpace=True, translation=position)
        cmds.xform(node, worldSpace=True, scale=scale)
        if action != "complete":
            cmds.xform(node, worldSpace=True, pivots=pivot)
    return resolve(cmds, node_id)
