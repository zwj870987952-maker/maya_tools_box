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
# Logic in this module is not optimal enough, need manually change path names, methods and parameters.


def GeneralWindow(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.modules.GeneralWindow as gtwindow
	gtwindow.GeneralWindow().RUN_DOCKED


# FILE
def SceneReload():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Scene as Scene
	Scene.Reload()

def ExitMaya():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Scene as Scene
	Scene.ExitMaya()


# UTILS
def SelectHierarchy():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Selector as Selector
	Selector.SelectHierarchy()

def SelectHierarchyTransforms():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Selector as Selector
	Selector.SelectHierarchyTransforms()

def SavePoseToShelf():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Install as Install
	Install.CreatePoseButton()

def ParentShapes():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Parent as Parent
	Parent.ParentShape()

def AnnotateSelected():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Annotation as Annotation
	Annotation.AnnotateSelected()


# TOGGLES
def ToggleCameras():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleCameras()

def ToggleControlVertices():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleControlVertices()

def ToggleDeformers():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleDeformers()

def ToggleDimensions():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleDimensions()

def ToggleDynamicConstraints():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleDynamicConstraints()

def ToggleDynamics():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleDynamics()

def ToggleFluids():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleFluids()

def ToggleFollicles():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleFollicles()

def ToggleGrid():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleGrid()

def ToggleHairSystems():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleHairSystems()

def ToggleHandles():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleHandles()

def ToggleHulls():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleHulls()

def ToggleIkHandles():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleIkHandles()

def ToggleJoints():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleJoints()

def ToggleLights():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleLights()

def ToggleLocators():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleLocators()

def ToggleManipulators():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleManipulators()

def ToggleNCloths():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleNCloths()

def ToggleNParticles():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleNParticles()

def ToggleNRigids():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleNRigids()

def ToggleNurbsCurves():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleNurbsCurves()

def ToggleNurbsSurfaces():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleNurbsSurfaces()

def TogglePivots():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.TogglePivots()

def TogglePlanes():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.TogglePlanes()

def TogglePolymeshes():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.TogglePolymeshes()

def ToggleShadows():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleShadows()

def ToggleStrokes():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleStrokes()

def ToggleSubdivSurfaces():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleSubdivSurfaces()

def ToggleTextures():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Toggles as Toggles
	Toggles.ToggleTextures()


# LOCATORS
def LocatorsSizeScale(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.SelectedLocatorsSizeScale

def LocatorsSizeSet():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.SelectedLocatorsSizeSet()

def LocatorCreate():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.Create()

def LocatorsMatch():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateOnSelected(constraint = False)

def LocatorsParent():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateOnSelected(constraint = True)

def LocatorsPin():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateOnSelected(constraint = True, bake = True, constrainReverse = True, constrainTranslate = True, constrainRotate = True)

def LocatorsPinWithoutReverse():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateOnSelected(constraint = True, bake = True)

def LocatorsPinPos():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateOnSelected(constraint = True, bake = True, constrainReverse = True, constrainTranslate = True, constrainRotate = False)

def LocatorsPinRot():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateOnSelected(constraint = True, bake = True, constrainReverse = True, constrainTranslate = False, constrainRotate = True)

def LocatorsRelative():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateAndBakeAsChildrenFromLastSelected(constraintReverse = True, skipLastReverse = False)

def LocatorsRelativeSkipLast():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateAndBakeAsChildrenFromLastSelected(constraintReverse = True)

def LocatorsRelativeWithoutReverse():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateAndBakeAsChildrenFromLastSelected()

def LocatorsChainDistribution1():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.ChainDistributionRig as ChainDistributionRig
	ChainDistributionRig.CreateRigVariant1(locatorSize = 10)

def LocatorsChainDistribution2():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.ChainDistributionRig as ChainDistributionRig
	ChainDistributionRig.CreateRigVariant2(locatorSize = 10)

def LocatorsAim(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Locators as Locators
	Locators.CreateOnSelectedAim


# BAKINNG
def BakeClassic(): # brackets added when method used
    import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Baker as Baker
    Baker.BakeSelected

def BakeCustom(): # brackets added when method used
    import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Baker as Baker
    Baker.BakeSelected

def BakeByLast(): # brackets added when method used
    import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Baker as Baker
    Baker.BakeSelectedByLastObject

def BakeByWorld(): # brackets added when method used
    import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Baker as Baker
    Baker.BakeSelectedByWorld


# ANIMATION
def AnimOffsetSelected(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Animation as Animation
	Animation.OffsetSelected

def DeleteKeys():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Animation as Animation
	Animation.DeleteKeys(True)

def DeleteNonkeyable():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Animation as Animation
	Animation.DeleteKeysNonkeyable()

def DeleteStatic():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Animation as Animation
	Animation.DeleteStaticCurves()

def EulerFilterOnSelected():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Animation as Animation
	Animation.EulerFilterOnSelected()

def SetInfinity(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Animation as Animation
	Animation.SetInfinity

def SetTimeline(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Timeline as Timeline
	Timeline.SetTime


# RIGGING
def Constraint(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Constraints as Constraints
	Constraints.ConstrainSelectedToLastObject

def DeleteConstraints():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Constraints as Constraints
	Constraints.DeleteConstraintsOnSelected()

def DisconnectTargets():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Constraints as Constraints
	Constraints.DisconnectTargetsFromConstraintOnSelected()

def RotateOrder(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Other as Other
	Other.RotateOrderVisibility

def SegmentScaleCompensate(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Other as Other
	Other.SegmentScaleCompensate

def JointDrawStyle(): # brackets added when method used
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Other as Other
	Other.JointDrawStyle

def CopySkin():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Skinning as Skinning
	Skinning.CopySkinWeightsFromLastMesh()

def SelectSkinnedMeshesOrJoints():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Skinning as Skinning
	Skinning.SelectSkinnedMeshesOrJoints()

def WrapsCreate():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Deformers as Deformers
	Deformers.WrapsCreateOnSelected()

def WrapsConvert(): # TODO
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Deformers as Deformers
	Deformers.WrapsConvertFromSelected()

def BlendshapesReconstruct():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Deformers as Deformers
	Deformers.BlendshapesReconstruction()

def BlendshapesExtractShapes():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Blendshapes as Blendshapes
	Blendshapes.ExtractShapesFromSelected()

def BlendshapesZeroWeights():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Blendshapes as Blendshapes
	Blendshapes.ZeroBlendshapeWeightsOnSelected()

def CreateCurveFromSelectedObjects():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Curves as Curves
	Curves.CreateCurveFromSelectedObjects()

def CreateCurveFromTrajectory():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.Curves as Curves
	Curves.CreateCurveFromTrajectory()


# MOTION TRAIL
def MotionTrailCreate():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.MotionTrail as MotionTrail
	MotionTrail.Create()

def MotionTrailSelect():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.MotionTrail as MotionTrail
	MotionTrail.Select()

def MotionTrailDelete():
	import maya_toolkit.tools.getools_overlappy.bundle.GETOOLS_SOURCE.utils.MotionTrail as MotionTrail
	MotionTrail.Delete()
