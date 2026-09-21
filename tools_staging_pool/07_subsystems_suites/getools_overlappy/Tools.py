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
from ..utils import Animation
from ..utils import Baker
from ..utils import ChainDistributionRig
from ..utils import Colors
from ..utils import Locators
from ..utils import Selector
from ..utils import Timeline
from ..values import Enums


class ToolsAnnotations:
	_onlyForTranslation = "仅用于位移"
	_onlyForRotation = "仅用于旋转"

	### Locators
	_rightClick = "右键更多选项"
	locatorScale = "缩放选中定位器"
	locatorScale50 = "{0} 0.5\n{1}".format(locatorScale, _rightClick)
	locatorScale90 = "{0} 0.9\n{1}".format(locatorScale, _rightClick)
	locatorScale110 = "{0} 1.1\n{1}".format(locatorScale, _rightClick)
	locatorScale200 = "{0} 2.0\n{1}".format(locatorScale, _rightClick)
	locatorSizeGet = "获取选中定位器近似大小"
	locatorSizeSet = "设置选中定位器大小\n右键选择具体缩放值"
	locatorSize = "创建定位器大小"
	#
	hideParent = "隐藏父级定位器\n建议与'子定位器'选项一起使用"
	subLocator = "在主定位器内创建额外定位器用于局部控制"
	locator = "在世界原点创建新定位器"
	locatorMatch = "创建并匹配定位器到选中对象"
	locatorParent = "创建并约束定位器到选中对象"
	locatorsBake = "在选中对象上创建定位器并烘焙动画"
	_reverseConstraint = "之后将原始对象约束回定位器"
	locatorsBakeReverse = "{bake}\n{reverse}".format(bake = locatorsBake, reverse = _reverseConstraint)
	locatorsBakeReversePos = "{0}\n{1}".format(_onlyForTranslation, locatorsBakeReverse)
	locatorsBakeReverseRot = "{0}\n{1}".format(_onlyForRotation, locatorsBakeReverse)
	#
	locatorsRelative = "{bake}\n最后一个定位器成为其他定位器的父级".format(bake = locatorsBake)
	locatorsRelativeReverse = "{relative}\n{reverse}\n右键可烘焙相同操作但约束最后一个对象".format(relative = locatorsRelative, reverse = _reverseConstraint)
	#
	chainDistribution = "创建带分布旋转的链。使用最后一个定位器动画。\n最好选择3个对象。\n选择4+个对象时，原始动画可能无法完全保留。\n\n右键使用替代模式，可保留100%原始动画。\n不如默认模式方便。"
	
	locatorAimSpace = "目标空间偏移\n非零值效果最佳"
	locatorAimSpaceBakeAll = "为选中对象创建目标空间定位器\n原始对象将约束回定位器"
	locatorAimSpaceBakeRotate = "{0}\n{1}".format(_onlyForRotation, locatorAimSpaceBakeAll)

	### Bake
	bakeSamples = "烘焙采样率，每N帧烘焙一次\n默认值1\n最小值0.001"
	_bakeCutOutside = "移除时间范围外的关键帧"
	bakeClassic = "标准Maya烘焙"
	bakeClassicCut = "{0}\n{1}".format(bakeClassic, _bakeCutOutside)
	bakeByLast = "相对于最后选中对象烘焙"
	bakeByLastPos = "{0}\n{1}".format(_onlyForTranslation, bakeByLast)
	bakeByLastRot = "{0}\n{1}".format(_onlyForRotation, bakeByLast)
	bakeByWorld = "相对于世界空间烘焙"
	bakeByWorldPos = "{0}\n{1}".format(_onlyForTranslation, bakeByWorld)
	bakeByWorldRot = "{0}\n{1}".format(_onlyForRotation, bakeByWorld)

	### Animation
	deleteAnimation = "删除选中对象动画\n高亮通道盒属性删除\n高亮时间轴范围删除特定范围\n未高亮则删除所有动画"
	deleteNonkeyableKeys = "删除选中对象不可关键帧属性的动画"
	deleteStaticCurves = "删除选中对象所有静态曲线"
	filterCurve = "欧拉过滤曲线，修复曲线问题"
	animationCurveInfinity = "曲线无限"

	timelineSetMinOut = "设置最小外时间值"
	timelineSetMinIn = "设置最小内时间值"
	timelineSetMaxIn = "设置最大内时间值"
	timelineSetMaxOut = "设置最大外时间值"
	timelineFocusOut = "聚焦外时间范围"
	timelineFocusIn = "聚焦内时间范围"
	timelineSetRange = "设置时间轴内范围到选中范围"

	desync = "按顺序错开选中对象动画曲线\n适用于通道盒属性"
	desyncSetValue = "设置预定义步长值"
	desyncIncrementValue = "步长值加1"
	desyncValue = "动画错开步长值"

