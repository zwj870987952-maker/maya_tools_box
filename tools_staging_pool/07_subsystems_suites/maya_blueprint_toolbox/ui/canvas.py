# -*- coding: utf-8 -*-
"""Node canvas widgets for Maya Blueprint Toolbox."""

import json

from ..core.executor import WorkflowExecutionError, WorkflowExecutor
from ..core.node_specs import default_node_specs
from ..core.types import canonical_port_type, port_types_compatible
from ..maya_api import attributes, selection
from ..maya_api.common import MayaApiError
from ..qt_compat import QtCore, QtGui, QtWidgets, qt_enum


PORT_RADIUS = 6
NODE_WIDTH = 220
NODE_HEADER_HEIGHT = 34
NODE_ROW_HEIGHT = 26


class PortGraphicsItem(QtWidgets.QGraphicsEllipseItem):
    """A typed input or output socket on a node."""

    def __init__(self, node_item, port_spec, direction, index):
        super(PortGraphicsItem, self).__init__(
            -PORT_RADIUS,
            -PORT_RADIUS,
            PORT_RADIUS * 2,
            PORT_RADIUS * 2,
            node_item,
        )
        self.node_item = node_item
        self.name = port_spec.name
        self.label = port_spec.label
        self.port_type = port_spec.port_type
        self.required = port_spec.required
        self.direction = direction
        self.index = index
        self.connections = []

        self.setBrush(QtGui.QBrush(self._color_for_type(self.port_type)))
        self.setPen(QtGui.QPen(QtGui.QColor("#1b1f24"), 1.0))
        self.setAcceptHoverEvents(True)
        self.setToolTip("{0}: {1}".format(self.label, self.port_type))

    def type_color(self):
        return self._color_for_type(self.port_type)

    def _color_for_type(self, port_type):
        port_type = canonical_port_type(port_type)
        colors = {
            "ANY": "#bfc7d5",
            "EXEC": "#f2c94c",
            "STRING": "#56ccf2",
            "PATH": "#6fcf97",
            "NUMBER": "#bb6bd9",
            "BOOL": "#f2994a",
            "VALUE": "#d0a8ff",
            "NODE_REF": "#2d9cdb",
            "NODE_LIST": "#2d9cdb",
            "ATTR_REF": "#f2994a",
            "ATTR_LIST": "#f2994a",
            "ATTR_PACKET": "#eb5757",
            "FRAME_RANGE": "#f2c94c",
            "FRAME_LIST": "#f2c94c",
            "CHANNEL_LIST": "#f2994a",
            "TRANSFORM_FRAME_DATA": "#d0a8ff",
            "ANIM_REPORT": "#7fb069",
            "FILE_RESULT": "#27ae60",
        }
        return QtGui.QColor(colors.get(port_type, "#bfc7d5"))

    def center_scene_pos(self):
        return self.mapToScene(self.rect().center())

    def mousePressEvent(self, event):
        if event.button() == qt_enum(
            (QtCore.Qt, "MouseButton.LeftButton"),
            (QtCore.Qt, "LeftButton"),
        ):
            self.scene().begin_connection(self)
            event.accept()
            return
        super(PortGraphicsItem, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.scene().update_pending_connection(event.scenePos())
        event.accept()

    def mouseReleaseEvent(self, event):
        self.scene().finish_connection_at(event.scenePos())
        event.accept()


class ConnectionGraphicsItem(QtWidgets.QGraphicsPathItem):
    """Bezier connection between two ports."""

    def __init__(self, source_port=None, target_port=None):
        super(ConnectionGraphicsItem, self).__init__()
        self.source_port = source_port
        self.target_port = target_port
        self.pending_end = None
        self.setZValue(-1)
        self.setPen(QtGui.QPen(self._connection_color(), 2.0))
        self.setFlag(
            qt_enum(
                (QtWidgets.QGraphicsItem, "GraphicsItemFlag.ItemIsSelectable"),
                (QtWidgets.QGraphicsItem, "ItemIsSelectable"),
            ),
            True,
        )

    def _connection_color(self):
        if self.source_port is not None:
            return self.source_port.type_color()
        return QtGui.QColor("#8da2bf")

    def set_pending_end(self, scene_pos):
        self.pending_end = scene_pos
        self.update_path()

    def update_path(self):
        if self.source_port is None:
            return

        start = self.source_port.center_scene_pos()
        if self.target_port is not None:
            end = self.target_port.center_scene_pos()
        elif self.pending_end is not None:
            end = self.pending_end
        else:
            end = start

        distance = max(60, abs(end.x() - start.x()) * 0.5)
        control_1 = QtCore.QPointF(start.x() + distance, start.y())
        control_2 = QtCore.QPointF(end.x() - distance, end.y())

        path = QtGui.QPainterPath(start)
        path.cubicTo(control_1, control_2, end)
        self.setPath(path)

    def serialize(self):
        return {
            "source_node": self.source_port.node_item.node_id,
            "source_port": self.source_port.name,
            "target_node": self.target_port.node_item.node_id,
            "target_port": self.target_port.name,
        }


class NodeGraphicsItem(QtWidgets.QGraphicsRectItem):
    """A movable node instance created from a NodeSpec."""

    def __init__(self, node_id, node_spec, parameters=None):
        self.node_id = node_id
        self.node_spec = node_spec
        self.parameters = node_spec.default_parameters()
        self.parameters.update(parameters or {})
        self._migrate_legacy_parameters()
        self.input_ports = []
        self.output_ports = []
        self.status = "idle"
        self.status_text_item = None
        self.last_result_text = ""

        height = NODE_HEADER_HEIGHT + max(len(node_spec.inputs), len(node_spec.outputs), 1) * NODE_ROW_HEIGHT + 14
        super(NodeGraphicsItem, self).__init__(0, 0, NODE_WIDTH, height)

        self.setBrush(QtGui.QBrush(QtGui.QColor("#262b33")))
        self.setPen(QtGui.QPen(QtGui.QColor("#465061"), 1.0))
        self.setFlag(
            qt_enum(
                (QtWidgets.QGraphicsItem, "GraphicsItemFlag.ItemIsMovable"),
                (QtWidgets.QGraphicsItem, "ItemIsMovable"),
            ),
            True,
        )
        self.setFlag(
            qt_enum(
                (QtWidgets.QGraphicsItem, "GraphicsItemFlag.ItemIsSelectable"),
                (QtWidgets.QGraphicsItem, "ItemIsSelectable"),
            ),
            True,
        )
        self.setFlag(
            qt_enum(
                (QtWidgets.QGraphicsItem, "GraphicsItemFlag.ItemSendsGeometryChanges"),
                (QtWidgets.QGraphicsItem, "ItemSendsGeometryChanges"),
            ),
            True,
        )

        self._build_visuals()
        self.set_status("idle")

    def _migrate_legacy_parameters(self):
        if self.node_spec.node_type == "maya.attributes.make_ref":
            legacy_attribute = self.parameters.get("attribute")
            attribute_items = self.parameters.get("attribute_items")
            if legacy_attribute and not attribute_items:
                self.parameters["attribute_items"] = [legacy_attribute]

    def _build_visuals(self):
        no_button = qt_enum(
            (QtCore.Qt, "MouseButton.NoButton"),
            (QtCore.Qt, "NoButton"),
        )

        header = QtWidgets.QGraphicsRectItem(0, 0, NODE_WIDTH, NODE_HEADER_HEIGHT, self)
        header_color = QtGui.QColor(self.node_spec.class_color())
        header.setBrush(QtGui.QBrush(header_color))
        header.setPen(QtGui.QPen(header_color, 0))
        header.setZValue(1)

        self._create_text_item(
            self.node_spec.title,
            QtCore.QPointF(12, 8),
            "#f4f7fb",
            no_button,
            font_size=10,
            bold=True,
        )

        for index, port_spec in enumerate(self.node_spec.inputs):
            port = PortGraphicsItem(self, port_spec, "input", index)
            y_pos = NODE_HEADER_HEIGHT + 14 + index * NODE_ROW_HEIGHT
            port.setPos(0, y_pos)
            self.input_ports.append(port)

            self._create_text_item(
                port_spec.label,
                QtCore.QPointF(16, y_pos - 8),
                "#d7dfec",
                no_button,
            )

        for index, port_spec in enumerate(self.node_spec.outputs):
            port = PortGraphicsItem(self, port_spec, "output", index)
            y_pos = NODE_HEADER_HEIGHT + 14 + index * NODE_ROW_HEIGHT
            port.setPos(NODE_WIDTH, y_pos)
            self.output_ports.append(port)

            label = self._create_text_item(
                port_spec.label,
                QtCore.QPointF(0, y_pos - 8),
                "#d7dfec",
                no_button,
            )
            label_width = label.boundingRect().width()
            label.setPos(NODE_WIDTH - label_width - 16, y_pos - 8)

        self.status_text_item = self._create_text_item(
            "",
            QtCore.QPointF(NODE_WIDTH - 42, 9),
            "#aeb8c8",
            no_button,
            font_size=8,
            bold=True,
        )

    def _create_text_item(self, text, position, color, accepted_buttons, font_size=9, bold=False):
        text_item = QtWidgets.QGraphicsSimpleTextItem(text, self)
        font = QtGui.QFont()
        font.setPointSize(font_size)
        font.setBold(bold)
        text_item.setFont(font)
        text_item.setBrush(QtGui.QBrush(QtGui.QColor(color)))
        text_item.setPos(position)
        text_item.setZValue(3)
        text_item.setAcceptedMouseButtons(accepted_buttons)
        return text_item

    def itemChange(self, change, value):
        position_change = qt_enum(
            (QtWidgets.QGraphicsItem, "GraphicsItemChange.ItemPositionHasChanged"),
            (QtWidgets.QGraphicsItem, "ItemPositionHasChanged"),
        )
        if change == position_change:
            for port in self.input_ports + self.output_ports:
                for connection in port.connections:
                    connection.update_path()
        return super(NodeGraphicsItem, self).itemChange(change, value)

    def port_by_name(self, direction, name):
        ports = self.input_ports if direction == "input" else self.output_ports
        for port in ports:
            if port.name == name:
                return port
        return None

    def set_parameter(self, name, value):
        self.parameters[name] = value

    def set_status(self, status, message=""):
        self.status = status
        color = self._status_color(status)
        self.setPen(QtGui.QPen(QtGui.QColor(color), 2.0))
        self.setToolTip(message or status)

        if self.status_text_item is not None:
            label = self._status_label(status)
            self.status_text_item.setText(label)
            self.status_text_item.setBrush(QtGui.QBrush(QtGui.QColor(color)))
            label_width = self.status_text_item.boundingRect().width()
            self.status_text_item.setPos(NODE_WIDTH - label_width - 12, 9)

    def _status_color(self, status):
        colors = {
            "idle": "#465061",
            "running": "#f2c94c",
            "success": "#27ae60",
            "failed": "#eb5757",
            "skipped": "#8b95a5",
        }
        return colors.get(status, "#465061")

    def _status_label(self, status):
        labels = {
            "idle": "待机",
            "running": "运行",
            "success": "完成",
            "failed": "错误",
            "skipped": "跳过",
        }
        return labels.get(status, status.upper())

    def clear_runtime_result(self):
        self.last_result_text = ""

    def set_runtime_result(self, outputs):
        if self.node_spec.node_type == "debug.print_result":
            self.last_result_text = str((outputs or {}).get("display", ""))

    def serialize(self):
        return {
            "id": self.node_id,
            "type": self.node_spec.node_type,
            "title": self.node_spec.title,
            "position": [self.pos().x(), self.pos().y()],
            "parameters": dict(self.parameters),
        }


class BlueprintGraphicsScene(QtWidgets.QGraphicsScene):
    """Graphics scene that owns nodes and connections."""

    def __init__(self, node_specs, parent=None):
        super(BlueprintGraphicsScene, self).__init__(parent)
        self.node_specs = node_specs
        self.pending_connection = None
        self.nodes_by_id = {}
        self.setSceneRect(-4000, -4000, 8000, 8000)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("#15191f")))

    def add_node_type(self, node_type, position=None, node_id=None, parameters=None):
        node_spec = self.node_specs[node_type]
        resolved_id = node_id or self._next_node_id(node_spec.node_type.rsplit(".", 1)[-1])
        node_item = NodeGraphicsItem(resolved_id, node_spec, parameters=parameters)
        self.addItem(node_item)
        node_item.setPos(position or QtCore.QPointF(0, 0))
        self.nodes_by_id[resolved_id] = node_item
        return node_item

    def begin_connection(self, port):
        if port.direction != "output":
            return
        self.pending_connection = ConnectionGraphicsItem(source_port=port)
        self.addItem(self.pending_connection)
        self.pending_connection.set_pending_end(port.center_scene_pos())

    def update_pending_connection(self, scene_pos):
        if self.pending_connection is not None:
            self.pending_connection.set_pending_end(scene_pos)

    def finish_connection(self, port):
        if self.pending_connection is None:
            return

        source_port = self.pending_connection.source_port
        if self._can_connect(source_port, port):
            self.pending_connection.target_port = port
            self.pending_connection.pending_end = None
            self.pending_connection.update_path()
            source_port.connections.append(self.pending_connection)
            port.connections.append(self.pending_connection)
        else:
            self.removeItem(self.pending_connection)

        self.pending_connection = None

    def finish_connection_at(self, scene_pos):
        target_port = None
        for item in self.items(scene_pos):
            if isinstance(item, PortGraphicsItem):
                if self.pending_connection is not None and item is not self.pending_connection.source_port:
                    target_port = item
                    break
        self.finish_connection(target_port)

    def delete_selected_items(self):
        for item in list(self.selectedItems()):
            if isinstance(item, ConnectionGraphicsItem):
                self.remove_connection(item)
            elif isinstance(item, NodeGraphicsItem):
                self.remove_node(item)

    def remove_node(self, node_item):
        for port in node_item.input_ports + node_item.output_ports:
            for connection in list(port.connections):
                self.remove_connection(connection)
        self.nodes_by_id.pop(node_item.node_id, None)
        self.removeItem(node_item)

    def remove_connection(self, connection):
        for port in (connection.source_port, connection.target_port):
            if port is not None and connection in port.connections:
                port.connections.remove(connection)
        self.removeItem(connection)

    def clear_workflow(self):
        self.clear()
        self.pending_connection = None
        self.nodes_by_id = {}

    def _can_connect(self, source_port, target_port):
        if source_port is None or target_port is None:
            return False
        if source_port.direction != "output" or target_port.direction != "input":
            return False
        if source_port.node_item is target_port.node_item:
            return False
        return port_types_compatible(source_port.port_type, target_port.port_type)

    def _next_node_id(self, title):
        slug = "".join(ch.lower() if ch.isalnum() else "_" for ch in title).strip("_")
        slug = slug or "node"
        index = 1
        node_id = "{0}_{1}".format(slug, index)
        while node_id in self.nodes_by_id:
            index += 1
            node_id = "{0}_{1}".format(slug, index)
        return node_id

    def serialize(self):
        nodes = []
        connections = []
        for item in self.items():
            if isinstance(item, NodeGraphicsItem):
                nodes.append(item.serialize())
            elif isinstance(item, ConnectionGraphicsItem) and item.target_port is not None:
                connections.append(item.serialize())
        nodes.sort(key=lambda node_data: node_data["id"])
        return {
            "version": 1,
            "nodes": nodes,
            "connections": connections,
        }

    def serialize_for_node_ids(self, target_node_ids):
        included_node_ids = self._upstream_node_ids(set(target_node_ids or []))
        nodes = []
        connections = []
        for item in self.items():
            if isinstance(item, NodeGraphicsItem) and item.node_id in included_node_ids:
                nodes.append(item.serialize())
            elif isinstance(item, ConnectionGraphicsItem) and item.target_port is not None:
                connection_data = item.serialize()
                if (
                    connection_data["source_node"] in included_node_ids
                    and connection_data["target_node"] in included_node_ids
                ):
                    connections.append(connection_data)
        nodes.sort(key=lambda node_data: node_data["id"])
        return {
            "version": 1,
            "nodes": nodes,
            "connections": connections,
        }

    def selected_node_ids(self):
        node_ids = []
        for item in self.selectedItems():
            if isinstance(item, NodeGraphicsItem):
                node_ids.append(item.node_id)
        return node_ids

    def mark_skipped_except(self, included_node_ids):
        included_node_ids = set(included_node_ids or [])
        for node_id, node_item in self.nodes_by_id.items():
            if node_id not in included_node_ids:
                node_item.set_status("skipped", "选中运行时跳过")

    def load_workflow(self, data):
        self.clear_workflow()
        for node_data in data.get("nodes", []):
            node_type = node_data.get("type")
            if node_type not in self.node_specs:
                continue
            position_data = node_data.get("position", [0, 0])
            position = QtCore.QPointF(float(position_data[0]), float(position_data[1]))
            self.add_node_type(
                node_type,
                position=position,
                node_id=node_data.get("id"),
                parameters=node_data.get("parameters", {}),
            )

        for connection_data in data.get("connections", []):
            source_node = self.nodes_by_id.get(connection_data.get("source_node"))
            target_node = self.nodes_by_id.get(connection_data.get("target_node"))
            if source_node is None or target_node is None:
                continue
            source_port = source_node.port_by_name("output", connection_data.get("source_port"))
            target_port = target_node.port_by_name("input", connection_data.get("target_port"))
            if self._can_connect(source_port, target_port):
                connection = ConnectionGraphicsItem(source_port, target_port)
                self.addItem(connection)
                connection.update_path()
                source_port.connections.append(connection)
                target_port.connections.append(connection)

    def validate_workflow(self, workflow_data=None):
        issues = []
        if workflow_data is None:
            node_ids = set(self.nodes_by_id.keys())
            connections = self.serialize()["connections"]
        else:
            node_ids = set(node_data["id"] for node_data in workflow_data.get("nodes", []))
            connections = workflow_data.get("connections", [])

        for node_id in sorted(node_ids):
            node_item = self.nodes_by_id.get(node_id)
            if node_item is None:
                continue
            for parameter_spec in node_item.node_spec.parameters:
                value = node_item.parameters.get(parameter_spec.name)
                if parameter_spec.required and self._is_missing_required_parameter(value):
                    issues.append(
                        "{0}.{1} 是必填参数。".format(node_item.node_id, parameter_spec.label)
                    )
            for port in node_item.input_ports:
                if port.required and not self._workflow_has_input_connection(connections, node_item.node_id, port.name):
                    issues.append(
                        "{0}.{1} 输入未连接。".format(node_item.node_id, port.label)
                    )
            if self._make_ref_needs_node_input(node_item) and not self._workflow_has_input_connection(
                connections,
                node_item.node_id,
                "nodes",
            ):
                issues.append("{0}.属性名需要连接 节点 输入。".format(node_item.node_id))
        return issues

    def _is_missing_required_parameter(self, value):
        if value is None:
            return True
        if value == "":
            return True
        if isinstance(value, (list, tuple)) and not value:
            return True
        return False

    def reset_node_statuses(self):
        for node_item in self.nodes_by_id.values():
            node_item.set_status("idle")
            node_item.clear_runtime_result()

    def set_node_status(self, node_id, status, message=""):
        node_item = self.nodes_by_id.get(node_id)
        if node_item is not None:
            node_item.set_status(status, message)

    def set_node_results(self, results):
        for node_id, outputs in (results or {}).items():
            node_item = self.nodes_by_id.get(node_id)
            if node_item is not None:
                node_item.set_runtime_result(outputs)

    def _workflow_has_input_connection(self, connections, node_id, port_name):
        for connection in connections:
            if connection.get("target_node") == node_id and connection.get("target_port") == port_name:
                return True
        return False

    def _make_ref_needs_node_input(self, node_item):
        if node_item.node_spec.node_type != "maya.attributes.make_ref":
            return False
        attribute_items = node_item.parameters.get("attribute_items")
        if attribute_items is None:
            attribute_items = node_item.parameters.get("attribute", "")
        for item in self._parameter_items(attribute_items):
            if "." not in item:
                return True
        return False

    def _parameter_items(self, value):
        if not value:
            return []
        if isinstance(value, (list, tuple)):
            values = value
        else:
            values = str(value).replace("\n", ",").replace(";", ",").split(",")
        return [str(item).strip() for item in values if str(item).strip()]

    def _upstream_node_ids(self, target_node_ids):
        included_node_ids = set(target_node_ids)
        changed = True
        while changed:
            changed = False
            for item in self.items():
                if not isinstance(item, ConnectionGraphicsItem) or item.target_port is None:
                    continue
                connection_data = item.serialize()
                if connection_data["target_node"] in included_node_ids:
                    source_node = connection_data["source_node"]
                    if source_node not in included_node_ids:
                        included_node_ids.add(source_node)
                        changed = True
        return included_node_ids


