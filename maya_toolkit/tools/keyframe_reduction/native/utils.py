from ..proxy import cmds
import decimal
EPSILON = 1.2e-10
THRESHOLD = 0.00012

class UndoChunkContext(object):
    """
    The undo context is used to combine a chain of commands into one undo.
    Can be used in combination with the "with" statement.

    with UndoChunkContext():
        # code
    """

    def __enter__(self):
        cmds.undoInfo(openChunk=True)

    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)

def floatRange(start, end, step):
    """
    :param int/float start:
    :param int/float end:
    :param int/float step:
    :return: Float range
    :rtype: list
    """
    values = []
    step = decimal.Decimal(str(step))
    while start < end:
        values.append(float(start))
        start += step
    return values

def validateAnimationCurve(animationCurve):
    from ..runtime import suitable
    return suitable(animationCurve)

def filterAnimationCurves(animationCurves):
    """
    Loop all the animation curves an run the validation function to make sure
    the animation curves are suitable for reduction.

    :param list animationCurves:
    :return: Animation curves
    :rtype: list
    """
    return [animationCurve for animationCurve in animationCurves if validateAnimationCurve(animationCurve)]

def filterAnimationCurvesByPlug(animationCurves):
    """
    :param list animationCurves:
    :return: Filtered animation curves
    :rtype: dict
    """
    data = {}
    for animationCurve in animationCurves:
        plug = cmds.listConnections('{}.output'.format(animationCurve), plugs=True, source=False, destination=True, skipConversionNodes=True)
        if not plug:
            continue
        attribute = plug[0].split('.', 1)[-1]
        if attribute not in list(data.keys()):
            data[attribute] = []
        data[attribute].append(animationCurve)
    return data

def getAllAnimationCurves():
    """
    :return: All suitable animation curves in the current scene
    :rtype: list
    """
    return filterAnimationCurves(cmds.ls(type='animCurve') or [])

def getSelectionAnimationCurves():
    """
    :return: Selection animation curves
    :rtype: list
    """
    animationCurves = set()
    selection = cmds.ls(sl=True) or []
    for sel in selection:
        if cmds.nodeType(sel).startswith('animCurve'):
            animationCurves.add(sel)
            continue
        for animationCurve in cmds.listConnections(sel, type='animCurve', source=True, destination=False, skipConversionNodes=True) or []:
            animationCurves.add(animationCurve)
    animationCurves = list(animationCurves)
    return filterAnimationCurves(animationCurves)
