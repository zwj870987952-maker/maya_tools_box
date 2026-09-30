from .proxy import pm
from . import runtime as _r
import maya.OpenMaya as om
import logging
'\n// Universal IK FK PRO\n// version 3.0\n// October 06, 2021\n// Monika Gelbmann\n// monikagelbmann@gmail.com\n// www.monikagelbmann.com\n\nUniversal IK FK Switch and Match Tool - PRO\n\nDESCRIPTION:\nThis script lets you switch and match Poses between IK/FK controls in the animation scene.\nWorks for Riggs that don\'t have IK/FK match built in and requires only Standard FK controls and IK Pole Vector Setup.\nThe Controls are defined once and can be stored in Node for easy re use throughout the animation.\n\nINSTALLATION:\na) Copy the file (mog_ikFkSwitch.py) to your Maya scripts directory. On Windows that is Documents/maya/20xx/scripts/\n\nb) Open Maya. In the Script Editor (Python), past the following code:\nimport pymel.core as pm\nimport mog_ikFkSwitchPro as mog_ikFkSwitchPro\nimport imp\nimp.reload(mog_ikFkSwitchPro)\nmog_ikFkSwitchPro.FkIk_UI()\n\nc) Hit execute (or Ctrl Enter)\n\nUSAGE:\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SETUP STORE NODE FOR LIMB MATCHING <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n1. Define Limb to work on\nThis always needs to be defined bofore loading/storing/switching. Sides are treated seperately\n\n2. Define Ctrls necessary by selecting them and hitting the << button\n<< FK1: Upper arm\n<< FK2: Lower arm\n<< FK3: FK Hand\n<< IK Ctrl: IK Hand\n<< IK Pole: IK Ellbow pole vector (rig need to have pole vecotr for ik ellbow control)\n<< Switch Ctrl: The ctrl that is used to switch between ik and fk mode\n<< Switch Attr: The attribute that is dialed to switch.\n\t\t\t\tIt can be highlighted in the channel box and hit <<\n\n3. Define Behavior\n>> Knee Bend: \tPrimary bend axis for the knee/ellbow. Bend the knee/ellbow 90 degree. What axis does it bend?\nKnee Bend values for common rigs:\nMalcolm(c Animschool): :\t\t+X Armx, -X Legs\nSteward(c Animation Mentor):\t-Y Arms, +Z Legs\nJack(c Animsquad): \t\t\t\t-Y Arms, +X Legs\nNorman:\t\t\t\t\t\t\t+Z Arms/Legs\nAdvanced Skeleton:\t\t\t\t-Z Arms/Legs \n\n>> Rotation Offset:\n\t\t\t\tSome Riggs have different orientations in their IK and FK ctrls and joints.\n\t\t\t\tThis becomes obvious when running \'Match\' from fk to ik and seeing a 90 degree offset in the wrist\n\t\t\t\tSet the offset with that value and run \'Match\' again to align them\t\nRotation Offsets for common rigs (X,Y,Z):\nMalcolm(c Animschool): :   \t\t(0, 0, 180) Right Arm/Leg, (0, 180, 0) Left Arm/Leg\nSteward(c Animation Mentor): \t(180, 0, 0) Right Arm, (-20,-90, 0) Right Leg, (160,-90, 0) Left Leg \nJack(c Animsquad): \t\t\t\t(-180, 0, 0) Right Side\nNorman: \t\t\t\t\t\t(0, -90, -90) Right Arm, (0, 90, -90) Left Arm, (-90,-90,0) Right Leg, (90,-90,0) Left Leg\nAdvanced Skeleton:\t\t\t\t (90,0,175) Right Arm, (-90,0,175) Left Arm\n\n4.Save/Update: Stores the Setup Node for this Limb in the Scene as a Null node\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> UPDATE A EXISTING STORE NODE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n1. Load: Selected a Ctl in viewport, if a Setup Node exists in the Scene, load it into the Setup fields in the UI2. Make modifications\n3. Save/Update and confirm to overwrite existing Store node\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SWITCH / MATCH <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n1. Select a Ctrl in the viewport and click "Load Store Node from Selections". \n\tWhen a Setup Node exists a green bar will light up \n2. Match IK >> FK or FK >> IK to match the limb between the modes\n\t\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ADDITONAL BUTTONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\nSwitch IK/FK: Simple switches between IK/FK modes (does not do any matching)\nSelect all IK or FK ctrls: Select all nodes for this mode as stored in the Seup node\n\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PRO BUTTONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\nKey all IK/FK: Creates a keyframe for all IK/FK Ctrls on current frame\nBake IK/FK Range: Bakes the entire timeline frame range to ik or fk. Leaves source keys clean\nBake IK/FK AllKeys: Bakes all keyframes in the timeline to ik or fk. Leaves source keys clean. Make sure your frame range is set to include all keys you want to bake.\n\nExport Store Nodes: Save all store nodes into .ma/.mb Store File saved in the same location as the scene.\n\t\t\tThe file name is the same as the scene + _IKFKSTORE  and located in the same folder as the file\n\t\t\tAlready existing store nodes in the scene will be overwritten\nImport Store Nodes: Opens file dialogue to select the previously exported Store File\n\nLIMITATIONS:\n- Pole Vector Control is required and will not run if controlled with attribute\n- Works only on Referenced Riggs\n\nFuture Improvements/Optimzations planned:\n\t-   Make script work/not error if there is no polevector\n\t-   create nodes in Rigg files and look for Referenced Nodes on Load\n\t-\t function on non referenced riggs\n\nVERSIONS:\n3.0 - Oktober 06, 2021 - Update for Maya 2022\n2.0 - January 27, 2021 - UI update for Maya 2020\n1.12 - September 27, 2020 - Fixed isses with \'Switch\' attribute for Baking (PRO)\n1.11 - July 21, 2020 - Bug fix FK to IK Match pole Vector computation for locked fk controls\n1.10 - July 05, 2020 -\tPro version: added option to Bake All Keyframes in Range IK/FK and FK/IK in addtion to Bake every Frame\n1.9 - June 03, 2020\t\tBug fix position snap for fk controls with transformation\n1.8 - September 20, 2019 -\tAdded knee/ellbow Bend Attribute to solve pole vector flip issues\n\t\t\t\t\t\t\tAdded more Info about Rotation Offset and Bend Angle to Help tab \n\t\t\t\t\t\t\tEvaluation update bug fixes\n\t\t\t\t\t\t\tPro version: changes save format from .fbx to .ma/.mb\t\n1.7 - May 25, 2018 - Too small Joint orientation on Malcolm fixed\n1.6 - August 27, 2017 - Offset Value Bug fix. Storing float values now.\n1.5 - August 27, 2017 - Blend Value 1 - 10 bug fix\n\t\t\t\t\t\tPro version: Bake range and Set Keyframe for all IK/FK ctrls\n\t\t\t\t\t\tFree version: Select all ik/fk ctrls\n1.4 - April 24, 2017 - Beta release. New interface. Auto detect limbs by selecting\n1.1 - Jan 12, 2017 - Improvement to interface and bug fixes.\n1.0 - Jan 07, 2017 - Initial Release.\n\n// Questions/comments/bugs/issues to\n// monikagelbmann@gmail.com\n\n'
debug = False
debugZero = False
_logger = logging.getLogger(__name__)

