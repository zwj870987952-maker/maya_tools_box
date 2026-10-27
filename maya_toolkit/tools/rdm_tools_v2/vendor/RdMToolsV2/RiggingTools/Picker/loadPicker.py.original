from PySide2 import QtGui,QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from PySide2.QtWidgets import QLabel, QMainWindow, QApplication, QWidget, QVBoxLayout
from PySide2.QtGui import QPixmap


import maya.cmds as cmds
import maya.OpenMayaUI as omui


#QT WIndow!

Title = 'Picker'
Folder = 'RdMToolsV2/RiggingTools/Picker'
UI_File = 'PickerUI.ui'
ResourcesPath = 'RdMToolsV2/Resources/'

def maya_main_window():
    
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)



class UIName(QtWidgets.QDialog):
    
    def __init__(self, parent=maya_main_window()):
        super(UIName, self).__init__(parent)

        self.setWindowTitle(Title)
        self.setFixedSize(485,570)


        imagePath  = cmds.internalVar(usd = True) + ResourcesPath
        
        label = QLabel(self)
        pixmap = QPixmap(imagePath+'Background.png')
        label.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

        self.init_ui()
        self.create_layout()
        self.create_connections()
        


    def init_ui(self):
        
        UIPath  = cmds.internalVar(usd = True) + Folder + '/'
        
        f = QtCore.QFile(UIPath + UI_File)
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

    def create_layout(self):
        
        
        imagePath  = cmds.internalVar(usd = True) + ResourcesPath

      
        #self.ui.RArmIKFK.setIcon(QtGui.QIcon(imagePath+'Switch.png'))
        #self.ui.LArmIKFK.setIcon(QtGui.QIcon(imagePath+'Switch.png'))
        #self.ui.RLegIKFK.setIcon(QtGui.QIcon(imagePath+'Switch.png'))
        #self.ui.LLegIKFK.setIcon(QtGui.QIcon(imagePath+'Switch.png'))
        #self.ui.TorsoNeck.setIcon(QtGui.QIcon(imagePath+'TorsoNeck.png'))
        self.ui.ShowRHand.setVisible(False)
        self.ui.ShowLHand.setVisible(False)
        self.ui.FKSpineBox.setVisible(False)
        self.ui.IKSpineON.setVisible(False)
        self.ui.RArmRibbonBox.setVisible(True)
        self.ui.LArmRibbonBox.setVisible(True)
        self.ui.LLegRibbonBox.setVisible(True)
        self.ui.RLegRibbonBox.setVisible(True)



        
        pass

    def create_connections( self):

        def selectControls (Namespace,controls, *args):    
        
            #Shift command
            print controls  
            mods = cmds.getModifiers()
            if (mods & 1) > 0:
                cmds.select(Namespace + controls, add=True)   
                
            else:
                print controls
                cmds.select (clear = True)
                cmds.select(Namespace + controls, tgl=True) 
        
        #All Controllers        
        controllers = ['Head_CC','Neck_CC','Spine_FK_03_CC','Spine_IK_03_CC','Spine_FK_02_CC','Spine_IK_02_CC','Spine_FK_01_CC','Spine_IK_01_CC','COG_CC','ReverseSpine_CC','Spine1_CC','Spine2_CC','Spine3_CC','Spine_End_CC']
        
        def addControllers(side):    
        

            sideControllers = (str(side)+'arm_IK_CC',str(side)+'Elbow_PV',str(side)+'Leg_IK_CC',str(side)+'Knee_PV',str(side)+'Shoulder_FK_CC',str(side)+'Elbow_FK_CC',str(side)+'Wrist_FK_CC',str(side)+'Leg_FK_CC',str(side)+'Knee_FK_CC',str(side)+'Ankle_FK_CC',str(side)+'Ball_FK_CC',
            str(side)+'ArmRibbon_JC_1_CC',str(side)+'ArmRibbon_JC_2_CC',str(side)+'ArmRibbon_JC_3_CC',str(side)+'ArmRibbon_JC_4_CC',str(side)+'ArmRibbon_JC_5_CC',str(side)+'ArmRibbon_JC_6_CC',str(side)+'ArmRibbon_JC_7_CC',str(side)+'LegRibbon_JC_1_CC',str(side)+'LegRibbon_JC_2_CC',str(side)+'LegRibbon_JC_3_CC',str(side)+'LegRibbon_JC_4_CC',str(side)+'LegRibbon_JC_5_CC',str(side)+'LegRibbon_JC_6_CC',str(side)+'LegRibbon_JC_7_CC',
             str(side)+'Thumb_2_CC', str(side)+'Thumb_1_CC', str(side)+'Thumb_0_CC', str(side)+'Pinky_3_CC', str(side)+'Pinky_2_CC', str(side)+'Pinky_1_CC', str(side)+'Pinky_0_CC',str(side)+'Ring_3_CC', str(side)+'Ring_2_CC', str(side)+'Middle_2_CC', str(side)+'Middle_1_CC', str(side)+'Middle_0_CC', str(side)+'Index_3_CC', str(side)+'Ring_1_CC', str(side)+'Ring_0_CC', str(side)+'Middle_3_CC', str(side)+'Index_2_CC', str(side)+'Index_1_CC', str(side)+'Index_0_CC',
             str(side)+'RF_Ball', str(side)+'RF_Ball2', str(side)+'RF_Fingers', str(side)+'RF_Heel', str(side)+'RF_InFoot', str(side)+'RF_OutFoot')
            
            
            for i in sideControllers:
                controllers.append(i)

        addControllers('L_')
        addControllers('R_')

        print 'Controllers : {}'.format(controllers)
        
        #Buttons Connections
            #Head
        self.ui.Head.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Head_CC') )
        self.ui.Neck.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Neck_CC' ) ) 
            
            #Spine IKFK
        self.ui.SpineFK01.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine_FK_01_CC') )
        self.ui.SpineFK02.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine_FK_02_CC') )
        self.ui.SpineFK03.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine_FK_03_CC') )
        self.ui.SpineIK01.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine_IK_02_CC') )
        self.ui.SpineIK02.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine_IK_03_CC') )
        
            #COG
        self.ui.COG.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'COG_CC') )
        self.ui.Pelvis.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine_IK_01_CC' if cmds.objExists('Spine_IK_01_CC') else 'ReverseSpine_CC') )

            #Spine FK
        self.ui.SpineFK01_2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine1_CC') )
        self.ui.SpineFK02_2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine2_CC') )
        self.ui.SpineFK03_2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine3_CC') )
        self.ui.SpineFK04_2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'Spine_End_CC') )

            #Clavicles
        self.ui.L_Clav.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Clavicule_CC') )
        self.ui.R_Clav.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Clavicule_CC') )
        
            #Arms IK
        self.ui.L_IKArm.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_arm_IK_CC') )
        self.ui.L_PVArm.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Elbow_PV') )
        self.ui.R_IKArm.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_arm_IK_CC') )
        self.ui.R_PVArm.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Elbow_PV') )

            #Arms FK
        self.ui.L_FKArm01.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Shoulder_FK_CC') )
        self.ui.L_FKArm02.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Elbow_FK_CC') )
        self.ui.L_FKArm03.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Wrist_FK_CC') )
        self.ui.R_FKArm01.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Shoulder_FK_CC') )
        self.ui.R_FKArm02.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Elbow_FK_CC') )
        self.ui.R_FKArm03.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Wrist_FK_CC') )

            #Legs IK
        self.ui.L_PVLeg.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Knee_PV') )
        self.ui.L_IKLeg.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Leg_IK_CC') )
        self.ui.R_PVLeg.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Knee_PV') )
        self.ui.R_IKLeg.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Leg_IK_CC') )                    

            #Legs FK
        self.ui.L_FKLeg01.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Leg_FK_CC') )
        self.ui.L_FKLeg02.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Knee_FK_CC') )
        self.ui.L_FKLeg03.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Ankle_FK_CC') )
        self.ui.L_FKLeg04.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Ball_FK_CC') )
        self.ui.R_FKLeg01.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Leg_FK_CC') )
        self.ui.R_FKLeg02.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Knee_FK_CC') )
        self.ui.R_FKLeg03.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Ankle_FK_CC') )
        self.ui.R_FKLeg04.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Ball_FK_CC') )
                
            #Reverse foot
        self.ui.LRF01.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_RF_OutFoot') )
        self.ui.LRF02.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_RF_InFoot') )
        self.ui.LRF03.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_RF_Heel') )
        self.ui.LRF04.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_RF_Ball') )
        self.ui.LRF05.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_RF_Ball2') )
        self.ui.LRF06.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_RF_Fingers') )
        self.ui.RRF01.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_RF_OutFoot') )
        self.ui.RRF02.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_RF_InFoot') )
        self.ui.RRF03.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_RF_Heel') )
        self.ui.RRF04.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_RF_Ball') )
        self.ui.RRF05.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_RF_Ball2') )
        self.ui.RRF06.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_RF_Fingers') )            
            
            #Hand Thumbs
        self.ui.L_ThumbBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Thumb_0_CC') )
        self.ui.L_ThumbBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Thumb_1_CC') )
        self.ui.L_ThumbBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Thumb_2_CC') )
        self.ui.R_ThumbBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Thumb_0_CC') )
        self.ui.R_ThumbBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Thumb_1_CC') )
        self.ui.R_ThumbBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Thumb_2_CC') )

            #Hand Index
        self.ui.L_IndexBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Index_0_CC') )
        self.ui.L_IndexBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Index_1_CC') )
        self.ui.L_IndexBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Index_2_CC') )
        self.ui.L_IndexBtn4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Index_3_CC') )
        self.ui.R_IndexBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Index_0_CC') )
        self.ui.R_IndexBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Index_1_CC') )
        self.ui.R_IndexBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Index_2_CC') )
        self.ui.R_IndexBtn4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Index_3_CC') )
                        
            #Hand Middle
        self.ui.L_MiddleBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Middle_0_CC') )
        self.ui.L_MiddleBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Middle_1_CC') )
        self.ui.L_MiddleBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Middle_2_CC') )
        self.ui.L_MiddleBtn4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Middle_3_CC') )
        self.ui.R_MiddleBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Middle_0_CC') )
        self.ui.R_MiddleBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Middle_1_CC') )
        self.ui.R_MiddleBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Middle_2_CC') )
        self.ui.R_MiddleBtn4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Middle_3_CC') )
                        
            #Hand Ring
        self.ui.L_RingBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Ring_0_CC') )
        self.ui.L_RingBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Ring_1_CC') )
        self.ui.L_RingBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Ring_2_CC') )
        self.ui.L_RingBtn4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Ring_3_CC') )            
        self.ui.R_RingBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Ring_0_CC') )
        self.ui.R_RingBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Ring_1_CC') )
        self.ui.R_RingBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Ring_2_CC') )
        self.ui.R_RingBtn4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Ring_3_CC') )            
                        
            #Hand Pinky
        self.ui.L_PinkyBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Pinky_0_CC') )
        self.ui.L_PinkyBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Pinky_1_CC') )
        self.ui.L_PinkyBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Pinky_2_CC') )
        self.ui.L_PinkyBtn4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_Pinky_3_CC') )
        self.ui.R_PinkyBtn1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Pinky_0_CC') )
        self.ui.R_PinkyBtn2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Pinky_1_CC') )
        self.ui.R_PinkyBtn3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Pinky_2_CC') )
        self.ui.R_PinkyBtn4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_Pinky_3_CC') )          

            #Arms Ribbons
        self.ui.LRibbonArm1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_ArmRibbon_JC_1_CC') )
        self.ui.LRibbonArm2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_ArmRibbon_JC_2_CC') )
        self.ui.LRibbonArm3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_ArmRibbon_JC_3_CC') )
        self.ui.LRibbonArm4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_ArmRibbon_JC_4_CC') )
        self.ui.LRibbonArm5.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_ArmRibbon_JC_5_CC') )
        self.ui.LRibbonArm6.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_ArmRibbon_JC_6_CC') )
        self.ui.LRibbonArm7.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_ArmRibbon_JC_7_CC') )
        self.ui.RRibbonArm1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_ArmRibbon_JC_1_CC') )
        self.ui.RRibbonArm2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_ArmRibbon_JC_2_CC') )
        self.ui.RRibbonArm3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_ArmRibbon_JC_3_CC') )
        self.ui.RRibbonArm4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_ArmRibbon_JC_4_CC') )
        self.ui.RRibbonArm5.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_ArmRibbon_JC_5_CC') )
        self.ui.RRibbonArm6.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_ArmRibbon_JC_6_CC') )
        self.ui.RRibbonArm7.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_ArmRibbon_JC_7_CC') )

            #Legs Ribbons
        self.ui.LRibbonLeg1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_LegRibbon_JC_1_CC') )
        self.ui.LRibbonLeg2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_LegRibbon_JC_2_CC') )
        self.ui.LRibbonLeg3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_LegRibbon_JC_3_CC') )
        self.ui.LRibbonLeg4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_LegRibbon_JC_4_CC') )
        self.ui.LRibbonLeg5.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_LegRibbon_JC_5_CC') )
        self.ui.LRibbonLeg6.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'L_LegRibbon_JC_6_CC') )
        self.ui.LRibbonLeg7.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_LegRibbon_JC_7_CC') )        
        self.ui.RRibbonLeg1.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_LegRibbon_JC_1_CC') )
        self.ui.RRibbonLeg2.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_LegRibbon_JC_2_CC') )
        self.ui.RRibbonLeg3.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_LegRibbon_JC_3_CC') )
        self.ui.RRibbonLeg4.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_LegRibbon_JC_4_CC') )
        self.ui.RRibbonLeg5.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_LegRibbon_JC_5_CC') )
        self.ui.RRibbonLeg6.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_LegRibbon_JC_6_CC') )
        self.ui.RRibbonLeg7.clicked.connect( lambda : selectControls( Namespace = self.ui.NamespaceLine.text(), controls = 'R_LegRibbon_JC_7_CC') )
          
           
        #Other
        self.ui.Lock.clicked.connect(lambda: self.ui.NamespaceLine.setDisabled(True))
        self.ui.UnLock.clicked.connect(lambda: self.ui.NamespaceLine.setEnabled(True))
          
                                      
if __name__ == "__main__":

    try:
        #UIName_ui.close() # pylint: disable=E0601
        #UIName_ui.deleteLater()
        print ''
    except:
        pass
    UIName_ui = UIName()
    UIName_ui.show()
