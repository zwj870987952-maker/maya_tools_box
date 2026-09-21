# GETOOLS is under the terms of the MIT License
# Copyright (c) 2018-2024 Eugene Gataulin (GenEugene). All Rights Reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Author: Eugene Gataulin tek942@gmail.com https://www.linkedin.com/in/geneugene https://discord.gg/heMxJhTqCz
# Source code: https://github.com/GenEugene/GETools or https://app.gumroad.com/geneugene

import maya.cmds as cmds
from functools import partial

from .. import Settings
from ..utils import Blendshapes
from ..utils import Colors
from ..utils import Constraints
from ..utils import Create
from ..utils import Curves
from ..utils import Deformers
from ..utils import Other
from ..utils import Skinning


class RiggingAnnotations:
	### Constraints
	_textAllSelectedConstrainToLast = "所有选中的对象将被约束到最后选中的对象"
	constraintReverse = "反转操作方向，从最后一个选中到第一个选中"
	constraintMaintain = "使用保持偏移"
	constraintOffset = "[开发中]\n添加额外的定位器结构，能够进行偏移动画"
	constraintParent = "父约束。\n{allToLast}".format(allToLast = _textAllSelectedConstrainToLast)
	constraintPoint = "点约束。\n{allToLast}".format(allToLast = _textAllSelectedConstrainToLast)
	constraintOrient = "方向约束。\n{allToLast}".format(allToLast = _textAllSelectedConstrainToLast)
	constraintScale = "缩放约束。\n{allToLast}".format(allToLast = _textAllSelectedConstrainToLast)
	constraintAim = "[开发中]\n目标约束。".format(allToLast = _textAllSelectedConstrainToLast) # TODO
	constraintDisconnectSelected = "断开目标对象与最后选中对象的连接。它们将从约束属性中删除。"
	constraintDelete = "删除选中对象上的所有约束"

	### Utils
	_rotateOrder = "通道框中所有选中对象的旋转顺序属性"
	rotateOrderShow = "显示 {0}".format(_rotateOrder)
	rotateOrderHide = "隐藏 {0}".format(_rotateOrder)
	_scaleCompensate = "所有选中关节的段缩放补偿属性"
	scaleCompensateOn = "激活 {0}".format(_scaleCompensate)
	scaleCompensateOff = "停用 {0}".format(_scaleCompensate)
	_jointDrawStyle = "选中关节的绘制样式"
	jointDrawStyleBone = "骨骼 {0}".format(_jointDrawStyle)
	jointDrawStyleHidden = "隐藏 {0}".format(_jointDrawStyle)
	copySkinWeights = "从最后选中的对象复制蒙皮权重到所有其他选中对象"

	### Deformers
	wrapsCreate = "在选中对象上创建包裹变形器。\n最后一个对象用作源变形对象。"
	blendshapeCopyFromTarget = "从最后选中的对象重建选中对象上的混合变形。\n最后一个对象必须有混合变形节点。"
	blendshapeExtract = "提取混合变形为复制的网格。\n如有需要，在提取前绘制权重。"
	blendshapeZeroWeights = "将选中对象上的所有混合变形权重归零"

	### Curves
	curveCreateFromSelectedObjects = "从选中对象创建曲线。\n每个曲线点将在枢轴处创建。"
	curveCreateFromTrajectory = "***草稿***\n从对象轨迹创建曲线。"

