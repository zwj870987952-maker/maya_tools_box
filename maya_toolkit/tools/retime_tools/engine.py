from .runtime import engine_cmds as cmds
import decimal, colorsys, traceback, copy, math
from collections import OrderedDict
from operator import itemgetter
def iteritems(obj, **kwargs):
    """Use this only if compatibility with Python versions before 2.7 is
    required. Otherwise, prefer viewitems().
    """
    func = getattr(obj, 'iteritems', None)
    if not func:
        func = obj.items
    return func(**kwargs)

class RetimeStates(object):
    Enable = 1
    Disable = 2
    Reset = 3
    Invert = 4
    Disconnect = 5
    Delete = 6

    @classmethod
    def get_state_for_string(cls, value):
        """
        lookup table
        """
        state_lookup = {}
        state_lookup[u'启用'] = RetimeStates.Enable
        state_lookup[u'禁用'] = RetimeStates.Disable
        state_lookup[u'重置'] = RetimeStates.Reset
        state_lookup[u'反向'] = RetimeStates.Invert
        state_lookup[u'断开连接'] = RetimeStates.Disconnect
        state_lookup[u'删除'] = RetimeStates.Delete
        '\n        return with fallback\n        '
        return state_lookup.get(value, RetimeStates.Enable)

    @classmethod
    def get_state_for_int(cls, value):
        """
        lookup table
        """
        state_lookup = {}
        state_lookup[1] = RetimeStates.Enable
        state_lookup[2] = RetimeStates.Disable
        state_lookup[3] = RetimeStates.Reset
        state_lookup[4] = RetimeStates.Invert
        state_lookup[5] = RetimeStates.Disconnect
        state_lookup[6] = RetimeStates.Delete
        '\n        return with fallback\n        '
        return state_lookup.get(value, 1)

    @classmethod
    def get_string_for_int(cls, value):
        """
        lookup table
        """
        state_lookup = {}
        state_lookup[1] = u'启用'
        state_lookup[2] = u'禁用'
        state_lookup[3] = u'重置'
        state_lookup[4] = u'反向'
        state_lookup[5] = u'断开连接'
        state_lookup[6] = u'删除'
        '\n        return with fallback\n        '
        return state_lookup.get(value, 1)

