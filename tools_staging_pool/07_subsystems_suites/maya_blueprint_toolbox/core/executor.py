# -*- coding: utf-8 -*-
"""Workflow execution engine for Maya Blueprint Toolbox."""

from ..maya_api import animation, attributes, constraints, export, io, scene_nodes, selection
from ..maya_api.common import MayaApiError


class WorkflowExecutionError(RuntimeError):
    """Raised when a workflow cannot be executed."""


class WorkflowExecutor(object):
    """Executes serialized blueprint workflow data."""

    def __init__(self, node_specs):
        self.node_specs = node_specs

    def execute(self, workflow_data, status_callback=None):
        nodes = workflow_data.get("nodes", [])
        connections = workflow_data.get("connections", [])
        nodes_by_id = dict((node["id"], node) for node in nodes)
        order = self._topological_order(nodes_by_id, connections)
        results = {}

        for node_id in order:
            node_data = nodes_by_id[node_id]
            input_values = self._collect_inputs(node_id, connections, results)
            connected_outputs = self._connected_outputs(node_id, connections)
            self._emit_status(status_callback, node_id, "running", "运行中")
            try:
                outputs = self._execute_node(node_data, input_values, connected_outputs)
            except Exception as error:
                self._emit_status(status_callback, node_id, "failed", str(error))
                raise
            results[node_id] = outputs
            self._emit_status(status_callback, node_id, "success", "成功")

        return results

    def _emit_status(self, status_callback, node_id, status, message):
        if status_callback is not None:
            status_callback(node_id, status, message)

    def _topological_order(self, nodes_by_id, connections):
        dependencies = dict((node_id, set()) for node_id in nodes_by_id)
        dependents = dict((node_id, set()) for node_id in nodes_by_id)

        for connection in connections:
            source_node = connection.get("source_node")
            target_node = connection.get("target_node")
            if source_node not in nodes_by_id or target_node not in nodes_by_id:
                continue
            dependencies[target_node].add(source_node)
            dependents[source_node].add(target_node)

        ready = sorted(node_id for node_id, deps in dependencies.items() if not deps)
        ordered = []

        while ready:
            node_id = ready.pop(0)
            ordered.append(node_id)
            for dependent_id in sorted(dependents[node_id]):
                dependencies[dependent_id].discard(node_id)
                if not dependencies[dependent_id] and dependent_id not in ordered and dependent_id not in ready:
                    ready.append(dependent_id)
            ready.sort()

        if len(ordered) != len(nodes_by_id):
            raise WorkflowExecutionError("Workflow has a cycle or unresolved dependency.")

        return ordered

    def _collect_inputs(self, node_id, connections, results):
        input_values = {}
        for connection in connections:
            if connection.get("target_node") != node_id:
                continue
            source_node = connection.get("source_node")
            source_port = connection.get("source_port")
            target_port = connection.get("target_port")
            source_outputs = results.get(source_node, {})
            input_values[target_port] = source_outputs.get(source_port)
        return input_values

    def _connected_outputs(self, node_id, connections):
        connected = {}
        for connection in connections:
            if connection.get("source_node") == node_id:
                connected[connection.get("source_port")] = True
        return connected

    def _execute_node(self, node_data, input_values, connected_outputs=None):
        node_type = node_data.get("type")
        parameters = node_data.get("parameters", {})
        connected_outputs = connected_outputs or {}

        if node_type == "constant.text":
            return {"value": parameters.get("value", "")}
        if node_type == "constant.number":
            return {"value": float(parameters.get("value", 0.0) or 0.0)}
        if node_type == "constant.bool":
            return {"value": bool(parameters.get("value", False))}
        if node_type == "constant.path":
            return {"value": parameters.get("value", "")}
        if node_type == "maya.nodes.node_names":
            return self._execute_node_names(parameters)
        if node_type == "maya.nodes.by_type":
            return self._execute_nodes_by_type(parameters)
        if node_type == "maya.nodes.skin_cluster":
            return self._execute_related_nodes(input_values, scene_nodes.related_skin_clusters)
        if node_type == "maya.nodes.blend_shape":
            return self._execute_related_nodes(input_values, scene_nodes.related_blend_shapes)
        if node_type == "maya.nodes.deformers":
            return self._execute_related_nodes(input_values, scene_nodes.related_deformers)
        if node_type == "maya.nodes.materials":
            return self._execute_materials(input_values)
        if node_type == "maya.nodes.constraints":
            return self._execute_constraints_lookup(input_values)
        if node_type == "maya.selection.current":
            return self._execute_current_selection(parameters)
        if node_type == "maya.timeline.current_frame":
            return self._execute_current_frame(input_values)
        if node_type == "maya.timeline.frame_range":
            return self._execute_frame_range(parameters, input_values)
        if node_type == "maya.channels.selected_channel_box":
            return self._execute_selected_channel_box(parameters)
        if node_type == "maya.selection.select_nodes":
            return self._execute_select_nodes(input_values)
        if node_type == "maya.animation.copy_frame":
            return self._execute_copy_frame(parameters, input_values, connected_outputs)
        if node_type == "maya.nodes.rename":
            return self._execute_rename_nodes(parameters, input_values)
        if node_type == "maya.nodes.group":
            return self._execute_group_nodes(parameters, input_values)
        if node_type == "maya.nodes.delete":
            return self._execute_delete_nodes(input_values)
        if node_type == "maya.attributes.make_ref":
            return self._execute_make_attribute_refs(parameters, input_values)
        if node_type == "animation.channels.transform_defaults":
            return self._execute_transform_channels(parameters, input_values)
        if node_type == "transform.node_list.merge":
            return self._execute_merge_node_lists(input_values)
        if node_type == "transform.node_list.unique":
            return self._execute_unique_node_list(input_values)
        if node_type == "transform.node_list.sort_by_name":
            return self._execute_sort_node_list_by_name(parameters, input_values)
        if node_type == "transform.node_list.reverse":
            return self._execute_reverse_node_list(input_values)
        if node_type == "transform.node_list.sort_by_hierarchy":
            return self._execute_sort_node_list_by_hierarchy(parameters, input_values)
        if node_type == "transform.node_list.filter_by_name":
            return self._execute_filter_node_list_by_name(parameters, input_values)
        if node_type == "transform.node_list.get_item":
            return self._execute_get_node_list_item(input_values)
        if node_type == "transform.node_list.count":
            return self._execute_node_list_count(input_values)
        if node_type == "transform.attr_list.merge":
            return self._execute_merge_attr_lists(input_values)
        if node_type == "transform.attr_list.unique":
            return self._execute_unique_attr_list(input_values)
        if node_type == "transform.attr_list.filter_by_name":
            return self._execute_filter_attr_list_by_name(parameters, input_values)
        if node_type == "transform.attr_list.get_item":
            return self._execute_get_attr_list_item(input_values)
        if node_type == "transform.attr_list.count":
            return self._execute_attr_list_count(input_values)
        if node_type == "maya.attributes.inspect":
            return self._execute_inspect_attributes(input_values)
        if node_type == "debug.print_result":
            return self._execute_print_result(parameters, input_values)
        if node_type == "maya.attributes.set":
            return self._execute_set_attribute(parameters, input_values)
        if node_type == "maya.attributes.get":
            return self._execute_get_attribute(parameters, input_values)
        if node_type.startswith("maya.constraints."):
            return self._execute_constraint(node_type, parameters, input_values)
        if node_type == "maya.io.import_file":
            return self._execute_import_file(parameters, input_values)
        if node_type == "maya.io.export_fbx":
            return self._execute_export_fbx(parameters, input_values)

        raise WorkflowExecutionError("No executor registered for node type: {0}".format(node_type))

    def _execute_node_names(self, parameters):
        return {"nodes": scene_nodes.parse_node_names(parameters.get("names", []))}

    def _execute_nodes_by_type(self, parameters):
        try:
            nodes = scene_nodes.nodes_by_type(
                parameters.get("maya_type", ""),
                shape_result=parameters.get("shape_result", "original"),
                long_name=bool(parameters.get("long_name", True)),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"nodes": nodes}

    def _execute_related_nodes(self, input_values, command):
        nodes = input_values.get("nodes") or []
        try:
            related_nodes = command(nodes)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"nodes": related_nodes}

    def _execute_materials(self, input_values):
        nodes = input_values.get("nodes") or []
        try:
            materials = scene_nodes.related_materials(nodes)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"materials": materials}

    def _execute_constraints_lookup(self, input_values):
        nodes = input_values.get("nodes") or []
        try:
            related_constraints = scene_nodes.related_constraints(nodes)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"constraints": related_constraints}

    def _execute_current_selection(self, parameters):
        include_shapes = bool(parameters.get("include_shapes", False))
        try:
            nodes = selection.get_current_selection(include_shapes=include_shapes)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"nodes": nodes}

    def _execute_current_frame(self, input_values):
        frame_value = input_values.get("frame")
        try:
            frames = animation.current_frame(frame_value)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"frames": frames}

    def _execute_frame_range(self, parameters, input_values):
        try:
            frame_range, frames = animation.frame_range(
                start_frame=input_values.get("start_frame"),
                end_frame=input_values.get("end_frame"),
                include_end=bool(parameters.get("include_end", True)),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {
            "frame_range": frame_range,
            "frames": frames,
        }

    def _execute_selected_channel_box(self, parameters):
        try:
            channels = animation.selected_channel_box_channels(
                default_transform=bool(parameters.get("default_transform", True)),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"channels": channels}

    def _execute_select_nodes(self, input_values):
        nodes = input_values.get("nodes") or []
        try:
            selected_nodes = scene_nodes.select_nodes(nodes)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {
            "selected_nodes": selected_nodes,
            "done": True,
        }

    def _execute_rename_nodes(self, parameters, input_values):
        nodes = input_values.get("nodes") or []
        try:
            renamed_nodes = scene_nodes.rename_nodes(
                nodes,
                parameters.get("base_name", ""),
                start_index=parameters.get("start_index", 1.0),
                padding=parameters.get("padding", 2.0),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"renamed_nodes": renamed_nodes}

    def _execute_group_nodes(self, parameters, input_values):
        nodes = input_values.get("nodes") or []
        try:
            group_node = scene_nodes.group_nodes(
                nodes,
                parameters.get("group_name", ""),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"group_node": group_node}

    def _execute_delete_nodes(self, input_values):
        nodes = input_values.get("nodes") or []
        try:
            done = scene_nodes.delete_nodes(nodes)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"done": done}

    def _execute_copy_frame(self, parameters, input_values, connected_outputs):
        nodes = input_values.get("nodes") or []
        frames = input_values.get("frames")
        channels = input_values.get("channels")
        save_json = (
            not connected_outputs.get("frame_data")
            and bool(parameters.get("save_json_when_unconnected", True))
        )
        try:
            frame_data = animation.copy_frame(
                nodes,
                frames,
                paste_channels=channels,
                save_json=save_json,
                json_path=parameters.get("json_path", ""),
                record_short_name=bool(parameters.get("record_short_name", True)),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"frame_data": frame_data}

    def _execute_set_attribute(self, parameters, input_values):
        value = input_values.get("value")
        value_type = parameters.get("value_type", "auto")

        if input_values.get("attrs"):
            try:
                changed_attrs = attributes.set_attribute_refs(
                    input_values.get("attrs"),
                    value,
                    value_type=value_type,
                )
            except MayaApiError as error:
                raise WorkflowExecutionError(str(error))
            return {
                "done": True,
            }

        raise WorkflowExecutionError("设置属性需要连接 属性引用 输入。")

    def _execute_get_attribute(self, parameters, input_values):
        if input_values.get("attrs"):
            try:
                value = attributes.get_attribute_refs(input_values.get("attrs"))
            except MayaApiError as error:
                raise WorkflowExecutionError(str(error))
            return {"value": value}

        raise WorkflowExecutionError("获取属性需要连接 属性引用 输入。")

    def _execute_make_attribute_refs(self, parameters, input_values):
        nodes = input_values.get("nodes") or []
        attribute_items = parameters.get("attribute_items")
        if attribute_items is None:
            attribute_items = parameters.get("attribute", "")
        try:
            attr_refs = attributes.make_attribute_refs_from_items(nodes, attribute_items)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {"attrs": attr_refs}

    def _execute_transform_channels(self, parameters, input_values):
        translate_enabled = input_values.get("translate_enabled")
        if translate_enabled is None:
            translate_enabled = parameters.get("default_translate", True)

        rotate_enabled = input_values.get("rotate_enabled")
        if rotate_enabled is None:
            rotate_enabled = parameters.get("default_rotate", True)

        scale_enabled = input_values.get("scale_enabled")
        if scale_enabled is None:
            scale_enabled = parameters.get("default_scale", False)

        channels = animation.transform_channels(
            include_translate=bool(translate_enabled),
            include_rotate=bool(rotate_enabled),
            include_scale=bool(scale_enabled),
        )
        return {"channels": channels}

    def _execute_merge_node_lists(self, input_values):
        nodes = self._as_list(input_values.get("nodes_a")) + self._as_list(input_values.get("nodes_b"))
        return {"nodes": nodes}

    def _execute_unique_node_list(self, input_values):
        return {"nodes": self._unique_items(self._as_list(input_values.get("nodes")))}

    def _execute_sort_node_list_by_name(self, parameters, input_values):
        nodes = self._as_list(input_values.get("nodes"))
        name_scope = parameters.get("name_scope", "short")
        case_sensitive = bool(parameters.get("case_sensitive", False))
        descending = bool(parameters.get("descending", False))

        sorted_nodes = sorted(
            nodes,
            key=lambda node: self._node_sort_text(node, name_scope, case_sensitive),
            reverse=descending,
        )
        return {"nodes": sorted_nodes}

    def _execute_reverse_node_list(self, input_values):
        nodes = self._as_list(input_values.get("nodes"))
        nodes.reverse()
        return {"nodes": nodes}

    def _execute_sort_node_list_by_hierarchy(self, parameters, input_values):
        nodes = self._as_list(input_values.get("nodes"))
        parent_first = bool(parameters.get("parent_first", True))
        sorted_nodes = sorted(
            nodes,
            key=lambda node: (str(node).count("|"), str(node)),
            reverse=not parent_first,
        )
        return {"nodes": sorted_nodes}

    def _execute_filter_node_list_by_name(self, parameters, input_values):
        nodes = self._as_list(input_values.get("nodes"))
        pattern = input_values.get("pattern") or ""
        match_mode = parameters.get("match_mode", "contains")
        case_sensitive = bool(parameters.get("case_sensitive", False))

        matched_nodes = []
        unmatched_nodes = []
        for node in nodes:
            if self._item_text_matches(node, pattern, match_mode, case_sensitive):
                matched_nodes.append(node)
            else:
                unmatched_nodes.append(node)

        return {
            "matched_nodes": matched_nodes,
            "unmatched_nodes": unmatched_nodes,
        }

    def _execute_get_node_list_item(self, input_values):
        nodes = self._as_list(input_values.get("nodes"))
        index = int(float(input_values.get("index") or 0))
        if 0 <= index < len(nodes):
            return {"nodes": [nodes[index]]}
        return {"nodes": []}

    def _execute_node_list_count(self, input_values):
        nodes = self._as_list(input_values.get("nodes"))
        return {"count": float(len(nodes))}

    def _execute_merge_attr_lists(self, input_values):
        attrs = self._as_list(input_values.get("attrs_a")) + self._as_list(input_values.get("attrs_b"))
        return {"attrs": attrs}

    def _execute_unique_attr_list(self, input_values):
        return {"attrs": self._unique_items(self._as_list(input_values.get("attrs")))}

    def _execute_filter_attr_list_by_name(self, parameters, input_values):
        attrs = self._as_list(input_values.get("attrs"))
        pattern = input_values.get("pattern") or ""
        match_mode = parameters.get("match_mode", "contains")
        case_sensitive = bool(parameters.get("case_sensitive", False))

        matched_attrs = []
        unmatched_attrs = []
        for attr in attrs:
            if self._item_text_matches(attr, pattern, match_mode, case_sensitive):
                matched_attrs.append(attr)
            else:
                unmatched_attrs.append(attr)

        return {
            "matched_attrs": matched_attrs,
            "unmatched_attrs": unmatched_attrs,
        }

    def _execute_get_attr_list_item(self, input_values):
        attrs = self._as_list(input_values.get("attrs"))
        index = int(float(input_values.get("index") or 0))
        if 0 <= index < len(attrs):
            return {"attrs": [attrs[index]]}
        return {"attrs": []}

    def _execute_attr_list_count(self, input_values):
        attrs = self._as_list(input_values.get("attrs"))
        return {"count": float(len(attrs))}

    def _item_text_matches(self, item, pattern, match_mode, case_sensitive):
        if pattern is None or pattern == "":
            return True

        item_text_candidates = self._item_text_candidates(item)
        pattern_text = str(pattern)

        if not case_sensitive:
            item_text_candidates = [text.lower() for text in item_text_candidates]
            pattern_text = pattern_text.lower()

        for item_text in item_text_candidates:
            if self._text_matches(item_text, pattern_text, match_mode):
                return True
        return False

    def _text_matches(self, item_text, pattern_text, match_mode):
        if match_mode == "prefix":
            return item_text.startswith(pattern_text)
        if match_mode == "suffix":
            return item_text.endswith(pattern_text)
        if match_mode == "exact":
            return item_text == pattern_text
        return pattern_text in item_text

    def _item_text_candidates(self, item):
        if hasattr(item, "full_attr"):
            return [item.full_attr, item.attr]
        if hasattr(item, "name"):
            text = item.name
        else:
            text = str(item)
        return [text, text.rsplit("|", 1)[-1]]

    def _node_sort_text(self, node, name_scope, case_sensitive):
        text = str(node)
        if name_scope == "short":
            text = text.rsplit("|", 1)[-1]
        if not case_sensitive:
            text = text.lower()
        return text

    def _as_list(self, value):
        if value is None:
            return []
        if isinstance(value, (list, tuple)):
            return list(value)
        return [value]

    def _unique_items(self, items):
        result = []
        seen = set()
        for item in items or []:
            key = self._item_key(item)
            if key not in seen:
                result.append(item)
                seen.add(key)
        return result

    def _item_key(self, item):
        if hasattr(item, "full_attr"):
            return item.full_attr
        if hasattr(item, "name"):
            return item.name
        return str(item)

    def _execute_inspect_attributes(self, input_values):
        attr_refs = input_values.get("attrs")
        try:
            packets = attributes.inspect_attributes(attr_refs)
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))

        values = [packet.value for packet in packets]
        return {
            "value": values[0] if len(values) == 1 else values,
            "report": attributes.packets_report(packets),
        }

    def _execute_print_result(self, parameters, input_values):
        label = parameters.get("label") or "打印结果"
        value = input_values.get("input")
        formatted_value = self._format_debug_value(value)
        print("Maya Blueprint {0}:".format(label))
        print(formatted_value)
        return {
            "display": formatted_value,
            "done": True,
        }

    def _format_debug_value(self, value, indent=0):
        prefix = " " * indent
        if hasattr(value, "to_dict"):
            return self._format_debug_value(value.to_dict(), indent=indent)
        if isinstance(value, dict):
            if not value:
                return "{}"
            lines = ["{"]
            for key in sorted(value.keys()):
                lines.append(
                    "{0}  {1}: {2}".format(
                        prefix,
                        key,
                        self._format_debug_value(value[key], indent=indent + 2),
                    )
                )
            lines.append("{0}}}".format(prefix))
            return "\n".join(lines)
        if isinstance(value, (list, tuple)):
            if not value:
                return "[]"
            lines = ["["]
            for index, item in enumerate(value):
                lines.append(
                    "{0}  {1}: {2}".format(
                        prefix,
                        index,
                        self._format_debug_value(item, indent=indent + 2),
                    )
                )
            lines.append("{0}]".format(prefix))
            return "\n".join(lines)
        return repr(value)

    def _execute_constraint(self, node_type, parameters, input_values):
        drivers = input_values.get("drivers") or []
        driven = input_values.get("driven") or []
        constraint_type = node_type.rsplit(".", 1)[-1]
        try:
            created_constraints = constraints.create_constraint(
                constraint_type,
                drivers,
                driven,
                maintain_offset=parameters.get("maintain_offset", True),
                weight=parameters.get("weight", 1.0),
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))
        return {
            "constraints": created_constraints,
            "done": True,
        }

    def _execute_import_file(self, parameters, input_values):
        file_path = input_values.get("file_path")
        if not file_path:
            raise WorkflowExecutionError("Import File requires file_path input.")

        mode = parameters.get("mode", "import")
        namespace = parameters.get("namespace", "")
        preserve_references = bool(parameters.get("preserve_references", True))

        try:
            imported_nodes = io.import_file(
                file_path,
                mode=mode,
                namespace=namespace,
                preserve_references=preserve_references,
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))

        return {
            "imported_nodes": imported_nodes,
            "done": True,
        }

    def _execute_export_fbx(self, parameters, input_values):
        nodes = input_values.get("nodes") or []
        target_path = input_values.get("target_path")
        if not nodes:
            raise WorkflowExecutionError("Export FBX requires nodes input.")
        if not target_path:
            raise WorkflowExecutionError("Export FBX requires target_path input.")

        overwrite_existing = bool(parameters.get("overwrite_existing", False))
        bake_animation = bool(parameters.get("bake_animation", False))
        frame_start = float(parameters.get("frame_start", 1.0))
        frame_end = float(parameters.get("frame_end", 120.0))

        try:
            result_path = export.export_fbx(
                nodes,
                target_path,
                bake_animation=bake_animation,
                frame_start=frame_start,
                frame_end=frame_end,
                overwrite_existing=overwrite_existing,
            )
        except MayaApiError as error:
            raise WorkflowExecutionError(str(error))

        return {"result": result_path}
