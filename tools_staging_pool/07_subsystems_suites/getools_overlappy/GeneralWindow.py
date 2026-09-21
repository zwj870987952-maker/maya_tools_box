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
from ..modules import Options
from ..modules import Transformations
from ..modules import Tools
from ..modules import Rigging
from ..modules import Overlappy
from ..modules import CenterOfMass
from ..modules import Experimental
from ..utils import Annotation
from ..utils import Blendshapes
from ..utils import Colors
from ..utils import Install
from ..utils import MayaSettings
from ..utils import MotionTrail
from ..utils import Parent
from ..utils import Print
from ..utils import Scene
from ..utils import Selector
from ..utils import Shelf
from ..utils import Skinning
from ..utils import Toggles
from ..utils import UI
from ..values import Icons


class GeneralWindow:
	_version = "v1.6.0"
	_name = "GETools"
	_title = _name + " " + _version

	def __init__(self):
		self.optionsPlugin = Options.PluginVariables()
		self.optionsPlugin.titleGeneral = GeneralWindow._title

		self.frameTransformations = None
		self.frameTools = None
		self.frameRigging = None
		self.frameOverlappy = None
		self.frameCenterOfMass = None
		self.frameMotionTrail = None
		self.frameExperimental = None
	
	def CreateUI(self):
		if cmds.window(Settings.windowName, exists = True):
			cmds.deleteUI(Settings.windowName)
		generalWindow = cmds.window(Settings.windowName, title = GeneralWindow._title, maximizeButton = False, sizeable = True, width = Settings.windowWidthOffset, height = Settings.windowHeight)
		
		layoutRoot = cmds.menuBarLayout(parent = generalWindow)
		self.LayoutMenuBar(parentLayout = layoutRoot)

		layoutScroll = cmds.scrollLayout(parent = generalWindow, width = Settings.windowWidthOffset)

		self.LayoutTransformations(parentLayout = layoutScroll)
		self.LayoutTools(parentLayout = layoutScroll)
		self.LayoutRigging(parentLayout = layoutScroll)
		self.LayoutOverlappy(parentLayout = layoutScroll)
		self.LayoutCenterOfMass(parentLayout = layoutScroll)
		self.LayoutMotionTrail(parentLayout = layoutScroll)
		self.LayoutExperimental(parentLayout = layoutScroll)

	### UI LAYOUTS
	def LayoutMenuBar(self, parentLayout):
		cmds.columnLayout("layoutMenuBar", parent = parentLayout, adjustableColumn = True)
		cmds.menuBarLayout()

		cmds.menu(label = "文件")
		cmds.menuItem(label = "重新加载场景（强制）", command = Scene.Reload, image = Icons.reset)
		cmds.menuItem(label = "退出 Maya（强制）", command = Scene.ExitMaya, image = Icons.off)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "重启 GETools", command = partial(self.RUN_DOCKED, self.optionsPlugin.directory, True), image = Icons.reset)
		cmds.menuItem(label = "关闭 GETools", command = self.DockDelete, image = Icons.off)
		
		cmds.menu(label = "显示", tearOff = True)
		cmds.menuItem(label = "全部折叠", command = partial(self.FramesCollapse, True), image = Icons.visibleOff)
		cmds.menuItem(label = "全部展开", command = partial(self.FramesCollapse, False), image = Icons.visibleOn)
		cmds.menuItem(dividerLabel = "停靠", divider = True)
		cmds.menuItem(label = "停靠左侧", command = partial(self.DockToSide, Settings.dockAllowedAreas[0]), image = Icons.arrowLeft)
		cmds.menuItem(label = "停靠右侧", command = partial(self.DockToSide, Settings.dockAllowedAreas[1]), image = Icons.arrowRight)
		cmds.menuItem(label = "取消停靠", command = self.DockOff, image = Icons.arrowDown)

		def ColorsPalette(*args):
			colorCalibration = Colors.ColorsPalette()
			colorCalibration.CreateUI()
		cmds.menu(label = "工具", tearOff = True)
		cmds.menuItem(label = "选择层级", command = Selector.SelectHierarchy, image = Icons.selectByHierarchy)
		cmds.menuItem(label = "选择层级变换", command = Selector.SelectHierarchyTransforms, image = Icons.selectByHierarchy)
		cmds.menuItem(label = "选择蒙皮网格或关节", command = Skinning.SelectSkinnedMeshesOrJoints)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "保存姿势到工具架", command = Install.CreatePoseButton)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "父级形状", command = Parent.ParentShape)
		cmds.menuItem(label = "注释选定", command = Annotation.AnnotateSelected)
		cmds.menuItem(dividerLabel = "打印", divider = True)
		cmds.menuItem(label = "打印选定对象到控制台", command = Print.PrintSelected, image = Icons.text)
		cmds.menuItem(label = "打印可动画属性", command = partial(Print.PrintAttributesAnimatableOnSelected, False), image = Icons.text)
		cmds.menuItem(label = "打印通道框选定属性", command = Print.PrintAttributesSelectedFromChannelBox, image = Icons.text)
		cmds.menuItem(dividerLabel = "混合形状", divider = True)
		cmds.menuItem(label = "打印混合形状基节点", command = Blendshapes.GetBlendshapeNodesFromSelected, image = Icons.text)
		cmds.menuItem(label = "打印混合形状名称", command = Blendshapes.GetBlendshapeWeightsFromSelected, image = Icons.text)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "打开颜色调色板", command = ColorsPalette, image = Icons.color)
		
		cmds.menu(label = "切换", tearOff = True)
		cmds.menuItem(label = "摄像机", command = Toggles.ToggleCameras, image = Icons.camera)
		cmds.menuItem(label = "控制顶点", command = Toggles.ToggleControlVertices, image = Icons.vertex)
		cmds.menuItem(label = "变形器", command = Toggles.ToggleDeformers)
		cmds.menuItem(label = "尺寸", command = Toggles.ToggleDimensions)
		cmds.menuItem(label = "动态约束", command = Toggles.ToggleDynamicConstraints, image = Icons.dynamicConstraint)
		cmds.menuItem(label = "动力学", command = Toggles.ToggleDynamics)
		cmds.menuItem(label = "流体", command = Toggles.ToggleFluids)
		cmds.menuItem(label = "毛囊", command = Toggles.ToggleFollicles, image = Icons.follicle)
		cmds.menuItem(label = "网格", command = Toggles.ToggleGrid, image = Icons.grid)
		cmds.menuItem(label = "毛发系统", command = Toggles.ToggleHairSystems, image = Icons.hairSystem)
		cmds.menuItem(label = "手柄", command = Toggles.ToggleHandles)
		cmds.menuItem(label = "壳", command = Toggles.ToggleHulls)
		cmds.menuItem(label = "IK 手柄", command = Toggles.ToggleIkHandles, image = Icons.ikHandle)
		cmds.menuItem(label = "关节", command = Toggles.ToggleJoints, image = Icons.joint)
		cmds.menuItem(label = "灯光", command = Toggles.ToggleLights, image = Icons.light)
		cmds.menuItem(label = "定位器", command = Toggles.ToggleLocators, image = Icons.locator)
		cmds.menuItem(label = "操控器", command = Toggles.ToggleManipulators, image = Icons.manipulator)
		cmds.menuItem(label = "NCloths", command = Toggles.ToggleNCloths, image = Icons.nCloth)
		cmds.menuItem(label = "NParticles", command = Toggles.ToggleNParticles, image = Icons.particle)
		cmds.menuItem(label = "NRigids", command = Toggles.ToggleNRigids, image = Icons.nRigid)
		cmds.menuItem(label = "Nurbs 曲线", command = Toggles.ToggleNurbsCurves, image = Icons.nurbsCurve)
		cmds.menuItem(label = "Nurbs 曲面", command = Toggles.ToggleNurbsSurfaces, image = Icons.nurbsSurface)
		cmds.menuItem(label = "枢轴", command = Toggles.TogglePivots)
		cmds.menuItem(label = "平面", command = Toggles.TogglePlanes, image = Icons.plane)
		cmds.menuItem(label = "多边形网格", command = Toggles.TogglePolymeshes, image = Icons.polyMesh)
		cmds.menuItem(label = "阴影", command = Toggles.ToggleShadows, image = Icons.shadows)
		cmds.menuItem(label = "笔触", command = Toggles.ToggleStrokes, image = Icons.stroke)
		cmds.menuItem(label = "细分曲面", command = Toggles.ToggleSubdivSurfaces)
		cmds.menuItem(label = "纹理", command = Toggles.ToggleTextures, image = Icons.image)

		self.LayoutMenuOptions()

		cmds.menu(label = "帮助", tearOff = True)
		def LinkVersionHistory(self): cmds.showHelp("https://github.com/GenEugene/GETools/blob/master/changelog.txt", absolute = True)
		def LinkGithub(self): cmds.showHelp("https://github.com/GenEugene/GETools", absolute = True)
		def LinkGumroad(self): cmds.showHelp("https://gumroad.com/l/iCNa", absolute = True)
		def LinkGithubWiki(self): cmds.showHelp("https://github.com/GenEugene/GETools/wiki", absolute = True)
		def LinkYoutubeVideos(self): cmds.showHelp("https://youtube.com/playlist?list=PLhwndaM4LAxhbl95yz9WVie1iYflTFy6S&si=UOoK-mdk4Rm5bVyp", absolute = True)
		def LinkLinkedin(self): cmds.showHelp("https://www.linkedin.com/in/geneugene", absolute = True)
		def LinkYoutube(self): cmds.showHelp("https://youtube.com/@EugeneGataulin", absolute = True)
		def LinkDiscord(self): cmds.showHelp("https://discord.gg/heMxJhTqCz", absolute = True)
		def LinkShareIdeas(self): cmds.showHelp("https://github.com/GenEugene/GETools/discussions/categories/ideas", absolute = True)
		def LinkReport(self): cmds.showHelp("https://github.com/GenEugene/GETools/discussions/categories/report-a-problem", absolute = True)
		
		cmds.menuItem(label = "版本历史", command = LinkVersionHistory)
		cmds.menuItem(dividerLabel = "链接", divider = True)
		cmds.menuItem(label = "GitHub", command = LinkGithub, image = Icons.home)
		cmds.menuItem(label = "Gumroad", command = LinkGumroad)
		cmds.menuItem(dividerLabel = "使用说明", divider = True)
		cmds.menuItem(label = "文档", command = LinkGithubWiki, image = Icons.help)
		cmds.menuItem(label = "视频播放列表", command = LinkYoutubeVideos, image = Icons.playblast)
		cmds.menuItem(dividerLabel = "联系方式", divider = True)
		cmds.menuItem(label = "Discord", command = LinkDiscord)
		cmds.menuItem(label = "Linkedin", command = LinkLinkedin)
		cmds.menuItem(label = "YouTube", command = LinkYoutube)
		cmds.menuItem(dividerLabel = "支持", divider = True)
		cmds.menuItem(label = "分享您的想法", command = LinkShareIdeas, image = Icons.light)
		cmds.menuItem(label = "报告问题", command = LinkReport, image = Icons.warning)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "更改图标", command = partial(Shelf.ToggleButtonIcons, self.optionsPlugin.directory))

	def LayoutMenuOptions(self):
		cmds.menu(label = "选项", tearOff = True)

		self.optionsPlugin.menuCheckboxEulerFilter = UI.MenuCheckbox(label = "烘焙后使用欧拉过滤器", value = Settings.checkboxEulerFilter, valueDefault = Settings.checkboxEulerFilter)

		cmds.menuItem(dividerLabel = "安装", divider = True)

		# 安装
		cmds.menuItem(subMenu = True, label = "安装按钮到当前工具架", tearOff = True, image = Icons.fileOpen)
		cmds.menuItem(subMenu = True, label = "文件", tearOff = True, image = Icons.fileOpen)
		cmds.menuItem(label = "重新加载场景（强制）", command = partial(Install.ToShelf_ReloadScene, self.optionsPlugin.directory), image = Icons.reset)
		cmds.menuItem(label = "退出 Maya（强制）", command = partial(Install.ToShelf_ExitMaya, self.optionsPlugin.directory), image = Icons.off)
		cmds.setParent('..', menu = True)

		cmds.menuItem(subMenu = True, label = "工具", tearOff = True)
		cmds.menuItem(label = "选择层级", command = partial(Install.ToShelf_SelectHierarchy, self.optionsPlugin.directory), image = Icons.selectByHierarchy)
		cmds.menuItem(label = "选择层级变换", command = partial(Install.ToShelf_SelectHierarchyTransforms, self.optionsPlugin.directory), image = Icons.selectByHierarchy)
		cmds.menuItem(label = "选择蒙皮网格或关节", command = partial(Install.ToShelf_SelectSkinnedMeshesOrJoints, self.optionsPlugin.directory))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "保存姿势到工具架", command = partial(Install.ToShelf_SavePoseToShelf, self.optionsPlugin.directory))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "父级形状", command = partial(Install.ToShelf_ParentShapes, self.optionsPlugin.directory))
		cmds.menuItem(label = "注释选定", command = partial(Install.ToShelf_AnnotateSelected, self.optionsPlugin.directory))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "切换", tearOff = True)
		cmds.menuItem(label = "摄像机", command = partial(Install.ToShelf_ToggleCameras, self.optionsPlugin.directory), image = Icons.camera)
		cmds.menuItem(label = "控制顶点", command = partial(Install.ToShelf_ToggleControlVertices, self.optionsPlugin.directory), image = Icons.vertex)
		cmds.menuItem(label = "变形器", command = partial(Install.ToShelf_ToggleDeformers, self.optionsPlugin.directory))
		cmds.menuItem(label = "尺寸", command = partial(Install.ToShelf_ToggleDimensions, self.optionsPlugin.directory))
		cmds.menuItem(label = "动态约束", command = partial(Install.ToShelf_ToggleDynamicConstraints, self.optionsPlugin.directory), image = Icons.dynamicConstraint)
		cmds.menuItem(label = "动力学", command = partial(Install.ToShelf_ToggleDynamics, self.optionsPlugin.directory))
		cmds.menuItem(label = "流体", command = partial(Install.ToShelf_ToggleFluids, self.optionsPlugin.directory))
		cmds.menuItem(label = "毛囊", command = partial(Install.ToShelf_ToggleFollicles, self.optionsPlugin.directory), image = Icons.follicle)
		cmds.menuItem(label = "网格", command = partial(Install.ToShelf_ToggleGrid, self.optionsPlugin.directory), image = Icons.grid)
		cmds.menuItem(label = "毛发系统", command = partial(Install.ToShelf_ToggleHairSystems, self.optionsPlugin.directory), image = Icons.hairSystem)
		cmds.menuItem(label = "手柄", command = partial(Install.ToShelf_ToggleHandles, self.optionsPlugin.directory))
		cmds.menuItem(label = "壳", command = partial(Install.ToShelf_ToggleHulls, self.optionsPlugin.directory))
		cmds.menuItem(label = "IK 手柄", command = partial(Install.ToShelf_ToggleIkHandles, self.optionsPlugin.directory), image = Icons.ikHandle)
		cmds.menuItem(label = "关节", command = partial(Install.ToShelf_ToggleJoints, self.optionsPlugin.directory), image = Icons.joint)
		cmds.menuItem(label = "灯光", command = partial(Install.ToShelf_ToggleLights, self.optionsPlugin.directory), image = Icons.light)
		cmds.menuItem(label = "定位器", command = partial(Install.ToShelf_ToggleLocators, self.optionsPlugin.directory), image = Icons.locator)
		cmds.menuItem(label = "操控器", command = partial(Install.ToShelf_ToggleManipulators, self.optionsPlugin.directory), image = Icons.manipulator)
		cmds.menuItem(label = "NCloths", command = partial(Install.ToShelf_ToggleNCloths, self.optionsPlugin.directory), image = Icons.nCloth)
		cmds.menuItem(label = "NParticles", command = partial(Install.ToShelf_ToggleNParticles, self.optionsPlugin.directory), image = Icons.particle)
		cmds.menuItem(label = "NRigids", command = partial(Install.ToShelf_ToggleNRigids, self.optionsPlugin.directory), image = Icons.nRigid)
		cmds.menuItem(label = "Nurbs 曲线", command = partial(Install.ToShelf_ToggleNurbsCurves, self.optionsPlugin.directory), image = Icons.nurbsCurve)
		cmds.menuItem(label = "Nurbs 曲面", command = partial(Install.ToShelf_ToggleNurbsSurfaces, self.optionsPlugin.directory), image = Icons.nurbsSurface)
		cmds.menuItem(label = "枢轴", command = partial(Install.ToShelf_TogglePivots, self.optionsPlugin.directory))
		cmds.menuItem(label = "平面", command = partial(Install.ToShelf_TogglePlanes, self.optionsPlugin.directory), image = Icons.plane)
		cmds.menuItem(label = "多边形网格", command = partial(Install.ToShelf_TogglePolymeshes, self.optionsPlugin.directory), image = Icons.polyMesh)
		cmds.menuItem(label = "阴影", command = partial(Install.ToShelf_ToggleShadows, self.optionsPlugin.directory), image = Icons.shadows)
		cmds.menuItem(label = "笔触", command = partial(Install.ToShelf_ToggleStrokes, self.optionsPlugin.directory), image = Icons.stroke)
		cmds.menuItem(label = "细分曲面", command = partial(Install.ToShelf_ToggleSubdivSurfaces, self.optionsPlugin.directory))
		cmds.menuItem(label = "纹理", command = partial(Install.ToShelf_ToggleTextures, self.optionsPlugin.directory), image = Icons.image)
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(dividerLabel = "工具 - 定位器", divider = True)
		cmds.menuItem(subMenu = True, label = "大小", tearOff = True, image = Icons.scale)
		cmds.menuItem(label = "50%", command = partial(Install.ToShelf_LocatorsSizeScale50, self.optionsPlugin.directory), image = Icons.minus)
		cmds.menuItem(label = "90%", command = partial(Install.ToShelf_LocatorsSizeScale90, self.optionsPlugin.directory), image = Icons.minus)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "110%", command = partial(Install.ToShelf_LocatorsSizeScale110, self.optionsPlugin.directory), image = Icons.plus)
		cmds.menuItem(label = "200%", command = partial(Install.ToShelf_LocatorsSizeScale200, self.optionsPlugin.directory), image = Icons.plus)
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "创建", tearOff = True, image = Icons.locator)
		cmds.menuItem(label = "定位器", command = partial(Install.ToShelf_LocatorCreate, self.optionsPlugin.directory))
		cmds.menuItem(label = "匹配", command = partial(Install.ToShelf_LocatorsMatch, self.optionsPlugin.directory))
		cmds.menuItem(label = "父级", command = partial(Install.ToShelf_LocatorsParent, self.optionsPlugin.directory))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "固定", tearOff = True, image = Icons.pin)
		cmds.menuItem(label = "固定", command = partial(Install.ToShelf_LocatorsPin, self.optionsPlugin.directory))
		cmds.menuItem(label = "无反向约束", command = partial(Install.ToShelf_LocatorsPinWithoutReverse, self.optionsPlugin.directory))
		cmds.menuItem(label = "位置", command = partial(Install.ToShelf_LocatorsPinPos, self.optionsPlugin.directory), image = Icons.move)
		cmds.menuItem(label = "旋转", command = partial(Install.ToShelf_LocatorsPinRot, self.optionsPlugin.directory), image = Icons.rotate)
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "相对", tearOff = True, image = Icons.pinInvert)
		cmds.menuItem(label = "相对", command = partial(Install.ToShelf_LocatorsRelative, self.optionsPlugin.directory))
		cmds.menuItem(label = "跳过最后一个对象反向约束", command = partial(Install.ToShelf_LocatorsRelativeSkipLast, self.optionsPlugin.directory))
		cmds.menuItem(label = "无反向约束", command = partial(Install.ToShelf_LocatorsRelativeWithoutReverse, self.optionsPlugin.directory))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "链分布", tearOff = True, image = Icons.pinInvert)
		cmds.menuItem(label = "默认模式", command = partial(Install.ToShelf_LocatorsChainDistribution1, self.optionsPlugin.directory))
		cmds.menuItem(label = "替代模式", command = partial(Install.ToShelf_LocatorsChainDistribution2, self.optionsPlugin.directory))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "瞄准", tearOff = True, image = Icons.pin)
		minus = "-"
		plus = "+"
		axisX = "X"
		axisY = "Y"
		axisZ = "Z"
		axisXMinus = minus + axisX
		axisYMinus = minus + axisY
		axisZMinus = minus + axisZ
		axisXPlus = plus + axisX
		axisYPlus = plus + axisY
		axisZPlus = plus + axisZ
		cmds.menuItem(dividerLabel = "全部", divider = True)
		cmds.menuItem(label = axisXMinus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisXMinus, False, (-1, 0, 0)))
		cmds.menuItem(label = axisXPlus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisXPlus, False, (1, 0, 0)))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = axisYMinus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisYMinus, False, (0, -1, 0)))
		cmds.menuItem(label = axisYPlus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisYPlus, False, (0, 1, 0)))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = axisZMinus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisZMinus, False, (0, 0, -1)))
		cmds.menuItem(label = axisZPlus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisZPlus, False, (0, 0, 1)))
		cmds.menuItem(dividerLabel = "旋转", divider = True)
		cmds.menuItem(label = axisXMinus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisXMinus, True, (-1, 0, 0)))
		cmds.menuItem(label = axisXPlus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisXPlus, True, (1, 0, 0)))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = axisYMinus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisYMinus, True, (0, -1, 0)))
		cmds.menuItem(label = axisYPlus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisYPlus, True, (0, 1, 0)))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = axisZMinus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisZMinus, True, (0, 0, -1)))
		cmds.menuItem(label = axisZPlus, command = partial(Install.ToShelf_LocatorsAim, self.optionsPlugin.directory, axisZPlus, True, (0, 0, 1)))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(dividerLabel = "工具 - 烘焙", divider = True)
		cmds.menuItem(subMenu = True, label = "烘焙", tearOff = True, image = Icons.bake)
		cmds.menuItem(label = "经典", command = partial(Install.ToShelf_BakeClassic, self.optionsPlugin.directory))
		cmds.menuItem(label = "经典剪切", command = partial(Install.ToShelf_BakeClassicCutOut, self.optionsPlugin.directory))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "自定义", command = partial(Install.ToShelf_BakeCustom, self.optionsPlugin.directory))
		cmds.menuItem(label = "自定义剪切", command = partial(Install.ToShelf_BakeCustomCutOut, self.optionsPlugin.directory))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "按最后一个", tearOff = True, image = Icons.bake)
		cmds.menuItem(label = "按最后一个", command = partial(Install.ToShelf_BakeByLast, self.optionsPlugin.directory, True, True))
		cmds.menuItem(label = "位置", command = partial(Install.ToShelf_BakeByLast, self.optionsPlugin.directory, True, False), image = Icons.move)
		cmds.menuItem(label = "旋转", command = partial(Install.ToShelf_BakeByLast, self.optionsPlugin.directory, False, True), image = Icons.rotate)
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "世界", tearOff = True, image = Icons.world)
		cmds.menuItem(label = "世界", command = partial(Install.ToShelf_BakeByWorld, self.optionsPlugin.directory, True, True))
		cmds.menuItem(label = "位置", command = partial(Install.ToShelf_BakeByWorld, self.optionsPlugin.directory, True, False), image = Icons.move)
		cmds.menuItem(label = "旋转", command = partial(Install.ToShelf_BakeByWorld, self.optionsPlugin.directory, False, True), image = Icons.rotate)
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(dividerLabel = "工具 - 动画", divider = True)
		cmds.menuItem(subMenu = True, label = "删除", tearOff = True, image = Icons.delete)
		cmds.menuItem(label = "动画", command = partial(Install.ToShelf_DeleteKeys, self.optionsPlugin.directory))
		cmds.menuItem(label = "不可键控", command = partial(Install.ToShelf_DeleteNonkeyable, self.optionsPlugin.directory))
		cmds.menuItem(label = "静态", command = partial(Install.ToShelf_DeleteStatic, self.optionsPlugin.directory))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(label = "欧拉过滤器", command = partial(Install.ToShelf_EulerFilterOnSelected, self.optionsPlugin.directory), image = Icons.filterActive)
		
		cmds.menuItem(subMenu = True, label = "无限", tearOff = True, image = Icons.infinity)
		cmds.menuItem(label = "常量", command = partial(Install.ToShelf_SetInfinity, self.optionsPlugin.directory, 1))
		cmds.menuItem(label = "线性", command = partial(Install.ToShelf_SetInfinity, self.optionsPlugin.directory, 2))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "循环", command = partial(Install.ToShelf_SetInfinity, self.optionsPlugin.directory, 3), image = Icons.cycle)
		cmds.menuItem(label = "偏移", command = partial(Install.ToShelf_SetInfinity, self.optionsPlugin.directory, 4), image = Icons.cycle)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "振荡", command = partial(Install.ToShelf_SetInfinity, self.optionsPlugin.directory, 5))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "偏移", tearOff = True, image = Icons.arrowsOutHorizontal)
		cmds.menuItem(label = "-3", command = partial(Install.ToShelf_AnimOffsetSelected, self.optionsPlugin.directory, -1, 3), image = Icons.minus)
		cmds.menuItem(label = "-2", command = partial(Install.ToShelf_AnimOffsetSelected, self.optionsPlugin.directory, -1, 2), image = Icons.minus)
		cmds.menuItem(label = "-1", command = partial(Install.ToShelf_AnimOffsetSelected, self.optionsPlugin.directory, -1, 1), image = Icons.minus)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "+1", command = partial(Install.ToShelf_AnimOffsetSelected, self.optionsPlugin.directory, 1, 1), image = Icons.plus)
		cmds.menuItem(label = "+2", command = partial(Install.ToShelf_AnimOffsetSelected, self.optionsPlugin.directory, 1, 2), image = Icons.plus)
		cmds.menuItem(label = "+3", command = partial(Install.ToShelf_AnimOffsetSelected, self.optionsPlugin.directory, 1, 3), image = Icons.plus)
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(dividerLabel = "工具 - 时间线", divider = True)
		cmds.menuItem(subMenu = True, label = "时间线", tearOff = True)
		cmds.menuItem(label = "最小输出", command = partial(Install.ToShelf_SetTimelineMinOut, self.optionsPlugin.directory))
		cmds.menuItem(label = "最小输入", command = partial(Install.ToShelf_SetTimelineMinIn, self.optionsPlugin.directory))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "最大输入", command = partial(Install.ToShelf_SetTimelineMaxIn, self.optionsPlugin.directory))
		cmds.menuItem(label = "最大输出", command = partial(Install.ToShelf_SetTimelineMaxOut, self.optionsPlugin.directory))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "聚焦输出", command = partial(Install.ToShelf_SetTimelineFocusOut, self.optionsPlugin.directory), image = Icons.arrowsOut)
		cmds.menuItem(label = "聚焦输入", command = partial(Install.ToShelf_SetTimelineFocusIn, self.optionsPlugin.directory), image = Icons.arrowsIn)
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "选定范围", command = partial(Install.ToShelf_SetTimelineSet, self.optionsPlugin.directory))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(dividerLabel = "绑定 - 约束", divider = True)
		cmds.menuItem(subMenu = True, label = "约束", tearOff = True, image = Icons.constraint)
		cmds.menuItem(label = "父级", command = partial(Install.ToShelf_Constraint, self.optionsPlugin.directory, False, True, False, False, False))
		cmds.menuItem(label = "点", command = partial(Install.ToShelf_Constraint, self.optionsPlugin.directory, False, False, True, False, False))
		cmds.menuItem(label = "方向", command = partial(Install.ToShelf_Constraint, self.optionsPlugin.directory, False, False, False, True, False))
		cmds.menuItem(label = "缩放", command = partial(Install.ToShelf_Constraint, self.optionsPlugin.directory, False, False, False, False, True))
		cmds.menuItem(divider = True)
		cmds.menuItem(label = "父级保持", command = partial(Install.ToShelf_Constraint, self.optionsPlugin.directory, True, True, False, False, False))
		cmds.menuItem(label = "点保持", command = partial(Install.ToShelf_Constraint, self.optionsPlugin.directory, True, False, True, False, False))
		cmds.menuItem(label = "方向保持", command = partial(Install.ToShelf_Constraint, self.optionsPlugin.directory, True, False, False, True, False))
		cmds.menuItem(label = "缩放保持", command = partial(Install.ToShelf_Constraint, self.optionsPlugin.directory, True, False, False, False, True))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "连接", tearOff = True, image = Icons.constraint)
		cmds.menuItem(label = "断开连接", command = partial(Install.ToShelf_DisconnectTargets, self.optionsPlugin.directory))
		cmds.menuItem(label = "删除约束", command = partial(Install.ToShelf_DeleteConstraints, self.optionsPlugin.directory))
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(dividerLabel = "绑定 - 工具", divider = True)
		cmds.menuItem(subMenu = True, label = "旋转顺序", tearOff = True)
		cmds.menuItem(label = "显示", command = partial(Install.ToShelf_RotateOrder, self.optionsPlugin.directory, True), image = Icons.visibleOn)
		cmds.menuItem(label = "隐藏", command = partial(Install.ToShelf_RotateOrder, self.optionsPlugin.directory, False), image = Icons.visibleOff)
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "段缩放补偿", tearOff = True, image = Icons.joint)
		cmds.menuItem(label = "开", command = partial(Install.ToShelf_SegmentScaleCompensate, self.optionsPlugin.directory, True), image = Icons.on)
		cmds.menuItem(label = "关", command = partial(Install.ToShelf_SegmentScaleCompensate, self.optionsPlugin.directory, False), image = Icons.off)
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(subMenu = True, label = "关节绘制样式", tearOff = True, image = Icons.joint)
		cmds.menuItem(label = "骨骼", command = partial(Install.ToShelf_JointDrawStyle, self.optionsPlugin.directory, 0), image = Icons.visibleOn)
		cmds.menuItem(label = "隐藏", command = partial(Install.ToShelf_JointDrawStyle, self.optionsPlugin.directory, 2), image = Icons.visibleOff)
		cmds.setParent('..', menu = True)
		
		cmds.menuItem(label = "从最后选定复制蒙皮权重", command = partial(Install.ToShelf_CopySkin, self.optionsPlugin.directory), image = Icons.copySkinWeights)
		
		cmds.menuItem(dividerLabel = "绑定 - 混合形状", divider = True)
		cmds.menuItem(label = "创建包裹", command = partial(Install.ToShelf_WrapsCreate, self.optionsPlugin.directory), image = Icons.wrap)
		cmds.menuItem(label = "重建", command = partial(Install.ToShelf_BlendshapesReconstruct, self.optionsPlugin.directory), image = Icons.blendshape)
		cmds.menuItem(label = "提取形状", command = partial(Install.ToShelf_BlendshapesExtractShapes, self.optionsPlugin.directory), image = Icons.polyMesh)
		cmds.menuItem(label = "零权重", command = partial(Install.ToShelf_BlendshapesZeroWeights, self.optionsPlugin.directory), image = Icons.zero)
		
		cmds.menuItem(dividerLabel = "绑定 - 曲线", divider = True)
		cmds.menuItem(label = "从选定对象创建曲线", command = partial(Install.ToShelf_CreateCurveFromSelectedObjects, self.optionsPlugin.directory), image = Icons.nurbsCurve)
		cmds.menuItem(label = "从轨迹创建曲线", command = partial(Install.ToShelf_CreateCurveFromTrajectory, self.optionsPlugin.directory), image = Icons.nurbsCurve)
		
		cmds.menuItem(dividerLabel = "运动轨迹", divider = True)
		cmds.menuItem(subMenu = True, label = "运动轨迹", tearOff = True, image = Icons.motionTrail)
		cmds.menuItem(label = "创建", command = partial(Install.ToShelf_MotionTrailCreate, self.optionsPlugin.directory), image = Icons.plus)
		cmds.menuItem(label = "选择", command = partial(Install.ToShelf_MotionTrailSelect, self.optionsPlugin.directory), image = Icons.cursor)
		cmds.menuItem(label = "删除", command = partial(Install.ToShelf_MotionTrailDelete, self.optionsPlugin.directory), image = Icons.minus)
		cmds.setParent('..', menu = True)
	
	def LayoutTransformations(self, parentLayout):
		self.frameTransformations = cmds.frameLayout(parent = parentLayout, label = "1. " + Transformations.Transformations._title, collapsable = True, backgroundColor = Settings.frames1Color, width = Settings.windowWidth, marginWidth = Settings.marginWidth, marginHeight = Settings.marginHeight)
		Transformations.Transformations(self.optionsPlugin).UICreate(self.frameTransformations)
	def LayoutTools(self, parentLayout):
		self.frameTools = cmds.frameLayout(parent = parentLayout, label = "2. " + Tools.Tools._title, collapsable = True, backgroundColor = Settings.frames1Color, width = Settings.windowWidth, marginWidth = Settings.marginWidth, marginHeight = Settings.marginHeight)
		Tools.Tools(self.optionsPlugin).UICreate(self.frameTools)
	def LayoutRigging(self, parentLayout):
		self.frameRigging = cmds.frameLayout(parent = parentLayout, label = "3. " + Rigging.Rigging._title, collapsable = True, backgroundColor = Settings.frames1Color, width = Settings.windowWidth, marginWidth = Settings.marginWidth, marginHeight = Settings.marginHeight)
		Rigging.Rigging(self.optionsPlugin).UICreate(self.frameRigging)
	def LayoutOverlappy(self, parentLayout):
		self.frameOverlappy = cmds.frameLayout(parent = parentLayout, label = "4. " + Overlappy.Overlappy._title, collapsable = True, backgroundColor = Settings.frames1Color, width = Settings.windowWidth, marginWidth = Settings.marginWidth, marginHeight = Settings.marginHeight)
		Overlappy.Overlappy(self.optionsPlugin).UICreate(self.frameOverlappy)
	def LayoutCenterOfMass(self, parentLayout):
		self.frameCenterOfMass = cmds.frameLayout(parent = parentLayout, label = "5. " + CenterOfMass.CenterOfMass._title, collapsable = True, backgroundColor = Settings.frames1Color, width = Settings.windowWidth, marginWidth = Settings.marginWidth, marginHeight = Settings.marginHeight)
		CenterOfMass.CenterOfMass(self.optionsPlugin).UICreate(self.frameCenterOfMass)
	def LayoutMotionTrail(self, parentLayout):
		versionMT = "v1.0" # TODO move to Motion Trail class when possible
		nameMT = "运动轨迹"
		titleMT = nameMT + " " + versionMT
				
		self.frameMotionTrail = cmds.frameLayout(parent = parentLayout, label = "6. " + titleMT, collapsable = True, backgroundColor = Settings.frames1Color, width = Settings.windowWidth, marginWidth = Settings.marginWidth, marginHeight = Settings.marginHeight)
		
		countOffsets = 3
		cmds.gridLayout(parent = self.frameMotionTrail, numberOfColumns = countOffsets, cellWidth = Settings.windowWidthMargin / countOffsets, cellHeight = Settings.lineHeight)
		cmds.button(label = "创建", command = MotionTrail.Create, backgroundColor = Colors.orange10)
		cmds.button(label = "选择全部", command = MotionTrail.Select, backgroundColor = Colors.orange50)
		cmds.button(label = "删除全部", command = MotionTrail.Delete, backgroundColor = Colors.orange100)
		cmds.separator(parent = self.frameMotionTrail, height = Settings.separatorHeight, style = "none")
	def LayoutExperimental(self, parentLayout):
		self.frameExperimental = cmds.frameLayout(parent = parentLayout, label = Experimental.Experimental._title, collapsable = True, backgroundColor = Settings.frames1Color, width = Settings.windowWidth, marginWidth = Settings.marginWidth, marginHeight = Settings.marginHeight)
		Experimental.Experimental(self.optionsPlugin).UICreate(self.frameExperimental)
	
	### 窗口
	def WindowCheck(self, *args):
		return cmds.window(Settings.windowName, exists = True)
	def WindowShow(self, *args):
		if self.WindowCheck():
			cmds.showWindow(Settings.windowName)
			print("窗口已显示")
		else:
			print("没有窗口")
	def WindowHide(self, *args):
		if self.WindowCheck():
			cmds.window(Settings.windowName, edit = True, visible = False)
			print("窗口已隐藏")
		else:
			print("没有窗口")
	def WindowDelete(self, *args):
		if self.WindowCheck():
			cmds.deleteUI(Settings.windowName)
			print("窗口已删除")
		else:
			print("没有窗口")
	def FramesCollapse(self, value, *args): # TODO collapse function for sub frames
		if self.frameTransformations is not None:
			cmds.frameLayout(self.frameTransformations, edit = True, collapse = value)
		if self.frameTools is not None:
			cmds.frameLayout(self.frameTools, edit = True, collapse = value)
		if self.frameRigging is not None:
			cmds.frameLayout(self.frameRigging, edit = True, collapse = value)
		if self.frameOverlappy is not None:
			cmds.frameLayout(self.frameOverlappy, edit = True, collapse = value)
		if self.frameCenterOfMass is not None:
			cmds.frameLayout(self.frameCenterOfMass, edit = True, collapse = value)
		if self.frameMotionTrail is not None:
			cmds.frameLayout(self.frameMotionTrail, edit = True, collapse = value)
		if self.frameExperimental is not None:
			cmds.frameLayout(self.frameExperimental, edit = True, collapse = value)

	### 停靠
	def DockCheckVisible(self, *args):
		return cmds.dockControl(Settings.dockName, query = True, visible = True)
	def DockCheck(self, *args):
		return cmds.dockControl(Settings.dockName, query = True, exists = True)
	def DockDelete(self, *args):
		if self.DockCheck():
			cmds.deleteUI(Settings.dockName, control = True)
		pass
	def DockOff(self, *args):
		if self.DockCheck():
			cmds.dockControl(Settings.dockName, edit = True, floating = True, height = Settings.windowHeight)
			print("{0} 已取消停靠".format(GeneralWindow._title))
		else:
			cmds.warning("未找到停靠控件")
	def DockToSide(self, areaSide, *args):
		if self.DockCheck():
			cmds.dockControl(Settings.dockName, edit = True, floating = False, area = areaSide)
		else:
			cmds.dockControl(Settings.dockName, label = GeneralWindow._title, content = Settings.windowName, area = areaSide, allowedArea = Settings.dockAllowedAreas)
		print("{0} 已停靠到 {1}".format(GeneralWindow._title, areaSide))

	### 执行
	def WindowCreate(self, *args):
		self.CreateUI()
		self.FramesCollapse(True)
	def RUN_DOCKED(self, path="", forced=False, *args):
		self.optionsPlugin.directory = path

		if (not forced and self.DockCheck()):
			if (self.DockCheckVisible()):
				self.DockDelete()
				print("{0} 已关闭".format(GeneralWindow._title))
				return

		self.DockDelete()
		self.WindowCreate()
		self.DockToSide(Settings.dockStartArea)

		MayaSettings.HelpPopupActivate()
		MayaSettings.CachedPlaybackDeactivate()