class CoreFunctions:

    @classmethod
    def get_retime_curves_in_scene(cls):
        nurbs_curves = cmds.ls(type='nurbsCurve', long=True)
        if not nurbs_curves:
            return False
        transforms = cmds.listRelatives(nurbs_curves, allParents=True, type='transform', fullPath=True)
        transforms = list(set(transforms))
        retime_curves = []
        for t in transforms:
            if cmds.attributeQuery('retimeState', node=t, exists=True):
                retime_curves.append(t)
        retime_curves = sorted(retime_curves)
        return retime_curves

    @classmethod
    def object_exists(cls, maya_node):
        return cmds.objExists(maya_node)

    @classmethod
    def getAttrFromObject(cls, objectVar):
        attrs = cmds.listAttr(objectVar, scalar=True, keyable=True, scalarAndArray=False)
        returnAttrs = []
        if attrs:
            for a in attrs:
                if '.' not in a:
                    returnAttrs.append(a)
        return returnAttrs

    @classmethod
    def isStringListInString(cls, stringListVar, stringVar):
        for s in stringListVar:
            if s.lower() in stringVar.lower():
                return True
        return False

    @classmethod
    def getConnectedNodes(cls, nodesVar):
        stringList = ['animcurveT', 'character', 'blend', 'onstrain']
        newNodes = []
        connectionQuery = cmds.listConnections(nodesVar, destination=False, source=True)
        if connectionQuery:
            for c in connectionQuery:
                nodeType = cmds.objectType(c)
                if cls.isStringListInString(stringList, nodeType):
                    if c not in newNodes:
                        newNodes.append(c)
        newNodes = list(set(newNodes) - set(nodesVar))
        if newNodes:
            newNodes = cls.getConnectedNodes(newNodes)
        nodesVar = list(set(nodesVar) | set(newNodes))
        return nodesVar

    @classmethod
    def getCurvesFromNodes(cls, nodes):
        curves = []
        for n in nodes:
            curves_query = cls.get_all_related_curves_for_object(n)
            if curves_query:
                curves += curves_query
        return list(set(curves))

    @classmethod
    def get_all_related_curves_for_object(cls, node, depth=2):
        anim_curves = [curve for curve in cmds.listHistory(node, pruneDagObjects=False, leaf=False, levels=depth) if cmds.nodeType(curve, inherited=True)[0] == 'animCurve']
        if not anim_curves:
            anim_curves = []
        return anim_curves

    @classmethod
    def getActiveTimewarp(cls):
        try:
            timewarpNode = cmds.textScrollList('eb_labs_tw_controlList', q=True, si=True)
            timewarpNode = timewarpNode[0].split(' ')[0]
            if cmds.objExists(timewarpNode):
                return timewarpNode
        except Exception as e:
            pass
        return False

    @classmethod
    def getSelected(cls):
        """
        get current selection
        """
        selection = cmds.ls(sl=True, long=True)
        if not selection:
            return []
        '\n        find connected shapes\n        '
        shapes = cmds.listRelatives(selection, fullPath=True, shapes=True)
        '\n        fallback if no shapes\n        '
        if not shapes:
            return selection
        '\n        return combined shapes + selection\n        '
        return selection + shapes

    @classmethod
    def addCurvesToTimewarp(cls, retime_curve):
        selection = cls.getSelected()
        timewarpAnimCurves = cls.getCurvesFromNodes([retime_curve])
        if not retime_curve or not selection:
            return False
        animCurves = cls.getCurvesFromNodes(selection)
        animCurves = list(set(animCurves) - set(timewarpAnimCurves))
        for a in animCurves:
            outPlug = '{0}.{1}'.format(retime_curve, 'timeWarp')
            inPlug = '{0}.{1}'.format(a, 'input')
            if not cmds.isConnected(outPlug, inPlug):
                cmds.connectAttr(outPlug, inPlug, force=True)

    @classmethod
    def getCurvesAttachedToRetime(cls, retimeObject):
        if not cmds.objExists(retimeObject):
            return False
        '\n        get connections to retime attribute\n        '
        connections = cmds.listConnections('{0}.{1}'.format(retimeObject, 'timeWarp'), source=False, type='animCurve')
        return connections

    @classmethod
    def getAllConnectionsToRetime(cls, retimeObject):
        if not cmds.objExists(retimeObject):
            return False
        '\n        get connections to retime attribute\n        '
        connections = cmds.listConnections('{0}.{1}'.format(retimeObject, 'timeWarp'), source=False)
        return connections

    @classmethod
    def getAttributeFromCurve(cls, curve_node):
        if not cmds.objExists(curve_node):
            return False
        '\n        handle character sets\n        '
        connections = cmds.listConnections(curve_node)
        curve_type = cmds.objectType(connections[0])
        if curve_type == 'character':
            '\n            get character set attribute\n            '
            characterSetPlug = cmds.listConnections(curve_node, plugs=True)
            objectAttribute = cmds.listConnections(characterSetPlug[0], plugs=True, source=False)
            return objectAttribute[0]
        else:
            objectAttribute = cmds.listConnections(curve_node, source=False, destination=True, plugs=True)
            return objectAttribute[0]

    @classmethod
    def get_hierarchical_connection_info_from_retime(cls, retimeObject):
        """
        data
        """
        data = {}
        '\n        start getting info\n        '
        connections = cls.getCurvesAttachedToRetime(retimeObject)
        if not connections:
            return data
        '\n        '
        for c in connections:
            '\n            get attr object.attribute\n            '
            attr = cls.getAttributeFromCurve(c)
            if not attr:
                continue
            buffer = attr.split('.')
            if buffer[0] not in data.keys():
                data[buffer[0]] = {}
            data[buffer[0]][buffer[1]] = c
        '\n        '
        return data

    @classmethod
    def print_curve_points(cls, close_shape=True):
        """
        points = []
        points.append([0.194834031727,0.580902610367])
        points.append([0.194834031727,0.648078016865])
        points.append([0.805165968273,0.648078016865])
        points.append([0.805165968273,0.580902610367])
        points.append([0.194834031727,0.580902610367])
        """
        selection = cmds.ls(sl=True)
        '\n        grouping header\n        '
        print('\n\n## Points Group Header:')
        print('points_group = []')
        '\n        itterate shapes\n        '
        for nurbs_curve in selection:
            '\n            print header\n            '
            print('## Shape: {0}'.format(nurbs_curve))
            print('points = []')
            '\n            print points\n            '
            cv_count = cmds.getAttr('{0}.spans'.format(nurbs_curve))
            for n in range(cv_count):
                cv = '{0}.cv[{1}]'.format(nurbs_curve, n)
                pos = cmds.xform(cv, query=True, t=True, worldSpace=True)
                print('points.append([{0},{1},{2}])'.format(pos[0], pos[1], pos[2]))
            '\n            close shape\n            '
            cv = '{0}.cv[{1}]'.format(nurbs_curve, 0)
            pos = cmds.xform(cv, query=True, t=True, worldSpace=True)
            print('points.append([{0},{1},{2}])'.format(pos[0], pos[1], pos[2]))
            print('points_group.append(points)\n\n')

    @classmethod
    def get_controller_shape_node(cls):
        points_group = []
        points = []
        points.append([-0.208226537704, 0.719860601425, 0.0536088585854])
        points.append([-0.191773462296, 0.719860601425, 0.0536088585854])
        points.append([-0.180139374733, 0.708226537704, 0.0536088585854])
        points.append([-0.180139374733, 0.691773462296, 0.0536088585854])
        points.append([-0.191773462296, 0.680139398575, 0.0536088585854])
        points.append([-0.208226537704, 0.680139398575, 0.0536088585854])
        points.append([-0.219860625267, 0.691773462296, 0.0536088585854])
        points.append([-0.219860625267, 0.708226537704, 0.0536088585854])
        points.append([-0.208226537704, 0.719860601425, 0.0536088585854])
        points_group.append(points)
        points = []
        points.append([0.180139374733, 0.708226537704, 0.0536088585854])
        points.append([0.191773462296, 0.719860601425, 0.0536088585854])
        points.append([0.208226537704, 0.719860601425, 0.0536088585854])
        points.append([0.219860625267, 0.708226537704, 0.0536088585854])
        points.append([0.219860625267, 0.691773462296, 0.0536088585854])
        points.append([0.208226537704, 0.680139398575, 0.0536088585854])
        points.append([0.191773462296, 0.680139398575, 0.0536088585854])
        points.append([0.180139374733, 0.691773462296, 0.0536088585854])
        points.append([0.180139374733, 0.708226537704, 0.0536088585854])
        points_group.append(points)
        points = []
        points.append([0.0198606207967, 0.191773462296, 0.0536088585854])
        points.append([0.00822653770447, 0.180139374733, 0.0536088585854])
        points.append([-0.00822653919458, 0.180139374733, 0.0536088585854])
        points.append([-0.0198606193066, 0.191773462296, 0.0536088585854])
        points.append([-0.0198606207967, 0.208226537704, 0.0536088585854])
        points.append([-0.00822653770447, 0.219860601425, 0.0536088585854])
        points.append([0.00822653919458, 0.219860601425, 0.0536088585854])
        points.append([0.0198606222868, 0.208226537704, 0.0536088585854])
        points.append([0.0198606207967, 0.191773462296, 0.0536088585854])
        points_group.append(points)
        points = []
        points.append([0.00822653770447, 0.519860601425, 0.0536088585854])
        points.append([0.019860625267, 0.508226537704, 0.0536088585854])
        points.append([0.0198606207967, 0.491773462296, 0.0536088585854])
        points.append([0.00822653770447, 0.480139398575, 0.0536088585854])
        points.append([-0.00822653919458, 0.480139398575, 0.0536088585854])
        points.append([-0.0198606193066, 0.491773462296, 0.0536088585854])
        points.append([-0.0198606193066, 0.508226537704, 0.0536088585854])
        points.append([-0.00822653770447, 0.519860601425, 0.0536088585854])
        points.append([0.00822653770447, 0.519860601425, 0.0536088585854])
        points_group.append(points)
        points = []
        points.append([-0.180139374733, 0.691773462296, 0.0536088585854])
        points.append([-0.156861448288, 0.6684237957, 0.0639001250267])
        points.append([-0.116200792789, 0.627763128281, 0.0704486727715])
        points.append([-0.075540137291, 0.587102460861, 0.0704486727715])
        points.append([-0.034879475832, 0.546441793442, 0.0639001250267])
        points.append([-0.00822653770447, 0.519860601425, 0.0536088585854])
        points.append([-0.0198606207967, 0.508226537704, 0.0536088585854])
        points.append([-0.0464418232441, 0.53487944603, 0.0639001250267])
        points.append([-0.0871024847031, 0.575540113449, 0.0704486727715])
        points.append([-0.127763140202, 0.616200780869, 0.0704486727715])
        points.append([-0.1684237957, 0.656861448288, 0.0639001250267])
        points.append([-0.191773462296, 0.680139398575, 0.0536088585854])
        points.append([-0.180139374733, 0.691773462296, 0.0536088585854])
        points_group.append(points)
        points = []
        points.append([0.00822653770447, 0.519860601425, 0.0536088585854])
        points.append([0.034879475832, 0.546441793442, 0.0639001250267])
        points.append([0.075540137291, 0.587102460861, 0.0704486727715])
        points.append([0.116200792789, 0.627763128281, 0.0704486727715])
        points.append([0.156861448288, 0.6684237957, 0.0639001250267])
        points.append([0.180139374733, 0.691773462296, 0.0536088585854])
        points.append([0.191773462296, 0.680139398575, 0.0536088585854])
        points.append([0.1684237957, 0.656861448288, 0.0639001250267])
        points.append([0.127763152122, 0.616200780869, 0.0704486727715])
        points.append([0.0871024847031, 0.575540113449, 0.0704486727715])
        points.append([0.0464418232441, 0.53487944603, 0.0639001250267])
        points.append([0.019860625267, 0.508226537704, 0.0536088585854])
        points.append([0.00822653770447, 0.519860601425, 0.0536088585854])
        points_group.append(points)
        points = []
        points.append([-0.00822653919458, 0.480139398575, 0.0536088585854])
        points.append([-0.00817581340671, 0.442497158051, 0.0639001250267])
        points.append([-0.00817581638694, 0.384994292259, 0.0704486727715])
        points.append([-0.00817581638694, 0.327491426468, 0.0704486727715])
        points.append([-0.00817581340671, 0.269988584518, 0.0639001250267])
        points.append([-0.00822653770447, 0.219860601425, 0.0536088585854])
        points.append([0.00822653919458, 0.219860601425, 0.0536088585854])
        points.append([0.00817581415176, 0.269988584518, 0.0639001250267])
        points.append([0.00817581191659, 0.327491426468, 0.0704486727715])
        points.append([0.00817581191659, 0.384994292259, 0.0704486727715])
        points.append([0.00817581415176, 0.442497158051, 0.0639001250267])
        points.append([0.00822653770447, 0.480139398575, 0.0536088585854])
        points.append([-0.00822653919458, 0.480139398575, 0.0536088585854])
        points_group.append(points)
        points = []
        points.append([-0.230901694298, 0.795105648041, 0.05])
        points.append([-0.169098293781, 0.795105648041, 0.05])
        points.append([-0.119098305702, 0.758778524399, 0.05])
        points.append([-0.0999999880791, 0.7, 0.05])
        points.append([-0.119098293781, 0.641221475601, 0.05])
        points.append([-0.169098305702, 0.604894351959, 0.05])
        points.append([-0.23090171814, 0.604894351959, 0.05])
        points.append([-0.28090171814, 0.641221475601, 0.05])
        points.append([-0.3, 0.7, 0.05])
        points.append([-0.28090171814, 0.758778524399, 0.05])
        points.append([-0.230901694298, 0.795105648041, 0.05])
        points_group.append(points)
        points = []
        points.append([0.119098293781, 0.758778524399, 0.05])
        points.append([0.169098305702, 0.795105648041, 0.05])
        points.append([0.230901694298, 0.795105648041, 0.05])
        points.append([0.280901694298, 0.758778524399, 0.05])
        points.append([0.3, 0.7, 0.05])
        points.append([0.28090171814, 0.641221475601, 0.05])
        points.append([0.230901694298, 0.604894351959, 0.05])
        points.append([0.16909828186, 0.604894351959, 0.05])
        points.append([0.11909828186, 0.641221475601, 0.05])
        points.append([0.0999999880791, 0.7, 0.05])
        points.append([0.119098293781, 0.758778524399, 0.05])
        points_group.append(points)
        points = []
        points.append([0.0309017032385, 0.295105648041, 0.05])
        points.append([-0.030901697278, 0.295105648041, 0.05])
        points.append([-0.0809017062187, 0.258778524399, 0.05])
        points.append([-0.100000011921, 0.2, 0.05])
        points.append([-0.0809017181396, 0.141221475601, 0.05])
        points.append([-0.0309017151594, 0.104894340038, 0.05])
        points.append([0.0309016942978, 0.104894328117, 0.05])
        points.append([0.0809017062187, 0.141221451759, 0.05])
        points.append([0.100000011921, 0.199999988079, 0.05])
        points.append([0.0809017002583, 0.258778524399, 0.05])
        points.append([0.0309017032385, 0.295105648041, 0.05])
        points_group.append(points)
        points = []
        points.append([-0.32800719738, 1.0, 0.05])
        points.append([-0.364003610611, 0.990354824066, 0.05])
        points.append([-0.390354800224, 0.964003562927, 0.05])
        points.append([-0.4, 0.928007221222, 0.05])
        points.append([-0.4, 0.0719928264618, 0.05])
        points.append([-0.390354800224, 0.035996389389, 0.05])
        points.append([-0.364003610611, 0.00964517593384, 0.05])
        points.append([-0.32800719738, 0.0, 0.05])
        points.append([0.32800719738, 0.0, 0.05])
        points.append([0.364003610611, 0.00964517593384, 0.05])
        points.append([0.390354800224, 0.035996389389, 0.05])
        points.append([0.4, 0.0719928264618, 0.05])
        points.append([0.4, 0.928007221222, 0.05])
        points.append([0.390354800224, 0.964003562927, 0.05])
        points.append([0.364003610611, 0.990354824066, 0.05])
        points.append([0.32800719738, 1.0, 0.05])
        points.append([-0.32800719738, 1.0, 0.05])
        points.append([-0.32800719142, 1.0, -0.0500000007451])
        points.append([-0.364003610611, 0.990354824066, -0.05])
        points.append([-0.364003610611, 0.990354824066, 0.05])
        points.append([-0.364003610611, 0.990354824066, -0.05])
        points.append([-0.390354800224, 0.964003562927, -0.05])
        points.append([-0.390354800224, 0.964003562927, 0.05])
        points.append([-0.390354800224, 0.964003562927, -0.05])
        points.append([-0.4, 0.928007221222, -0.05])
        points.append([-0.4, 0.928007221222, 0.05])
        points.append([-0.4, 0.928007221222, -0.05])
        points.append([-0.4, 0.0719928264618, -0.05])
        points.append([-0.4, 0.0719928264618, 0.05])
        points.append([-0.4, 0.0719928264618, -0.05])
        points.append([-0.390354800224, 0.035996389389, -0.05])
        points.append([-0.390354800224, 0.035996389389, 0.05])
        points.append([-0.390354800224, 0.035996389389, -0.05])
        points.append([-0.364003610611, 0.00964517593384, -0.05])
        points.append([-0.364003610611, 0.00964517593384, 0.05])
        points.append([-0.364003610611, 0.00964517593384, -0.05])
        points.append([-0.32800719738, 0.0, -0.05])
        points.append([-0.32800719738, 0.0, 0.05])
        points.append([-0.32800719738, 0.0, -0.05])
        points.append([0.32800719738, 0.0, -0.05])
        points.append([0.32800719738, 0.0, 0.05])
        points.append([0.32800719738, 0.0, -0.05])
        points.append([0.364003610611, 0.00964517593384, -0.05])
        points.append([0.364003610611, 0.00964517593384, 0.05])
        points.append([0.364003610611, 0.00964517593384, -0.05])
        points.append([0.390354800224, 0.035996389389, -0.05])
        points.append([0.390354800224, 0.035996389389, 0.05])
        points.append([0.390354800224, 0.035996389389, -0.05])
        points.append([0.4, 0.0719928264618, -0.05])
        points.append([0.4, 0.0719928264618, 0.05])
        points.append([0.4, 0.0719928264618, -0.05])
        points.append([0.4, 0.928007221222, -0.05])
        points.append([0.4, 0.928007221222, 0.05])
        points.append([0.4, 0.928007221222, -0.05])
        points.append([0.390354800224, 0.964003562927, -0.05])
        points.append([0.390354800224, 0.964003562927, 0.05])
        points.append([0.390354800224, 0.964003562927, -0.05])
        points.append([0.364003610611, 0.990354824066, -0.05])
        points.append([0.364003610611, 0.990354824066, 0.05])
        points.append([0.364003610611, 0.990354824066, -0.05])
        points.append([0.32800719738, 1.0, -0.05])
        points.append([0.32800719738, 1.0, 0.05])
        points.append([0.32800719738, 1.0, -0.05])
        points.append([-0.32800719142, 1.0, -0.0500000007451])
        points.append([-0.32800719738, 1.0, 0.05])
        points_group.append(points)
        '\n        create curve objects\n        '
        node_list = []
        for points in points_group:
            temp_curve = cmds.curve(degree=1, p=points)
            node_list.append(temp_curve)
        '\n        combine\n        '
        main_node = node_list.pop()
        for n in node_list:
            '\n            get shape\n            '
            shape_node = cmds.listRelatives(n, shapes=True)
            if shape_node:
                shape_node = shape_node[0]
                '\n                hide shapes\n                '
                cmds.setAttr('{0}.{1}'.format(shape_node, 'isHistoricallyInteresting'), 0)
                cmds.setAttr('{0}.{1}'.format(shape_node, 'hiddenInOutliner'), True)
                '\n                reparent shape\n                '
                cmds.parent(shape_node, main_node, shape=True, addObject=True)
                cmds.delete(n)
        '\n        rename main node\n        '
        combined_node = cmds.rename(main_node, 'retime_controller')
        '\n        set color\n        '
        cmds.setAttr('{0}.{1}'.format(combined_node, 'overrideEnabled'), 1)
        cmds.setAttr('{0}.{1}'.format(combined_node, 'overrideColor'), 17)
        '\n        return\n        '
        return combined_node

    @classmethod
    def create_new_retime_controller(cls, retime_controller='retime_controller'):
        """
        undo chunck
        """

        cls.create_new_retime_controller_exec(retime_controller=retime_controller)
        '\n        undo chunck\n        '

    @classmethod
    def create_new_retime_controller_exec(cls, retime_controller='retime_controller'):
        """
        - create curve shape
        - add attributes
        - reset based on selection
        """
        retime_controller = cls.get_controller_shape_node()
        '\n        add attributes\n        '
        cmds.addAttr(retime_controller, longName='timeWarp', attributeType='time')
        cmds.addAttr(retime_controller, longName='store', dataType='string')
        cmds.addAttr(retime_controller, longName='timeWarp_offline', attributeType='time')
        states_enum = ['Enable=1', 'Disable=2', 'Reset=3', 'Invert=4', 'Disconnect=5', 'Delete=6']
        cmds.addAttr(retime_controller, ln='retimeState', at='enum', enumName=':'.join(states_enum))
        '\n        keyable and channelbox\n        '
        for a in ['timeWarp']:
            attribute = '{0}.{1}'.format(retime_controller, a)
            cmds.setAttr(attribute, edit=True, channelBox=True)
            cmds.setAttr(attribute, edit=True, keyable=True)
        '\n        non-keyable\n        '
        for a in ['timeWarp_offline', 'retimeState']:
            attribute = '{0}.{1}'.format(retime_controller, a)
            cmds.setAttr(attribute, edit=True, keyable=False)
        '\n        misc attributes\n        '
        for a in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']:
            attribute = '{0}.{1}'.format(retime_controller, a)
            cmds.setAttr(attribute, edit=True, keyable=False)
            cmds.setAttr(attribute, edit=True, channelBox=True)
        '\n        non-channelbox\n        '
        for a in ['timeWarp_offline', 'store', 'retimeState']:
            attribute = '{0}.{1}'.format(retime_controller, a)
            cmds.setAttr(attribute, edit=True, channelBox=False)
        '\n        reset anim\n        '
        cls.set_retime_controller_state(retime_controller, RetimeStates.Reset)
        return retime_controller

    @classmethod
    def set_retime_controller_state(cls, retime_controller, new_state):
        if not retime_controller or not new_state:
            return False
        '\n        do nothing\n        '
        previous_state = cls.get_retime_controller_status(retime_controller)
        if previous_state == new_state:
            return new_state
        '\n        change to a default state temporarily\n        * disconnect time\n        * copy offline back timeWarp \n        '
        attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        online_key_count = cmds.keyframe(attr, query=True, keyframeCount=True)
        attr = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
        offline_key_count = cmds.keyframe(attr, query=True, keyframeCount=True)
        time_node = cmds.ls(type='time')[0]
        time_attr = '{0}.{1}'.format(time_node, 'outTime')
        attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        if cmds.isConnected(time_attr, attr):
            cmds.disconnectAttr(time_attr, attr)
        if offline_key_count > 0:
            attribute = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
            cmds.cutKey(attribute, option='keys')
            attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
            cmds.pasteKey(attribute, option='replace')
            '\n            update online keycount\n            '
            online_key_count = cmds.keyframe(attr, query=True, keyframeCount=True)
        '\n        fix empty\n        '
        if online_key_count == 0:
            cls.reset_retime(retime_controller)
        '\n        states\n        '
        if new_state == RetimeStates.Reset:
            '\n            reset\n            '
            cls.reset_retime(retime_controller)
            '\n            set state to enable\n            '
            cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Enable)
            return RetimeStates.Enable
        elif new_state == RetimeStates.Disable:
            try:
                '\n                cut/paste to offline\n                '
                attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
                cmds.cutKey(attribute, option='keys')
                attribute = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
                cmds.pasteKey(attribute, option='replace')
                '\n                connect to time\n                '
                time_nodes = cmds.ls(type='time')
                time_attr = '{0}.{1}'.format(time_nodes[0], 'outTime')
                retime_attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
                cmds.connectAttr(time_attr, retime_attr, force=True)
                '\n                set state to disable\n                '
                cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Disable)
                return RetimeStates.Disable
            except Exception as e:
                print(1280, 'RetimeStates.Enable', Exception, e)
                cls.set_retime_controller_state(retime_controller, RetimeStates.Reset)
        elif new_state == RetimeStates.Enable:
            try:
                '\n                set state to Enable\n                '
                cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Enable)
                return RetimeStates.Enable
            except Exception as e:
                print(1270, 'RetimeStates.Enable', Exception, e)
                print(traceback.format_exc())
                cls.set_retime_controller_state(retime_controller, RetimeStates.Reset)
        elif new_state == RetimeStates.Delete:
            cls.delete_retime(retime_controller)
            return RetimeStates.Delete
        elif new_state == RetimeStates.Disconnect:
            '\n            disconnect\n            '
            cls.completely_disconnect_retime(retime_controller)
            '\n            set state to enable\n            '
            cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Enable)
            return RetimeStates.Enable
        elif new_state == RetimeStates.Invert:
            '\n            invert\n            * copy to offline\n            * rekey back to online inverted\n            '
            cls.invert_retime(retime_controller)
            '\n            set state to enable\n            '
            cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), RetimeStates.Invert)
            return RetimeStates.Enable

    @classmethod
    def reset_retime(cls, retime_controller):
        """
        set start and end keys
        """
        start_time = cmds.playbackOptions(query=True, animationStartTime=True)
        end_time = cmds.playbackOptions(query=True, animationEndTime=True)
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
        cmds.cutKey(attribute)
        cmds.setKeyframe(attribute, time=start_time, value=start_time, inTangentType='linear', outTangentType='linear')
        cmds.setKeyframe(attribute, time=end_time, value=end_time, inTangentType='linear', outTangentType='linear')
        '\n        clear offline\n        '
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
        cmds.cutKey(attribute, option='keys')

    @classmethod
    def invert_retime(cls, retime_controller):
        """
        * copy main curve to offline
        * invert keys back to main curve
        """
        '\n        get info\n        '
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
        start_frame = int(cmds.findKeyframe(attribute, which='first'))
        end_frame = int(cmds.findKeyframe(attribute, which='last'))
        duration = end_frame - start_frame
        if duration <= 1:
            return False
        '\n        cut/paste to offline\n        '
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
        cmds.cutKey(attribute, option='keys')
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
        cmds.pasteKey(attribute, option='replace')
        '\n        copy/invert\n        '
        source_attr = '{0}.{1}'.format(retime_controller, 'timeWarp_offline')
        target_attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        for t in range(start_frame, end_frame + 1):
            value = cmds.getAttr(source_attr, time=t)
            cmds.setKeyframe(target_attr, value=t, time=value, inTangentType='spline', outTangentType='spline')

    @classmethod
    def completely_disconnect_retime(cls, retime_controller):
        """
        get connected curves
        """
        connections = cls.getAllConnectionsToRetime(retime_controller)
        if not connections:
            return False
        '\n        disconnect\n        '
        retime_attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        for c in connections:
            curve_attr = '{0}.{1}'.format(c, 'input')
            if cmds.isConnected(retime_attr, curve_attr):
                cmds.disconnectAttr(retime_attr, curve_attr)

    @classmethod
    def disconnect_curve(cls, retime_controller, connections):
        if not cmds.objExists(retime_controller):
            return False
        '\n        disconnect\n        '
        retime_attr = '{0}.{1}'.format(retime_controller, 'timeWarp')
        for c in connections:
            curve_attr = '{0}.{1}'.format(c, 'input')
            if cmds.isConnected(retime_attr, curve_attr):
                cmds.disconnectAttr(retime_attr, curve_attr)

    @classmethod
    def delete_retime(cls, retime_controller):
        cmds.delete(retime_controller)

    @classmethod
    def select_maya_nodes(cls, nodes):
        if not nodes:
            return False
        if type(nodes) != type([]):
            nodes = [nodes]
        existing_nodes = []
        for n in nodes:
            if cls.object_exists(n):
                existing_nodes.append(n)
        if not existing_nodes:
            return False
        '\n        select\n        '
        cmds.select(existing_nodes, replace=True)
        return True

    @classmethod
    def get_retime_controller_status(cls, retime_controller):
        if not cmds.objExists(retime_controller):
            return RetimeStates.Delete
        '\n        check the attr\n        '
        attr = '{0}.{1}'.format(retime_controller, 'retimeState')
        state_query = cmds.getAttr(attr)
        '\n        lookup table\n        '
        state_lookup = {}
        state_lookup[1] = RetimeStates.Enable
        state_lookup[2] = RetimeStates.Disable
        state_lookup[3] = RetimeStates.Reset
        state_lookup[4] = RetimeStates.Invert
        state_lookup[5] = RetimeStates.Disconnect
        state_lookup[6] = RetimeStates.Delete
        '\n        return with fallback\n        '
        return state_lookup.get(state_query, 1)

    @classmethod
    def bake_retime_controller(cls, retime_controller):
        """
        get all connected plugs, object.attr
        """
        connections = cls.getCurvesAttachedToRetime(retime_controller)
        all_plugs = cls.get_plugs_for_anim_curves(connections)
        '\n        get stats\n        '
        attribute = '{0}.{1}'.format(retime_controller, 'timeWarp')
        start_frame = int(cmds.findKeyframe(attribute, which='first'))
        end_frame = int(cmds.findKeyframe(attribute, which='last'))
        time_range = (start_frame, end_frame)
        '\n        bake\n        '
        cmds.bakeResults(all_plugs, simulation=True, time=time_range, sampleBy=1, disableImplicitControl=True, preserveOutsideKeys=False, sparseAnimCurveBake=False, shape=True)

    @classmethod
    def get_plugs_for_anim_curves(cls, anim_curves):
        if not anim_curves:
            return []
        all_plugs = []
        for c in anim_curves:
            if cmds.objExists(c):
                plugs = (cmds.listConnections(c + '.output', plugs=True, source=False, destination=True) or [])
                all_plugs += plugs
        '\n        clean\n        '
        all_plugs = list(set(all_plugs))
        return all_plugs

    @classmethod
    def cleanSubframeKeys(cls, *args, **kwargs):
        """
        pull args
        """
        curve_nodes = kwargs.get('curve_nodes', False)
        '\n        get selections\n        '
        if not curve_nodes:
            selection = cmds.ls(sl=True)
            checkShapes = cmds.listRelatives(selection, shapes=True, fullPath=True)
            if checkShapes:
                selection += checkShapes
            selection = list(set(selection))
            curve_nodes = cls.getCurvesFromNodes(selection)
        if curve_nodes:
            for curveNode in curve_nodes:
                timesValues = cmds.getAttr('{0}.{1}'.format(curveNode, 'keyTimeValue[:]'))
                if timesValues:
                    times = []
                    values = []
                    wholeTimes = set()
                    subframeTimes = set()
                    for t, v in timesValues:
                        times.append(t)
                        wholeTimes.add(int(math.floor(float(t) + 0.5)))
                        values.append(v)
                        if not float(t).is_integer():
                            subframeTimes.add(t)
                    newTimes = list(wholeTimes - set(times))
                    for t in newTimes:
                        cmds.setKeyframe(curveNode, insert=True, time=tuple([t, t]))
                    for t in subframeTimes:
                        cmds.cutKey(curveNode, time=tuple([t, t]))

    @classmethod
    def find_old_retime_curves(cls, *args, **kwargs):
        nurbs_curves = cmds.ls(type='nurbsCurve', long=True)
        if not nurbs_curves:
            return False
        transforms = cmds.listRelatives(nurbs_curves, allParents=True, type='transform', fullPath=True)
        transforms = list(set(transforms))
        old_retime_curves = []
        for t in transforms:
            has_shuffle_data_attr = cmds.objExists('{0}.{1}'.format(t, 'shuffleData'))
            has_offline_attr = cmds.objExists('{0}.{1}'.format(t, 'timeWarp_offline'))
            if has_shuffle_data_attr and has_offline_attr:
                if t not in old_retime_curves:
                    old_retime_curves.append(t)
        return old_retime_curves

    @classmethod
    def update_old_retime_curves(cls, *args, **kwargs):
        """"""
        old_retime_curves = cls.find_old_retime_curves()
        if not old_retime_curves:
            return

        def update():
            for c in old_retime_curves:
                cls.update_old_retime_curve(c)
        kwargs = {}
        kwargs['parentWidget'] = QTHelpers.get_main_window()
        kwargs['titleText'] = 'Update Retime Curves?'
        message = []
        message.append('It looks like there are some outdated retime curves in your scene, would you like to update?\n')
        message += old_retime_curves
        message.append('\n')
        message.append('Make sure to back up your scene before proceeding!')
        kwargs['messageText'] = '\n'.join(message)
        kwargs['successCallback'] = update
        QTHelpers.getYesNoFromUser(**kwargs)

    @classmethod
    def update_old_retime_curve(cls, retime_controller):
        print('Updating ', retime_controller)
        try:
            states_enum = ['Enable=1', 'Disable=2', 'Reset=3', 'Invert=4', 'Disconnect=5', 'Delete=6']
            cmds.addAttr(retime_controller, ln='retimeState', at='enum', enumName=':'.join(states_enum))
            state = RetimeStates.Enable
            keyframe_count = cmds.keyframe('{0}.{1}'.format(retime_controller, 'timeWarp_offline'), query=True, time=(), keyframeCount=True)
            if keyframe_count > 0:
                state = RetimeStates.Disable
            cmds.setAttr('{0}.{1}'.format(retime_controller, 'retimeState'), state)
            cmds.deleteAttr('{0}.{1}'.format(retime_controller, 'shuffleData'))
        except Exception as e:
            print('Error', 'update_old_retime_curve', Exception, e)