class Rigging:
	_version = "v1.6"
	_name = "绑定"
	_title = _name + " " + _version

	def __init__(self, options):
		self.optionsPlugin = options
		### Check Maya version to avoid cycle import, Maya 2020 and older can't use cycle import
		if cmds.about(version = True) in ["2022", "2023", "2024", "2025"]:
			from ..modules import Options
			if isinstance(options, Options.PluginVariables):
				self.optionsPlugin = options
		
		self.checkboxConstraintReverse = None
		self.checkboxConstraintMaintain = None
		# self.checkboxConstraintOffset = None

		self.intFieldPolygonWithLocatorsPoints = None
		self.floatFieldPolygonWithLocatorsRadius = None
		self.floatFieldPolygonWithLocatorsAngle = None
	
	def UICreate(self, layoutMain):
		self.UILayoutPolygonWithLocators(layoutMain)
		self.UILayoutConstraints(layoutMain)
		self.UILayoutUtils(layoutMain)
		self.UILayoutBlendshapes(layoutMain)
		self.UILayoutCurves(layoutMain)
		cmds.separator(parent = layoutMain, height = Settings.separatorHeight, style = "none")

	def UILayoutPolygonWithLocators(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "多边形与定位器", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)

		cellWidths = (75, 75, 75, 50)
		rowLayout = cmds.rowLayout(parent = layoutColumn, adjustableColumn = 4, numberOfColumns = 4, columnWidth4 = (cellWidths[0], cellWidths[1], cellWidths[2], cellWidths[3]), columnAlign = [(1, "right"), (2, "center"), (3, "center"), (4, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0), (4, "both", 0)])
		
		cmds.gridLayout(parent = rowLayout, numberOfColumns = 2, cellWidth = cellWidths[0] / 2, cellHeight = Settings.lineHeight)
		cmds.text(label = "点数")
		self.intFieldPolygonWithLocatorsPoints = cmds.intField(value = 3, minValue = 3)
		
		cmds.gridLayout(parent = rowLayout, numberOfColumns = 2, cellWidth = cellWidths[1] / 2, cellHeight = Settings.lineHeight)
		cmds.text(label = "半径")
		self.floatFieldPolygonWithLocatorsRadius = cmds.floatField(value = 10, minValue = 0, precision = 1)
		
		cmds.gridLayout(parent = rowLayout, numberOfColumns = 2, cellWidth = cellWidths[2] / 2, cellHeight = Settings.lineHeight)
		cmds.text(label = "角度")
		self.floatFieldPolygonWithLocatorsAngle = cmds.floatField(value = 0, precision = 1)
		
		cmds.button(parent = rowLayout, label = "创建", command = self.CreatePolygonWithLocators, backgroundColor = Colors.green10)
	def UILayoutConstraints(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "约束", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		countOffsets = 4
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.separator(style = "none")
		self.checkboxConstraintReverse = cmds.checkBox(label = "反转", value = False, annotation = RiggingAnnotations.constraintReverse)
		self.checkboxConstraintMaintain = cmds.checkBox(label = "保持", value = False, annotation = RiggingAnnotations.constraintMaintain)
		# self.checkboxConstraintOffset = UI.Checkbox(label = "**偏移", value = False, annotation = RiggingAnnotations.constraintOffset)
		cmds.separator(style = "none")
		
		countOffsets = 4
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.button(label = "父约束", command = self.ConstrainParent, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintParent)
		cmds.button(label = "点约束", command = self.ConstrainPoint, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintPoint)
		cmds.button(label = "方向约束", command = self.ConstrainOrient, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintOrient)
		cmds.button(label = "缩放约束", command = self.ConstrainScale, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintScale)
		# cmds.button(label = "**目标约束", command = self.ConstrainAim, backgroundColor = Colors.red10, annotation = RiggingAnnotations.constraintAim, enable = False) # TODO
		
		countOffsets = 2
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.button(label = "断开连接", command = Constraints.DisconnectTargetsFromConstraintOnSelected, backgroundColor = Colors.red50, annotation = RiggingAnnotations.constraintDisconnectSelected)
		cmds.button(label = "删除约束", command = Constraints.DeleteConstraintsOnSelected, backgroundColor = Colors.red50, annotation = RiggingAnnotations.constraintDelete)
	def UILayoutUtils(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "工具", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		rowLayoutSize = (130, 50, 50)
		
		cmds.rowLayout(parent = layoutColumn, numberOfColumns = 3, columnWidth3 = rowLayoutSize, columnAlign = [(1, "right"), (2, "center"), (3, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0)])
		cmds.text(label = "旋转顺序 ")
		cmds.button(label = "显示", command = partial(Other.RotateOrderVisibility, True), backgroundColor = Colors.green10, annotation = RiggingAnnotations.rotateOrderShow)
		cmds.button(label = "隐藏", command = partial(Other.RotateOrderVisibility, False), backgroundColor = Colors.green10, annotation = RiggingAnnotations.rotateOrderHide)
		
		cmds.rowLayout(parent = layoutColumn, numberOfColumns = 3, columnWidth3 = rowLayoutSize, columnAlign = [(1, "right"), (2, "center"), (3, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0)])
		cmds.text(label = "缩放补偿 ")
		cmds.button(label = "开启", command = partial(Other.SegmentScaleCompensate, True), backgroundColor = Colors.orange10, annotation = RiggingAnnotations.scaleCompensateOn)
		cmds.button(label = "关闭", command = partial(Other.SegmentScaleCompensate, False), backgroundColor = Colors.orange10, annotation = RiggingAnnotations.scaleCompensateOff)
		
		cmds.rowLayout(parent = layoutColumn, numberOfColumns = 3, columnWidth3 = rowLayoutSize, columnAlign = [(1, "right"), (2, "center"), (3, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0)])
		cmds.text(label = "关节绘制样式 ")
		cmds.button(label = "骨骼", command = partial(Other.JointDrawStyle, 0), backgroundColor = Colors.yellow10, annotation = RiggingAnnotations.jointDrawStyleBone)
		cmds.button(label = "隐藏", command = partial(Other.JointDrawStyle, 2), backgroundColor = Colors.yellow10, annotation = RiggingAnnotations.jointDrawStyleHidden)
		
		countOffsets = 1
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.button(label = "从最后选中复制蒙皮权重", command = Skinning.CopySkinWeightsFromLastMesh, backgroundColor = Colors.blue10, annotation = RiggingAnnotations.copySkinWeights)
	def UILayoutBlendshapes(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "混合变形", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		countOffsets = 3
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.button(label = "包裹", command = Deformers.WrapsCreateOnSelected, backgroundColor = Colors.yellow10, annotation = RiggingAnnotations.wrapsCreate)
		# cmds.button(label = "**转换", command = Deformers.WrapConvertToBlendshapes) # TODO
		cmds.button(label = "重建", command = Deformers.BlendshapesReconstruction, backgroundColor = Colors.green50, annotation = RiggingAnnotations.blendshapeCopyFromTarget)
		cmds.button(label = "提取形状", command = Blendshapes.ExtractShapesFromSelected, backgroundColor = Colors.green10, annotation = RiggingAnnotations.blendshapeExtract)
		
		countOffsets = 1
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.button(label = "权重归零", command = Blendshapes.ZeroBlendshapeWeightsOnSelected, backgroundColor = Colors.blackWhite100, annotation = RiggingAnnotations.blendshapeZeroWeights)
	def UILayoutCurves(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "曲线", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		countOffsets = 2
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.button(label = "从选中对象", command = Curves.CreateCurveFromSelectedObjects, backgroundColor = Colors.blue10, annotation = RiggingAnnotations.curveCreateFromSelectedObjects)
		cmds.button(label = "从轨迹", command = Curves.CreateCurveFromTrajectory, backgroundColor = Colors.orange10, annotation = RiggingAnnotations.curveCreateFromTrajectory)

	### CONSTRAINTS
	def GetCheckboxConstraintReverse(self):
		return cmds.checkBox(self.checkboxConstraintReverse, query = True, value = True)
	def GetCheckboxConstraintMaintain(self):
		return cmds.checkBox(self.checkboxConstraintMaintain, query = True, value = True)

	def ConstrainParent(self, *args):
		Constraints.ConstrainSelectedToLastObject(reverse = self.GetCheckboxConstraintReverse(), maintainOffset = self.GetCheckboxConstraintMaintain(), parent = True, point = False, orient = False, scale = False, aim = False)
	def ConstrainPoint(self, *args):
		Constraints.ConstrainSelectedToLastObject(reverse = self.GetCheckboxConstraintReverse(), maintainOffset = self.GetCheckboxConstraintMaintain(), parent = False, point = True, orient = False, scale = False, aim = False)
	def ConstrainOrient(self, *args):
		Constraints.ConstrainSelectedToLastObject(reverse = self.GetCheckboxConstraintReverse(), maintainOffset = self.GetCheckboxConstraintMaintain(), parent = False, point = False, orient = True, scale = False, aim = False)
	def ConstrainScale(self, *args):
		Constraints.ConstrainSelectedToLastObject(reverse = self.GetCheckboxConstraintReverse(), maintainOffset = self.GetCheckboxConstraintMaintain(), parent = False, point = False, orient = False, scale = True, aim = False)
	def ConstrainAim(self, *args): # TODO
		Constraints.ConstrainSelectedToLastObject(reverse = self.GetCheckboxConstraintReverse(), maintainOffset = self.GetCheckboxConstraintMaintain(), parent = False, point = False, orient = False, scale = False, aim = True)

	### MESH
	def CreatePolygonWithLocators(self, *args):
		points = cmds.intField(self.intFieldPolygonWithLocatorsPoints, query = True, value = True)
		radius = cmds.floatField(self.floatFieldPolygonWithLocatorsRadius, query = True, value = True)
		angle = cmds.floatField(self.floatFieldPolygonWithLocatorsAngle, query = True, value = True)
		Create.CreatePolygonWithLocators(countPoints = points, radius = radius, rotation = angle)

