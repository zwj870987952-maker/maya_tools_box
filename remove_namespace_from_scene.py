import maya.cmds as cmds


def _get_namespace(node):
    """Return the absolute namespace of a node."""
    leaf_name = node.rsplit("|", 1)[-1]

    if ":" not in leaf_name:
        return None

    return ":" + leaf_name.rpartition(":")[0].lstrip(":")


def _base_name(node):
    """Return a node's leaf name without namespaces."""
    return node.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


def _reference_edits(reference_node):
    """Return edits stored on a reference."""
    try:
        return cmds.referenceQuery(
            reference_node,
            editStrings=True,
            successfulEdits=True,
            failedEdits=True,
        ) or []
    except RuntimeError:
        return []


def _reference_in_root(reference_node):
    """
    Recreate a top-level reference in the root namespace.

    The new nodes remain referenced. The old reference is removed only after
    the new reference has been created and verified successfully.
    """
    if cmds.referenceQuery(reference_node, isNodeReferenced=True):
        raise RuntimeError(
            "Nested references cannot be reassigned from the parent scene."
        )

    if not cmds.referenceQuery(reference_node, isLoaded=True):
        raise RuntimeError("The reference must be loaded.")

    edits = _reference_edits(reference_node)
    if edits:
        raise RuntimeError(
            "The reference contains {} reference edit(s). "
            "Recreating it would discard those edits.".format(len(edits))
        )

    reference_file = cmds.referenceQuery(reference_node, filename=True)
    references_before = set(cmds.ls(type="reference") or [])
    new_reference_node = None

    try:
        # Editing an existing reference directly to ':' is illegal in Maya.
        # Creating a new reference in ':' is supported.
        cmds.file(
            reference_file,
            reference=True,
            namespace=":",
            mergeNamespacesOnClash=True,
        )

        references_after = set(cmds.ls(type="reference") or [])
        created_references = list(references_after - references_before)

        if len(created_references) != 1:
            raise RuntimeError(
                "Could not uniquely identify the new root reference."
            )

        new_reference_node = created_references[0]
        new_namespace = cmds.referenceQuery(
            new_reference_node,
            namespace=True,
        )

        if new_namespace != ":":
            raise RuntimeError(
                "The new reference was not created in the root namespace."
            )

        # Verify the new nodes are still referenced before removing the old one.
        new_nodes = cmds.referenceQuery(
            new_reference_node,
            nodes=True,
            dagPath=True,
        ) or []

        if not new_nodes:
            raise RuntimeError("The new root reference contains no nodes.")

        if not all(
            cmds.referenceQuery(node, isNodeReferenced=True)
            for node in new_nodes
            if cmds.objExists(node)
        ):
            raise RuntimeError("Some new nodes are not referenced.")

        old_reference_file = cmds.referenceQuery(
            reference_node,
            filename=True,
        )
        cmds.file(old_reference_file, removeReference=True)

        return new_reference_node

    except Exception:
        # If creation or verification failed, remove only the newly-created
        # reference and leave the original reference untouched.
        if new_reference_node and cmds.objExists(new_reference_node):
            try:
                new_reference_file = cmds.referenceQuery(
                    new_reference_node,
                    filename=True,
                )
                cmds.file(new_reference_file, removeReference=True)
            except Exception:
                pass
        raise


def remove_namespace_from_scene():
    """
    Remove namespaces from selected objects.

    Local nodes are moved to root normally. Top-level references are recreated
    in root so their nodes remain referenced/read-only.
    """
    selected_objects = cmds.ls(
        selection=True,
        objectsOnly=True,
        long=True,
    ) or []

    if not selected_objects:
        cmds.warning("No objects selected.")
        return

    references = {}
    local_namespaces = set()
    untouched_selection = []

    for obj in selected_objects:
        namespace = _get_namespace(obj)

        if not namespace:
            untouched_selection.append(obj)
            continue

        try:
            is_referenced = cmds.referenceQuery(
                obj,
                isNodeReferenced=True,
            )
        except RuntimeError:
            is_referenced = False

        if is_referenced:
            reference_node = cmds.referenceQuery(
                obj,
                referenceNode=True,
            )
            references.setdefault(reference_node, []).append(obj)
        else:
            local_namespaces.add(namespace)

    replacement_selection = []

    cmds.undoInfo(openChunk=True, chunkName="RemoveSelectedNamespaces")
    try:
        for reference_node, selected_reference_nodes in references.items():
            old_namespace = cmds.referenceQuery(
                reference_node,
                namespace=True,
            )

            old_reference_nodes = cmds.referenceQuery(
                reference_node,
                nodes=True,
                dagPath=True,
            ) or []
            old_reference_nodes = [
                (cmds.ls(node, long=True) or [node])[0]
                for node in old_reference_nodes
            ]

            selection_records = []
            for selected_node in selected_reference_nodes:
                selected_long = (
                    cmds.ls(selected_node, long=True) or [selected_node]
                )[0]
                try:
                    node_index = old_reference_nodes.index(selected_long)
                except ValueError:
                    node_index = None

                selection_records.append(
                    (
                        node_index,
                        _base_name(selected_node),
                        cmds.nodeType(selected_node),
                    )
                )

            try:
                new_reference_node = _reference_in_root(reference_node)
                new_nodes = cmds.referenceQuery(
                    new_reference_node,
                    nodes=True,
                    dagPath=True,
                ) or []
                new_nodes = [
                    (cmds.ls(node, long=True) or [node])[0]
                    for node in new_nodes
                ]

                # The node order remains stable when the same file is
                # re-referenced. Index matching also survives automatic
                # renaming caused by root-name clashes.
                for node_index, base_name, node_type in selection_records:
                    if (
                        node_index is not None
                        and node_index < len(new_nodes)
                        and cmds.objExists(new_nodes[node_index])
                        and cmds.nodeType(new_nodes[node_index]) == node_type
                    ):
                        replacement_selection.append(new_nodes[node_index])
                        continue

                    # Fallback for unusual translators that reorder nodes.
                    matches = [
                        node
                        for node in new_nodes
                        if cmds.objExists(node)
                        and _base_name(node) == base_name
                        and cmds.nodeType(node) == node_type
                    ]
                    if matches:
                        replacement_selection.append(matches[0])

                print(
                    "Removed reference namespace {}. "
                    "Nodes remain referenced in root.".format(old_namespace)
                )

            except RuntimeError as error:
                cmds.warning(
                    "Failed to remove reference namespace {}: {}".format(
                        old_namespace,
                        error,
                    )
                )

        for namespace in sorted(
            local_namespaces,
            key=lambda name: name.count(":"),
            reverse=True,
        ):
            if not cmds.namespace(exists=namespace):
                continue

            try:
                cmds.namespace(
                    moveNamespace=(namespace, ":"),
                    force=True,
                )

                if cmds.namespace(exists=namespace):
                    cmds.namespace(removeNamespace=namespace)

                print("Removed local namespace: {}".format(namespace))

            except RuntimeError as error:
                cmds.warning(
                    "Failed to remove local namespace {}: {}".format(
                        namespace,
                        error,
                    )
                )

        valid_selection = [
            node
            for node in untouched_selection + replacement_selection
            if cmds.objExists(node)
        ]

        if valid_selection:
            cmds.select(valid_selection, replace=True)
        else:
            cmds.select(clear=True)

    finally:
        cmds.undoInfo(closeChunk=True)


remove_namespace_from_scene()
