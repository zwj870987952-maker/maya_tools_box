from maya_toolkit.tools.rdm_tools_v2.support import legacy_reload, bundled_scripts_dir, checked_output, explicit_ui_input
from maya import cmds

def VerticalSlider(Name='Slider', Size=3, Square=False, Negatives=True, *args):
    cmds.undoInfo(openChunk=True)
    Name = Name
    Size = Size
    Color = 16
    cmds.symmetricModelling(symmetry=False)
    cmds.softSelect(sse=0)
    Circulo = cmds.circle(n=Name)
    cmds.select(str(Circulo[0]) + '.cv[0:2]')
    cmds.scale(1, 1e-05, 1, r=True, p=(0, 0.945903, 0))
    cmds.move(0, Size, 0, r=True)
    cmds.select(str(Circulo[0]) + '.cv[4:6]')
    cmds.scale(1, 1e-05, 1, r=True, p=(0, -0.945903, 0))
    if Negatives:
        cmds.move(0, -Size, 0, r=True)
    cmds.select(str(Circulo[0]) + '.cv[6:7]', str(Circulo[0]) + '.cv[0]')
    cmds.scale(1e-05, 1, 1, r=True, p=(0.945903, 0, 0))
    if Square:
        cmds.move(Size, 0, 0, r=True)
    cmds.select(str(Circulo[0]) + '.cv[2:4]')
    cmds.scale(1e-05, 1, 1, r=True, p=(-0.945903, 0, 0))
    if Square:
        cmds.move(-Size, 0, 0, r=True)
    cmds.select(cl=True)
    CirculoMover = cmds.circle(n='%s_Mover' % Name)
    CirculoMoverGrupo = cmds.group(CirculoMover, n='%s_GRP' % CirculoMover[0])
    CirculoGrupo = cmds.group(Circulo, n='%s_GRP' % Circulo[0])
    cmds.setAttr('%s.overrideEnabled' % Circulo[0], 1)
    cmds.setAttr('%s.overrideColor' % Circulo[0], Color)
    cmds.setAttr('%s.overrideEnabled' % CirculoMover[0], 1)
    cmds.setAttr('%s.overrideColor' % CirculoMover[0], Color)
    cmds.select(CirculoMover[0])
    if Negatives == True:
        cmds.transformLimits(tx=(0, 0), etx=(1, 1))
        cmds.transformLimits(ty=(-Size, Size), ety=(1, 1))
        cmds.transformLimits(tz=(0, 0), etz=(1, 1))
    else:
        cmds.transformLimits(tx=(0, 0), etx=(1, 1))
        cmds.transformLimits(ty=(0, Size), ety=(1, 1))
        cmds.transformLimits(tz=(0, 0), etz=(1, 1))
    if Square == True:
        cmds.transformLimits(tx=(-Size, Size), etx=(1, 1))
        cmds.transformLimits(ty=(-Size, Size), ety=(1, 1))
        cmds.transformLimits(tz=(0, 0), etz=(1, 1))
    cmds.parent(str(Name) + '_Mover_GRP', str(Name))
    cmds.select(str(Name) + '_GRP')
    cmds.undoInfo(closeChunk=True)


def run_script():
    exec(compile('', __file__, "exec"), globals())
