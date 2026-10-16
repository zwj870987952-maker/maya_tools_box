"""Required plugs used by native asConnectMocapX; no replacement mapping."""


def required_plugs():
    source = ['browInnerUp', 'cheekPuff', 'jawForward', 'jawLeft', 'jawRight',
              'mouthPucker', 'jawOpen', 'mouthRollUpper', 'mouthRollLower',
              'mouthShrugUpper', 'mouthShrugLower',
              'transformRotateX', 'transformRotateY', 'transformRotateZ']
    target = ['FKHead_M.rx', 'FKHead_M.ry', 'FKHead_M.rz', 'ctrlBox.limits',
              'Jaw_M.tx', 'Jaw_M.tz', 'upperLip_M.ty', 'lowerLip_M.ty',
              'ctrlMouth_M.tx', 'ctrlMouth_M.ty', 'ctrlLips_M.upperRoll', 'ctrlLips_M.lowerRoll']
    for side, word, cap in [('_R', 'right', 'Right'), ('_L', 'left', 'Left')]:
        source += [word+'EyeTransformRotateY', word+'EyeTransformRotateX', 'mouth'+cap]
        source += [a+side for a in ['eyeBlink', 'browDown', 'browOuterUp', 'eyeSquint',
                    'eyeWide', 'cheekSquint', 'noseSneer', 'mouthSmile', 'mouthFrown',
                    'mouthDimple', 'mouthUpperUp', 'mouthLowerDown', 'mouthStretch']]
        target += [node+side+'.'+attr for node, attr in [
            ('ctrlEye','tx'), ('ctrlEye','ty'), ('ctrlEye','blink'), ('ctrlEye','squint'),
            ('EyeBrowInner','tx'), ('EyeBrowInner','ty'), ('EyeBrowOuter','ty'),
            ('lowerLid','ty'), ('Cheek','tx'), ('Cheek','tz'),
            ('NoseCorner','tx'), ('NoseCorner','ty'), ('ctrlMouthCorner','tx'), ('ctrlMouthCorner','ty')]]
    return ['MocapX.'+a for a in source], target


def validate(cmds, namespace):
    if namespace:
        raise ValueError('原生 asConnectMocapX 使用无命名空间的曲线名；当前仅验证并支持根命名空间角色。')
    if cmds.objExists('AdvancedSkeletonHeadOffset'):
        raise ValueError('已存在 AdvancedSkeletonHeadOffset；不能重复连接 MocapX。')
    source, target = required_plugs()
    for side in ('_R','_L'):
        if cmds.objExists('Lip'+side+'.sticky'):
            source.append('MocapX.mouthClose')
            target.append('Lip'+side+'.sticky')
        if cmds.objExists('upperLipA'+side):
            target += ['upperLipA'+side+'.ty', 'lowerLipA'+side+'.ty']
    missing = [p for p in source+target if not cmds.objExists(p)]
    if missing:
        raise ValueError('MocapX / ADV Face 缺少属性: '+', '.join(missing))
    blocked = [p for p in target if not cmds.getAttr(p, settable=True)
               or cmds.listConnections(p, source=True, destination=False)]
    if blocked:
        raise ValueError('MocapX 目标属性已锁定或已有输入: '+', '.join(blocked))
    # Native MEL refers to these exact generated curve names.
    collisions = [n for side in ('_R','_L') for axis in ('X','Y')
                  for n in ['ctrlEye'+side+'_translate'+axis] if cmds.objExists(n)]
    if collisions:
        raise ValueError('原生 MocapX 曲线名称冲突: '+', '.join(collisions))
