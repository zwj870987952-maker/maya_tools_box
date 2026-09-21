# -*- coding: utf-8 -*-
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
from ..utils import Baker
from ..utils import Colors
from ..utils import Constraints
from ..utils import Locators
from ..utils import Selector
from ..utils import Text


class CenterOfMassAnnotations:
	### Setup
	create = "创建质心对象。\n这只是一个简单的关节，临时存储在内存中。"
	activate = "将选定的质心对象设为活动。\n如果您有多个质心对象或关闭了脚本或Maya，这个功能很有用。\
	\n如果您想使用脚本的其他功能，必须激活质心。"
	select = "选择当前激活的质心对象"
	clean = "删除质心对象"
	_projector = "创建从质心投影的额外对象到"
	projectorYZ = _projector + " YZ 平面"
	projectorXZ = _projector + " XZ 平面"
	projectorXY = _projector + " XY 平面"

	### Weights
	disconnectTargets = "断开选定对象与质心的连接"
	weightsCustom = "自定义权重"
	_weightInfo = "近似权重为百分比。所有权重的总和应为100%。"
	_weightSymmetry = "选择两侧的对象并激活按钮。"
	weightHead = _weightInfo
	weightChest = _weightInfo
	weightAbdomen = _weightInfo
	weightShoulder = "{1}\n{0}".format(_weightInfo, _weightSymmetry)
	weightElbow = "{1}\n{0}".format(_weightInfo, _weightSymmetry)
	weightHand = "{1}\n{0}".format(_weightInfo, _weightSymmetry)
	weightThigh = "{1}\n{0}".format(_weightInfo, _weightSymmetry)
	weightKnee = "{1}\n{0}".format(_weightInfo, _weightSymmetry)
	weightFoot = "{1}\n{0}".format(_weightInfo, _weightSymmetry)

	### Baking
	bakeToCOMLink = "将选定对象烘焙为相对于质心对象的定位器。\n烘焙后将选定对象重新约束到定位器。"
	bakeOriginal = "将动画从定位器烘焙回原始对象。"
	link = "将缓存对象约束到烘焙的定位器。"
	linkOffset = "{0}\n使用保持偏移以保持变换差异".format(link)
	selectRoot = "选择根定位器（如果存在）"

class CenterOfMassSettings:
	COMRadius = 10 / 3
	weightMinMax = (1, 10)

	# BODYPARTS MAPPING PERCENTAGE
	partHead = ("head", 7.3)
	partChest = ("chest", 35.8)
	partAbdomen = ("abdomen", 10.1)
	partShoulder = ("shoulder", 3.1)
	partElbow = ("elbow", 1.7)
	partHand = ("hand ", 0.8)
	partThigh = ("thigh", 11.5)
	partKnee = ("knee", 4.4)
	partFoot = ("foot", 1.9)