class BlueprintCanvasView(QtWidgets.QGraphicsView):
    """Viewport for the blueprint scene."""

    def __init__(self, scene, parent=None):
        super(BlueprintCanvasView, self).__init__(scene, parent)
        self.search_node_requested_callback = None
        self.category_node_requested_callback = None
        self._panning = False
        self._space_pan_enabled = False
        self._pan_start_pos = None
        self._pan_start_h_value = 0
        self._pan_start_v_value = 0
        self.setRenderHint(
            qt_enum(
                (QtGui.QPainter, "RenderHint.Antialiasing"),
                (QtGui.QPainter, "Antialiasing"),
            ),
            True,
        )
        self.setDragMode(
            qt_enum(
                (QtWidgets.QGraphicsView, "DragMode.RubberBandDrag"),
                (QtWidgets.QGraphicsView, "RubberBandDrag"),
            )
        )
        self.setTransformationAnchor(
            qt_enum(
                (QtWidgets.QGraphicsView, "ViewportAnchor.AnchorUnderMouse"),
                (QtWidgets.QGraphicsView, "AnchorUnderMouse"),
            )
        )
        self.setFocusPolicy(
            qt_enum(
                (QtCore.Qt, "FocusPolicy.StrongFocus"),
                (QtCore.Qt, "StrongFocus"),
            )
        )

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        scale_factor = 1.12 if delta > 0 else 1.0 / 1.12
        self.scale(scale_factor, scale_factor)

    def contextMenuEvent(self, event):
        if self.category_node_requested_callback is not None:
            self.category_node_requested_callback(self.mapToScene(event.pos()), event.globalPos())
            event.accept()
            return
        super(BlueprintCanvasView, self).contextMenuEvent(event)

    def mouseDoubleClickEvent(self, event):
        left_button = qt_enum(
            (QtCore.Qt, "MouseButton.LeftButton"),
            (QtCore.Qt, "LeftButton"),
        )
        if event.button() == left_button and self.search_node_requested_callback is not None:
            self.search_node_requested_callback(self.mapToScene(event.pos()), self._event_global_pos(event))
            event.accept()
            return
        super(BlueprintCanvasView, self).mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        middle_button = qt_enum(
            (QtCore.Qt, "MouseButton.MiddleButton"),
            (QtCore.Qt, "MiddleButton"),
        )
        left_button = qt_enum(
            (QtCore.Qt, "MouseButton.LeftButton"),
            (QtCore.Qt, "LeftButton"),
        )
        if event.button() == middle_button or (
            self._space_pan_enabled and event.button() == left_button
        ):
            self._begin_pan(event)
            event.accept()
            return
        super(BlueprintCanvasView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._panning:
            current_pos = self._event_pos(event)
            delta = current_pos - self._pan_start_pos
            self.horizontalScrollBar().setValue(self._pan_start_h_value - delta.x())
            self.verticalScrollBar().setValue(self._pan_start_v_value - delta.y())
            event.accept()
            return
        super(BlueprintCanvasView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._panning:
            self._end_pan()
            event.accept()
            return
        super(BlueprintCanvasView, self).mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        delete_key = qt_enum(
            (QtCore.Qt, "Key.Key_Delete"),
            (QtCore.Qt, "Key_Delete"),
        )
        backspace_key = qt_enum(
            (QtCore.Qt, "Key.Key_Backspace"),
            (QtCore.Qt, "Key_Backspace"),
        )
        space_key = qt_enum(
            (QtCore.Qt, "Key.Key_Space"),
            (QtCore.Qt, "Key_Space"),
        )
        if event.key() in (delete_key, backspace_key):
            self.scene().delete_selected_items()
            event.accept()
            return
        if event.key() == space_key:
            self._space_pan_enabled = True
            self._set_open_hand_cursor()
            event.accept()
            return
        super(BlueprintCanvasView, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        space_key = qt_enum(
            (QtCore.Qt, "Key.Key_Space"),
            (QtCore.Qt, "Key_Space"),
        )
        if event.key() == space_key:
            self._space_pan_enabled = False
            if self._panning:
                self._end_pan()
            else:
                self.unsetCursor()
            event.accept()
            return
        super(BlueprintCanvasView, self).keyReleaseEvent(event)

    def _begin_pan(self, event):
        self._panning = True
        self._pan_start_pos = self._event_pos(event)
        self._pan_start_h_value = self.horizontalScrollBar().value()
        self._pan_start_v_value = self.verticalScrollBar().value()
        closed_hand = qt_enum(
            (QtCore.Qt, "CursorShape.ClosedHandCursor"),
            (QtCore.Qt, "ClosedHandCursor"),
        )
        self.setCursor(QtGui.QCursor(closed_hand))

    def _end_pan(self):
        self._panning = False
        self._pan_start_pos = None
        if self._space_pan_enabled:
            self._set_open_hand_cursor()
        else:
            self.unsetCursor()

    def _set_open_hand_cursor(self):
        open_hand = qt_enum(
            (QtCore.Qt, "CursorShape.OpenHandCursor"),
            (QtCore.Qt, "OpenHandCursor"),
        )
        self.setCursor(QtGui.QCursor(open_hand))

    def _event_pos(self, event):
        try:
            return event.position().toPoint()
        except AttributeError:
            return event.pos()

    def _event_global_pos(self, event):
        try:
            return event.globalPosition().toPoint()
        except AttributeError:
            return event.globalPos()


class NodeSearchDialog(QtWidgets.QDialog):
    """Searchable node picker used by the canvas context menu."""

    def __init__(self, node_specs, parent=None):
        super(NodeSearchDialog, self).__init__(parent)
        self.node_specs = node_specs
        self.selected_node_type = None
        self.search_field = QtWidgets.QLineEdit(self)
        self.node_list = QtWidgets.QListWidget(self)
        self.add_button = QtWidgets.QPushButton("添加", self)
        self.cancel_button = QtWidgets.QPushButton("取消", self)
        self.user_role = qt_enum(
            (QtCore.Qt, "ItemDataRole.UserRole"),
            (QtCore.Qt, "UserRole"),
        )

        self.setWindowTitle("添加节点")
        self.resize(360, 420)
        self._build_ui()
        self._populate_list("")

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        self.search_field.setPlaceholderText("搜索节点...")
        self.search_field.textChanged.connect(self._populate_list)
        self.search_field.returnPressed.connect(self._accept_current)
        self.node_list.itemDoubleClicked.connect(lambda _item: self._accept_current())

        button_row = QtWidgets.QHBoxLayout()
        button_row.addStretch()
        button_row.addWidget(self.cancel_button)
        button_row.addWidget(self.add_button)
        self.add_button.clicked.connect(self._accept_current)
        self.cancel_button.clicked.connect(self.reject)

        layout.addWidget(self.search_field)
        layout.addWidget(self.node_list)
        layout.addLayout(button_row)

    def _populate_list(self, filter_text):
        filter_text = (filter_text or "").lower()
        self.node_list.clear()

        for node_type in sorted(self.node_specs.keys()):
            spec = self.node_specs[node_type]
            search_text = "{0} {1} {2}".format(spec.category, spec.title, node_type).lower()
            if filter_text and filter_text not in search_text:
                continue

            item = QtWidgets.QListWidgetItem(spec.title)
            item.setToolTip(spec.category)
            item.setData(self.user_role, node_type)
            self.node_list.addItem(item)

        if self.node_list.count():
            self.node_list.setCurrentRow(0)

    def _accept_current(self):
        item = self.node_list.currentItem()
        if item is None:
            return
        self.selected_node_type = item.data(self.user_role)
        self.accept()

    def focus_search(self):
        self.search_field.setFocus()
        self.search_field.selectAll()


class ListParameterEditor(QtWidgets.QWidget):
    """Editable list parameter with add/remove controls."""

    def __init__(self, values=None, on_change=None, parent=None):
        super(ListParameterEditor, self).__init__(parent)
        self.items = self._normalize_values(values)
        self.on_change = on_change
        self.list_widget = QtWidgets.QListWidget(self)
        self.message_label = QtWidgets.QLabel("", self)
        self.message_label.setStyleSheet("color: #8b95a5;")
        self.user_role = qt_enum(
            (QtCore.Qt, "ItemDataRole.UserRole"),
            (QtCore.Qt, "UserRole"),
        )
        self._build_base_ui()
        self._sync_list()

    def _build_base_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.list_widget.setMinimumHeight(90)
        self.list_widget.setSelectionMode(
            qt_enum(
                (QtWidgets.QAbstractItemView, "SelectionMode.ExtendedSelection"),
                (QtWidgets.QAbstractItemView, "ExtendedSelection"),
            )
        )
        layout.addWidget(self.list_widget)
        layout.addWidget(self.message_label)

    def add_items(self, items):
        added = 0
        for item in self._normalize_values(items):
            if item not in self.items:
                self.items.append(item)
                added += 1
        self._sync_list()
        self._emit_changed()
        return added

    def remove_selected_items(self):
        selected_items = self.list_widget.selectedItems()
        selected_values = set(item.data(self.user_role) for item in selected_items)
        if not selected_values:
            self._set_message("没有选中要删除的条目。")
            return
        self.items = [item for item in self.items if item not in selected_values]
        self._sync_list()
        self._emit_changed()
        self._set_message("已删除 {0} 个条目。".format(len(selected_values)))

    def _sync_list(self):
        self.list_widget.clear()
        for item_text in self.items:
            item = QtWidgets.QListWidgetItem(item_text)
            item.setData(self.user_role, item_text)
            self.list_widget.addItem(item)

    def _emit_changed(self):
        if self.on_change is not None:
            self.on_change(list(self.items))

    def _set_message(self, message):
        self.message_label.setText(message)
        if message:
            print("Maya Blueprint: {0}".format(message))

    def _normalize_values(self, values):
        if not values:
            return []
        if isinstance(values, (list, tuple)):
            source_values = values
        else:
            source_values = str(values).replace("\n", ",").replace(";", ",").split(",")

        result = []
        seen = set()
        for value in source_values:
            text = str(value).strip()
            if text and text not in seen:
                result.append(text)
                seen.add(text)
        return result


class NodeListParameterEditor(ListParameterEditor):
    """Node list editor that can capture the current Maya selection."""

    def __init__(self, values=None, on_change=None, parent=None):
        self.manual_field = QtWidgets.QLineEdit(parent)
        self.add_manual_button = QtWidgets.QPushButton("添加", parent)
        self.capture_button = QtWidgets.QPushButton("录入当前选择", parent)
        self.remove_button = QtWidgets.QPushButton("删除选中", parent)
        super(NodeListParameterEditor, self).__init__(values, on_change, parent)

    def _build_base_ui(self):
        super(NodeListParameterEditor, self)._build_base_ui()
        layout = self.layout()

        self.manual_field.setPlaceholderText("手写节点名，可选")
        manual_row = QtWidgets.QHBoxLayout()
        manual_row.addWidget(self.manual_field, 1)
        manual_row.addWidget(self.add_manual_button)

        button_row = QtWidgets.QHBoxLayout()
        button_row.addWidget(self.capture_button)
        button_row.addWidget(self.remove_button)

        layout.insertLayout(0, manual_row)
        layout.addLayout(button_row)

        self.add_manual_button.clicked.connect(self._add_manual_text)
        self.capture_button.clicked.connect(self._capture_selection)
        self.remove_button.clicked.connect(self.remove_selected_items)

    def _add_manual_text(self):
        added = self.add_items(self.manual_field.text())
        self.manual_field.clear()
        self._set_message("已添加 {0} 个节点。".format(added))

    def _capture_selection(self):
        try:
            selected_nodes = selection.get_current_selection(include_shapes=False)
        except MayaApiError as error:
            self._set_message(str(error))
            return
        if not selected_nodes:
            self._set_message("Maya 当前没有选择对象。")
            return
        added = self.add_items(selected_nodes)
        self._set_message("已录入 {0} 个选择对象。".format(added))


class AttributeItemListParameterEditor(ListParameterEditor):
    """Attribute item editor for reusable attribute names."""

    def __init__(self, values=None, on_change=None, parent=None):
        self.attribute_combo = QtWidgets.QComboBox(parent)
        self.add_attribute_button = QtWidgets.QPushButton("添加属性", parent)
        self.refresh_button = QtWidgets.QPushButton("刷新选择属性", parent)
        self.capture_button = QtWidgets.QPushButton("录入通道栏属性", parent)
        self.remove_button = QtWidgets.QPushButton("删除选中", parent)
        super(AttributeItemListParameterEditor, self).__init__(values, on_change, parent)

    def _build_base_ui(self):
        super(AttributeItemListParameterEditor, self)._build_base_ui()
        layout = self.layout()

        self.attribute_combo.setEditable(True)
        for attr_name in attributes.common_attribute_names():
            self.attribute_combo.addItem(attr_name)

        picker_row = QtWidgets.QHBoxLayout()
        picker_row.addWidget(self.attribute_combo, 1)
        picker_row.addWidget(self.add_attribute_button)

        button_row = QtWidgets.QHBoxLayout()
        button_row.addWidget(self.refresh_button)
        button_row.addWidget(self.capture_button)
        button_row.addWidget(self.remove_button)

        layout.insertLayout(0, picker_row)
        layout.addLayout(button_row)

        self.add_attribute_button.clicked.connect(self._add_combo_attribute)
        self.refresh_button.clicked.connect(self._refresh_selection_attributes)
        self.capture_button.clicked.connect(self._capture_channel_box_attributes)
        self.remove_button.clicked.connect(self.remove_selected_items)

    def _add_combo_attribute(self):
        text = self.attribute_combo.currentText()
        added = self.add_items(text)
        self._set_message("已添加 {0} 个属性。".format(added))

    def _refresh_selection_attributes(self):
        try:
            attr_names = attributes.selected_node_attribute_names()
        except MayaApiError as error:
            self._set_message(str(error))
            return
        existing = set(self.attribute_combo.itemText(index) for index in range(self.attribute_combo.count()))
        added = 0
        for attr_name in attr_names:
            if attr_name not in existing:
                self.attribute_combo.addItem(attr_name)
                existing.add(attr_name)
                added += 1
        self._set_message("已刷新 {0} 个可选属性。".format(added))

    def _capture_channel_box_attributes(self):
        try:
            attr_names = attributes.selected_channel_box_attribute_names()
        except MayaApiError as error:
            self._set_message(str(error))
            return
        added = self.add_items(attr_names)
        self._set_message("已录入 {0} 个通道栏属性。".format(added))


class NodePropertiesPanel(QtWidgets.QWidget):
    """Property editor for the selected node."""

    def __init__(self, parent=None):
        super(NodePropertiesPanel, self).__init__(parent)
        self.node_item = None
        self.editor_widgets = {}
        self.form_layout = QtWidgets.QFormLayout()
        self.title_label = QtWidgets.QLabel("未选择节点", self)
        self.title_label.setStyleSheet("font-weight: bold;")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.title_label)
        layout.addLayout(self.form_layout)
        layout.addStretch()

    def set_node(self, node_item):
        self.node_item = node_item
        self._rebuild()

    def _rebuild(self):
        self.editor_widgets = {}
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if self.node_item is None:
            self.title_label.setText("未选择节点")
            return

        self.title_label.setText(self.node_item.node_spec.title)
        for parameter_spec in self.node_item.node_spec.parameters:
            editor = self._create_editor(parameter_spec)
            self.editor_widgets[parameter_spec.name] = editor
            self.form_layout.addRow(parameter_spec.label, editor)
        if self.node_item.node_spec.node_type == "debug.print_result":
            self.form_layout.addRow("结果", self._create_result_view())

    def _create_editor(self, parameter_spec):
        value = self.node_item.parameters.get(parameter_spec.name, parameter_spec.default)

        if parameter_spec.param_type == "node_list":
            return NodeListParameterEditor(
                value,
                on_change=lambda new_value, name=parameter_spec.name: self._set_value(name, new_value),
                parent=self,
            )

        if parameter_spec.param_type == "attribute_item_list":
            return AttributeItemListParameterEditor(
                value,
                on_change=lambda new_value, name=parameter_spec.name: self._set_value(name, new_value),
                parent=self,
            )

        if parameter_spec.param_type == "bool":
            editor = QtWidgets.QCheckBox(self)
            editor.setChecked(bool(value))
            editor.stateChanged.connect(
                lambda _state, name=parameter_spec.name, widget=editor: self._set_value(name, widget.isChecked())
            )
            return editor

        if parameter_spec.param_type == "number":
            editor = QtWidgets.QDoubleSpinBox(self)
            editor.setRange(-1000000.0, 1000000.0)
            editor.setDecimals(3)
            editor.setValue(float(value or 0.0))
            editor.valueChanged.connect(
                lambda new_value, name=parameter_spec.name: self._set_value(name, new_value)
            )
            return editor

        if parameter_spec.param_type == "choice":
            editor = QtWidgets.QComboBox(self)
            labels = parameter_spec.choice_labels or parameter_spec.choices
            for index, choice in enumerate(parameter_spec.choices):
                label = labels[index] if index < len(labels) else choice
                editor.addItem(label, choice)
            if value in parameter_spec.choices:
                editor.setCurrentIndex(parameter_spec.choices.index(value))
            editor.currentIndexChanged.connect(
                lambda _index, name=parameter_spec.name, widget=editor: self._set_value(
                    name,
                    widget.itemData(widget.currentIndex()),
                )
            )
            return editor

        editor = QtWidgets.QLineEdit(self)
        editor.setText("" if value is None else str(value))
        editor.textChanged.connect(
            lambda new_value, name=parameter_spec.name: self._set_value(name, new_value)
        )
        return editor

    def _set_value(self, name, value):
        if self.node_item is not None:
            self.node_item.set_parameter(name, value)

    def _create_result_view(self):
        editor = QtWidgets.QPlainTextEdit(self)
        editor.setReadOnly(True)
        editor.setMinimumHeight(120)
        editor.setPlainText(self.node_item.last_result_text or "尚未运行。")
        return editor


class BlueprintCanvasWidget(QtWidgets.QWidget):
    """Complete canvas panel with toolbar, graphics view, and property panel."""

    def __init__(self, parent=None):
        super(BlueprintCanvasWidget, self).__init__(parent)
        self.node_specs = default_node_specs()
        self.executor = WorkflowExecutor(self.node_specs)
        self.scene = BlueprintGraphicsScene(self.node_specs, self)
        self.view = BlueprintCanvasView(self.scene, self)
        self.view.search_node_requested_callback = self.add_node_from_search
        self.view.category_node_requested_callback = self.add_node_from_category_menu
        self.properties_panel = NodePropertiesPanel(self)
        self.status_label = QtWidgets.QLabel("就绪", self)
        self.node_combo = QtWidgets.QComboBox(self)
        self.run_count_spinbox = QtWidgets.QSpinBox(self)
        self._build_ui()
        self._add_starter_nodes()
        self.scene.selectionChanged.connect(self._sync_properties_panel)

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(6)

        toolbar = QtWidgets.QHBoxLayout()
        for node_type in sorted(self.node_specs.keys()):
            spec = self.node_specs[node_type]
            self.node_combo.addItem(spec.title, node_type)

        add_button = QtWidgets.QPushButton("添加节点", self)
        save_button = QtWidgets.QPushButton("保存", self)
        load_button = QtWidgets.QPushButton("加载", self)
        validate_button = QtWidgets.QPushButton("检查", self)
        run_button = QtWidgets.QPushButton("运行", self)
        serialize_button = QtWidgets.QPushButton("打印流程", self)
        self.run_count_spinbox.setRange(1, 999)
        self.run_count_spinbox.setValue(1)
        self.run_count_spinbox.setPrefix("x ")
        self.run_count_spinbox.setToolTip("运行次数")
        self.run_count_spinbox.setFixedWidth(58)
        run_button.setMinimumWidth(96)
        run_button.setToolTip("有选中节点时运行该节点的上游流程；未选中节点时运行全部流程。")
        run_button.setStyleSheet(
            "QPushButton {"
            "background-color: #2fbf71;"
            "color: #07130c;"
            "font-weight: bold;"
            "border: 1px solid #7ee2a8;"
            "border-radius: 4px;"
            "padding: 5px 12px;"
            "}"
            "QPushButton:hover { background-color: #3ed682; }"
            "QPushButton:pressed { background-color: #23975a; }"
        )

        add_button.clicked.connect(self.add_selected_node)
        save_button.clicked.connect(self.save_workflow)
        load_button.clicked.connect(self.load_workflow)
        validate_button.clicked.connect(self.validate_workflow)
        run_button.clicked.connect(self.run_workflow)
        serialize_button.clicked.connect(self.print_workflow)

        toolbar.addWidget(self.node_combo, 1)
        toolbar.addWidget(add_button)
        toolbar.addStretch()
        toolbar.addWidget(save_button)
        toolbar.addWidget(load_button)
        toolbar.addWidget(validate_button)
        toolbar.addWidget(self.run_count_spinbox)
        toolbar.addWidget(run_button)
        toolbar.addWidget(serialize_button)

        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(self.view)
        splitter.addWidget(self.properties_panel)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        main_layout.addLayout(toolbar)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.status_label)

    def _add_starter_nodes(self):
        self.scene.add_node_type("constant.path", QtCore.QPointF(-420, -120))
        self.scene.add_node_type("maya.io.import_file", QtCore.QPointF(-120, -80))
        self.scene.add_node_type("maya.io.export_fbx", QtCore.QPointF(220, -40))

    def add_selected_node(self):
        node_type = self.node_combo.itemData(self.node_combo.currentIndex())
        node_item = self.scene.add_node_type(node_type, position=self._next_spawn_position())
        self.scene.clearSelection()
        node_item.setSelected(True)

    def add_node_from_search(self, scene_position=None, global_position=None):
        dialog = NodeSearchDialog(self.node_specs, self)
        if global_position is not None:
            dialog.move(global_position)
        dialog.focus_search()
        if self._exec_dialog(dialog):
            node_type = dialog.selected_node_type
            position = scene_position or self._next_spawn_position()
            node_item = self.scene.add_node_type(node_type, position=position)
            self.scene.clearSelection()
            node_item.setSelected(True)
            self.status_label.setText("已添加节点：{0}".format(self.node_specs[node_type].title))

    def add_node_from_category_menu(self, scene_position=None, global_position=None):
        menu = QtWidgets.QMenu(self)
        menu_lookup = {}

        for node_type in sorted(self.node_specs.keys()):
            spec = self.node_specs[node_type]
            parent_menu = menu
            category_parts = [part.strip() for part in spec.category.split("/") if part.strip()]
            current_path = []
            for part in category_parts:
                current_path.append(part)
                path_key = "/".join(current_path)
                if path_key not in menu_lookup:
                    menu_lookup[path_key] = parent_menu.addMenu(part)
                parent_menu = menu_lookup[path_key]

            action = parent_menu.addAction(spec.title)
            action.setData(node_type)

        chosen_action = self._exec_menu(menu, global_position)
        if chosen_action is None:
            return

        node_type = chosen_action.data()
        position = scene_position or self._next_spawn_position()
        node_item = self.scene.add_node_type(node_type, position=position)
        self.scene.clearSelection()
        node_item.setSelected(True)
        self.status_label.setText("已添加节点：{0}".format(self.node_specs[node_type].title))

    def _exec_dialog(self, dialog):
        try:
            result = dialog.exec()
        except AttributeError:
            result = dialog.exec_()
        accepted = qt_enum(
            (QtWidgets.QDialog, "DialogCode.Accepted"),
            (QtWidgets.QDialog, "Accepted"),
        )
        return result == accepted

    def _exec_menu(self, menu, global_position):
        if global_position is None:
            global_position = self.view.mapToGlobal(self.view.viewport().rect().center())
        try:
            return menu.exec(global_position)
        except AttributeError:
            return menu.exec_(global_position)

    def save_workflow(self):
        file_path, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "保存流程",
            "",
            "流程 JSON (*.json)",
        )
        if not file_path:
            return
        data = self.scene.serialize()
        with open(file_path, "w", encoding="utf-8") as file_handle:
            json.dump(data, file_handle, indent=2, sort_keys=True, ensure_ascii=False)
        self.status_label.setText("已保存流程：{0}".format(file_path))

    def load_workflow(self):
        file_path, _selected_filter = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "加载流程",
            "",
            "流程 JSON (*.json)",
        )
        if not file_path:
            return
        with open(file_path, "r", encoding="utf-8") as file_handle:
            data = json.load(file_handle)
        self.scene.load_workflow(data)
        self.properties_panel.set_node(None)
        self.status_label.setText("已加载流程：{0}".format(file_path))

    def validate_workflow(self):
        issues = self.scene.validate_workflow()
        if issues:
            self.status_label.setText("检查发现 {0} 个问题，请看 Script Editor。".format(len(issues)))
            print("Maya Blueprint 检查问题：")
            for issue in issues:
                print("- {0}".format(issue))
        else:
            self.status_label.setText("检查通过。")

    def run_workflow(self):
        selected_node_ids = self.scene.selected_node_ids()
        run_count = self.run_count_spinbox.value()

        for run_index in range(run_count):
            workflow_data = self._workflow_for_current_run(selected_node_ids)
            included_node_ids = set(node_data["id"] for node_data in workflow_data.get("nodes", []))
            run_label = self._run_label(selected_node_ids, run_index, run_count)

            self.scene.reset_node_statuses()
            if selected_node_ids:
                self.scene.mark_skipped_except(included_node_ids)

            issues = self.scene.validate_workflow(workflow_data)
            if issues:
                self._mark_validation_issues(issues)
                self.status_label.setText("{0} 已停止：检查发现 {1} 个问题。".format(run_label, len(issues)))
                print("Maya Blueprint 运行因检查问题停止：")
                for issue in issues:
                    print("- {0}".format(issue))
                return

            try:
                results = self.executor.execute(
                    workflow_data,
                    status_callback=self._set_node_run_status,
                )
                self.scene.set_node_results(results)
            except WorkflowExecutionError as error:
                self.status_label.setText("{0} 失败，请看 Script Editor。".format(run_label))
                print("Maya Blueprint 运行失败：{0}".format(error))
                return
            except Exception as error:
                self.status_label.setText("{0} 失败，请看 Script Editor。".format(run_label))
                print("Maya Blueprint 意外运行错误：{0}".format(error))
                raise

            self.status_label.setText("{0} 完成：{1} 个节点。".format(run_label, len(results)))
            print("Maya Blueprint {0} 完成：{1} 个节点。".format(run_label, len(results)))
            self._sync_properties_panel()

    def _workflow_for_current_run(self, selected_node_ids):
        if selected_node_ids:
            return self.scene.serialize_for_node_ids(selected_node_ids)
        return self.scene.serialize()

    def _run_label(self, selected_node_ids, run_index, run_count):
        scope = "选中" if selected_node_ids else "全部"
        if run_count > 1:
            return "运行{0} {1}/{2}".format(scope, run_index + 1, run_count)
        return "运行{0}".format(scope)

    def _set_node_run_status(self, node_id, status, message=""):
        self.scene.set_node_status(node_id, status, message)
        QtWidgets.QApplication.processEvents()

    def _mark_validation_issues(self, issues):
        failed_node_ids = set()
        for issue in issues:
            if "." in issue:
                failed_node_ids.add(issue.split(".", 1)[0])
        for node_id in failed_node_ids:
            self.scene.set_node_status(node_id, "failed", "检查失败")

    def print_workflow(self):
        data = self.scene.serialize()
        print("Maya Blueprint 流程：")
        print(json.dumps(data, indent=2, sort_keys=True))
        self.status_label.setText(
            "流程包含 {0} 个节点和 {1} 条连接。".format(
                len(data["nodes"]),
                len(data["connections"]),
            )
        )

    def _sync_properties_panel(self):
        selected_node = None
        for item in self.scene.selectedItems():
            if isinstance(item, NodeGraphicsItem):
                selected_node = item
                break
        self.properties_panel.set_node(selected_node)

    def _next_spawn_position(self):
        center = self.view.mapToScene(self.view.viewport().rect().center())
        return QtCore.QPointF(center.x() - 100, center.y() - 60)