class FkIk_UI:
    COLOR_PRESETS = {'grey': (0.5, 0.5, 0.5), 'lightgrey': (0.7, 0.7, 0.7), 'darkgrey': (0.25, 0.25, 0.25), 'turquoise': (0.3, 0.55, 0.55)}

    def __init__(self):
        global win
        win = 'mtbIKFK_'
        _logger.disabled = not debug
        if pm.window('mtbIKFK_UI', exists=True):
            pm.deleteUI('mtbIKFK_UI')
        windowWidth = 320
        windowHeight = 250
        window = pm.window('mtbIKFK_UI', width=windowWidth, height=windowHeight, title='Universal IK FK - PRO')
        topLevelColumn = pm.columnLayout(adjustableColumn=True, columnAlign='center')
        tabHeight = 250
        tabWidth = 300
        scrollWidth = tabWidth - 40
        riggTab = self.initializeTab(tabHeight, tabWidth)
        pm.setParent('..')
        pm.showWindow('mtbIKFK_UI')

    def initializeTab(self, tabHeight, tabWidth):
        frameWidth = tabWidth - 20
        mainColumnLayout = pm.columnLayout(win + 'mainColumnLayout', w=tabWidth, columnAttach=('left', 10))
        pm.setParent(win + 'mainColumnLayout')
        pm.frameLayout(win + 'setupFrameLayout', w=tabWidth, label='Setup Store Node', collapsable=True, collapse=True)
        pm.separator(h=10)
        pm.text('1. Choose Limb ')
        pm.separator(h=10)
        pm.columnLayout(win + 'ctrlinputColumn', cal='left', columnWidth=20)
        pm.rowLayout(win + 'switchLimb', numberOfColumns=5)
        self.collection2 = pm.radioCollection(win + 'limbRadioCollt')
        self.rb1 = pm.radioButton(win + 'R_arm', w=frameWidth / 5, label='R Arm')
        self.rb2 = pm.radioButton(win + 'L_arm', w=frameWidth / 5, label='L Arm')
        self.rb3 = pm.radioButton(win + 'R_leg', w=frameWidth / 5, label='R Leg')
        self.rb4 = pm.radioButton(win + 'L_leg', w=frameWidth / 5, label='L Leg')
        pm.button(label='   From Sel   ', w=frameWidth / 5, command=lambda a: self.autoDetectSideAndLimbWin())
        pm.setParent(win + 'setupFrameLayout')
        pm.separator(h=10)
        pm.text('2. Define Controls')
        pm.separator(h=10)
        pm.textFieldButtonGrp(win + 'fkshldrTfb', label='', text='', cw3=(0, 200, 100), ad3=3, buttonLabel=' < FK Upper Limb', bc=lambda: self.inputSelTfb('fkshldrTfb'), columnAlign3=('right', 'left', 'left'))
        pm.textFieldButtonGrp(win + 'fkellbowTfb', label='', text='', cw3=(0, 200, 100), ad3=3, buttonLabel='< FK Lower Limb', bc=lambda: self.inputSelTfb('fkellbowTfb'))
        pm.textFieldButtonGrp(win + 'fkwristTfb', label='', text='', cw3=(0, 200, 100), ad3=3, buttonLabel='< FK Wrist/Foot', bc=lambda: self.inputSelTfb('fkwristTfb'))
        pm.textFieldButtonGrp(win + 'ikwristTfb', label='', text='', cw3=(0, 200, 100), ad3=3, buttonLabel='< IK Wrist/Foot', bc=lambda: self.inputSelTfb('ikwristTfb'))
        pm.textFieldButtonGrp(win + 'ikpvTfb', label='', text='', cw3=(0, 200, 100), ad3=3, buttonLabel='< Pole Vector', bc=lambda: self.inputSelTfb('ikpvTfb'))
        pm.setParent(win + 'setupFrameLayout')
        pm.textFieldButtonGrp(win + 'switchCtrlTfb', label='', cw3=(0, 200, 100), ad3=3, text='', buttonLabel='< Switch Ctrl', bc=lambda: self.inputSelTfb('switchCtrlTfb'))
        pm.textFieldButtonGrp(win + 'switchAttrTfb', label='', cw3=(0, 200, 100), ad3=3, text='', buttonLabel='< Switch Attr', bc=lambda: self.inputChannelboxSelectionTbf('switchAttrTfb'))
        pm.rowLayout(win + 'ikIsValueRow', numberOfColumns=3)
        pm.text('Attribute on 0 is', w=frameWidth / 3)
        collection2 = pm.radioCollection(win + 'switch0isfkTfb')
        rb1 = pm.radioButton(win + 'attr0IsIk', label='IK mode', w=frameWidth / 3)
        rb2 = pm.radioButton(win + 'attr0IsFk', label='FK mode', w=frameWidth / 3)
        pm.radioCollection(win + 'switch0isfkTfb', e=1, select=rb2)
        pm.setParent(win + 'setupFrameLayout')
        pm.rowLayout(win + 'ikIsRangeRow', numberOfColumns=3)
        pm.text('Attribute Range', w=frameWidth / 3)
        collection2 = pm.radioCollection(win + 'switchAttrRangeTfb')
        rb1 = pm.radioButton(win + 'attr1', label='0 to 1', w=frameWidth / 3)
        rb2 = pm.radioButton(win + 'attr10', label='0 to 10', w=frameWidth / 3)
        pm.radioCollection(win + 'switchAttrRangeTfb', e=1, select=rb1)
        pm.setParent(win + 'setupFrameLayout')
        pm.rowLayout(win + 'bendKneeAxisRowTfb', numberOfColumns=7)
        pm.text('Knee Bend', w=frameWidth / 4)
        collection2 = pm.radioCollection(win + 'bendKneeAxisTfb')
        rb1 = pm.radioButton(win + 'pX', label='+X', w=frameWidth / 8)
        rb2 = pm.radioButton(win + 'nX', label='-X', w=frameWidth / 8)
        rb3 = pm.radioButton(win + 'pY', label='+Y', w=frameWidth / 8)
        rb4 = pm.radioButton(win + 'nY', label='-Y', w=frameWidth / 8)
        rb5 = pm.radioButton(win + 'pZ', label='+Z', w=frameWidth / 8)
        rb6 = pm.radioButton(win + 'nZ', label='-Z', w=frameWidth / 8)
        pm.radioCollection(win + 'bendKneeAxisTfb', e=1, select=rb1)
        pm.setParent(win + 'setupFrameLayout')
        pm.rowColumnLayout('rotOffsetRow', numberOfColumns=4, columnWidth=[(1, frameWidth / 4), (2, frameWidth / 4), (3, frameWidth / 4)])
        pm.text(l='rotOffset')
        pm.textField(win + 'rotOffsetX', tx=0)
        pm.textField(win + 'rotOffsetY', tx=0)
        pm.textField(win + 'rotOffsetZ', tx=0)
        pm.setParent(win + 'setupFrameLayout')
        self.inputTxtFldBtnGrps = [win + 'fkshldrTfb', win + 'fkellbowTfb', win + 'fkwristTfb', win + 'ikwristTfb', win + 'ikpvTfb', win + 'switchCtrlTfb', win + 'switchAttrTfb']
        self.inputTxtFlds = [win + 'rotOffsetX', win + 'rotOffsetY', win + 'rotOffsetZ']
        pm.button(label='   Save/Update  ', w=300, bgc=self.COLOR_PRESETS['turquoise'], command=lambda a: self.saveIkFkCtrlsWin())
        pm.button(label='Load', bgc=self.COLOR_PRESETS['darkgrey'], w=300, h=20, command=lambda a: self.loadIkFkCtrlsWin())
        pm.button(label='clear Fields', bgc=self.COLOR_PRESETS['darkgrey'], w=300, h=20, command=lambda a: self.clearInputFields())
        pm.separator(h=10)
        pm.rowColumnLayout(win + 'exportRow', numberOfColumns=2, columnWidth=[(1, 150), (2, 150)])
        pm.button(label='Export Store Nodes', command=lambda a: self.exportStoreNode())
        pm.button(label='Import Store Nodes', command=lambda a: self.importStoreNode())
        pm.setParent(win + 'setupFrameLayout')
        pm.separator(h=10)
        pm.setParent(win + 'mainColumnLayout')
        pm.frameLayout(win + 'helpFrameLayout', w=300, label='Help', collapsable=True, collapse=True)
        pm.columnLayout(win + 'helpColumn', cal='left', columnWidth=300)
        pm.scrollField(w=300, wordWrap=True, editable=False, tx='Use <<< Button to Fill the Fields by what you have selected in the Viewport.\n\n' + 'Switch Ctrl: Choose the Ctrls that sets IK/FK mode\n\n' + 'Switch Attr: Highlight the "ikfk"  Attribute in the Channelbox and hit <<\n\n' + 'Knee Bend: What axis does the knee/ellbow bend?\n' + 'Malcolm(Animschool): +X Armx, -X Legs\n' + 'Steward(AnimationMentor): -Y Arms, +Z Legs \n' + 'Jack(Animsquad): -Y Arms, +X Legs\n' + 'Norman: -Y Arms, +X Legs\n' + 'Advanced Skeleeton: -Z Arms and Legs\n\n' + 'Rotation Offset: Orientation difference of IK/FK wrist\n' + 'Malcolm(Animschool): (0,0,180) R Arm/Leg, (0,180,0) L Arm/Leg\n' + 'Steward(AnimationMentor): (180,0,0) R Arm, (-20,-90,0) R Leg, (160,-90,0) L Leg\n' + 'Jack(Animsquad): (-180,0,0) R Arm/Leg \n' + 'Norman: (0,-90,-90) R Arm, (0,90,-90) L Arm, (-90,-90,0) R Leg, (90,-90,0) L Leg\n' + 'Adanced Skeleton:  (90,0,175) R Arm,  (-90,0,175) L Arm\n\n' + 'Match IK/FK: Does the matching between IK/FK\n\n' + 'Switch IK/FK: Simple switches between IK/FK modes (does not do any matching)\n\n' + 'Steps:\n' + '1. Fill Setup Input Fields\n' + '2. Hit "Save/Update"\n' + '3. Hit Load "Store Node from Selection"\n' + '4. Hit "Match IK>FK" or "Match FK>IK"\n\n' + 'Find more details in "how to install and use.txt"')
        pm.separator(h=10)
        pm.setParent(win + 'mainColumnLayout')
        pm.frameLayout(win + 'matchFrameLayout', w=300, label='Match and Switch', collapsable=True)
        pm.text('3. Match / Switch')
        pm.separator(h=10)
        pm.button(label='Load Store Node from Selection', w=300, command=lambda a: self.findStoreNodeFromSelectionWin())
        self.readyText = pm.text(win + 'readyText', label='Not Ready.', align='left', bgc=(0.6, 0.4, 0.4))
        pm.separator(h=10)
        pm.rowColumnLayout(win + 'matchIKRow', numberOfColumns=2, columnWidth=[(1, 150), (2, 150)])
        pm.button(label='Match IK >> FK', bgc=self.COLOR_PRESETS['turquoise'], command=lambda a: self.matchIkFkWin(tofk=1))
        pm.button(label='Match FK >> IK', bgc=self.COLOR_PRESETS['turquoise'], command=lambda a: self.matchIkFkWin(tofk=0))
        pm.setParent(win + 'matchFrameLayout')
        pm.rowColumnLayout(win + 'switchIKRow', numberOfColumns=2, columnWidth=[(1, 150), (2, 150)])
        pm.button(label='Switch IK', command=lambda a: self.switchIkFkWin())
        pm.button(label='Switch FK', command=lambda a: self.switchFkIkWin())
        pm.button(label='Select all IK', command=lambda a: self.selectAll(fk=0))
        pm.button(label='Select all FK', command=lambda a: self.selectAll(fk=1))
        pm.button(label='Key all IK', command=lambda a: self.keyAll(fk=0))
        pm.button(label='Key all FK', command=lambda a: self.keyAll(fk=1))
        pm.setParent(win + 'matchFrameLayout')
        pm.rowColumnLayout(win + 'bakeIKRow', numberOfColumns=2, columnWidth=[(1, 150), (2, 150)])
        pm.button(label='Bake IK >> FK Range', command=lambda a: self.bakeIkFkWin(tofk=1))
        pm.button(label='Bake FK >> IK Range', command=lambda a: self.bakeIkFkWin(tofk=0))
        pm.button(label='Bake IK >> FK AllKeys', command=lambda a: self.bakeIkFkWin(tofk=1, keysonly=1))
        pm.button(label='Bake FK >> IK AllKeys', command=lambda a: self.bakeIkFkWin(tofk=0, keysonly=1))
        pm.setParent(win + 'mainColumnLayout')
        pm.separator(h=5)
        pm.text('Release 3.0                Monika Gelbmann                10/2021')
        pm.separator(h=5)

    def inputSelTfb(self, name):
        if len(pm.selected()) == 0:
            pm.textFieldButtonGrp(win + name, e=1, tx='')
            return []
        pm.textFieldButtonGrp(win + name, e=1, tx=pm.selected()[0])

    def getAndCheckInputWin(self):
        inputValues = []
        errorFields = []
        switch0isfkTfb = pm.radioCollection(win + 'switch0isfkTfb', q=1, sl=1)
        if switch0isfkTfb == 'mtbIKFK_attr0IsFk':
            _logger.info('FK switch0isfk is %s' % switch0isfkTfb)
            switch0isfk = 1
        else:
            _logger.info('IK switch0isfk is %s' % switch0isfkTfb)
            switch0isfk = 0
        switchAttrRangeTfb = pm.radioCollection(win + 'switchAttrRangeTfb', q=1, sl=1)
        if switchAttrRangeTfb == 'mtbIKFK_attr1':
            switchAttrRange = 1
        else:
            switchAttrRange = 10
        for inputTxtFldBtnGrp in self.inputTxtFldBtnGrps:
            input = pm.textFieldButtonGrp(inputTxtFldBtnGrp, q=1, tx=1)
            if len(input) == 0:
                errorFields.append(pm.textFieldButtonGrp(inputTxtFldBtnGrp, q=1, buttonLabel=1))
        if len(errorFields) > 0:
            message = 'Empty input field found. Please pick Ctrl to use.\n%s' % errorFields
            self.popupWarning(message)
            pm.error(message)
            return False
        for inputTxtFldBtnGrp in self.inputTxtFldBtnGrps[:-1]:
            input = pm.textFieldButtonGrp(inputTxtFldBtnGrp, q=1, tx=1)
            if pm.objExists(input) == 0:
                errorFields.append(pm.textFieldButtonGrp(inputTxtFldBtnGrp, q=1, buttonLabel=1))
            else:
                inputValues.append(input)
        if len(errorFields) > 0:
            message = 'Non existing ctrls found. Check those names are correct:\n%s' % errorFields
            self.popupWarning(message)
            pm.error(message)
            return False
        ctrlInput = pm.textFieldButtonGrp(self.inputTxtFldBtnGrps[-2], q=1, tx=1)
        attrInput = pm.textFieldButtonGrp(self.inputTxtFldBtnGrps[-1], q=1, tx=1)
        attr = '%s.%s' % (ctrlInput, attrInput)
        if pm.objExists(attr) == False:
            message = 'Switch Attribute does not exist. Check the naming:\n%s' % attr
            pm.warning(message)
            self.popupWarning(message)
            pm.error(message)
            return False
        else:
            inputValues.append(attrInput)
        limbRadio = pm.radioCollection(win + 'limbRadioCollt', q=1, sl=1)
        _logger.info('raidobuttons: %s' % limbRadio)
        if limbRadio == 'NONE':
            message = 'Limb choice missing. Please choose R Arm / L Arm / R Leg / L Leg'
            self.popupWarning(message=message)
            pm.warning(message)
            return False
        rotOffsetX = pm.textField(win + 'rotOffsetX', q=1, tx=1)
        _logger.debug('checking offsets')
        try:
            rotOffsetX = float(rotOffsetX)
        except:
            rotOffsetX = 0.0
            pass
        rotOffsetY = pm.textField(win + 'rotOffsetY', q=1, tx=1)
        try:
            rotOffsetY = float(rotOffsetY)
        except:
            rotOffsetY = 0.0
            pass
        rotOffsetZ = pm.textField(win + 'rotOffsetZ', q=1, tx=1)
        try:
            rotOffsetZ = float(rotOffsetZ)
        except:
            rotOffsetZ = 0.0
            pass
        rotOffset = [rotOffsetX, rotOffsetY, rotOffsetZ]
        bendKneeAxis = pm.radioCollection(win + 'bendKneeAxisTfb', q=1, sl=1)
        if bendKneeAxis == 'mtbIKFK_pX':
            bendKneeAxis = '+X'
        elif bendKneeAxis == 'mtbIKFK_nX':
            bendKneeAxis = '-X'
        elif bendKneeAxis == 'mtbIKFK_pY':
            bendKneeAxis = '+Y'
        elif bendKneeAxis == 'mtbIKFK_nY':
            bendKneeAxis = '-Y'
        elif bendKneeAxis == 'mtbIKFK_pZ':
            bendKneeAxis = '+Z'
        elif bendKneeAxis == 'mtbIKFK_nZ':
            bendKneeAxis = '-Z'
        inputValues.append(switch0isfk)
        inputValues.append(switchAttrRange)
        inputValues.append(rotOffset)
        inputValues.append(bendKneeAxis)
        _logger.info('returning %s' % inputValues)
        return inputValues

    def clearInputFields(self):
        for inputTxtFldBtnGrp in self.inputTxtFldBtnGrps:
            pm.textFieldButtonGrp(inputTxtFldBtnGrp, e=1, tx='')
        for inputTxtFld in self.inputTxtFlds:
            pm.textField(inputTxtFld, e=1, tx='')

    def popupWarning(self, message, title='Input Error'):
        result = pm.confirmDialog(title=title, message=message, button=['OK'], defaultButton='OK')
        return result

    def autoDetectSideAndLimbWin(self):
        side, limb = autoDetectSideAndLimb(pm.selected()[0])
        if side and limb:
            pm.displayInfo('Matching Side and Limb found: %s %s' % (side, limb))
            if side == 'R' and limb == 'arm':
                pm.radioCollection(win + 'limbRadioCollt', edit=1, select=self.rb1)
            elif side == 'L' and limb == 'arm':
                pm.radioCollection(win + 'limbRadioCollt', edit=1, select=self.rb2)
            elif side == 'R' and limb == 'leg':
                pm.radioCollection(win + 'limbRadioCollt', edit=1, select=self.rb3)
            elif side == 'L' and limb == 'leg':
                pm.radioCollection(win + 'limbRadioCollt', edit=1, select=self.rb4)
            self.loadIkFkCtrlsWin()

    def inputChannelboxSelectionTbf(self, name):
        channelBox = pm.mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
        attrs = pm.channelBox(channelBox, q=True, sma=True)
        if not attrs:
            pm.textFieldButtonGrp(win + name, e=1, tx='')
            return []
        if len(attrs) != 1:
            pm.warning('Highlight only the IK/FK Switch Attribute in the Channelbox')
            return []
        pm.textFieldButtonGrp(win + name, e=1, tx=attrs[0])
        return attrs

    def findStoreNodeFromSelectionWin(self):
        store_node = findStoreNodeFromSelection()
        _logger.debug('store node found is %s' % store_node)
        if store_node == []:
            message = 'No Storenode found for Selection. Fill out Setup section first and hit SAVE for future detection'
            pm.warning(message)
            pm.text(self.readyText, e=1, label='No Storenode found. Use Setup. Not Ready.', align='left', bgc=(0.6, 0.4, 0.4))
        else:
            ns = store_node.split('__')[0] if len(store_node.split('__')) > 0 else ''
            side = store_node.split('_')[-3]
            limb = store_node.split('_')[-2]
            pm.displayInfo('Storenode found for %s %s. Loading %s' % (side, limb, store_node))
            if side and limb:
                _logger.info('Machting Side and Limb found')
                if side == 'R' and limb == 'arm':
                    pm.radioCollection(win + 'limbRadioCollt', edit=1, select=self.rb1)
                elif side == 'L' and limb == 'arm':
                    pm.radioCollection(win + 'limbRadioCollt', edit=1, select=self.rb2)
                elif side == 'R' and limb == 'leg':
                    pm.radioCollection(win + 'limbRadioCollt', edit=1, select=self.rb3)
                elif side == 'L' and limb == 'leg':
                    pm.radioCollection(win + 'limbRadioCollt', edit=1, select=self.rb4)
            self.loadIkFkCtrlsWin()
            pm.text(self.readyText, e=1, label='Storenode found >> %s %s. Ready.' % (side, limb), align='left', bgc=(0.4, 0.6, 0.4))

    @_r.ui_operation('saveIkFkCtrlsWin')
    def saveIkFkCtrlsWin(self):
        fkshldr, fkellbow, fkwrist, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, bendKneeAxis = self.getAndCheckInputWin()
        limbRadio = pm.radioCollection(win + 'limbRadioCollt', q=1, sl=1)
        if limbRadio == 'NONE':
            pm.warning('Limb choice missing. Please choose form the UI options')
            return False
        limb = limbRadio.split('_')[-1]
        side = limbRadio.split('_')[1]
        storeNode = saveIKFkCtrls(limb, side, fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, bendKneeAxis)
        if storeNode:
            pm.displayInfo('Successfully saved.')

    def loadIkFkCtrlsWin(self):
        limbRadio = pm.radioCollection(win + 'limbRadioCollt', q=1, sl=1)
        if limbRadio == 'NONE':
            message = 'Limb choice missing. Please choose R Arm / L Arm / R Leg / L Leg'
            self.popupWarning(message=message)
            pm.warning(message)
            return False
        limb = limbRadio.split('_')[-1]
        side = limbRadio.split('_')[1]
        if len(pm.selected()) == 0:
            pm.warning('Select anything from the rigg')
            return False
        ns = pm.selected()[0].split(':')[0] if len(pm.selected()[0].split(':')) > 1 else ''
        storedic = loadIkFkCtrl(ns, limb, side)
        if len(storedic) == 0:
            pm.warning('No Store Node for %s. Define Limbs and Save Store Node' % limb)
        else:
            pm.displayInfo('Found Store Node for %s. Loading.' % limb)
        for attrName, value in list(storedic.items()):
            if attrName == 'switch0isfk':
                _logger.info('load switch0isfk is %s' % value)
                if value == '0':
                    pm.radioCollection(win + 'switch0isfkTfb', e=1, select=win + 'attr0IsIk')
                else:
                    pm.radioCollection(win + 'switch0isfkTfb', e=1, select=win + 'attr0IsFk')
            elif attrName == 'attrRange':
                _logger.info('load attrRange value is %s' % value)
                if value == '1':
                    pm.radioCollection(win + 'switchAttrRangeTfb', e=1, select=win + 'attr1')
                else:
                    pm.radioCollection(win + 'switchAttrRangeTfb', e=1, select=win + 'attr10')
            elif attrName == 'rotOffset':
                rotList = _r.literal_data(value)
                _logger.debug('rotation list eval is %rotList' % rotList)
                pm.textField(win + 'rotOffsetX', e=1, tx=rotList[0])
                pm.textField(win + 'rotOffsetY', e=1, tx=rotList[1])
                pm.textField(win + 'rotOffsetZ', e=1, tx=rotList[2])
            elif attrName == 'side':
                continue
            elif attrName == 'bendKneeAxis':
                _logger.info('load bendKneeAxis value is %s' % value)
                if value == '+X':
                    pm.radioCollection(win + 'bendKneeAxisTfb', e=1, select=win + 'pX')
                elif value == '-X':
                    pm.radioCollection(win + 'bendKneeAxisTfb', e=1, select=win + 'nX')
                elif value == '+Y':
                    pm.radioCollection(win + 'bendKneeAxisTfb', e=1, select=win + 'pY')
                elif value == '-Y':
                    pm.radioCollection(win + 'bendKneeAxisTfb', e=1, select=win + 'nY')
                elif value == '+Z':
                    pm.radioCollection(win + 'bendKneeAxisTfb', e=1, select=win + 'pZ')
                elif value == '-Z':
                    pm.radioCollection(win + 'bendKneeAxisTfb', e=1, select=win + 'nZ')
            else:
                pm.textFieldButtonGrp(win + '%sTfb' % attrName, e=1, tx=value)

    @_r.ui_operation('matchIkFkWin')
    def matchIkFkWin(self, tofk=1):
        try:
            fkshldr, fkellbow, fkwrist, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, bendKneeAxis = self.getAndCheckInputWin()
        except:
            pm.warning('input error matchIkFkWin')
            return
        rotOffsetX = pm.textField(win + 'rotOffsetX', q=1, tx=1)
        _logger.debug('rotOffset X is %s' % rotOffsetX)
        if rotOffsetX == '':
            rotOffsetX = 0.0
        else:
            rotOffsetX = float(rotOffsetX)
        rotOffsetY = pm.textField(win + 'rotOffsetY', q=1, tx=1)
        if rotOffsetY == '':
            rotOffsetY = 0.0
        else:
            rotOffsetY = float(rotOffsetY)
        rotOffsetZ = pm.textField(win + 'rotOffsetZ', q=1, tx=1)
        if rotOffsetZ == '':
            rotOffsetZ = 0.0
        else:
            rotOffsetZ = float(rotOffsetZ)
        limbRadio = pm.radioCollection(win + 'limbRadioCollt', q=1, sl=1)
        side = limbRadio.split('_')[1]
        limb = limbRadio.split('_')[2]
        if tofk == 1:
            ikfkMatch(fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk=switch0isfk, switchAttrRange=switchAttrRange, rotOffset=[rotOffsetX, rotOffsetY, rotOffsetZ], side=side, limb=limb, bendKneeAxis=bendKneeAxis)
        elif tofk == 0:
            fkikMatch(fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk=switch0isfk, switchAttrRange=switchAttrRange, rotOffset=[rotOffsetX, rotOffsetY, rotOffsetZ], side=side, limb=limb)
        pm.select(switchCtrl)

    @_r.ui_operation('switchIkFkWin')
    def switchIkFkWin(self):
        fkshldr, fkellbow, fkwrist, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, kneeBendAxis = self.getAndCheckInputWin()
        if switch0isfk == 1:
            setSwitchTo = switchAttrRange
        else:
            setSwitchTo = 0
        pm.setAttr('%s.%s' % (switchCtrl, switchAttr), setSwitchTo)
        pm.displayInfo('Done. Switched IK >> FK')

    @_r.ui_operation('switchFkIkWin')
    def switchFkIkWin(self):
        fkshldr, fkellbow, fkwrist, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, kneeBendAxis = self.getAndCheckInputWin()
        if switch0isfk == 1:
            setSwitchTo = 0
        else:
            setSwitchTo = switchAttrRange
        pm.setAttr('%s.%s' % (switchCtrl, switchAttr), setSwitchTo)
        pm.displayInfo('Done. Switched FK >> IK')

    def selectAll(self, fk=1):
        try:
            fkshldr, fkellbow, fkwrist, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, kneeBendAxis = self.getAndCheckInputWin()
        except:
            pm.warning('Input error selectAll')
            return
        if fk == 1:
            pm.select(fkshldr, fkellbow, fkwrist)
            pm.displayInfo('Done.  Select 3 fk Ctrls.')
        elif fk == 0:
            pm.select(ikpv, ikwrist)
            pm.displayInfo('Done. Select 2 ik Ctrls.')
        return

    @_r.ui_operation('keyAll')
    def keyAll(self, fk=1):
        try:
            fkshldr, fkellbow, fkwrist, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, bendKneeAxis = self.getAndCheckInputWin()
        except:
            pm.warning('Input error keyAll')
            return
        if fk == 1:
            pm.setKeyframe(fkwrist, s=0, rk=1, mr=1)
            pm.setKeyframe(fkellbow, s=0, rk=1, mr=1)
            pm.setKeyframe(fkshldr, s=0, rk=1, mr=1)
            pm.displayInfo('Done. Set Keyframes on 3 fk Ctrls.')
        elif fk == 0:
            pm.setKeyframe(ikpv, s=0, rk=1, mr=1)
            pm.setKeyframe(ikwrist, s=0, rk=1, mr=1)
            pm.displayInfo('Done. Set Keyframes on 2 ik Ctrls.')
        return

    @_r.ui_operation('bakeIkFkWin')
    def bakeIkFkWin(self, tofk=1, keysonly=0):
        autkeystate_remeber = pm.autoKeyframe(query=True, state=True)
        try:
            fkshldr, fkellbow, fkwrist, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, bendKneeAxis = self.getAndCheckInputWin()
        except:
            pm.warning('Input error bakeIkFkWin')
            return
        minFrame = pm.playbackOptions(q=1, min=1)
        maxFrame = pm.playbackOptions(q=1, max=1)
        confirmStr = 'Range'
        if keysonly == 1:
            confirmStr = 'all Keyframes from'
        confirm = pm.confirmDialog(title='Confirm', message='Are you you want to bake %s %s to %s?' % (confirmStr, minFrame, maxFrame), button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if confirm == 'Yes':
            autkeystate_remeber = pm.autoKeyframe(state=1, q=1)
            pm.autoKeyframe(state=0)
            rotOffsetX = pm.textField(win + 'rotOffsetX', q=1, tx=1)
            if rotOffsetX == '':
                rotOffsetX = 0.0
            else:
                rotOffsetX = float(rotOffsetX)
            rotOffsetY = pm.textField(win + 'rotOffsetY', q=1, tx=1)
            if rotOffsetY == '':
                rotOffsetY = 0.0
            else:
                rotOffsetY = float(rotOffsetY)
            rotOffsetZ = pm.textField(win + 'rotOffsetZ', q=1, tx=1)
            if rotOffsetZ == '':
                rotOffsetZ = 0.0
            else:
                rotOffsetZ = float(rotOffsetZ)
            limbRadio = pm.radioCollection(win + 'limbRadioCollt', q=1, sl=1)
            side = limbRadio.split('_')[1]
            limb = limbRadio.split('_')[2]
            keying_frames = list(range(int(minFrame), int(maxFrame) + 1))
            if keysonly == 1:
                if tofk == 1:
                    driverCtrls = [ikwrist, ikpv]
                else:
                    driverCtrls = [fkshldr, fkellbow, fkwrist]
                keying_frames = [t for t in sorted(list(dict.fromkeys(pm.keyframe(driverCtrls, q=1)))) if minFrame <= t <= maxFrame]
                if tofk == 1:
                    pm.cutKey([fkwrist, fkellbow, fkshldr], t=[min(keying_frames), max(keying_frames)])
                else:
                    pm.cutKey([ikpv, ikwrist], t=[min(keying_frames), max(keying_frames)])
            _logger.info('Keying frames is %s' % keying_frames)
            switch = '%s.%s' % (switchCtrl, switchAttr)
            for fr in keying_frames:
                pm.currentTime(fr)
                if tofk == 1:
                    if switch0isfk == 0:
                        pm.setAttr(switch, 0)
                    else:
                        pm.setAttr(switch, switchAttrRange)
                    pm.cutKey([fkwrist, fkellbow, fkshldr], t=fr)
                    ikfkMatch(fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk=switch0isfk, switchAttrRange=switchAttrRange, rotOffset=[rotOffsetX, rotOffsetY, rotOffsetZ], side=side, limb=limb, bendKneeAxis=bendKneeAxis)
                    pm.setKeyframe(fkwrist, s=0)
                    pm.setKeyframe(fkellbow, s=0)
                    pm.setKeyframe(fkshldr, s=0)
                elif tofk == 0:
                    if switch0isfk == 0:
                        pm.setAttr(switch, switchAttrRange)
                    else:
                        pm.setAttr(switch, 0)
                    fkikMatch(fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk=switch0isfk, switchAttrRange=switchAttrRange, rotOffset=[rotOffsetX, rotOffsetY, rotOffsetZ])
                    pm.setKeyframe(ikpv, s=0, rk=1, mr=1)
                    pm.setKeyframe(ikwrist, s=0, rk=1, mr=1)
        pm.select(switchCtrl)
        pm.autoKeyframe(state=autkeystate_remeber)
        pm.displayInfo('Done baking range %s to %s.' % (minFrame, maxFrame))

    def exportStoreNode(self):
        return _r.file_ui('export_store')

    def importStoreNode(self):
        return _r.file_ui('import_store')

def findStoreNodeFromSelection():
    return _r.find_store_from_selection()

def autoDetectSideAndLimb(ctrl=None):
    """
	Need to have one ctrl selecte. This ctrl will determine side, namespace and suffix
	From there we list all matching nodes and try to find Limb
	From there we filter FK IK
	Returns:

	"""
    if ctrl == None:
        ctrl = pm.selected()[0]
    ctrlname = pm.PyNode(ctrl).nodeName()
    namespace = ctrl.split(':')[0] + ':' if len(ctrl.split(':')) > 1 else ''
    suffix = '_' + ctrlname.split('_')[-1] if 'ctrl' in ctrlname.split('_')[-1] else ''
    side = None
    limb = None
    for search_str in ['rt', 'Rt', 'R_', '_R', 'r_', '_r', 'right']:
        if search_str in ctrlname:
            side, side_str = ('R', search_str)
            break
    if side == None:
        for search_str in ['lf', 'Lf', 'L_', '_L', 'l_', '_l', 'left']:
            if search_str in ctrlname:
                side, side_str = ('L', search_str)
                break
    for search_str in ['hand', 'Hand', 'arm', 'Arm', 'elbow', 'ellbow', 'Elbow', 'wrist', 'Wrist']:
        if search_str in ctrlname:
            limb = 'arm'
            break
    if limb == None:
        for search_str in ['leg', 'Leg', 'knee', 'Knee', 'foot', 'Foot']:
            if search_str in ctrlname:
                limb = 'leg'
                break
    return (side, limb)

def fkikMatch(fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk=1, switchAttrRange=1, rotOffset=[0, 0, 0], side='R', limb='arm'):
    """
	Match fk to ik. Recreate the ik chain
	Args:
		fkwrist:
		fkellbow:
		fkshldr:
		ikwrist:
		ikpv:
		switchCtrl:
		switchAttr:
		switch0isfk:
		rotOffset:

	Returns:

	"""
    _r.require_active()
    switch = '%s.%s' % (switchCtrl, switchAttr)
    if pm.objExists('mtbIKFK_private_snapGrp'):
        pm.delete('mtbIKFK_private_snapGrp')
    snapGrp = pm.createNode('transform', name='mtbIKFK_private_snapGrp')
    clist = []
    fk_wristDup = pm.duplicate(fkwrist, parentOnly=1, n='fk_wristDup')[0]
    unlockAttributes([fk_wristDup])
    pm.parent(fk_wristDup, snapGrp)
    if switch0isfk == 0:
        pm.setAttr(switch, switchAttrRange)
    else:
        pm.setAttr(switch, 0)
    fkwrist_key, fkellbow_key, fkshldr_key = (pm.keyframe(fkwrist, q=1, t=pm.currentTime()), pm.keyframe(fkellbow, q=1, t=pm.currentTime()), pm.keyframe(fkshldr, q=1, t=pm.currentTime()))
    fkwRaw = pm.xform(fkwrist, ws=1, q=1, t=1)
    fkwPos = om.MVector(fkwRaw[0], fkwRaw[1], fkwRaw[2])
    fkeRaw = pm.xform(fkellbow, ws=1, q=1, t=1)
    fkePos = om.MVector(fkeRaw[0], fkeRaw[1], fkeRaw[2])
    fksRaw = pm.xform(fkshldr, ws=1, q=1, t=1)
    fksPos = om.MVector(fksRaw[0], fksRaw[1], fksRaw[2])
    fkwRotRaw = pm.xform(fkwrist, q=1, ro=1)
    fkeRotRaw = pm.xform(fkellbow, q=1, ro=1)
    fksRotRaw = pm.xform(fkshldr, q=1, ro=1)
    pm.xform(fkshldr, ro=(0, 0, 0))
    pm.xform(fkellbow, ro=(0, 0, 0))
    pm.xform(fkwrist, ro=(0, 0, 0))
    snap(fkwrist, fk_wristDup)
    pm.xform(ikwrist, ro=(0, 0, 0))
    ik_wristDup = pm.duplicate(ikwrist, parentOnly=1, n='ik_wristDup')[0]
    unlockAttributes([ik_wristDup])
    pm.parent(ik_wristDup, fk_wristDup)
    snap(fk_wristDup, ik_wristDup, pos=1, rot=1)
    ik_wristDupOffset = pm.duplicate(ik_wristDup, parentOnly=1, n='ik_wristDup_offset')[0]
    pm.parent(ik_wristDupOffset, ik_wristDup)
    clist.append(pm.parentConstraint(fkwrist, fk_wristDup, mo=0))
    pm.xform(fkshldr, ro=fksRotRaw)
    pm.xform(fkellbow, ro=fkeRotRaw)
    pm.xform(fkwrist, ro=fkwRotRaw)
    pm.setAttr('%s.rx' % ik_wristDupOffset, rotOffset[0])
    pm.setAttr('%s.ry' % ik_wristDupOffset, rotOffset[1])
    pm.setAttr('%s.rz' % ik_wristDupOffset, rotOffset[2])
    fkshldr_dup = pm.spaceLocator(n='fkShld_dup')
    snap(fkshldr, fkshldr_dup)
    pm.parent(fkshldr_dup, snapGrp)
    fkellbow_dup = pm.spaceLocator(n='fkEllbow_dup')
    snap(fkellbow, fkellbow_dup)
    pm.parent(fkellbow_dup, snapGrp)
    fkwrist_dup = pm.spaceLocator(n='fkwrist_dup')
    snap(fkwrist, fkwrist_dup)
    pm.parent(fkwrist_dup, snapGrp)
    pvLoc = poleVectorPosition(fkshldr_dup, fkellbow_dup, fkwrist_dup, length=12, createLoc=1)
    pm.select([fkshldr, fkellbow, fkwrist])
    pm.parent(pvLoc, snapGrp)
    for ctrl in [ikwrist, ikpv]:
        if len(pm.keyframe(ctrl, q=1)) > 0:
            pm.cutKey(ctrl, t=pm.currentTime())
    snap(ik_wristDupOffset, ikwrist)
    snap(pvLoc, ikpv, pos=1, rot=0)
    for ctrl in [ikwrist, ikpv]:
        if len(pm.keyframe(ctrl, q=1)) > 0:
            pm.setKeyframe(ctrl, t=pm.currentTime(), s=0)
    if debug == True:
        clist.append(pm.parentConstraint(ik_wristDupOffset, ikwrist))
    if debug == False:
        pm.delete(clist)
        pm.delete(snapGrp)
    if len(fkwrist_key) == 0:
        try:
            pm.cutKey(fkwrist, t=pm.currentTime())
        except:
            pass
    if len(fkellbow_key) == 0:
        try:
            pm.cutKey(fkellbow, t=pm.currentTime())
        except:
            pass
    if len(fkshldr_key) == 0:
        try:
            pm.cutKey(fkshldr, t=pm.currentTime())
        except:
            pass
    if switch0isfk == 0:
        pm.setAttr(switch, 0)
    else:
        pm.setAttr(switch, switchAttrRange)
    pm.dgdirty([ikwrist, ikpv])
    pm.dgdirty([fkwrist, fkellbow, fkshldr])
    _logger.info('Done matching FK to IK.')

def keyframeAll(fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk=1, rotOffset=[0, 0, 0]):
    _r.require_active()
    for ctrl in [fkwrist, fkellbow, fkshldr, ikwrist, ikpv]:
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
            try:
                pm.setKeyframe(ctrl, at=attr)
            except:
                pass
    pm.setKeyframe(switchCtrl, at=switchAttr)

def ikfkMatch(fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk=1, switchAttrRange=1, rotOffset=[0, 0, 0], side='R', limb='arm', guessUp=1, bendKneeAxis='+X'):
    """
	Snap fk to ik controls by building ik joint form fk control position and lining up to ik
	Args:
	Returns:

	"""
    _r.require_active()
    ns = fkwrist.split(':')[0]
    switch = '%s.%s' % (switchCtrl, switchAttr)
    clist = []
    if pm.objExists('mtbIKFK_private_snapGrp'):
        pm.delete('mtbIKFK_private_snapGrp')
    snapGrp = pm.createNode('transform', name='mtbIKFK_private_snapGrp')
    ikwrist_key, ikpv_key = (pm.keyframe(ikwrist, q=1, t=pm.currentTime()), pm.keyframe(ikpv, q=1, t=pm.currentTime()))
    _logger.info('matching. switch attr range is %s' % switchAttrRange)
    if switch0isfk == 0:
        pm.setAttr(switch, switchAttrRange)
    else:
        pm.setAttr(switch, 0)
    pm.xform(fkshldr, ro=(0, 0, 0))
    pm.xform(fkellbow, ro=(0, 0, 0))
    pm.xform(fkwrist, ro=(0, 0, 0))
    try:
        pm.xform(fkshldr, t=(0, 0, 0))
    except:
        pass
    try:
        pm.xform(fkellbow, t=(0, 0, 0))
    except:
        pass
    try:
        pm.xform(fkwrist, t=(0, 0, 0))
    except:
        pass
    _logger.info('root loc')
    pm.dgdirty([fkshldr, fkellbow, fkwrist])
    root_loc = pm.group(empty=1, n='fk_shld_root')
    pm.parent(root_loc, snapGrp)
    snap(fkshldr, root_loc)
    fkshldr_dup = pm.duplicate(fkshldr, parentOnly=1)[0]
    fkellbow_dup = pm.duplicate(fkellbow, parentOnly=1)[0]
    fkwrist_dup = pm.duplicate(fkwrist, parentOnly=1)[0]
    basicTransforms = ['translateX', 'translateY', 'translateZ', 'translate', 'rotateX', 'rotateY', 'rotateZ', 'rotate']
    for attr in basicTransforms:
        pm.setAttr(fkshldr_dup + '.' + attr, lock=False, k=True)
        pm.setAttr(fkellbow_dup + '.' + attr, lock=False, k=True)
        pm.setAttr(fkwrist_dup + '.' + attr, lock=False, k=True)
    pm.select([fkshldr_dup, fkellbow_dup, fkwrist_dup])
    _logger.info('line up fk duplicates to fk controlssss %s %s %s' % (fkshldr_dup, fkellbow_dup, fkwrist_dup))
    pm.parent(fkshldr_dup, snapGrp)
    snap(fkshldr, fkshldr_dup, pos=1, rot=1)
    pm.parent(fkellbow_dup, fkshldr_dup)
    snap(fkellbow, fkellbow_dup, pos=1, rot=1)
    pm.parent(fkwrist_dup, fkellbow_dup)
    snap(fkwrist, fkwrist_dup, pos=1, rot=1)
    pm.select(snapGrp)
    _logger.info('snapping fk shoulder to ik')
    root_ikSnap = pm.joint(n='root_ikSnap', p=pm.xform(fkshldr, t=1, q=1, ws=1), orientation=(0, 0, 0))
    pm.parent(root_ikSnap, root_loc)
    snap(fkshldr, root_ikSnap, rot=1, pos=1)
    ikshldr_jnt = pm.joint(n='ikshldr_jnt', p=pm.xform(fkshldr, t=1, q=1, ws=1), orientation=(0, 0, 0))
    snap(fkellbow, ikshldr_jnt, rot=1, pos=0)
    try:
        snap(fkshldr, ikshldr_jnt, rot=0, pos=1)
    except:
        pass
    _logger.info('snapping fk ellbow to ik')
    ikellbow_jnt = pm.joint(n='ikellbow_jnt', p=pm.xform(fkellbow, t=1, q=1, ws=1), orientation=(0, 0, 0))
    snap(fkellbow, ikellbow_jnt, rot=1, pos=0)
    try:
        snap(fkellbow, ikellbow_jnt, rot=0, pos=1)
    except:
        pass
    _logger.info('snapping fk wrist to ik')
    ikwrist_jnt = pm.joint(n='ikwrist_jnt', p=pm.xform(fkwrist, t=1, q=1, ws=1), orientation=(0, 0, 0))
    snap(fkellbow, ikwrist_jnt, rot=1, pos=0)
    try:
        snap(fkwrist, ikwrist_jnt, rot=0, pos=1)
    except:
        pass
    _logger.info('freeze transform')
    pm.makeIdentity(ikshldr_jnt, apply=1)
    pm.makeIdentity(ikellbow_jnt, apply=1)
    pm.makeIdentity(ikwrist_jnt, apply=1)
    multiplyer = 1
    if bendKneeAxis[0] == '-':
        multiplyer = -1
    if abs(pm.getAttr('%s.jointOrient%s' % (ikellbow_jnt, bendKneeAxis[1]))) < 0.1:
        pm.warning('Warning small joint orient. Setting Prefferec Angle to Y ')
        pm.setAttr('%s.preferredAngle%s' % (ikellbow_jnt, bendKneeAxis[1]), 12.0 * multiplyer)
        pm.setAttr('%s.jointOrient%s' % (ikellbow_jnt, bendKneeAxis[1]), 0.01 * multiplyer)
    pole_ikSnap = pm.spaceLocator(n='pole_ikSnap')
    pm.parent(pole_ikSnap, fkellbow_dup)
    _logger.info('snap pole ik to fkellbow knee bend axis is %s' % bendKneeAxis)
    snap(fkellbow_dup, pole_ikSnap)
    _logger.info('considering kneebendaxis. %s' % bendKneeAxis)
    reverse = 1
    if side == 'L':
        reverse = -1
    if bendKneeAxis == '-X':
        pole_ikSnap.tz.set(pole_ikSnap.tz.get() + 0.5 * reverse)
    elif bendKneeAxis == '+X':
        pole_ikSnap.tz.set(pole_ikSnap.tz.get() - 0.5 * reverse)
    elif bendKneeAxis == '-Y':
        pole_ikSnap.tz.set(pole_ikSnap.tz.get() + 0.5 * reverse)
    elif bendKneeAxis == '+Y':
        pole_ikSnap.tz.set(pole_ikSnap.tx.get() - 0.5 * reverse)
    elif bendKneeAxis == '-Z':
        pole_ikSnap.ty.set(pole_ikSnap.ty.get() - 0.5 * reverse)
    elif bendKneeAxis == '+Z':
        pole_ikSnap.ty.set(pole_ikSnap.ty.get() + 0.5 * reverse)
    pm.parent(pole_ikSnap, snapGrp)
    ikHandle_ikSnap = pm.ikHandle(sj=ikshldr_jnt, ee=ikwrist_jnt, sol='ikRPsolver')
    pm.parent(ikHandle_ikSnap[0], snapGrp)
    pm.poleVectorConstraint(pole_ikSnap, ikHandle_ikSnap[0])
    _logger.info('done polevector constraint')
    ikrot = pm.xform(ikwrist, q=1, ro=1)
    pm.xform(ikwrist, ro=(0, 0, 0))
    ikwrist_loc = pm.spaceLocator(n='ikwrist_loc')
    pm.setAttr('%s.rotateOrder' % ikwrist_loc, pm.getAttr('%s.rotateOrder' % ikwrist))
    pm.parent(ikwrist_loc, fkwrist_dup)
    snap(fkwrist, ikwrist_loc, rot=0, pos=1)
    snap(fkwrist, ikwrist_loc, rot=1, pos=0)
    ikwrist_loc_offset = pm.spaceLocator(n='ikwrist_loc_offset')
    pm.setAttr('%s.rotateOrder' % ikwrist_loc_offset, pm.getAttr('%s.rotateOrder' % ikwrist))
    pm.parent(ikwrist_loc_offset, ikwrist_loc)
    snap(ikwrist_jnt, ikwrist_loc_offset, rot=0, pos=1)
    snap(fkwrist, ikwrist_loc_offset, rot=1, pos=0)
    _logger.info('considering rotation offset')
    fkwrist_rotOrder = pm.getAttr('%s.rotateOrder' % fkwrist)
    ikwrist_rotOrder = pm.getAttr('%s.rotateOrder' % ikwrist)
    _logger.debug('rotation order ikwrist: %s. fkwrist: %s' % (fkwrist_rotOrder, ikwrist_rotOrder))
    pm.setAttr('%s.rx' % ikwrist_loc_offset, rotOffset[0])
    pm.setAttr('%s.ry' % ikwrist_loc_offset, rotOffset[1])
    pm.setAttr('%s.rz' % ikwrist_loc_offset, rotOffset[2])
    _logger.info('constrain fk ctrl dups to ikSnap locs')
    clist.append(pm.parentConstraint(ikshldr_jnt, fkshldr_dup, skipTranslate=['x', 'y', 'z'], mo=1))
    clist.append(pm.parentConstraint(ikellbow_jnt, fkellbow_dup, skipTranslate=['x', 'y', 'z'], mo=1))
    clist.append(pm.parentConstraint(ikwrist_jnt, fkwrist_dup, mo=1))
    fkwrist_loc = pm.spaceLocator(n='fkwrist_loc')
    pm.setAttr('%s.rotateOrder' % fkwrist_loc, pm.getAttr('%s.rotateOrder' % fkwrist))
    pm.parent(fkwrist_loc, ikwrist_loc_offset)
    snap(fkwrist, fkwrist_loc)
    pm.setAttr('%s.rx' % ikwrist_loc_offset, 0)
    pm.setAttr('%s.ry' % ikwrist_loc_offset, 0)
    pm.setAttr('%s.rz' % ikwrist_loc_offset, 0)
    _logger.info('rotate back ik')
    pm.xform(ikwrist, ro=ikrot)
    clist.append(pm.parentConstraint(ikwrist, ikwrist_loc, mo=0))
    if debugZero:
        return
    if switch0isfk == 0:
        pm.setAttr(switch, 0)
    else:
        pm.setAttr(switch, switchAttrRange)
    _logger.info('line up to ik wrist and pole')
    clist.append(pm.pointConstraint(ikwrist, ikHandle_ikSnap[0]))
    snap(ikpv, pole_ikSnap, rot=0, pos=1)
    _logger.debug('snapping back to original fk')
    for ctrl in [fkshldr, fkellbow, fkwrist]:
        if len(pm.keyframe(ctrl, q=1)) > 0:
            pm.cutKey(ctrl, t=pm.currentTime())
    _logger.info('snap fk shoulder')
    snap(fkshldr_dup, fkshldr, rot=1, pos=0)
    try:
        snap(fkshldr_dup, fkshldr, pos=1)
    except:
        pass
    _logger.info('snap fk ellbow')
    snap(fkellbow_dup, fkellbow, rot=1, pos=0)
    try:
        snap(fkellbow_dup, fkellbow, pos=1)
    except:
        pass
    _logger.info('snap fk wrist')
    snap(fkwrist_loc, fkwrist, rot=1, pos=0)
    try:
        snap(fkwrist_loc, fkwrist, pos=1)
    except:
        pass
    for ctrl in [fkshldr, fkellbow, fkwrist]:
        if len(pm.keyframe(ctrl, q=1)) > 0:
            pm.setKeyframe(ctrl, t=pm.currentTime(), s=0)
    pm.dgdirty([fkshldr, fkellbow, fkwrist])
    if debug == True:
        pm.parentConstraint(fkwrist_loc, fkwrist, mo=0, st=('x', 'y', 'z'))
    if debug == False:
        pm.delete(clist)
        pm.delete(snapGrp)
    if len(ikwrist_key) == 0:
        try:
            pm.cutKey(ikwrist, t=pm.currentTime())
        except:
            pass
    if len(ikpv_key) == 0:
        try:
            pm.cutKey(ikpv, t=pm.currentTime())
        except:
            pass
    if switch0isfk == 0:
        pm.setAttr(switch, switchAttrRange)
    else:
        pm.setAttr(switch, 0)

def saveIKFkCtrls(limb, side, fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, bendKneeAxis):
    _r.require_active()
    return _r.save_from_native(limb, side, fkwrist, fkellbow, fkshldr, ikwrist, ikpv, switchCtrl, switchAttr, switch0isfk, switchAttrRange, rotOffset, bendKneeAxis)

def loadIkFkCtrl(ns, limb, side):
    return _r.load_store(ns, limb, side)

def get_variable_name(var_value, main_var):
    mvar = [key for key, val in list(main_var.items()) if val == var_value][0]
    _logger.info('var: %s >> %s' % (mvar, var_value))
    return [mvar, var_value]

def matchTransform(slave, master, rot=1, pos=1):
    """
	Mimicking innate matchTransform of maya 2016.5 and up
	Args:
		slave: this object will be moved to master
		master: target position and rotation
	"""
    _r.require_active()
    if rot == 0:
        skipRotAxis = ['x', 'y', 'z']
    else:
        skipRotAxis = []
    if pos == 0:
        skipTransAxis = ['x', 'y', 'z']
    else:
        skipTransAxis = []
    if rot == 1:
        target = pm.xform(master, q=1, ro=1, ws=1)
        pm.xform(slave, ro=target, ws=1)
    if pos == 1:
        target = pm.xform(master, q=1, t=1, ws=1)
        pm.xform(slave, t=target, ws=1)

def snap(master=None, slave=None, pos=1, rot=1):
    """
	Snap slave to master. Check if attribute locked and skip
	"""
    _r.require_active()
    lastSel = pm.selected()
    if master == None:
        master = pm.selected()[0]
    if slave == None:
        slave = pm.selected()[1:]
    slaves = pm.ls(slave)
    ptC, ptR = ([], [])
    for slave in slaves:
        slaveDup = pm.duplicate(slave, parentOnly=True)[0]
        _logger.debug('snapping slaveDup')
        basicTransforms = ['translateX', 'translateY', 'translateZ', 'translate', 'rotateX', 'rotateY', 'rotateZ', 'rotate']
        for attr in basicTransforms:
            pm.setAttr(slaveDup + '.' + attr, lock=False, k=1)
        ptC = pm.parentConstraint(master, slaveDup, mo=False)
        if pos == 1:
            for att in ['tx', 'ty', 'tz']:
                if pm.getAttr('%s.%s' % (slave, att), l=1) == False:
                    pm.setAttr(slave + '.' + att, pm.getAttr(slaveDup + '.' + att))
                    _logger.info('Snap Constraining Traslation %s %s. Skiplist is ' % (master, slave))
        if rot == 1:
            for att in ['rx', 'ry', 'rz']:
                if pm.getAttr('%s.%s' % (slave, att), l=1) == False:
                    pm.setAttr(slave + '.' + att, pm.getAttr(slaveDup + '.' + att))
                    _logger.info('Snap Constraining Rotation %s %s. Skiplist is ' % (master, slave))
        pm.delete(ptC)
        pm.delete(slaveDup)
    pm.select(lastSel)

def poleVectorPosition(startJnt, midJnt, endJnt, length=12, createLoc=0):
    _r.require_active()
    import maya.api.OpenMaya as om
    start = pm.xform(startJnt, q=1, ws=1, t=1)
    mid = pm.xform(midJnt, q=1, ws=1, t=1)
    end = pm.xform(endJnt, q=1, ws=1, t=1)
    startV = om.MVector(start[0], start[1], start[2])
    midV = om.MVector(mid[0], mid[1], mid[2])
    endV = om.MVector(end[0], end[1], end[2])
    startEnd = endV - startV
    startMid = midV - startV
    proj = startMid * startEnd.normal()
    startEndN = startEnd.normal()
    projV = startEndN * proj
    arrowV = startMid - projV
    arrowVN = arrowV.normal()
    finalV = arrowVN * length + midV
    if createLoc:
        loc = pm.spaceLocator(n='polePos')
        pm.xform(loc, ws=1, t=(finalV.x, finalV.y, finalV.z))
        return loc
    return finalV

def unlockAttributes(objects, attributes=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'visibility']):
    _r.require_active()
    for obj in objects:
        for attr in attributes:
            pm.setAttr(obj + '.' + attr, lock=False, k=True)
            pm.setAttr(obj + '.' + attr, lock=False, k=True)
            pm.setAttr(obj + '.' + attr, lock=False, k=True)
            if attr == 'visibility':
                pm.setAttr(obj + '.' + attr, 1)