class ShuffleKeys(object):

    @classmethod
    def process(cls, retimeObject):
        """
        build retime helpers
        """
        curveNodes = cmds.findKeyframe(retimeObject, curve=True, at='timeWarp')
        if not curveNodes:
            return False
        curve = curveNodes[0]
        retime_lookup = RetimeLookup(curve)
        '\n        find connected anim curves\n        '
        animCurves = CoreFunctions.getCurvesAttachedToRetime(retimeObject)
        if not animCurves:
            return False
        '\n        iterate curves\n        '
        for curve in animCurves:
            '\n            get key times\n            '
            timesValues = cmds.getAttr('{0}.{1}'.format(curve, 'keyTimeValue[:]'))
            if not timesValues:
                continue
            '\n            create temp curve\n            '
            nodeType = cmds.nodeType(curve)
            tmpCurve = cmds.createNode(nodeType, name='{0}_tempCurve'.format(curve))
            '\n            check infinities\n            '
            pre_infinity = cmds.getAttr(curve + '.preInfinity')
            post_infinity = cmds.getAttr(curve + '.postInfinity')
            '\n            copy keys into temp curve\n            '
            for t, v in timesValues:
                '\n                copy\n                '
                cmds.copyKey(curve, time=(t, t), option='keys')
                '\n                remap time\n                '
                lookup_info = retime_lookup.getSingleKeyTimeLookup(t)
                for i, data in enumerate(lookup_info):
                    rt, slope_multiplier = data
                    if rt is None:
                        continue
                    '\n                    paste key\n                    '
                    cmds.pasteKey(tmpCurve, time=(rt, rt), option='merge')
                    '\n                    apply slope\n                    '
                    out_tangent_type = cmds.keyTangent(tmpCurve, time=(rt, rt), query=True, outTangentType=True)[0]
                    if out_tangent_type != 'step':
                        in_tangent_angle = cmds.keyTangent(tmpCurve, time=(rt, rt), query=True, inAngle=True)[0]
                        in_tangent_weight = cmds.keyTangent(tmpCurve, time=(rt, rt), query=True, inWeight=True)[0]
                        out_tangent_angle = cmds.keyTangent(tmpCurve, time=(rt, rt), query=True, outAngle=True)[0]
                        out_tangent_weight = cmds.keyTangent(tmpCurve, time=(rt, rt), query=True, outWeight=True)[0]
                        in_tangent_x = cmds.keyTangent(tmpCurve, time=(rt, rt), query=True, ix=True)[0]
                        in_tangent_y = cmds.keyTangent(tmpCurve, time=(rt, rt), query=True, iy=True)[0]
                        out_tangent_x = cmds.keyTangent(tmpCurve, time=(rt, rt), query=True, ox=True)[0]
                        out_tangent_y = cmds.keyTangent(tmpCurve, time=(rt, rt), query=True, oy=True)[0]
                        in_tangent_angle *= slope_multiplier
                        out_tangent_angle *= slope_multiplier
                        in_tangent_y *= slope_multiplier
                        cmds.keyTangent(tmpCurve, edit=True, absolute=True, time=(rt, rt), ix=in_tangent_x)
                        cmds.keyTangent(tmpCurve, edit=True, absolute=True, time=(rt, rt), iy=in_tangent_y)
            '\n            replace curve\n            '
            try:
                cmds.cutKey(tmpCurve, option='curve')
                cmds.pasteKey(curve, option='replaceCompletely')
            except Exception as e:
                raise RuntimeError("Shuffle failed for " + curve) from e
            '\n            set infinity\n            '
            cmds.setAttr(curve + '.preInfinity', pre_infinity)
            cmds.setAttr(curve + '.postInfinity', post_infinity)
            '\n            remove temp curve\n            '
            cmds.delete(tmpCurve)

