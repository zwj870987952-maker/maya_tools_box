from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds
import maya.mel as mel

def TextToCurve(Textisimo='Name', font='Arial', *args):
    cmds.undoInfo(openChunk=True)
    if cmds.objExists('makeTextCurves1'):
        cmds.rename('makeTextCurves1', 'makeTextCurves1LOL')
    Texto = '_' + Textisimo
    Color = 16
    LetrasDobles = []
    Text = cmds.textCurves(n=Texto, t=Texto, o=True, f=font)
    Lista = cmds.listRelatives(Text, ad=True)
    Shape = Lista[1]
    cmds.delete('makeTextCurves1')
    for Curva in Lista:
        if cmds.objectType(str(Curva), isType='nurbsCurve'):
            curvaPapa = cmds.listRelatives(Curva, p=True)
            curvaAbuelo = cmds.listRelatives(curvaPapa, p=True)
            DobleCurva = cmds.listRelatives(curvaAbuelo)
            if len(DobleCurva) == 2:
                LetrasDobles.append(Curva)
            else:
                if not Shape == curvaPapa[0]:
                    cmds.makeIdentity(curvaAbuelo, a=True, t=True, r=True)
                    cmds.parent(Curva, Shape, r=True, s=True)
                cmds.setAttr(Curva + '.overrideEnabled', 1)
                cmds.setAttr(Curva + '.overrideColor', Color)
    for dl in LetrasDobles:
        dlPapa = cmds.listRelatives(dl, p=True)
        dlAbuelo = cmds.listRelatives(dlPapa, p=True)
        cmds.makeIdentity(dlAbuelo, a=True, t=True, r=True)
        cmds.parent(dl, Shape, r=True, s=True)
        cmds.setAttr(dl + '.overrideEnabled', 1)
        cmds.setAttr(dl + '.overrideColor', Color)
    cmds.parent(Shape, w=True)
    cmds.rename(Shape, Texto + str('_CV'))
    cmds.delete(Text[0])
    cmds.delete(Texto + str('_CVShape'))
    cmds.move(-0.5, 0, 0, r=True)
    cmds.xform(cp=True)
    cmds.rename(Textisimo + '_CV')
    cmds.undoInfo(closeChunk=True)


def run_script():
    exec(compile('', __file__, "exec"), globals())
