"""Constraint helpers for blueprint Maya operations."""

from .common import MayaApiError, UndoChunk, maya_modules
from .scene_nodes import existing_nodes


def create_constraint(constraint_type, drivers, driven, maintain_offset=True, weight=1.0):
    """Create constraints from driver nodes to driven nodes."""
    cmds = maya_modules()
    driver_nodes = existing_nodes(drivers, label="driver nodes")
    driven_nodes = existing_nodes(driven, label="driven nodes")
    command = _constraint_command(cmds, constraint_type)
    created_constraints = []

    with UndoChunk("Blueprint {0} Constraint".format(constraint_type.title())):
        for driven_node in driven_nodes:
            result = command(
                *(driver_nodes + [driven_node]),
                maintainOffset=bool(maintain_offset),
                weight=float(weight),
            ) or []
            created_constraints.extend(result)

    print(
        "{0} Constraint: {1} constraint node(s).".format(
            constraint_type.title(),
            len(created_constraints),
        )
    )
    return created_constraints


def _constraint_command(cmds, constraint_type):
    commands = {
        "parent": cmds.parentConstraint,
        "point": cmds.pointConstraint,
        "orient": cmds.orientConstraint,
        "scale": cmds.scaleConstraint,
    }
    if constraint_type not in commands:
        raise MayaApiError("Unsupported constraint type: {0}".format(constraint_type))
    return commands[constraint_type]