class RetimeLookup(object):

    def __init__(self, retime_animCurve):
        """
        properties
        """
        self.retime_animCurve = retime_animCurve
        '\n        sections\n        '
        self.sections = self.getSections(self.retime_animCurve)
        '\n        value time lookup\n        '
        self.value_time_lookup = self.create_value_time_lookup(self.sections)
        self.value_time_cache = {}

    @classmethod
    def getDirection(cls, itemIndex, prevValue, currValue, nextValue):
        direction = 0
        if itemIndex == 0:
            '\n            first\n            '
            if nextValue > currValue:
                direction = 1
            elif nextValue < currValue:
                direction = -1
            else:
                direction = 0
        else:
            '\n            any other position\n            '
            if currValue > prevValue:
                direction = 1
            elif currValue < prevValue:
                direction = -1
            else:
                direction = 0
        '\n        '
        return direction

    @classmethod
    def drange(cls, x, y, jump):
        while x < y:
            yield float(x)
            x += decimal.Decimal(jump)

    @classmethod
    def getKeyTimes(cls, curve):
        timesValues = cmds.getAttr('{0}.{1}'.format(curve, 'keyTimeValue[:]'))
        times = []
        values = []
        if timesValues:
            wholeTimes = set()
            subframeTimes = set()
            for t, v in timesValues:
                times.append(t)
                wholeTimes.add(int(math.floor(float(t) + 0.5)))
                values.append(v)
        return times

    @classmethod
    def getSections(cls, curve):
        """
        get keytimes needed for sampling retime curve
        """
        keyframeTimes = cls.getKeyTimes(curve)
        firstFrame = int(min(keyframeTimes))
        lastFrame = int(max(keyframeTimes))
        sampleStep = 0.1
        allKeyframeTimes = sorted(list(set(list(cls.drange(firstFrame, lastFrame + sampleStep, sampleStep)) + keyframeTimes)))
        '\n        simultaniously group by direction\n        '
        currentValue = None
        previousDirection = None
        direction = None
        newSection = True
        section = {}
        sections = []
        for i, t in enumerate(allKeyframeTimes):
            '\n            check directions\n            '
            previousValue = cmds.getAttr('{0}.{1}'.format(curve, 'output'), time=allKeyframeTimes[max(i - 1, 0)])
            currentValue = cmds.getAttr('{0}.{1}'.format(curve, 'output'), time=allKeyframeTimes[i])
            nextValue = cmds.getAttr('{0}.{1}'.format(curve, 'output'), time=allKeyframeTimes[min(i + 1, len(allKeyframeTimes) - 1)])
            direction = cls.getDirection(i, previousValue, currentValue, nextValue)
            if newSection:
                previousDirection = direction
                newSection = False
            '\n            new direction\n            '
            if direction != previousDirection:
                '\n                indicate starting new section\n                '
                newSection = True
                '\n                create new section\n                '
                if section:
                    sections.append(section)
                section = {}
            '\n            add info to section\n            '
            section[t] = cmds.getAttr('{0}.{1}'.format(curve, 'output'), time=t)
            '\n            cache\n            '
            previousDirection = direction
        '\n        add last section\n        '
        sections.append(section)
        return sections

    @classmethod
    def create_value_time_lookup(cls, sections):
        """
        section/value int/[value float = time]
        """
        data = OrderedDict()
        '\n        construct lookup\n        '
        for i, section in enumerate(sections):
            '\n            section grouping\n            '
            if i not in data.keys():
                data[i] = OrderedDict()
            for k, v in iteritems(section):
                '\n                value int grouping\n                adding neighbouring values in each section for overlap\n                '
                for offset in [-1, 0, 1]:
                    value_int = int(v + offset)
                    if value_int not in data[i].keys():
                        data[i][value_int] = []
                    '\n                    adding values\n                    '
                    data[i][value_int].append([v, k])
        '\n        return\n        '
        return data

    @classmethod
    def get_nearest_pair_index(cls, pairs, target_value, sort=False):
        if sort:
            pairs = sorted(pairs, key=itemgetter(1))
        return min(enumerate(pairs), key=lambda x: abs(x[1][0] - target_value))

    @classmethod
    def float_lerp(cls, a, b, f):
        return a * (1.0 - f) + b * f

    @classmethod
    def slope(cls, x1, y1, x2, y2):
        diff = x2 - x1
        if diff == 0:
            return 1
        return (y2 - y1) / diff

    @classmethod
    def clamp(cls, n, minn, maxn):
        return max(min(maxn, n), minn)

    @classmethod
    def get_slope_between_pairs(cls, pairs, index_a, index_b):
        """
        clamp indexes
        """
        index_a = cls.clamp(index_a, 0, len(pairs) - 1)
        index_b = cls.clamp(index_b, 0, len(pairs) - 1)
        '\n        if the index are the same, spread them out by a step\n        end check as well\n        '
        if index_a == index_b:
            if index_a == 0:
                index_b += 1
            else:
                index_a -= 1
        '\n        \n        '
        try:
            slope = cls.slope(pairs[index_a][0], pairs[index_a][1], pairs[index_b][0], pairs[index_b][1])
        except Exception as e:
            slope = 1
            print(2248, 'Slope Calculate Fail', Exception, e)
            print('index_a', index_a)
            print('index_b', index_b)
            print('pairs', pairs)
        return slope

    def getSingleKeyTimeLookup(self, target_time):
        """
        get nearest 2 t/v pairs from data
        """
        if target_time not in self.value_time_cache.keys():
            '\n            if not already cached, do brute force lookup\n            '
            lookup_times = []
            for section, int_groups in iteritems(self.value_time_lookup):
                value_int = int(target_time)
                if value_int in int_groups.keys():
                    '\n                    matching pair\n                    '
                    pairs = int_groups[value_int]
                    '\n                    lerp lookup\n                    '
                    pairs = sorted(pairs, key=itemgetter(0))
                    nearest_index, nearest_pair = self.get_nearest_pair_index(pairs, target_time)
                    '\n                    where? under, equal, over than matching value\n                    '
                    if target_time == nearest_pair[0]:
                        '\n                        found a match, onto next section\n                        '
                        slope = self.get_slope_between_pairs(pairs, nearest_index, nearest_index + 1)
                        lookup_times.append((nearest_pair[1], 1.0 / slope))
                        continue
                    elif nearest_pair[0] > target_time:
                        min_index = nearest_index
                        max_index = nearest_index + 1
                    else:
                        min_index = nearest_index
                        max_index = nearest_index - 1
                    '\n                    clamp if only one set of pairs in list\n                    '
                    max_index = min(len(pairs) - 1, max_index)
                    '\n                    get lerp ratio and apply to value\n                    '
                    diff = 0
                    try:
                        diff = pairs[max_index][0] - pairs[min_index][0]
                    except Exception as e:
                        pass
                    if diff == 0:
                        '\n                        both min and max are the same, just pick one\n                        '
                        ratio = False
                        lerp_value = pairs[min_index][1]
                    else:
                        ratio = (target_time - pairs[min_index][0]) / (pairs[max_index][0] - pairs[min_index][0])
                        lerp_value = self.float_lerp(pairs[min_index][1], pairs[max_index][1], ratio)
                    '\n                    slope\n                    '
                    slope = self.get_slope_between_pairs(pairs, min_index, max_index)
                    '\n                    store data\n                    '
                    lookup_times.append((lerp_value, 1.0 / slope))
            '\n            store results to cache\n            '
            self.value_time_cache[target_time] = lookup_times
        '\n        final return\n        '
        return self.value_time_cache[target_time]

