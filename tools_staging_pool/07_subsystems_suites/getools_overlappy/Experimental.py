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
# from functools import partial

from .. import Settings
from ..utils import File
from ..utils import Layers
from ..utils import Selector
# from ..utils import Blendshapes
# from ..experimental import Physics
# from ..experimental import PhysicsHair
from ..experimental import PhysicsParticle


class Experimental:
	_title = "实验功能"

	def __init__(self, options):
		self.optionsPlugin = options
		### Check Maya version to avoid cycle import, Maya 2020 and older can't use cycle import
		if cmds.about(version = True) in ["2022", "2023", "2024", "2025"]:
			from ..modules import Options
			if isinstance(options, Options.PluginVariables):
				self.optionsPlugin = options
	
	def UICreate(self, layoutMain):
		cmds.menuBarLayout(parent = layoutMain)

		cmds.menu(label = "图层", tearOff = True)
		cmds.menuItem(label = "创建图层", command = self.LayerCreate)
		cmds.menuItem(label = "为选定对象创建图层", command = self.LayerCreateForSelected)
		cmds.menuItem(label = "删除图层", command = self.LayerDelete)
		cmds.menuItem(label = "获取选定图层", command = self.LayerGetSelected)
		cmds.menuItem(label = "移动图层", command = self.LayerMove)

		### 按钮
		countOffsets = 4
		cmds.gridLayout(parent = layoutMain, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.button(label = "粒子", command = PhysicsParticle.CreateOnSelected)
		cmds.button(label = "粒子瞄准", command = PhysicsParticle.CreateAimOnSelected)
		cmds.button(label = "粒子组合", command = PhysicsParticle.CreateComboOnSelected)

		countOffsets = 2
		cmds.gridLayout(parent = layoutMain, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		def GetCheckboxEulerFilter(*args):
			self.optionsPlugin.PrintAllOptions()
		cmds.button(label = "打印通用选项", command = GetCheckboxEulerFilter)

	### 测试图层方法
	def LayerCreate(*args):
		Layers.Create("测试图层")
	
	def LayerCreateForSelected(*args):
		selected = Selector.MultipleObjects()
		if (selected == None):
			return
		Layers.CreateForSelected(selected)
	
	def LayerDelete(*args):
		Layers.Delete("测试图层")
	
	def LayerGetSelected(*args):
		Layers.GetSelected()
	
	def LayerMove(*args):
		selected = Layers.GetSelected()
		if (selected == None or len(selected) < 2):
			cmds.warning("需要至少选择两个图层")
			return
		Layers.MoveChildrenToParent(selected[:-1], selected[-1]) # FIXME 主要问题是图层没有选择顺序，它们只是从上到下列出

