from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya_toolkit.tools.rdm_tools_v2.qt_compat import QtGui, QtCore
from maya_toolkit.tools.rdm_tools_v2.qt_compat import QtUiTools
from maya_toolkit.tools.rdm_tools_v2.qt_compat import QtWidgets
from maya_toolkit.tools.rdm_tools_v2.qt_compat import wrapInstance
import maya.cmds as cmds
import maya.OpenMayaUI as omui
import maya.mel as mel
from maya_toolkit.tools.rdm_tools_v2.native import RmdTools_Path
from maya_toolkit.tools.rdm_tools_v2.native import RdMToolsV2
'\nlicense: EULA\n         https://www.eulatemplate.com/live.php?token=Izv1fodFF2LI2iq8rhySiedABF6e3rti\n\n'
'\n\nfrom RdMToolsV2.ShowUI import RdMV2UI\nRdMV2_ui = RdMV2UI()\nRdMV2_ui.show()\n\n'

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class RdMV2UI(QtWidgets.QDialog):

    def __init__(self, parent=None):
        if parent is None:
            parent = maya_main_window()
        super(RdMV2UI, self).__init__(parent)
        self.setWindowTitle('RdM Tools V2')
        self.path = RmdTools_Path._RdMlocpath
        self.init_ui()
        self.create_layout()

    def init_ui(self):
        UIPath = self.path + '/RdMToolsV2/'
        f = QtCore.QFile(UIPath + 'RdMV2.ui')
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)
        f.close()

    def create_layout(self):
        self.ui.layout().setContentsMargins(3, 3, 3, 3)
        imagePath = self.path + '/RdMToolsV2/Resources/'
        self.ui.SpineLoc.setIcon(QtGui.QIcon(imagePath + 'Locator.png'))
        self.ui.HeadLoc.setIcon(QtGui.QIcon(imagePath + 'Locator.png'))
        self.ui.ArmsLoc.setIcon(QtGui.QIcon(imagePath + 'Locator.png'))
        self.ui.LegsLoc.setIcon(QtGui.QIcon(imagePath + 'Locator.png'))
        self.ui.SpineJnt.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.HeadJnt.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.ArmsJnt.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.LegsJnt.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.HandJnt.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.FacialBtn.setIcon(QtGui.QIcon(imagePath + 'Cabezas.png'))
        self.ui.BodyBtn.setIcon(QtGui.QIcon(imagePath + 'Picker.png'))
        self.ui.ExtraJointsBtn.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.MouthRefBtn.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.CreateMouthBtn.setIcon(QtGui.QIcon(imagePath + 'Labios.png'))
        self.ui.CreateBrowsBtn.setIcon(QtGui.QIcon(imagePath + 'Cejas.png'))
        self.ui.JointsOnVertexBtn.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.FaceToNurbsBtn.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.EdgeToCurveBtn.setIcon(QtGui.QIcon(imagePath + 'Joint.png'))
        self.ui.RenameBtn.setIcon(QtGui.QIcon(imagePath + 'Rename.png'))
        self.ui.LeftPrefix.setIcon(QtGui.QIcon(imagePath + 'LeftArrow.png'))
        self.ui.RightPrefix.setIcon(QtGui.QIcon(imagePath + 'RightArrow.png'))
        self.ui.ChangeNameBtn.setIcon(QtGui.QIcon(imagePath + 'SearchReplace.png'))
        self.ui.ChangeNameBtn2.setIcon(QtGui.QIcon(imagePath + 'SearchReplace2.png'))
        self.ui.ShowAxisBtn.setIcon(QtGui.QIcon(imagePath + 'Eye.png'))
        self.ui.HideAxisBtn.setIcon(QtGui.QIcon(imagePath + 'NoEye.png'))
        self.ui.AddTwistBtn.setIcon(QtGui.QIcon(imagePath + 'Twist.png'))
        self.ui.SimpleFKBtn.setIcon(QtGui.QIcon(imagePath + 'Chain.png'))
        self.ui.IKFKBtn.setIcon(QtGui.QIcon(imagePath + 'IKFK.png'))
        self.ui.OrientJointsBtn.setIcon(QtGui.QIcon(imagePath + 'Axis.png'))
        self.ui.ParentConstraintBtn.setIcon(QtGui.QIcon(imagePath + 'ParentConstraint.png'))
        self.ui.PointConstraintBtn.setIcon(QtGui.QIcon(imagePath + 'PointConstraint.png'))
        self.ui.OrientConstraintBtn.setIcon(QtGui.QIcon(imagePath + 'OrientConstraint.png'))
        self.ui.ScaleConstraintBtn.setIcon(QtGui.QIcon(imagePath + 'ScaleConstraint.png'))
        self.ui.CreateFollicleBtn.setIcon(QtGui.QIcon(imagePath + 'Follicle.png'))
        self.ui.HideBtn.setIcon(QtGui.QIcon(imagePath + 'Add.png'))
        self.ui.RevealBtn.setIcon(QtGui.QIcon(imagePath + 'Remove.png'))
        self.ui.ConnectWithLineBtn.setIcon(QtGui.QIcon(imagePath + 'Connect.png'))
        self.ui.CreateTextBtn.setIcon(QtGui.QIcon(imagePath + 'CurveText.png'))
        self.ui.CreateSliderBtn.setIcon(QtGui.QIcon(imagePath + 'Slider.png'))
        self.ui.RootAutoBtn.setIcon(QtGui.QIcon(imagePath + 'RootAuto.png'))
        self.ui.OffsetBtn.setIcon(QtGui.QIcon(imagePath + 'OffsetGrp.png'))
        self.ui.MatchTransformBtn.setIcon(QtGui.QIcon(imagePath + 'MatchTrasnforms.png'))
        self.ui.JointCCBtn.setIcon(QtGui.QIcon(imagePath + 'JointCv.png'))
        self.ui.LocatorCCBtn.setIcon(QtGui.QIcon(imagePath + 'LocatorCv.png'))
        self.ui.CircleCCBtn.setIcon(QtGui.QIcon(imagePath + 'Circle.png'))
        self.ui.SphereCCBtn.setIcon(QtGui.QIcon(imagePath + 'Sphere.png'))
        self.ui.CubeCCBtn.setIcon(QtGui.QIcon(imagePath + 'Cube.png'))
        self.ui.HandCCBtn.setIcon(QtGui.QIcon(imagePath + 'Hand.png'))
        self.ui.FootCCBtn.setIcon(QtGui.QIcon(imagePath + 'Foot.png'))
        self.ui.PringleCCBtn.setIcon(QtGui.QIcon(imagePath + 'Pringle.png'))
        self.ui.EyeVisorBtn.setIcon(QtGui.QIcon(imagePath + 'Visor.png'))
        self.ui.PyramidsCCBtn.setIcon(QtGui.QIcon(imagePath + 'PyramidsCC.png'))
        self.ui.SquareCCBtn.setIcon(QtGui.QIcon(imagePath + 'SquareCC.png'))
        self.ui.ArrowCCBtn.setIcon(QtGui.QIcon(imagePath + 'ArrowCC.png'))
        self.ui.MultipleArrowsCCBtn.setIcon(QtGui.QIcon(imagePath + 'MultipleArrowsCC.png'))
        self.ui.SideArrowsCCBtn.setIcon(QtGui.QIcon(imagePath + 'SideArrowsCC.png'))
        self.ui.LineArrowCCBtn.setIcon(QtGui.QIcon(imagePath + 'LineArrowCC.png'))
        self.ui.MirrorBehavior01Btn.setIcon(QtGui.QIcon(imagePath + 'MirroBehavior2.png'))
        self.ui.MirrorBehavior02Btn.setIcon(QtGui.QIcon(imagePath + 'MirroBehavior.png'))
        self.ui.BindSkinBtn.setIcon(QtGui.QIcon(imagePath + 'BindSkin.png'))
        self.ui.copyButton.setIcon(QtGui.QIcon(imagePath + 'Copy.png'))
        self.ui.SelecJointsFromBtn.setIcon(QtGui.QIcon(imagePath + 'MirrorWeights.png'))
        self.ui.JointsEditOn.setIcon(QtGui.QIcon(imagePath + 'EditOn.png'))
        self.ui.JointsEditOff.setIcon(QtGui.QIcon(imagePath + 'EditOff.png'))
        self.ui.Mirror1.setIcon(QtGui.QIcon(imagePath + 'Mirror.png'))
        self.ui.Mirror2.setIcon(QtGui.QIcon(imagePath + 'Mirror.png'))
        self.ui.Mirror3.setIcon(QtGui.QIcon(imagePath + 'Mirror.png'))
        pass
        self.ui.BodyBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.ui.BodyBtn.clicked.connect(lambda: self.ui.BodyBtn.setStyleSheet('font: 8pt "MS Shell Dlg 2";\ntext-decoration: underline;'))
        self.ui.BodyBtn.clicked.connect(lambda: self.ui.FacialBtn.setStyleSheet(''))
        self.ui.FacialBtn.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(1))
        self.ui.FacialBtn.clicked.connect(lambda: self.ui.FacialBtn.setStyleSheet('font: 8pt "MS Shell Dlg 2";\ntext-decoration: underline;'))
        self.ui.FacialBtn.clicked.connect(lambda: self.ui.BodyBtn.setStyleSheet(''))
        self.ui.SpineLoc.clicked.connect(self.RdMSpineLoc)
        self.ui.SpineJnt.clicked.connect(self.RdMSpineJnt)
        self.ui.SpineCreate.clicked.connect(self.RdMSpineCreate)
        self.ui.HeadLoc.clicked.connect(self.RdMAutoHeadLoc)
        self.ui.HeadJnt.clicked.connect(self.RdMAutoHeadJnt)
        self.ui.HeadCreate.clicked.connect(self.RdMHeadCreate)
        self.ui.LegsLoc.clicked.connect(self.RdMAutoLegsLoc)
        self.ui.LegsJnt.clicked.connect(self.RdMAutoLegsJnt)
        self.ui.LegsCreate.clicked.connect(self.RdMLegsCreate)
        self.ui.ArmsLoc.clicked.connect(self.RdMAutoArmsLoc)
        self.ui.ArmsJnt.clicked.connect(self.RdMAutoArmsJnt)
        self.ui.ArmsCreate.clicked.connect(self.RdMArmsCreate)
        self.ui.HandJnt.clicked.connect(self.RdMHandJnt)
        self.ui.HandsCreate.clicked.connect(self.RdMHandCreate)
        self.ui.CreateBaseController.clicked.connect(self.RdMCreateBaseController)
        self.ui.ConnectSpine.clicked.connect(self.RdMConnectSpine)
        self.ui.ConnectHead.clicked.connect(self.RdMConnectHead)
        self.ui.ConnectArms.clicked.connect(self.RdMConnectArms)
        self.ui.ConnectLegs.clicked.connect(self.RdMConnectLegs)
        self.ui.BindRdmTools.clicked.connect(self.RdMBindSkinAutoRig)
        self.ui.ImproveArmsBtn.clicked.connect(self.RdMImproveArms)
        self.ui.ImproveLegsBtn.clicked.connect(self.RdMImproveLegs)
        self.ui.ImproveSpineBtn.clicked.connect(self.RdMImproveSpine)
        self.ui.ImproveHeadBtn.clicked.connect(self.RdMImproveHands)
        self.ui.improveHelp.clicked.connect(lambda: cmds.launch(web='https://renderdemartes.com/2020/04/14/improve-parts-rdm-tools-v2/'))
        self.ui.RenameBtn.clicked.connect(self.RdMRename)
        self.ui.SetPrefixBtn.clicked.connect(self.RdMRenamePref)
        self.ui.SetSufixBtn.clicked.connect(self.RdMRenameSuf)
        self.ui.JointSufix.clicked.connect(self.RdMJointSufix)
        self.ui.JointCtrlSufix.clicked.connect(self.RdMJointCtrlSufix)
        self.ui.ControllerSufix.clicked.connect(self.RdMControllerSufix)
        self.ui.GroupSufix.clicked.connect(self.RdMGroupSufix)
        self.ui.RightPrefix.clicked.connect(self.RdMRightPrefix)
        self.ui.LeftPrefix.clicked.connect(self.RdMLeftPrefix)
        self.ui.ChangeNameBtn.clicked.connect(self.RdMSearchReplace)
        self.ui.ChangeNameBtn2.clicked.connect(self.RdMSearchReplace2)
        self.ui.IKFKBtn.clicked.connect(self.RdMIKFK)
        self.ui.AddTwistBtn.clicked.connect(self.RdMAutoTwist)
        self.ui.ShowJntsBtn.clicked.connect(self.RdMShowJoints)
        self.ui.HideJointsBtn.clicked.connect(self.RdMHideJoints)
        self.ui.HideAxisBtn.clicked.connect(self.RdMHideAxis)
        self.ui.ShowAxisBtn.clicked.connect(self.RdMShowAxis)
        self.ui.JointSizeSlider.valueChanged.connect(lambda: cmds.jointDisplayScale(self.ui.JointSizeSlider.value() * 0.04))
        self.ui.OrientJointsBtn.clicked.connect(self.RdMOrientJoints)
        self.ui.HideBtn.clicked.connect(self.RdMHideAttr)
        self.ui.RevealBtn.clicked.connect(self.RdMShowAttr)
        self.ui.ParentConstraintBtn.clicked.connect(lambda: cmds.parentConstraint(mo=1 if self.ui.MantainOffsetBtn.isChecked() == True else 0))
        self.ui.PointConstraintBtn.clicked.connect(lambda: cmds.pointConstraint(mo=1 if self.ui.MantainOffsetBtn.isChecked() == True else 0))
        self.ui.OrientConstraintBtn.clicked.connect(lambda: cmds.orientConstraint(mo=1 if self.ui.MantainOffsetBtn.isChecked() == True else 0))
        self.ui.ScaleConstraintBtn.clicked.connect(lambda: cmds.scaleConstraint(mo=1 if self.ui.MantainOffsetBtn.isChecked() == True else 0))
        self.ui.SimpleFKBtn.clicked.connect(self.RdMSimpleFK)
        self.ui.CreateFollicleBtn.clicked.connect(self.RdMCreateFollicle)
        self.ui.ConnectWithLineBtn.clicked.connect(self.RdMConnectWithLine)
        self.ui.RefPlane.clicked.connect(self.RdMRefPlane)
        self.ui.CreateSliderBtn.clicked.connect(self.RdMSlider)
        self.ui.CreateTextBtn.clicked.connect(self.RdMTextToCurve)
        self.ui.RootAutoBtn.clicked.connect(self.RdMRootAuto)
        self.ui.OffsetBtn.clicked.connect(self.RdMOffsetGrp)
        self.ui.MatchTransformBtn.clicked.connect(lambda: cmds.matchTransform())
        self.ui.ParentRS.clicked.connect(lambda: cmds.parent(r=True, s=True))
        self.ui.ParentSAdd.clicked.connect(lambda: cmds.parent(s=True, add=True))
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Curves.curveOnSelection import curveOnSelectionFunc
        legacy_reload(RdMToolsV2.RiggingTools.Curves.curveOnSelection)
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Curves.CurveColors import colorShape
        legacy_reload(RdMToolsV2.RiggingTools.Curves.CurveColors)
        self.ui.JointCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Joint', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.LocatorCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Locator', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.CircleCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='CircleX' if self.ui.XAxis.isChecked() else 'CircleY' if self.ui.YAxis.isChecked() else 'CircleZ', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.SphereCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Sphere', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.CubeCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Cube', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.HandCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Hand', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.FootCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Foot', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.PringleCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Pringle', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.EyeVisorBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='EyeVisor', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.PyramidsCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Pyramids', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.SquareCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Square', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.ArrowCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='Arrow', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.MultipleArrowsCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='MultipleArrows', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.SideArrowsCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='SideArrows', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.LineArrowCCBtn.clicked.connect(lambda: curveOnSelectionFunc(mode='LineArrow', Constraint=True if self.ui.ParentConstraintCheckBox.isChecked() else False))
        self.ui.RedBtn.clicked.connect(lambda: colorShape(Color=13))
        self.ui.BlueBtn.clicked.connect(lambda: colorShape(Color=6))
        self.ui.GreenBtn.clicked.connect(lambda: colorShape(Color=14))
        self.ui.WhiteBtn.clicked.connect(lambda: colorShape(Color=16))
        self.ui.PurpleBtn.clicked.connect(lambda: colorShape(Color=9))
        self.ui.YellowBtn.clicked.connect(lambda: colorShape(Color=17))
        self.ui.LightBlueBtn.clicked.connect(lambda: colorShape(Color=18))
        self.ui.GreyBtn.clicked.connect(lambda: colorShape(Color=1))
        self.ui.MirrorBehavior01Btn.clicked.connect(self.MirrorBehaviorFunc01)
        self.ui.MirrorBehavior02Btn.clicked.connect(self.MirrorBehaviorFunc02)
        self.ui.JointsEditOn.clicked.connect(self.JointsOn)
        self.ui.JointsEditOff.clicked.connect(self.JointsOff)
        self.ui.BindSkinBtn.clicked.connect(self.bindSkinFunc)
        self.ui.SkinHelpButton.clicked.connect(self.SkinHelpFunc)
        self.ui.CleanKeysBtn.clicked.connect(self.CleanKeysFunc)
        self.ui.copyButton.clicked.connect(lambda: cmds.copySkinWeights(surfaceAssociation='closestPoint', normalize=1, influenceAssociation='closestJoint', noMirror=1))
        self.ui.SelecJointsFromBtn.clicked.connect(self.jointsFromSel)
        self.ui.ExportWeightBtn.clicked.connect(lambda: mel.eval('ExportSkinWeightMaps;'))
        self.ui.ImportWeightBtn.clicked.connect(lambda: mel.eval('ImportSkinWeightMaps;'))
        self.ui.Mirror1.clicked.connect(self.MirrorSkinMethod1)
        self.ui.Mirror2.clicked.connect(self.MirrorSkinMethod2)
        self.ui.Mirror3.clicked.connect(self.MirrorSkinMethod3)
        self.ui.LegacyBtn.clicked.connect(self.ImportLegacy)
        self.ui.TutorialsBtn.clicked.connect(lambda: cmds.launch(web='https://www.youtube.com/channel/UCZuDxwetGtgKYL2XvbAC1-w?'))
        self.ui.ExtraJointsBtn.clicked.connect(self.facialExtraJointsUI)
        self.ui.FacialControllersBtn.clicked.connect(self.facialExtraControllersUI)
        self.ui.UpMouthArrows.clicked.connect(lambda: self.ui.UpMouthLine.setText(str(cmds.ls(sl=True))))
        self.ui.DownMouthArrows.clicked.connect(lambda: self.ui.DownMouthLine.setText(str(cmds.ls(sl=True))))
        self.ui.MouthRefBtn.clicked.connect(self.MouthRefUI)
        self.ui.CreateMouthBtn.clicked.connect(self.MouthBuildUI)
        self.ui.BrowsArrows.clicked.connect(lambda: self.ui.BrowsLine.setText(str(cmds.ls(sl=True))))
        self.ui.CreateBrowsBtn.clicked.connect(self.CreateBrowsUI)
        pass

    def ImportLegacy(self):
        import RdMTools.RdMMenu

    def RdMSpineLoc(self):
        if self.ui.SpineFKBtn.isChecked() == True:
            from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRig.RdMAutoSpine import LocatorsBtn
            legacy_reload(RdMToolsV2.RiggingTools.AutoRig.RdMAutoSpine)
            LocatorsBtn(jointsNumVar=self.ui.SpineSlider.value())
        else:
            from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoSpine_V2 import LocatorsBtn
            legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoSpine_V2)
            LocatorsBtn(jointsNumVar=self.ui.SpineSlider.value())

    def RdMSpineJnt(self):
        if self.ui.SpineFKBtn.isChecked() == True:
            from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRig.RdMAutoSpine import JointsBtn
            legacy_reload(RdMToolsV2.RiggingTools.AutoRig.RdMAutoSpine)
            JointsBtn(jointsNumVar=self.ui.SpineSlider.value())
        else:
            from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoSpine_V2 import JointsBtn
            legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoSpine_V2)
            JointsBtn(jointsNumVar=self.ui.SpineSlider.value())

    def RdMSpineCreate(self):
        if self.ui.SpineFKBtn.isChecked() == True:
            print('FK Spine')
            from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRig.RdMAutoSpine import SpineBtn
            legacy_reload(RdMToolsV2.RiggingTools.AutoRig.RdMAutoSpine)
            SpineBtn(jointsNumVar=self.ui.SpineSlider.value(), GlobalMultVar=self.ui.SizeSlider.value())
        else:
            print('IKFK Spine')
            from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoSpine_V2 import SpineBtn
            legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoSpine_V2)
            SpineBtn(jointsNumVar=self.ui.SpineSlider.value(), GlobalMultVar=self.ui.SizeSlider.value())

    def RdMAutoHeadLoc(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoHeadV3 import LocatorsChickenHead
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoHeadV3)
        LocatorsChickenHead()

    def RdMAutoHeadJnt(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoHeadV3 import JointsChickenHead
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoHeadV3)
        JointsChickenHead()

    def RdMHeadCreate(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoHeadV3 import ChickenHead
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoHeadV3)
        ChickenHead(GlobalMultVar=self.ui.SizeSlider.value())

    def RdMAutoLegsLoc(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoLegs_V2 import LocatorsBtn
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoLegs_V2)
        LocatorsBtn()

    def RdMAutoLegsJnt(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoLegs_V2 import JointsBtn
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoLegs_V2)
        JointsBtn()

    def RdMLegsCreate(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoLegs_V2 import IKFKLegs
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoLegs_V2)
        IKFKLegs(LegsSize=self.ui.SizeSlider.value() * 2, Twist=True if self.ui.LegsTwistBtn.isChecked() else False, Ribbon=True if self.ui.LegsRibbonBtn.isChecked() else False)

    def RdMAutoArmsLoc(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoArms_V2 import LocatorsBtn
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoArms_V2)
        LocatorsBtn()

    def RdMAutoArmsJnt(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoArms_V2 import JointsBtn
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoArms_V2)
        JointsBtn()

    def RdMArmsCreate(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoArms_V2 import IKFKArms
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoArms_V2)
        IKFKArms(ArmsSize=self.ui.SizeSlider.value() * 2, Twist=True if self.ui.ArmsTwistBtn.isChecked() else False, Ribbon=True if self.ui.ArmsRibonBtn.isChecked() else False)

    def RdMHandJnt(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoHands_V3 import CreateJoints
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoHands_V3)
        CreateJoints(ThumbCheckOn=1 if self.ui.ThumbsCheckBox.isChecked() else 0, IndexCheckOn=1 if self.ui.IndexCheckBox.isChecked() else 0, MiddleCheckOn=1 if self.ui.MiddleCheckBox.isChecked() else 0, RingCheckOn=1 if self.ui.RingCheckBox.isChecked() else 0, PinkyCheckOn=1 if self.ui.PinkyCheckBox.isChecked() else 0)

    def RdMHandCreate(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.AutoHands_V3 import CreateControllers
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.AutoHands_V3)
        CreateControllers(GlobalMultVar=self.ui.SizeSlider.value())

    def RdMCreateBaseController(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2 import MasterControl
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2)
        MasterControl(CharacterNameVar=self.ui.CharacterControllerName.text(), ControlScaleVar=self.ui.MasterControllerSize.value())

    def RdMConnectSpine(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2 import ConnectSpine
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2)
        ConnectSpine(CharacterNameVar=self.ui.CharacterControllerName.text())

    def RdMConnectHead(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2 import ConnectHead
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2)
        ConnectHead(CharacterNameVar=self.ui.CharacterControllerName.text())

    def RdMConnectArms(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2 import ConnectArms
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2)
        ConnectArms(CharacterNameVar=self.ui.CharacterControllerName.text())

    def RdMConnectLegs(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2 import ConnectLegs
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.RdMAutoCompletev2)
        ConnectLegs(CharacterNameVar=self.ui.CharacterControllerName.text())

    def RdMBindSkinAutoRig(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.RdMBindSkinV2 import BindSkin
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.RdMBindSkinV2)
        BindSkin()

    def RdMImproveArms(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.improveParts import improveArms
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.improveParts)
        improveArms()

    def RdMImproveLegs(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.improveParts import improveLegs
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.improveParts)
        improveLegs()

    def RdMImproveSpine(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.improveParts import improveSpineHead
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.improveParts)
        improveSpineHead(SpineAmount=self.ui.SpineSlider.value(), mode='FK' if self.ui.SpineFKBtn.isChecked() else 'IK')

    def RdMImproveHands(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.AutoRigV2.improveParts import improveHands
        legacy_reload(RdMToolsV2.RiggingTools.AutoRigV2.improveParts)
        improveHands()

    def RdMRename(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import RenameThis
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        RenameThis(NewName=self.ui.NewNameLineEdit.text(), NumCheck=1 if self.ui.RenameNumCheckBox.isChecked() else 0)

    def RdMRenamePref(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import AddCustomPrefix
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        AddCustomPrefix(customText=self.ui.NewNameLineEdit.text())

    def RdMRenameSuf(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import AddCustomSufix
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        AddCustomSufix(customText=self.ui.NewNameLineEdit.text())

    def RdMJointSufix(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import JointSufix
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        JointSufix(sufix='Jnt')

    def RdMJointCtrlSufix(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import JointSufix
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        JointSufix(sufix='JntCtrl')

    def RdMControllerSufix(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import JointSufix
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        JointSufix(sufix='Ctrl')

    def RdMGroupSufix(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import JointSufix
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        JointSufix(sufix='GRP')

    def RdMRightPrefix(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import AddPrefix
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        AddPrefix(side='R')

    def RdMLeftPrefix(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import AddPrefix
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        AddPrefix(side='L')

    def RdMSearchReplace(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import SearchReplace
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        SearchReplace(Search=self.ui.SearchLineEdit.text(), Replace=self.ui.ReplaceLineEdit.text())

    def RdMSearchReplace2(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.Renamer import SearchReplaceHerarchy
        legacy_reload(RdMToolsV2.RiggingTools.Tools.Renamer)
        SearchReplaceHerarchy(Search=self.ui.SearchLineEdit.text(), Replace=self.ui.ReplaceLineEdit.text())

    def RdMIKFK(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.AutoIKFK import RdM_IKFK
        legacy_reload(RdMToolsV2.RiggingTools.Tools.AutoIKFK)
        RdM_IKFK()

    def RdMAutoTwist(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.AutoTwist import AutoTwistFunc
        legacy_reload(RdMToolsV2.RiggingTools.Tools.AutoTwist)
        AutoTwistFunc(Axis='X' if self.ui.XAxisRadioButton.isChecked() == True else 'Y' if self.ui.YAxisRadioButton.isChecked() == True else 'Z', SwitchVar=1 if self.ui.ReverseTwistCheckBox.isChecked() == True else 0)

    def RdMHideJoints(self):
        import maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.ShowHide.RdMHideJoints as NotSeeJoints
        from maya_toolkit.tools.rdm_tools_v2.native import RdMToolsV2
        legacy_reload(NotSeeJoints)

    def RdMShowJoints(self):
        import maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.ShowHide.RdMShowJoints as SeeJoints
        from maya_toolkit.tools.rdm_tools_v2.native import RdMToolsV2
        legacy_reload(SeeJoints)

    def RdMShowAxis(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.ShowHide.RdMToggleAxis import setAxisDisplay
        legacy_reload(RdMToolsV2.RiggingTools.ShowHide.RdMToggleAxis)
        setAxisDisplay(display=True)

    def RdMHideAxis(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.ShowHide.RdMToggleAxis import setAxisDisplay
        legacy_reload(RdMToolsV2.RiggingTools.ShowHide.RdMToggleAxis)
        setAxisDisplay(display=False)

    def RdMOrientJoints(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.RdMOrientJoint import OrientJoints
        OrientJoints(oj='xzy' if self.ui.SpineOrientRadioButton.isChecked() == True else 'xyz', sao='zup')

    def RdMHideAttr(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.ShowHideAttr import hideSelection
        legacy_reload(RdMToolsV2.RiggingTools.Tools.ShowHideAttr)
        hideSelection(hideT=self.ui.HideTranslateCheckBox.isChecked(), hideR=self.ui.HideRotateCheckBox.isChecked(), hideS=self.ui.HideScaleCheckBox.isChecked(), hideV=self.ui.HideVisibilityCheckBox.isChecked())

    def RdMShowAttr(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.ShowHideAttr import showAll
        legacy_reload(RdMToolsV2.RiggingTools.Tools.ShowHideAttr)
        showAll()

    def RdMSimpleFK(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.RdMSimpleFK import SimpleFKFunc
        legacy_reload(RdMToolsV2.RiggingTools.Tools.RdMSimpleFK)
        SimpleFKFunc()

    def RdMCreateFollicle(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.FollicleOnPositionAlt import createFol
        legacy_reload(RdMToolsV2.RiggingTools.Tools.FollicleOnPositionAlt)
        createFol(addJoint=True if self.ui.FolicleJointCheckBox.isChecked() else False, NewName=self.ui.FollicleNewName.text())

    def RdMConnectWithLine(self):
        import maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.ConnectPart as ConnectPart
        from maya_toolkit.tools.rdm_tools_v2.native import RdMToolsV2

    def RdMRefPlane(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.PlaneRef import RefPlane
        legacy_reload(RdMToolsV2.RiggingTools.Tools.PlaneRef)
        RefPlane()

    def RdMSlider(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Curves.SliderCreator import VerticalSlider
        legacy_reload(RdMToolsV2.RiggingTools.Curves.SliderCreator)
        VerticalSlider(Name=self.ui.SliderName.text(), Size=self.ui.SliderSize.value(), Square=True if self.ui.SquareSliderCheckBox.isChecked() else False, Negatives=True if self.ui.NeagtiveSliderCheckBox.isChecked() else False)

    def RdMTextToCurve(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Curves.RdMTextCurve import TextToCurve
        legacy_reload(RdMToolsV2.RiggingTools.Curves.RdMTextCurve)
        TextToCurve(Textisimo=self.ui.TextlineEdit.text(), font=self.ui.fontComboBox.currentText())

    def RdMRootAuto(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Curves.RootAuto import rootAuto
        legacy_reload(RdMToolsV2.RiggingTools.Curves.RootAuto)
        rootAuto()

    def RdMOffsetGrp(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Curves.RootAuto import offsetGrp
        legacy_reload(RdMToolsV2.RiggingTools.Curves.RootAuto)
        offsetGrp()

    def MirrorBehaviorFunc01(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.MirrorBehavior import mirrorParts
        legacy_reload(RdMToolsV2.RiggingTools.Tools.MirrorBehavior)
        mirrorParts(world=False)

    def MirrorBehaviorFunc02(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Tools.MirrorBehavior import mirrorParts
        legacy_reload(RdMToolsV2.RiggingTools.Tools.MirrorBehavior)
        mirrorParts(world=True)

    def JointsOn(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Skin.MoveBindJoints import moveJoints
        legacy_reload(RdMToolsV2.RiggingTools.Skin.MoveBindJoints)
        moveJoints(mode=True)

    def JointsOff(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Skin.MoveBindJoints import moveJoints
        legacy_reload(RdMToolsV2.RiggingTools.Skin.MoveBindJoints)
        moveJoints(mode=False)

    def jointsFromSel(self):
        import maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Skin.JointsFromSkin as jfs
        from maya_toolkit.tools.rdm_tools_v2.native import RdMToolsV2
        legacy_reload(jfs)

    def bindSkinFunc(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Skin.RdMBindSkin import rdmBindSkin
        legacy_reload(RdMToolsV2.RiggingTools.Skin.RdMBindSkin)
        rdmBindSkin()

    def SkinHelpFunc(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Skin.SkinHelp import helpSkin
        legacy_reload(RdMToolsV2.RiggingTools.Skin.SkinHelp)
        helpSkin(rotation=self.ui.SkinHelpSlider.value())

    def CleanKeysFunc(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Skin.SkinHelp import cleanHelp
        legacy_reload(RdMToolsV2.RiggingTools.Skin.SkinHelp)
        cleanHelp()

    def MirrorSkinMethod1(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Skin.RdMMirrorSkin import RdMMirrorSkin
        legacy_reload(RdMToolsV2.RiggingTools.Skin.RdMMirrorSkin)
        RdMMirrorSkin(influenceAssociation1='closetJoint01' if self.ui.closetJoint01.isChecked() else 'oneToOne' if self.ui.oneToOne01.isChecked() else 'label', influenceAssociation2='closetJoint01' if self.ui.closetJoint02.isChecked() else 'oneToOne' if self.ui.oneToOne02.isChecked() else 'label', surfaceAssociation='closestPoint')

    def MirrorSkinMethod2(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Skin.RdMMirrorSkin import RdMMirrorSkin
        legacy_reload(RdMToolsV2.RiggingTools.Skin.RdMMirrorSkin)
        RdMMirrorSkin(influenceAssociation1='closetJoint01' if self.ui.closetJoint01.isChecked() else 'oneToOne' if self.ui.oneToOne01.isChecked() else 'label', influenceAssociation2='closetJoint01' if self.ui.closetJoint02.isChecked() else 'oneToOne' if self.ui.oneToOne02.isChecked() else 'label', surfaceAssociation='rayCast')

    def MirrorSkinMethod3(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Skin.RdMMirrorSkin import RdMMirrorSkin
        legacy_reload(RdMToolsV2.RiggingTools.Skin.RdMMirrorSkin)
        RdMMirrorSkin(influenceAssociation1='closetJoint01' if self.ui.closetJoint01.isChecked() else 'oneToOne' if self.ui.oneToOne01.isChecked() else 'label', influenceAssociation2='closetJoint01' if self.ui.closetJoint02.isChecked() else 'oneToOne' if self.ui.oneToOne02.isChecked() else 'label', surfaceAssociation='closestComponent')

    def facialExtraJointsUI(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Facial.ExtraFacial import extraJointsFace
        legacy_reload(RdMToolsV2.RiggingTools.Facial.ExtraFacial)
        extraJointsFace(GlobalMult=self.ui.SizeSlider.value())

    def facialExtraControllersUI(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Facial.ExtraFacial import extraControlJointsFace
        legacy_reload(RdMToolsV2.RiggingTools.Facial.ExtraFacial)
        extraControlJointsFace(GlobalMult=self.ui.SizeSlider.value())

    def MouthRefUI(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Facial.AutoMouth import LipNurbs
        legacy_reload(RdMToolsV2.RiggingTools.Facial.AutoMouth)
        cmds.select(cl=True)
        txt = self.ui.UpMouthLine.text()
        print(txt)
        txt = txt.replace('u', '')
        txt = txt.replace("'", '')
        txt = txt[:-1]
        txt = txt.split(',')
        for i in txt:
            print(i)
            if str(i)[0] == '[':
                cmds.select(str(i)[1:], add=True)
            else:
                cmds.select(i, add=True)
        LipNurbs(size=1, Name='upperLip')
        cmds.select(cl=True)
        txt = self.ui.DownMouthLine.text()
        print(txt)
        txt = txt.replace('u', '')
        txt = txt.replace("'", '')
        txt = txt[:-1]
        txt = txt.split(',')
        for i in txt:
            print(i)
            if str(i)[0] == '[':
                cmds.select(str(i)[1:], add=True)
            else:
                cmds.select(i, add=True)
        LipNurbs(size=1, Name='lowerLip')

    def MouthBuildUI(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Facial.AutoMouth import LipsSystem
        legacy_reload(RdMToolsV2.RiggingTools.Facial.AutoMouth)
        LipsSystem(Scale=self.ui.SizeSlider.value())

    def CreateBrowsUI(self):
        from maya_toolkit.tools.rdm_tools_v2.native.RdMToolsV2.RiggingTools.Facial.AutoBrows import polyToNurbs, createRibbons
        legacy_reload(RdMToolsV2.RiggingTools.Facial.AutoBrows)
        txt = self.ui.BrowsLine.text()
        print(txt)
        txt = txt.replace('u', '')
        txt = txt.replace("'", '')
        txt = txt[:-1]
        txt = txt.split(',')
        for i in txt:
            print(i)
            if str(i)[0] == '[':
                cmds.select(str(i)[1:], add=True)
            else:
                cmds.select(i, add=True)
        polyToNurbs(Name='L_Brow', mirror=True)
        createRibbons(bindJoints=5, controljoints=3, controllersSize=1, mode='u' if self.ui.UModeRadio.isChecked() == True else 'v')


def run_script():
    exec(compile('try:\n    RdMV2_ui.close()\n    RdMV2_ui.deleteLater()\nexcept:\n    pass\nRdMV2_ui = RdMV2UI()\nRdMV2_ui.show()', __file__, "exec"), globals())