class Color(object):

    def __init__(self, rgba):
        self.set_rgba(rgba)

    def get_rgba(self):
        return self.rgba

    def set_rgba(self, rgba):
        """
        validate, should include alpha
        """
        rgba += [1.0] * (4 - len(rgba))
        '\n        set\n        '
        self.rgba = rgba

    def r(self):
        return self.rgba[0]

    def g(self):
        return self.rgba[1]

    def b(self):
        return self.rgba[2]

    def a(self):
        return self.rgba[3]

    def r_int(self):
        return self.float_to_int(self.r())

    def g_int(self):
        return self.float_to_int(self.g())

    def b_int(self):
        return self.float_to_int(self.b())

    def a_int(self):
        return self.float_to_int(self.a())

    def multiply_hsva(self, m_rgba):
        """
        get hsva
        """
        hsva = self.float_rgba_to_hsva(self.rgba)
        '\n        multiply by values\n        '
        m_hsva = []
        for i, v in enumerate(hsva):
            m_hsva.append(hsva[i] * m_rgba[i])
        '\n        back to rgb\n        '
        rgba = self.float_hsva_to_rgba(m_hsva)
        '\n        return copy\n        '
        return Color(rgba)

    def lighten_hsva(self, m_rgba):
        """
        get hsva
        """
        hsva = self.float_rgba_to_hsva(self.rgba)
        '\n        multiply by values\n        '
        m_hsva = []
        for i, v in enumerate(hsva):
            m_hsva.append(self.lerp(hsva[i], 1, m_rgba[i]))
        '\n        back to rgb\n        '
        rgba = self.float_hsva_to_rgba(m_hsva)
        '\n        return copy\n        '
        return Color(rgba)

    def get_average_intensity(self):
        intensity = 0.3 * self.r() + 0.59 * self.g() + 0.11 * self.b()
        return intensity

    def get_int_rgba(self):
        return [self.r_int(), self.g_int(), self.b_int(), self.a_int()]

    def get_int_rgba_string(self):
        """
        helper for qt stylesheets
        """
        return 'rgb({0},{1},{2},{3})'.format(*self.get_int_rgba())

    @classmethod
    def lerp(cls, a, b, f):
        return a * (1.0 - f) + b * f

    @classmethod
    def float_to_int(cls, f):
        return int(f * 255)

    @classmethod
    def float_rgba_to_hsva(cls, rgba):
        h, s, v = colorsys.rgb_to_hsv(*rgba[:3])
        a = rgba[3]
        return [h, s, v, a]

    @classmethod
    def float_hsva_to_rgba(cls, hsva):
        r, g, b = colorsys.hsv_to_rgb(*hsva[:3])
        a = hsva[3]
        return [r, g, b, a]
