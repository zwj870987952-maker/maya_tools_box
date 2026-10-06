import maya.cmds as cmds
import maya.mel as mel
from contextlib import contextmanager


@contextmanager
def suspended_evaluation():
    eval_mode = cmds.evaluationManager(q=True, mode=True)
    cmds.waitCursor(state=True)
    cmds.refresh(suspend=True)
    cmds.evaluationManager(mode="off")
    try:
        yield
    finally:
        cmds.evaluationManager(mode=eval_mode[0])
        cmds.refresh(suspend=False)
        cmds.waitCursor(state=False)


class AnimoBounceTool(object):

    WINDOW_NAME = 'animoBounceWin'
    BOUNCE_SET = 'animo_bounce_set'

    def __init__(self):
        self.smoothness_field = None
        self.weight_field = None
        self.new_layer_check = None
        self.build_ui()

    def build_ui(self):
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)

        window = cmds.window(self.WINDOW_NAME,
                            title='Animo Bounce Tool',
                            resizeToFitChildren=True,
                            sizeable=False,
                            minimizeButton=False,
                            maximizeButton=False,
                            menuBar=False)
        cmds.window(window, edit=True, h=100, w=100)

        cmds.columnLayout(columnAttach=('both', 0), columnWidth=190)

        cmds.rowLayout(numberOfColumns=2)
        cmds.text(label='Overshoot', width=120)
        self.smoothness_field = cmds.floatField(value=1.5, precision=2, changeCommand=self.update_smoothness)

        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2)
        cmds.text(label='Snap Strength', width=120)
        self.weight_field = cmds.floatField(value=0.50, precision=2, changeCommand=self.update_weight)

        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=1, height=30, width=100, columnAttach=(1, 'left', 8))
        self.new_layer_check = cmds.checkBox(label='New Anim Layer', width=175, value=False)

        cmds.setParent('..')
        buttonRow = cmds.formLayout(height=30)
        bounceBtn = cmds.button(label='BOUNCE', command=self.bounce)
        bakeBtn = cmds.button(label='BAKE', command=self.bake)
        cmds.formLayout(buttonRow, edit=True,
                        attachForm=[(bounceBtn, 'left', 8), (bounceBtn, 'top', 0), (bounceBtn, 'bottom', 0),
                                    (bakeBtn, 'right', 8), (bakeBtn, 'top', 0), (bakeBtn, 'bottom', 0)],
                        attachPosition=[(bounceBtn, 'right', 4, 50), (bakeBtn, 'left', 4, 50)])

        cmds.setParent('..')
        cmds.text(label='', height=8)

        cmds.showWindow(window)

    def get_bounce_objects(self):
        if cmds.objExists(self.BOUNCE_SET):
            return cmds.sets(self.BOUNCE_SET, query=True) or []
        return []

    def get_live_particles(self):
        particles = []
        for obj in self.get_bounce_objects():
            particle = 'animo_' + obj + '_particle'
            if cmds.objExists(particle):
                particles.append(particle)
        return particles

    def update_smoothness(self, *args):
        value = cmds.floatField(self.smoothness_field, query=True, value=True)
        for particle in self.get_live_particles():
            cmds.setAttr(particle + '.goalSmoothness', value)

    def update_weight(self, *args):
        value = cmds.floatField(self.weight_field, query=True, value=True)
        for particle in self.get_live_particles():
            cmds.setAttr(particle + '.goalWeight[0]', value)

    def create_spring_rig(self, obj, startTime, endTime, goalWeight, goalSmooth):
        loc = cmds.spaceLocator(name='animo_' + obj + '_goalLocator')
        cmds.hide(loc)
        cmds.parentConstraint(obj, loc, maintainOffset=False)
        cmds.bakeResults(loc, time=(startTime, endTime), simulation=True)
        cmds.delete(loc, constraints=True)

        cmds.currentTime(startTime)
        springParticle = cmds.particle(n='animo_' + obj + '_particle')
        springEmitter = cmds.emitter(n='animo_' + obj + '_emitter', position=(0, 0, 0), rate=100)
        cmds.connectDynamic(springParticle, em=springEmitter)

        cmds.setAttr(str(springParticle[0]) + '.maxCount', 1)
        cmds.setAttr(str(springParticle[0]) + '.startFrame', startTime - 50)

        cmds.matchTransform(springParticle, obj, position=True)
        cmds.matchTransform(springEmitter, obj, position=True)

        cmds.goal(springParticle, goal=loc, weight=goalWeight, useTransformAsGoal=0)

        springParticleShape = cmds.listRelatives(springParticle, shapes=True)[0]
        springLoc = cmds.spaceLocator(name='animo_' + obj + '_locator')
        cmds.setAttr('%s.goalSmoothness' % springParticle[0], goalSmooth)
        mel.eval("connectAttr -f " + str(springParticleShape) + ".worldCentroid " + str(springLoc[0]) + ".translate")

        springGrp = cmds.group(loc, springParticle, springEmitter, springLoc, name='ANIMO_' + obj + '_BOUNCE')
        cmds.setAttr(springGrp + '.useOutlinerColor', True)
        cmds.setAttr(springGrp + '.outlinerColor', 1, 1, 0, type='double3')

        cmds.pointConstraint(springLoc, obj)
        cmds.sets(obj, addElement=self.BOUNCE_SET)

    def bounce(self, *args):
        objects = cmds.ls(orderedSelection=True, long=False)
        if not objects:
            cmds.inViewMessage(amg='Please select something!', pos='midCenter', fade=True, alpha=0.9)
            return

        goalWeight = cmds.floatField(self.weight_field, query=True, value=True)
        goalSmooth = cmds.floatField(self.smoothness_field, query=True, value=True)

        startTime = cmds.playbackOptions(q=True, minTime=True)
        endTime = cmds.playbackOptions(q=True, maxTime=True)

        if not cmds.objExists(self.BOUNCE_SET):
            cmds.sets(name=self.BOUNCE_SET, empty=True)

        with suspended_evaluation():
            for obj in objects:
                self.create_spring_rig(obj, startTime, endTime, goalWeight, goalSmooth)

        cmds.currentTime(startTime + 1)
        cmds.currentTime(startTime)
        cmds.select(objects)

    def bake(self, *args):
        objects = self.get_bounce_objects()
        if not objects:
            cmds.inViewMessage(amg='Nothing to bake!', pos='midCenter', fade=True, alpha=0.9)
            return

        bakeNewLayer = cmds.checkBox(self.new_layer_check, query=True, value=True)
        startTime = cmds.playbackOptions(q=True, minTime=True)
        endTime = cmds.playbackOptions(q=True, maxTime=True)

        with suspended_evaluation():
            if bakeNewLayer:
                springLayer = cmds.animLayer('animo_springLayer')
                cmds.animLayer(springLayer, edit=True, override=True)
                cmds.bakeResults(objects, time=(startTime, endTime), simulation=True,
                                preserveOutsideKeys=True, destinationLayer=springLayer)
            else:
                cmds.bakeResults(objects, time=(startTime, endTime), simulation=True, preserveOutsideKeys=True)

            for obj in objects:
                cmds.delete(obj, constraints=True)
                springGrp = 'ANIMO_' + obj + '_BOUNCE'
                if cmds.objExists(springGrp):
                    cmds.delete(springGrp)

            cmds.delete(self.BOUNCE_SET)

        cmds.select(objects)


def animo_bounce_ui():
    AnimoBounceTool()


animo_bounce_ui()