class CenterOfMass:
	_version = "v1.5"
	_name = "质心"
	_title = _name + " " + _version

	def __init__(self, options):
		self.optionsPlugin = options
		### Check Maya version to avoid cycle import, Maya 2020 and older can't use cycle import
		if cmds.about(version = True) in ["2022", "2023", "2024", "2025"]:
			from ..modules import Options
			if isinstance(options, Options.PluginVariables):
				self.optionsPlugin = options

		self.COMObject = None
		self.CachedSelectedObjects = None

		# self.layoutSetup = None
		# self.layoutWeights = None
		# self.layoutBaking = None
	
	def UICreate(self, layoutMain):
		self.UILayoutSetup(layoutMain)
		self.UILayoutWeights(layoutMain)
		self.UILayoutBaking(layoutMain)
		cmds.separator(parent = layoutMain, height = Settings.separatorHeight, style = "none")
	
	def UILayoutSetup(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "设置", collapsable = True, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		countCells = 4
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCells, cellWidth = Settings.windowWidthMargin / countCells, cellHeight = Settings.lineHeight)
		cmds.button(label = "创建", command = self.COMCreate, backgroundColor = Colors.green50, annotation = CenterOfMassAnnotations.create)
		cmds.button(label = "激活", command = self.COMActivate, backgroundColor = Colors.yellow50, annotation = CenterOfMassAnnotations.activate)
		cmds.button(label = "选择", command = self.COMSelect, backgroundColor = Colors.lightBlue50, annotation = CenterOfMassAnnotations.select)
		cmds.button(label = "清除", command = self.COMClean, backgroundColor = Colors.red50, annotation = CenterOfMassAnnotations.clean)
		
		cmds.rowLayout(parent = layoutColumn, numberOfColumns = 4, columnWidth4 = (110, 40, 40, 40), columnAlign = [(1, "right"), (2, "center"), (3, "center"), (4, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0), (4, "both", 0)])
		cmds.text(label = "投影到平面")
		cmds.button(label = "YZ", command = partial(self.COMFloorProjection, "x"), backgroundColor = Colors.red10, annotation = CenterOfMassAnnotations.projectorYZ)
		cmds.button(label = "XZ", command = partial(self.COMFloorProjection, "y"), backgroundColor = Colors.green10, annotation = CenterOfMassAnnotations.projectorXZ)
		cmds.button(label = "XY", command = partial(self.COMFloorProjection, "z"), backgroundColor = Colors.blue10, annotation = CenterOfMassAnnotations.projectorXY)
	def UILayoutWeights(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "权重", collapsable = True, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)

		countCells1 = 1
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCells1, cellWidth = Settings.windowWidthMargin / countCells1, cellHeight = Settings.lineHeight)
		cmds.button(label = "断开与质心的连接", command = self.COMDisconnectTargets, backgroundColor = Colors.red10, annotation = CenterOfMassAnnotations.disconnectTargets)
		
		def PartButton(partInfo = ("", 0), minMaxValue = CenterOfMassSettings.weightMinMax, onlyValue = False, annotation = ""):
			value = partInfo[1]
			text = "{1}" if onlyValue else "{0} {1}"
			colorValue = 1 - (value / (minMaxValue[1] - minMaxValue[0]))
			colorFinal = (colorValue, colorValue, colorValue)
			cmds.button(label = text.format(partInfo[0], value), command = partial(self.COMConstrainToSelected, value), backgroundColor = colorFinal, annotation = annotation)

		### WEIGHTS PALETTE
		countCells2 = 10
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCells2, cellWidth = Settings.windowWidthMargin / countCells2, cellHeight = Settings.lineHeight)
		
		def CustomButton(value):
			PartButton(("", value), onlyValue = True, annotation = CenterOfMassAnnotations.weightsCustom)
		
		CustomButton(1)
		CustomButton(2)
		CustomButton(3)
		CustomButton(4)
		CustomButton(5)
		CustomButton(6)
		CustomButton(7)
		CustomButton(8)
		CustomButton(9)
		CustomButton(10)

		### BODYPARTS
		countCells3 = 3
		layoutBodyGrid = cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCells3, cellWidth = Settings.windowWidthMargin / countCells3, cellHeight = Settings.lineHeight * countCells3)
		
		cmds.columnLayout(parent = layoutBodyGrid, adjustableColumn = True)
		PartButton(CenterOfMassSettings.partHead, minMaxValue = (CenterOfMassSettings.partHand[1], CenterOfMassSettings.partChest[1]), annotation = CenterOfMassAnnotations.weightHead)
		PartButton(CenterOfMassSettings.partChest, minMaxValue = (CenterOfMassSettings.partHand[1], CenterOfMassSettings.partChest[1]), annotation = CenterOfMassAnnotations.weightChest)
		PartButton(CenterOfMassSettings.partAbdomen, minMaxValue = (CenterOfMassSettings.partHand[1], CenterOfMassSettings.partChest[1]), annotation = CenterOfMassAnnotations.weightAbdomen)
		
		cmds.columnLayout(parent = layoutBodyGrid, adjustableColumn = True)
		PartButton(CenterOfMassSettings.partShoulder, minMaxValue = (CenterOfMassSettings.partHand[1], CenterOfMassSettings.partChest[1]), annotation = CenterOfMassAnnotations.weightShoulder)
		PartButton(CenterOfMassSettings.partElbow, minMaxValue = (CenterOfMassSettings.partHand[1], CenterOfMassSettings.partChest[1]), annotation = CenterOfMassAnnotations.weightElbow)
		PartButton(CenterOfMassSettings.partHand, minMaxValue = (CenterOfMassSettings.partHand[1], CenterOfMassSettings.partChest[1]), annotation = CenterOfMassAnnotations.weightHand)
		
		cmds.columnLayout(parent = layoutBodyGrid, adjustableColumn = True)
		PartButton(CenterOfMassSettings.partThigh, minMaxValue = (CenterOfMassSettings.partHand[1], CenterOfMassSettings.partChest[1]), annotation = CenterOfMassAnnotations.weightThigh)
		PartButton(CenterOfMassSettings.partKnee, minMaxValue = (CenterOfMassSettings.partHand[1], CenterOfMassSettings.partChest[1]), annotation = CenterOfMassAnnotations.weightKnee)
		PartButton(CenterOfMassSettings.partFoot, minMaxValue = (CenterOfMassSettings.partHand[1], CenterOfMassSettings.partChest[1]), annotation = CenterOfMassAnnotations.weightFoot)
	def UILayoutBaking(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "烘焙", collapsable = True, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)

		countCells = 3
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCells, cellWidth = Settings.windowWidthMargin / countCells, cellHeight = Settings.lineHeight)

		cmds.button(label = "烘焙到质心", command = self.BakeScenario3, backgroundColor = Colors.orange10, annotation = CenterOfMassAnnotations.bakeToCOMLink)
		cmds.popupMenu()
		cmds.menuItem(label = "不带约束", command = self.BakeScenario2)
		cmds.button(label = "烘焙回去", command = self.BakeCached, backgroundColor = Colors.orange50, annotation = CenterOfMassAnnotations.bakeOriginal)
		cmds.button(label = "选择根", command = self.SelectParent, backgroundColor = Colors.lightBlue10, annotation = CenterOfMassAnnotations.selectRoot)


	### CENTER OF MASS
	def COMObjectCheck(self, *args):
		if self.COMObject is None:
			cmds.warning("Center of mass doesn't stored in the script memory. You need to create new COM object or select one in the scene and press \"Activate\" button")
			return False
		else:
			if (cmds.objExists(self.COMObject)):
				return True
			else:
				cmds.warning("Center of mass stored in the script memory, but doesn't exist in the scene. You need to create new COM object or select one in the scene and press \"Activate\" button")
				return False
	def COMCreate(self, *args):
		# self.centerOfMass = cmds.polySphere(name = "myCenterOfMass", subdivisionsX = 8, subdivisionsY = 6, radius = 10)
		# self.centerOfMass = Locators.Create("locCenterOfMass", 5)
		# self.COMObjectRef = cmds.polyPrimitive(name = "objCenterOfMass", radius = CenterOfMassSettings.COMRadius, polyType = 0, constructionHistory = 0)
		# cmds.polySoftEdge(angle = 0, constructionHistory = 0)
		# self.COMGroupRef = cmds.group(name = "grpCenterOfMass")
		
		cmds.select(clear = True)
		self.COMObject = cmds.joint(name = Text.SetUniqueFromText("objCenterOfMass"), radius = CenterOfMassSettings.COMRadius)
		cmds.setAttr(self.COMObject + ".drawLabel", 1)
		cmds.setAttr(self.COMObject + ".type", 18)
		cmds.setAttr(self.COMObject + ".otherType", "Center Of Mass", type = "string")
		cmds.select(self.COMObject)
	def COMActivate(self, *args):
		# Check selected objects
		selectedList = Selector.MultipleObjects(1)
		if selectedList is None:
			return
		self.COMObject = selectedList[0]
	def COMSelect(self, *args):
		if (self.COMObjectCheck()):
			cmds.select(self.COMObject)
	def COMClean(self, *args):
		if self.COMObjectCheck():
			cmds.delete(self.COMObject)
			self.COMObject = None
			cmds.warning("Last active center of mass object was deleted")
	def COMFloorProjection(self, skipAxis="y", *args):
		if not self.COMObjectCheck():
			return

		name = "COM" + "Projection" + "xyz".replace(skipAxis, "").upper()
		projection = cmds.polyPrimitive(name = Text.SetUniqueFromText(name), radius = CenterOfMassSettings.COMRadius, polyType = 0, constructionHistory = 0)
		cmds.polySoftEdge(angle = 0, constructionHistory = 0)

		cmds.setAttr(projection[0] + "Shape" + ".visibility", 0)
		cmds.setAttr(projection[0] + "Shape" + ".overrideEnabled", 1)
		cmds.setAttr(projection[0] + "Shape" + ".overrideDisplayType", 2)

		cmds.select(clear = True)

		cmds.pointConstraint(self.COMObject, projection, maintainOffset = False, skip = skipAxis)

		joint1 = cmds.joint(name = Text.SetUniqueFromText("objCenterOfMassFloorProjectionJoint1"), radius = 1)
		joint2 = cmds.joint(name = Text.SetUniqueFromText("objCenterOfMassFloorProjectionJoint2"), radius = 1)
		cmds.pointConstraint(self.COMObject, joint1, maintainOffset = False)
		cmds.pointConstraint(projection, joint2, maintainOffset = False)
		cmds.setAttr(joint1 + ".overrideEnabled", 1)
		cmds.setAttr(joint2 + ".overrideEnabled", 1)
		cmds.setAttr(joint1 + ".overrideDisplayType", 2)
		cmds.setAttr(joint2 + ".overrideDisplayType", 2)
		cmds.parent(joint1, projection)

		cmds.select(clear = True)
	def COMConstrainToSelected(self, weight, *args):
		if not self.COMObjectCheck():
			return
		
		# Check selected objects
		selectedList = Selector.MultipleObjects(minimalCount = 1)
		if selectedList is None:
			return
		
		finalList = []
		finalList.append(self.COMObject)
		finalList.append(selectedList)

		Constraints.ConstrainListToLastElement(selected = finalList, maintainOffset = False, parent = False, point = True, weight = weight)
	def COMDisconnectTargets(self, *args):
		if (self.COMObject is None or not cmds.objExists(self.COMObject)):
			cmds.warning("Center Of Mass object is not connected to script. Please select Center Of Mass object and press Activate button before")
			return

		selectedList = Selector.MultipleObjects(1)
		if selectedList is None:
			return
		
		selectedList.append(self.COMObject)
		Constraints.DisconnectTargetsFromConstraint(selectedList)
		cmds.select(selectedList[:-1], replace = True)


	### BAKING
	def BakeScenario2(self, *args):
		if (not self.COMObjectCheck()):
			return
		
		cmds.select(self.COMObject, add = True)
		selectedList = cmds.ls(selection = True)

		if (len(selectedList) == 1):
			cmds.warning("Need to select at least 1 object (except CenterOfMass joint)")
			cmds.select(clear = True)
			return

		self.CachedSelectedObjects = Locators.CreateAndBakeAsChildrenFromLastSelected(euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
		return self.CachedSelectedObjects
	def BakeScenario3(self, *args):
		objects = self.BakeScenario2()
		if objects is None:
			return None
		
		self.LinkCached(maintainOffset = False)
		
		return objects
	def BakeCached(self, *args):
		if self.CachedSelectedObjects is None:
			cmds.warning("No cached objects yet, operation cancelled")
			return
		
		cmds.select(self.CachedSelectedObjects[0][0:-1])
		Baker.BakeSelected(euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
		cmds.delete(self.CachedSelectedObjects[1][-1])
	
	def LinkCached(self, maintainOffset=False, *args):
		if self.CachedSelectedObjects is None:
			cmds.warning("No cached objects yet, operation cancelled")
			return

		for i in range(len(self.CachedSelectedObjects[0])):
			if (i == len(self.CachedSelectedObjects[0]) - 1):
				return
			Constraints.ConstrainSecondToFirstObject(self.CachedSelectedObjects[1][i], self.CachedSelectedObjects[0][i], maintainOffset = maintainOffset)
	def SelectParent(self, *args):
		if self.CachedSelectedObjects is None:
			cmds.warning("No cached objects yet, operation cancelled")
			return
		try:
			cmds.select(self.CachedSelectedObjects[1][-1])
		except:
			cmds.warning("Cached object not found")