def orientJoints(joints, aimAxis, upAxis, upDir, doAuto):
    """
	*
	*  $joints is array of joints to orient
	*  $aimAxis = is xyz array of what axis of joint does aim
	*  $upAxis = is xyz array of what axis of joint does up
	*  $upDir = what vector to use for up direction?
	*  $doAuto = If possible will try to guess the up axis otherwise
	*      it will use prev joint up axis or else world upDir.
	*
	"""
    _r.require_active()
    nJnt = len(joints)
    i = 0
    prevUp = pm.dt.Vector([0, 0, 0])
    for i in range(0, nJnt):
        childs = pm.listRelatives(joints[i], type=['transform', 'joint'], children=1)
        if len(childs) > 0:
            childs = pm.parent(childs, w=1)
        parents = pm.listRelatives(joints[i], parent=1)
        parent = parents[0]
        aimTgt = ''
        child = ''
        for child in childs:
            if pm.nodeType(child) == 'joint':
                aimTgt = str(child)
                break
        if aimTgt != '':
            upVec = [0, 0, 0]
            if doAuto:
                posJ = pm.xform(joints[i], q=1, rp=1, ws=1)
                posP = posJ
                if parent != '':
                    posP = pm.xform(parent, q=1, rp=1, ws=1)
                tol = 0.0001
                if parent == '' or (abs(posJ[0] - posP[0]) <= tol and abs(posJ[1] - posP[1]) <= tol and (abs(posJ[2] - posP[2]) <= tol)):
                    aimChilds = pm.listRelatives(aimTgt, children=1)
                    aimChild = ''
                    child = ''
                    for child in aimChilds:
                        if pm.nodeType(child) == 'joint':
                            aimChild = str(child)
                            break
                    upVec = pm.mel.cJO_getCrossDir(joints[i], aimTgt, aimChild)
                else:
                    upVec = pm.mel.cJO_getCrossDir(parent, joints[i], aimTgt)
            if not doAuto or (upVec[0] == 0.0 and upVec[1] == 0.0 and (upVec[2] == 0.0)):
                upVec = upDir
            aCons = pm.aimConstraint(aimTgt, joints[i], aim=(aimAxis[0], aimAxis[1], aimAxis[2]), worldUpType='vector', weight=1.0, upVector=(upAxis[0], upAxis[1], upAxis[2]), worldUpVector=(upVec[0], upVec[1], upVec[2]))
            pm.delete(aCons)
            curUp = pm.dt.Vector([upVec[0], upVec[1], upVec[2]])
            curUp = pm.dt.Vector(pm.mel.unit(curUp))
            dot = float(curUp * prevUp)
            prevUp = pm.dt.Vector([upVec[0], upVec[1], upVec[2]])
            if i > 0 and dot <= 0.0:
                pm.xform(joints[i], r=1, os=1, ra=(aimAxis[0] * 180.0, aimAxis[1] * 180.0, aimAxis[2] * 180.0))
                prevUp *= pm.dt.Vector(-1.0)
            pm.joint(joints[i], zso=1, e=1)
            pm.makeIdentity(joints[i], apply=True)
        elif parent != '':
            oCons = pm.orientConstraint(parent, joints[i], weight=1.0)
            pm.delete(oCons)
            pm.joint(joints[i], zso=1, e=1)
            pm.makeIdentity(joints[i], apply=True)
        if len(childs) > 0:
            pm.parent(childs, joints[i])
