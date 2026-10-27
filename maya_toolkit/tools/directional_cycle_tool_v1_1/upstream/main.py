import os

import maya.cmds as cmds
from maya import OpenMayaUI as omui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from . import version, functions

RedColor = "#59120c"
GreenColor = "#0c590c"

class UISetup_DirCycleTool(MayaQWidgetDockableMixin, QtWidgets.QDialog):

    def __init__(self, parent=None):
        super(UISetup_DirCycleTool, self).__init__(parent)

        self.initUI()



    def initUI(self):

        self.setWindowTitle(version.Title)
        self.setGeometry(100, 100, 400, 150)
        self.SavedController = None


        # Create Main Layout and Main Widget
        mainLayout = QVBoxLayout()

        # Layouts
        HLayout_Buttons = QHBoxLayout()
        HLayout_FeetNumber = QHBoxLayout()
        VLayout_LeftRight = QVBoxLayout()
        HLayout_Angle = QHBoxLayout()


        # Buttons
        self.Button_SelectionSave = QPushButton("Click here to save controllers")
        self.Button_SelectionSave.setStyleSheet(f"background-color: {RedColor}")
        Button_Left = QPushButton("Left")
        Button_Right = QPushButton("Right")
        Button_Back = QPushButton("Back")

        # SpinBox
        self.SpinBox_RotationValue = QSpinBox()
        self.SpinBox_RotationValue.setValue(45)
        self.SpinBox_RotationValue.setMinimum(0)
        self.SpinBox_RotationValue.setMaximum(90)

        self.SpinBox_FeetNumber = QSpinBox()
        self.SpinBox_FeetNumber.setValue(version.FeetNumber)
        self.SpinBox_FeetNumber.setMinimum(0)
        self.SpinBox_FeetNumber.setMaximum(999)

        # Textfield
        Text_SelectionTuto = QLabel("Select your controllers in correct order and save them:\nMaster, Feet, Main body, Upperbody, Head")
        self.Text_FeetNumber = QLabel("Feet number:")
        self.Text_SavedController = QLabel("No controller saved")
        Text_Angle = QLabel("Body angle:")

        # Checkbox
        self.Check_Bake = QCheckBox()
        self.Check_Bake.setChecked(version.Bake)
        self.Check_Bake.setText("Bake to layer?")
        # self.Check_CorrectionLoc = QCheckBox()
        # self.Check_CorrectionLoc.setChecked(False)
        # self.Check_CorrectionLoc.setText("Create correction locators? (will disable Bake to layer)")
        self.Check_CounterRotation = QCheckBox()
        self.Check_CounterRotation.setChecked(False)
        self.Check_CounterRotation.setText("Preserve feet position relative to body (great for non-biped characters)")

        # Add buttons and layouts
        mainLayout.addWidget(Text_SelectionTuto)
        mainLayout.addSpacing(10)
        mainLayout.addWidget(separator())
        mainLayout.addLayout(HLayout_FeetNumber)
        mainLayout.addWidget(self.Button_SelectionSave)
        mainLayout.addWidget(self.Text_SavedController)
        mainLayout.addWidget(separator())
        mainLayout.addSpacing(10)
        mainLayout.addWidget(self.Check_Bake)
        # mainLayout.addWidget(self.Check_CorrectionLoc)
        mainLayout.addWidget(self.Check_CounterRotation)
        mainLayout.addSpacing(10)
        mainLayout.addWidget(separator())
        mainLayout.addLayout(HLayout_Buttons)
        mainLayout.addStretch()

        HLayout_FeetNumber.addWidget(self.Text_FeetNumber)
        HLayout_FeetNumber.addWidget(self.SpinBox_FeetNumber)
        HLayout_FeetNumber.addStretch()

        HLayout_Buttons.addLayout(VLayout_LeftRight)
        HLayout_Buttons.addWidget(Button_Back)

        VLayout_LeftRight.addLayout(HLayout_Angle)
        VLayout_LeftRight.addWidget(Button_Left)
        VLayout_LeftRight.addWidget(Button_Right)

        HLayout_Angle.addWidget(Text_Angle)
        HLayout_Angle.addWidget(self.SpinBox_RotationValue)

        # Create window
        self.setLayout(mainLayout)

        # Signals
        # self.Check_CorrectionLoc.stateChanged.connect(self.checkbox_behavior)
        # self.Check_Bake.stateChanged.connect(self.checkbox_behavior)

        # Button connect
        self.Button_SelectionSave.clicked.connect(self.save_controller)

        Button_Left.clicked.connect(lambda: self.launch_left_right())
        Button_Right.clicked.connect(lambda: self.launch_left_right(Right=True))
        Button_Back.clicked.connect(lambda: self.launch_back())

        


    def launch_left_right(self, Right = False):

        if functions.check_controller_number(self.SavedController, self.RequiredController):
            return
        
        Angle = self.SpinBox_RotationValue.value()
        functions.run_side(
            Right, 
            Angle, 
            self.SavedController, 
            self.Check_Bake.isChecked(), 
            self.SpinBox_FeetNumber.value(), 
            CorrectionLoc = True, 
            CounterRotation = self.Check_CounterRotation.isChecked()
            )

    def launch_back(self):
        functions.run_back(
            self.SavedController, 
            self.Check_Bake.isChecked(), 
            self.SpinBox_FeetNumber.value(), 
            CorrectionLoc = True
            )

    def save_controller(self):
        self.RequiredController = 4 + self.SpinBox_FeetNumber.value()
        self.SavedController = cmds.ls(selection = True)
        NumOfCtrl = len(self.SavedController)

        if NumOfCtrl == self.RequiredController:
            self.Button_SelectionSave.setStyleSheet(f"background-color: {GreenColor}")
            self.Text_SavedController.setText(f"{NumOfCtrl} controllers saved")
        elif NumOfCtrl < self.RequiredController:
            self.Button_SelectionSave.setStyleSheet(f"background-color: {RedColor}")
            self.Text_SavedController.setText(f"Warning! Not enough controllers saved ({NumOfCtrl}). Need {self.RequiredController}.")
        elif NumOfCtrl > self.RequiredController:
            self.Button_SelectionSave.setStyleSheet(f"background-color: {RedColor}")
            self.Text_SavedController.setText(f"Warning! Too many controllers saved ({NumOfCtrl}). Need {self.RequiredController}.")

        print(self.SavedController)

    def load_controllers(self):
        print(self.SavedController)
        cmds.select(self.SavedController)

    def reset_controllers(self):
        self.SavedController = None
        self.Button_SelectionSave.setStyleSheet(f"background-color: {RedColor}")
        self.Text_SavedController.setText("Empty")

    def checkbox_behavior(self):
        Sender = self.sender()

        if Sender == self.Check_CorrectionLoc and self.Check_CorrectionLoc.isChecked():
            self.Check_Bake.blockSignals(True)
            self.Check_Bake.setChecked(False)
            self.Check_Bake.blockSignals(False)
        
        elif Sender == self.Check_Bake and self.Check_Bake.isChecked():
            self.Check_CorrectionLoc.blockSignals(True)
            self.Check_CorrectionLoc.setChecked(False)
            self.Check_CorrectionLoc.blockSignals(False)


          
def separator():
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    line.setStyleSheet("QFrame { background-color: rgb(85,85,85); }")
    return line