class ToolsSettings:
	locatorSize = 10

	### Aim Space
	aimSpaceOffsetValue = 100
	aimSpaceRadioButtonDefault = 0

class Tools:
	_version = "v1.5"
	_name = "工具"
	_title = _name + " " + _version

	def __init__(self, options):
		self.optionsPlugin = options
		### Check Maya version to avoid cycle import, Maya 2020 and older can't use cycle import
		if cmds.about(version = True) in ["2022", "2023", "2024", "2025"]:
			from ..modules import Options
			if isinstance(options, Options.PluginVariables):
				self.optionsPlugin = options

		self.checkboxLocatorHideParent = None
		self.checkboxLocatorSubLocator = None
		self.floatLocatorSize = None
		### Locator Aim Space
		self.aimSpaceFloatField = None
		self.aimSpaceRadioButtons = [None, None, None]
		self.aimSpaceCheckbox = None
		### Desync
		self.desyncFloatField = None

		self.bakingSamplesValue = None

	def UICreate(self, layoutMain):
		# layoutColumn = cmds.columnLayout(parent = layoutMain, adjustableColumn = True) # TODO remove ghost empty spacing when collapse
		self.UILayoutLocators(layoutMain)
		self.UILayoutBaking(layoutMain)
		self.UILayoutAnimation(layoutMain)
		self.UILayoutTimeline(layoutMain)
		cmds.separator(parent = layoutMain, height = Settings.separatorHeight, style = "none")
	
	def UILayoutLocators(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "定位器 // 空间切换", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		### LOCATORS SIZE
		countCells1 = 6
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCells1, cellWidth = Settings.windowWidthMargin / countCells1, cellHeight = Settings.lineHeight)
		cmds.button(label = "50%", command = partial(Locators.SelectedLocatorsSizeScale, 0.5), backgroundColor = Colors.blackWhite50, annotation = ToolsAnnotations.locatorScale50)
		cmds.popupMenu()
		cmds.menuItem(label = "10%", command = partial(Locators.SelectedLocatorsSizeScale, 0.1))
		cmds.menuItem(label = "20%", command = partial(Locators.SelectedLocatorsSizeScale, 0.2))
		cmds.menuItem(label = "30%", command = partial(Locators.SelectedLocatorsSizeScale, 0.3))
		cmds.menuItem(label = "40%", command = partial(Locators.SelectedLocatorsSizeScale, 0.4))
		cmds.button(label = "90%", command = partial(Locators.SelectedLocatorsSizeScale, 0.9), backgroundColor = Colors.blackWhite50, annotation = ToolsAnnotations.locatorScale90)
		cmds.popupMenu()
		cmds.menuItem(label = "99%", command = partial(Locators.SelectedLocatorsSizeScale, 0.99))
		cmds.button(label = "110%", command = partial(Locators.SelectedLocatorsSizeScale, 1.1), backgroundColor = Colors.blackWhite70, annotation = ToolsAnnotations.locatorScale110)
		cmds.popupMenu()
		cmds.menuItem(label = "101%", command = partial(Locators.SelectedLocatorsSizeScale, 1.01))
		cmds.button(label = "200%", command = partial(Locators.SelectedLocatorsSizeScale, 2), backgroundColor = Colors.blackWhite70, annotation = ToolsAnnotations.locatorScale200)
		cmds.popupMenu()
		cmds.menuItem(label = "500%", command = partial(Locators.SelectedLocatorsSizeScale, 5))
		cmds.menuItem(label = "1000%", command = partial(Locators.SelectedLocatorsSizeScale, 10))
		cmds.menuItem(label = "2000%", command = partial(Locators.SelectedLocatorsSizeScale, 20))
		cmds.button(label = "获取", command = self.GetLocatorSize, backgroundColor = Colors.blackWhite100, annotation = ToolsAnnotations.locatorSizeGet)
		cmds.button(label = "设置", command = self.SelectedLocatorsSizeSetValue, backgroundColor = Colors.blackWhite100, annotation = ToolsAnnotations.locatorSizeSet)
		cmds.popupMenu()
		cmds.menuItem(label = "0.1", command = partial(Locators.SelectedLocatorsSizeSet, 0.1))
		cmds.menuItem(label = "0.5", command = partial(Locators.SelectedLocatorsSizeSet, 0.5))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "1", command = partial(Locators.SelectedLocatorsSizeSet, 1))
		cmds.menuItem(label = "5", command = partial(Locators.SelectedLocatorsSizeSet, 5))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "10", command = partial(Locators.SelectedLocatorsSizeSet, 10))
		cmds.menuItem(label = "50", command = partial(Locators.SelectedLocatorsSizeSet, 50))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "100", command = partial(Locators.SelectedLocatorsSizeSet, 100))
		cmds.menuItem(label = "500", command = partial(Locators.SelectedLocatorsSizeSet, 500))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "1000", command = partial(Locators.SelectedLocatorsSizeSet, 1000))
		cmds.menuItem(label = "5000", command = partial(Locators.SelectedLocatorsSizeSet, 5000))
		# cmds.setParent("..")

		### OPTIONS
		cmds.rowLayout(parent = layoutColumn, adjustableColumn = 4, numberOfColumns = 4, columnWidth4 = (80, 80, 35, 40), columnAlign = [(1, "center"), (2, "center"), (3, "right"), (4, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0), (4, "both", 0)])
		self.checkboxLocatorHideParent = cmds.checkBox(label = "隐藏父级", value = False, annotation = ToolsAnnotations.hideParent)
		self.checkboxLocatorSubLocator = cmds.checkBox(label = "子定位器", value = False, annotation = ToolsAnnotations.subLocator)
		cmds.text(label = "大小 ", annotation = ToolsAnnotations.locatorSize)
		self.floatLocatorSize = cmds.floatField(value = ToolsSettings.locatorSize, precision = 3, annotation = ToolsAnnotations.locatorSize)
		# cmds.setParent("..")

		### LOCATORS ROW 1
		countCells2 = 6
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCells2, cellWidth = Settings.windowWidthMargin / countCells2, cellHeight = Settings.lineHeight)
		cmds.button(label = "定位器", command = self.Locator, backgroundColor = Colors.green10, annotation = ToolsAnnotations.locator)
		cmds.button(label = "匹配", command = self.LocatorsMatch, backgroundColor = Colors.green10, annotation = ToolsAnnotations.locatorMatch)
		cmds.button(label = "父级", command = self.LocatorsParent, backgroundColor = Colors.green10, annotation = ToolsAnnotations.locatorParent)
		cmds.button(label = "固定", command = partial(self.LocatorsBakeReverse, True, True), backgroundColor = Colors.yellow50, annotation = ToolsAnnotations.locatorsBakeReverse)
		cmds.popupMenu()
		cmds.menuItem(label = "无反向约束", command = self.LocatorsBake)
		cmds.button(label = "P-位移", command = partial(self.LocatorsBakeReverse, True, False), backgroundColor = Colors.yellow50, annotation = ToolsAnnotations.locatorsBakeReversePos)
		cmds.button(label = "P-旋转", command = partial(self.LocatorsBakeReverse, False, True), backgroundColor = Colors.yellow50, annotation = ToolsAnnotations.locatorsBakeReverseRot)
		# cmds.setParent("..")

		### LOCATORS ROW 2
		cmds.rowLayout(parent = layoutColumn, adjustableColumn = 1, numberOfColumns = 2, columnWidth2 = (50, 150), columnAlign = [(1, "center"), (2, "center")], columnAttach = [(1, "both", 0), (2, "both", 0)])
		cmds.button(label = "相对", command = self.LocatorsRelativeReverse, backgroundColor = Colors.orange10, annotation = ToolsAnnotations.locatorsRelativeReverse)
		cmds.popupMenu()
		cmds.menuItem(label = "跳过最后对象反向约束", command = self.LocatorsRelativeReverseSkipLast)
		cmds.menuItem(label = "无反向约束", command = self.LocatorsRelative)
		cmds.button(label = "链分布", command = partial(self.CreateChainDistributionRig, 1), backgroundColor = Colors.purple10, annotation = ToolsAnnotations.chainDistribution)
		cmds.popupMenu()
		cmds.menuItem(label = "替代模式", command = partial(self.CreateChainDistributionRig, 2))
		# cmds.setParent("..")

		### AIM SPACE SWITCHING
		layoutAimSpace = cmds.frameLayout(parent = layoutColumn, label = "目标空间切换", labelIndent = 75, collapsable = False, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
		#
		cmds.rowLayout(parent = layoutAimSpace, adjustableColumn = 2, numberOfColumns = 6, columnWidth6 = (40, 40, 28, 28, 28, 60), columnAlign = [1, "right"], columnAttach = [(1, "both", 0)])
		cmds.text(label = "偏移 ")
		self.aimSpaceFloatField = cmds.floatField(value = ToolsSettings.aimSpaceOffsetValue, precision = 3, minValue = 0, annotation = ToolsAnnotations.locatorAimSpace)
		cmds.radioCollection()
		self.aimSpaceRadioButtons[0] = cmds.radioButton(label = "X")
		self.aimSpaceRadioButtons[1] = cmds.radioButton(label = "Y")
		self.aimSpaceRadioButtons[2] = cmds.radioButton(label = "Z")
		self.aimSpaceCheckbox = cmds.checkBox(label = "反向", value = False)
		cmds.radioButton(self.aimSpaceRadioButtons[ToolsSettings.aimSpaceRadioButtonDefault], edit = True, select = True)
		# cmds.setParent("..")
		#
		cmds.rowLayout(parent = layoutAimSpace, adjustableColumn = 1, numberOfColumns = 3, columnWidth3 = (30, 105, 105), columnAlign = [(1, "right"), (2, "center"), (3, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0)])
		cmds.text(label = "创建 ")
		cmds.button(label = "位移+旋转", command = partial(self.LocatorsBakeAim, False), backgroundColor = Colors.orange10, annotation = ToolsAnnotations.locatorAimSpaceBakeAll)
		cmds.button(label = "仅旋转", command = partial(self.LocatorsBakeAim, True), backgroundColor = Colors.orange10, annotation = ToolsAnnotations.locatorAimSpaceBakeRotate)
		# cmds.setParent("..")
	def UILayoutBaking(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "烘焙", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)

		rowLayout = cmds.rowLayout(parent = layoutColumn, adjustableColumn = 2, numberOfColumns = 3, columnWidth3 = (80, 40, 120), height = Settings.lineHeight, columnAlign = [(1, "right"), (2, "center"), (3, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0)])
		cmds.text(parent = rowLayout, label = "烘焙步长 ", annotation = ToolsAnnotations.locatorSize)
		self.bakingSamplesValue = cmds.floatField(parent = rowLayout, value = 1, precision = 3, minValue = 0.001, annotation = ToolsAnnotations.bakeSamples)
		cmds.gridLayout(parent = rowLayout, numberOfColumns = 6, cellWidth = 20, cellHeight = Settings.lineHeight)
		cmds.button(label = "-", command = partial(self.BakeSamplesAdd, -1), backgroundColor = Colors.blackWhite70, annotation = ToolsAnnotations.bakeSamples)
		cmds.button(label = "+", command = partial(self.BakeSamplesAdd, 1), backgroundColor = Colors.blackWhite70, annotation = ToolsAnnotations.bakeSamples)
		cmds.button(label = "1", command = partial(self.BakeSamplesSet, 1), backgroundColor = Colors.lightBlue10, annotation = ToolsAnnotations.bakeSamples)
		cmds.button(label = "2", command = partial(self.BakeSamplesSet, 2), backgroundColor = Colors.lightBlue10, annotation = ToolsAnnotations.bakeSamples)
		cmds.button(label = "3", command = partial(self.BakeSamplesSet, 3), backgroundColor = Colors.lightBlue10, annotation = ToolsAnnotations.bakeSamples)
		cmds.button(label = "4", command = partial(self.BakeSamplesSet, 4), backgroundColor = Colors.lightBlue10, annotation = ToolsAnnotations.bakeSamples)
		
		countCells1 = 2
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCells1, cellWidth = Settings.windowWidthMargin / countCells1, cellHeight = Settings.lineHeight)
		cmds.button(label = "标准烘焙", command = self.BakeSelectedClassic, backgroundColor = Colors.orange10, annotation = ToolsAnnotations.bakeClassic)
		cmds.popupMenu()
		cmds.menuItem(label = "自定义", command = self.BakeSelectedCustom)
		cmds.button(label = "标准烘焙裁剪", command = self.BakeSelectedClassicCut, backgroundColor = Colors.orange10, annotation = ToolsAnnotations.bakeClassicCut)
		cmds.popupMenu()
		cmds.menuItem(label = "自定义", command = self.BakeSelectedCustomCut)

		countCells2 = 6
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCells2, cellWidth = Settings.windowWidthMargin / countCells2, cellHeight = Settings.lineHeight)
		cmds.button(label = "相对最后", command = partial(self.BakeSelectedByLastObject, True, True), backgroundColor = Colors.orange100, annotation = ToolsAnnotations.bakeByLast)
		cmds.button(label = "BL-位移", command = partial(self.BakeSelectedByLastObject, True, False), backgroundColor = Colors.orange100, annotation = ToolsAnnotations.bakeByLastPos)
		cmds.button(label = "BL-旋转", command = partial(self.BakeSelectedByLastObject, False, True), backgroundColor = Colors.orange100, annotation = ToolsAnnotations.bakeByLastRot)
		cmds.button(label = "世界", command = partial(self.BakeSelectedByWorld, True, True), backgroundColor = Colors.yellow50, annotation = ToolsAnnotations.bakeByWorld)
		cmds.button(label = "W-位移", command = partial(self.BakeSelectedByWorld, True, False), backgroundColor = Colors.yellow50, annotation = ToolsAnnotations.bakeByWorldPos)
		cmds.button(label = "W-旋转", command = partial(self.BakeSelectedByWorld, False, True), backgroundColor = Colors.yellow50, annotation = ToolsAnnotations.bakeByWorldRot)
	def UILayoutAnimation(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "动画", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		cmds.rowLayout(parent = layoutColumn, numberOfColumns = 4, columnWidth4 = (80, 35, 75, 50), columnAlign = [(1, "right"), (2, "center"), (3, "center"), (4, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0), (4, "both", 0)])
		cmds.text(label = "删除关键帧 ")
		cmds.button(label = "全部", command = partial(Animation.DeleteKeys, True), backgroundColor = Colors.red100, annotation = ToolsAnnotations.deleteAnimation)
		cmds.button(label = "不可关键", command = Animation.DeleteKeysNonkeyable, backgroundColor = Colors.red50, annotation = ToolsAnnotations.deleteNonkeyableKeys)
		cmds.button(label = "静态", command = Animation.DeleteStaticCurves, backgroundColor = Colors.red10, annotation = ToolsAnnotations.deleteStaticCurves)
		#
		countCellsEuler = 1
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCellsEuler, cellWidth = Settings.windowWidthMargin / countCellsEuler, cellHeight = Settings.lineHeight)
		cmds.button(label = "欧拉过滤", command = Animation.EulerFilterOnSelected, backgroundColor = Colors.yellow10, annotation = ToolsAnnotations.filterCurve)
		#
		countCellsInfinity = 5
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countCellsInfinity, cellWidth = Settings.windowWidthMargin / countCellsInfinity, cellHeight = Settings.lineHeight)
		cmds.button(label = "恒定", command = partial(Animation.SetInfinity, 1, None), backgroundColor = Colors.blue10, annotation = ToolsAnnotations.animationCurveInfinity)
		cmds.button(label = "线性", command = partial(Animation.SetInfinity, 2, None), backgroundColor = Colors.blue10, annotation = ToolsAnnotations.animationCurveInfinity)
		cmds.button(label = "循环", command = partial(Animation.SetInfinity, 3, None), backgroundColor = Colors.blue50, annotation = ToolsAnnotations.animationCurveInfinity)
		cmds.button(label = "偏移", command = partial(Animation.SetInfinity, 4, None), backgroundColor = Colors.blue50, annotation = ToolsAnnotations.animationCurveInfinity)
		cmds.button(label = "振荡", command = partial(Animation.SetInfinity, 5, None), backgroundColor = Colors.blue100, annotation = ToolsAnnotations.animationCurveInfinity)
		#

		### Desync
		cmds.frameLayout(parent = layoutColumn, label = "错开", labelIndent = 110, collapsable = False, backgroundColor = Settings.frames2Color, marginWidth = 0, marginHeight = 0)
		rowLayout = cmds.rowLayout(adjustableColumn = 2, numberOfColumns = 4, columnWidth4 = (120, 30, 30, 70), columnAlign = [(1, "center"), (2, "center"), (3, "right"), (4, "center")], columnAttach = [(1, "both", 0), (2, "both", 0), (3, "both", 0), (4, "both", 0)])
		# 1
		cmds.gridLayout(parent = rowLayout, numberOfColumns = 6, cellWidth = 20, cellHeight = Settings.lineHeight)
		cmds.button(label = "0.1", command = partial(self.AnimationOffsetSetValue, 0.1), backgroundColor = Colors.blackWhite90, annotation = ToolsAnnotations.desyncSetValue)
		cmds.button(label = "0.5", command = partial(self.AnimationOffsetSetValue, 0.5), backgroundColor = Colors.blackWhite90, annotation = ToolsAnnotations.desyncSetValue)
		cmds.button(label = "1", command = partial(self.AnimationOffsetSetValue, 1), backgroundColor = Colors.blackWhite90, annotation = ToolsAnnotations.desyncSetValue)
		cmds.button(label = "4", command = partial(self.AnimationOffsetSetValue, 4), backgroundColor = Colors.blackWhite90, annotation = ToolsAnnotations.desyncSetValue)
		cmds.button(label = "-", command = self.AnimationOffsetAddValueNegative, backgroundColor = Colors.blackWhite70, annotation = ToolsAnnotations.desyncIncrementValue)
		cmds.button(label = "+", command = self.AnimationOffsetAddValuePositive, backgroundColor = Colors.blackWhite70, annotation = ToolsAnnotations.desyncIncrementValue)
		# 2
		self.desyncFloatField = cmds.floatField(parent = rowLayout, value = 1, precision = 3, minValue = 0, annotation = ToolsAnnotations.desyncValue)
		# 3
		cmds.text(parent = rowLayout, label = "移动 ", annotation = ToolsAnnotations.desync)
		# 4
		cmds.gridLayout(parent = rowLayout, numberOfColumns = 2, cellWidth = 35, cellHeight = Settings.lineHeight)
		cmds.button(label = "左", command = self.AnimationOffsetMoveLeft, backgroundColor = Colors.red50, annotation = ToolsAnnotations.desync)
		cmds.button(label = "右", command = self.AnimationOffsetMoveRight, backgroundColor = Colors.green50, annotation = ToolsAnnotations.desync)
	def UILayoutTimeline(self, layoutMain):
		cmds.frameLayout(parent = layoutMain, label = Settings.frames2Prefix + "时间轴", collapsable = True, backgroundColor = Settings.frames2Color, highlightColor = Colors.green100, marginWidth = 0, marginHeight = 0, borderVisible = True)
		layoutColumn = cmds.columnLayout(adjustableColumn = True, rowSpacing = Settings.columnLayoutRowSpacing)
		
		countOffsets = 7
		cmds.gridLayout(parent = layoutColumn, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.button(label = "<<", command = partial(Timeline.SetTime, 3), backgroundColor = Colors.green10, annotation = ToolsAnnotations.timelineSetMinOut)
		cmds.button(label = "<-", command = partial(Timeline.SetTime, 1), backgroundColor = Colors.green50, annotation = ToolsAnnotations.timelineSetMinIn)
		cmds.button(label = "->", command = partial(Timeline.SetTime, 2), backgroundColor = Colors.green50, annotation = ToolsAnnotations.timelineSetMaxIn)
		cmds.button(label = ">>", command = partial(Timeline.SetTime, 4), backgroundColor = Colors.green10, annotation = ToolsAnnotations.timelineSetMaxOut)
		cmds.button(label = "<->", command = partial(Timeline.SetTime, 5), backgroundColor = Colors.orange10, annotation = ToolsAnnotations.timelineFocusOut)
		cmds.button(label = ">-<", command = partial(Timeline.SetTime, 6), backgroundColor = Colors.orange10, annotation = ToolsAnnotations.timelineFocusIn)
		cmds.button(label = "|<->|", command = partial(Timeline.SetTime, 7), backgroundColor = Colors.orange50, annotation = ToolsAnnotations.timelineSetRange)


	### LOCATORS
	def GetFloatLocatorSize(self):
		return cmds.floatField(self.floatLocatorSize, query = True, value = True)

	def GetLocatorSize(self, *args):
		selectedList = Selector.MultipleObjects(1)
		if (selectedList == None):
			return None

		values = []
		for item in selectedList:
			shape = cmds.listRelatives(item, shapes = True, type = Enums.Types.locator)[0]
			if (shape != None):
				values.append(Locators.GetSize(item))
		
		count = len(values)
		if (count == 0):
			cmds.warning("Locators are not detected in selected objects")
			return

		approximate = [0, 0, 0]
		for i in range(count):
			approximate[0] = approximate[0] + values[i][0]
			approximate[1] = approximate[1] + values[i][1]
			approximate[2] = approximate[2] + values[i][2]

		approximate[0] = approximate[0] / count
		approximate[1] = approximate[1] / count
		approximate[2] = approximate[2] / count

		result = (approximate[0] + approximate[1] + approximate[2]) / 3
		cmds.floatField(self.floatLocatorSize, edit = True, value = result)
	def SelectedLocatorsSizeSetValue(self, *args):
		Locators.SelectedLocatorsSizeSet(value = self.GetFloatLocatorSize())

	def GetCheckboxLocatorHideParent(self):
		return cmds.checkBox(self.checkboxLocatorHideParent, query = True, value = True)
	def GetCheckboxLocatorSubLocator(self):
		return cmds.checkBox(self.checkboxLocatorSubLocator, query = True, value = True)

	def Locator(self, *args):
		Locators.Create(scale = self.GetFloatLocatorSize(), hideParent = self.GetCheckboxLocatorHideParent(), subLocator = self.GetCheckboxLocatorSubLocator())
	def LocatorsMatch(self, *args):
		Locators.CreateOnSelected(scale = self.GetFloatLocatorSize(), hideParent = self.GetCheckboxLocatorHideParent(), subLocator = self.GetCheckboxLocatorSubLocator())
	def LocatorsParent(self, *args):
		Locators.CreateOnSelected(scale = self.GetFloatLocatorSize(), hideParent = self.GetCheckboxLocatorHideParent(), subLocator = self.GetCheckboxLocatorSubLocator(), constraint = True)
	
	def LocatorsBake(self, *args):
		Locators.CreateOnSelected(scale = self.GetFloatLocatorSize(), hideParent = self.GetCheckboxLocatorHideParent(), subLocator = self.GetCheckboxLocatorSubLocator(), constraint = True, bake = True)
	def LocatorsBakeReverse(self, translate=True, rotate=True, *args): # TODO , channelBox = False
		Locators.CreateOnSelected(scale = self.GetFloatLocatorSize(), hideParent = self.GetCheckboxLocatorHideParent(), subLocator = self.GetCheckboxLocatorSubLocator(), constraint = True, bake = True, constrainReverse = True, constrainTranslate = translate, constrainRotate = rotate)
	
	def LocatorsRelative(self, *args):
		Locators.CreateAndBakeAsChildrenFromLastSelected(scale = self.GetFloatLocatorSize(), hideParent = self.GetCheckboxLocatorHideParent(), subLocator = self.GetCheckboxLocatorSubLocator(), euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
	def LocatorsRelativeReverseSkipLast(self, *args):
		Locators.CreateAndBakeAsChildrenFromLastSelected(scale = self.GetFloatLocatorSize(), hideParent = self.GetCheckboxLocatorHideParent(), subLocator = self.GetCheckboxLocatorSubLocator(), constraintReverse = True, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
	def LocatorsRelativeReverse(self, *args):
		Locators.CreateAndBakeAsChildrenFromLastSelected(scale = self.GetFloatLocatorSize(), hideParent = self.GetCheckboxLocatorHideParent(), subLocator = self.GetCheckboxLocatorSubLocator(), constraintReverse = True, skipLastReverse = False, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
	
	def LocatorsBakeAim(self, rotateOnly=False, *args):
		scale = self.GetFloatLocatorSize()
		distance = cmds.floatField(self.aimSpaceFloatField, query = True, value = True)
		hideParent = self.GetCheckboxLocatorHideParent()
		subLocators = self.GetCheckboxLocatorSubLocator()
		reverse = cmds.checkBox(self.aimSpaceCheckbox, query = True, value = True)

		### Compile value and return
		valueAimTarget = 1 * (-1 if reverse else 1)
		if (cmds.radioButton(self.aimSpaceRadioButtons[0], query = True, select = True)):
			axisVector = [valueAimTarget, 0, 0]
		if (cmds.radioButton(self.aimSpaceRadioButtons[1], query = True, select = True)):
			axisVector = [0, valueAimTarget, 0]
		if (cmds.radioButton(self.aimSpaceRadioButtons[2], query = True, select = True)):
			axisVector = [0, 0, valueAimTarget]

		Locators.CreateOnSelectedAim(scale = scale, hideParent = hideParent, subLocator = subLocators, rotateOnly = rotateOnly, vectorAim = axisVector, distance = distance, reverse = True, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())

		if (distance == 0):
			cmds.warning("Aim distance is 0. Highly recommended to use non-zero value.")

	### CHAIN DISTRIBUTION RIG
	def CreateChainDistributionRig(self, mode=1, *args):
		if mode == 1:
			ChainDistributionRig.CreateRigVariant1(locatorSize = self.GetFloatLocatorSize())
		if mode == 2:
			ChainDistributionRig.CreateRigVariant2(locatorSize = self.GetFloatLocatorSize())


	### BAKING
	def BakeSampleGet(self):
		return cmds.floatField(self.bakingSamplesValue, query = True, value = True)
	def BakeSamplesSet(self, value=1, *args):
		cmds.floatField(self.bakingSamplesValue, edit = True, value = value)
	def BakeSamplesAdd(self, direction=1, *args): # TODO use FloatValueAdd() instead
		value = self.BakeSampleGet()

		addition = 0
		if (direction == 1):
			if (value < 1):
				addition = 0.1
			else:
				addition = 1
		else:
			if (value <= 1):
				addition = -0.1
			else:
				addition = -1

		value = value + addition

		if (value <= 0.1):
			value = 0.1
			cmds.warning("Baking sample rate can't be zero or less. To use values below 0.1 type it manually.")
		
		self.BakeSamplesSet(value)
	def BakeSelectedClassic(self, *args):
		Baker.BakeSelected(classic = True, preserveOutsideKeys = True, sampleBy = self.BakeSampleGet(), selectedRange = True, channelBox = True, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
	def BakeSelectedClassicCut(self, *args):
		Baker.BakeSelected(classic = True, preserveOutsideKeys = False, sampleBy = self.BakeSampleGet(), selectedRange = True, channelBox = True, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
	def BakeSelectedCustom(self, *args): # TODO , sampleBy = self.fieldBakingStep.Get()
		Baker.BakeSelected(classic = False, preserveOutsideKeys = True, selectedRange = True, channelBox = True, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
	def BakeSelectedCustomCut(self, *args): # TODO , sampleBy = self.fieldBakingStep.Get()
		Baker.BakeSelected(classic = False, preserveOutsideKeys = False, selectedRange = True, channelBox = True, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
	def BakeSelectedByLastObject(self, translate=True, rotate=True, *args):
		if (translate and rotate):
			Baker.BakeSelectedByLastObject(sampleBy = self.BakeSampleGet(), selectedRange = True, channelBox = True, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
		elif (translate and not rotate):
			Baker.BakeSelectedByLastObject(sampleBy = self.BakeSampleGet(), selectedRange = True, channelBox = False, attributes = Enums.Attributes.translateLong, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
		elif (not translate and rotate):
			Baker.BakeSelectedByLastObject(sampleBy = self.BakeSampleGet(), selectedRange = True, channelBox = False, attributes = Enums.Attributes.rotateLong, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
	def BakeSelectedByWorld(self, translate=True, rotate=True, *args):
		if (translate and rotate):
			Baker.BakeSelectedByWorld(sampleBy = self.BakeSampleGet(), selectedRange = True, channelBox = True, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
		elif (translate and not rotate):
			Baker.BakeSelectedByWorld(sampleBy = self.BakeSampleGet(), selectedRange = True, channelBox = False, attributes = Enums.Attributes.translateLong, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())
		elif (not translate and rotate):
			Baker.BakeSelectedByWorld(sampleBy = self.BakeSampleGet(), selectedRange = True, channelBox = False, attributes = Enums.Attributes.rotateLong, euler = self.optionsPlugin.menuCheckboxEulerFilter.Get())


	### ANIMATION
	def FloatValueAdd(self, value, direction=1, *args):
		addition = 0
		if (direction == 1):
			if (value < 1):
				addition = 0.1
			else:
				addition = 1
		else:
			if (value <= 1):
				addition = -0.1
			else:
				addition = -1

		result = value + addition

		if (result <= 0.1):
			result = 0.1
			cmds.warning("Value can't be zero or less. To use values below 0.1 type it manually.")
		
		return result
	def AnimationOffsetSetValue(self, value, *args):
		cmds.floatField(self.desyncFloatField, edit = True, value = value)
	def AnimationOffsetAddValue(self, direction):
		value = cmds.floatField(self.desyncFloatField, query = True, value = True)
		valueNew = self.FloatValueAdd(value, direction)
		self.AnimationOffsetSetValue(valueNew)
	def AnimationOffsetAddValueNegative(self, *args):
		self.AnimationOffsetAddValue(direction = -1)
	def AnimationOffsetAddValuePositive(self, *args):
		self.AnimationOffsetAddValue(direction = 1)
	def AnimationOffsetMove(self, direction=1):
		value = cmds.floatField(self.desyncFloatField, query = True, value = True)
		self.AnimationOffset(direction, value)
	def AnimationOffsetMoveLeft(self, *args):
		self.AnimationOffsetMove(direction = -1)
	def AnimationOffsetMoveRight(self, *args):
		self.AnimationOffsetMove(direction = 1)
	def AnimationOffset(self, direction=1, step=1, *args):
		Animation.OffsetSelected(direction, step)

