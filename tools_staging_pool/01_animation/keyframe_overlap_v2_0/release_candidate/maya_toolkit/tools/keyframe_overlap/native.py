from .proxy import cmds
from . import runtime as _r
import time, os, sys, json
from collections import Counter

class scene:

    @staticmethod
    def get_fps(*_):
        timeUnitSet = {'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60}
        timeUnit = cmds.currentUnit(q=True, t=True)
        if timeUnit in timeUnitSet:
            return timeUnitSet[timeUnit]
        else:
            return float(str(''.join([i for i in timeUnit if i.isdigit() or i == '.'])))

    @staticmethod
    def get_timeline():
        min_time = int(round(cmds.playbackOptions(q=1, minTime=1), 0))
        max_time = int(round(cmds.playbackOptions(q=1, maxTime=1), 0))
        return [min_time, max_time]

class util:

    @staticmethod
    def return_none_func():
        cmds.warning('return_none_func')

    @staticmethod
    def get_space_locator(name='locator1', color=[1, 0.8, 0], scale=[1, 1, 1], position=[0, 0, 0]):
        _r.require_active()
        for i in range(3):
            scale[i] = 1.0 if scale[i] < 1.0 else scale[i]
        loc = cmds.spaceLocator(n=name)[0]
        shp = cmds.listRelatives(loc, shapes=1, f=1)[0]
        cmds.setAttr(shp + '.overrideEnabled', 1)
        cmds.setAttr(shp + '.overrideRGBColors', 1)
        cmds.setAttr(shp + '.overrideColorRGB', color[0], color[1], color[2])
        cmds.setAttr(shp + '.localPosition', position[0], position[1], position[2])
        cmds.setAttr(shp + '.localScale', scale[0], scale[1], scale[2])
        return loc

    @staticmethod
    def match_transform(src, dst, is_rot=True, is_pos=True):
        _r.require_active()
        rotate_order_ls = ['xyz', 'yzx', 'zxy', 'xzy', 'yxz', 'zyx']
        roo_idx = int(cmds.getAttr(dst + '.rotateOrder'))
        pos = cmds.xform(dst, q=1, ws=1, t=1)
        rot = cmds.xform(dst, q=1, ws=1, ro=1)
        if is_rot:
            cmds.xform(src, ro=rot, ws=1, roo=rotate_order_ls[roo_idx])
        if is_pos:
            cmds.xform(src, t=pos, ws=1)

    @staticmethod
    def get_object_size(obj):
        shp = cmds.listRelatives(obj, shapes=1, f=1)[0]
        bbox = cmds.exactWorldBoundingBox(shp)
        min_x, min_y, min_z, max_x, max_y, max_z = bbox
        width = max_x - min_x
        height = max_y - min_y
        depth = max_z - min_z
        scale_x = width * 0.5
        scale_y = height * 0.5
        scale_z = depth * 0.5
        return [scale_x, scale_y, scale_z]

class loc_delay_system:

    def __init__(self):
        _r.require_active()
        print('Initialize Locator Delay Script')

        def init_scene():
            cmds.refresh(suspend=0)
            cmds.namespace(set=':')
        self.pre_post_roll = 10
        self.prefix = 'kfo'
        self.license_key = None
        self.modes = {'rotation': {'x': {'color': (0.98, 0.374, 0), 'rot_order': 1, 'axis': [1.0, 0.0, 0.0], 'skip': ['x'], 'key_at': ['ry', 'rz']}, 'y': {'color': (0.7067, 1, 0), 'rot_order': 2, 'axis': [0.0, 1.0, 0.0], 'skip': ['y'], 'key_at': ['rx', 'rz']}, 'z': {'color': (0.1, 0.6, 0.9), 'rot_order': 0, 'axis': [0.0, 0.0, 1.0], 'skip': ['z'], 'key_at': ['ry', 'rx']}}, 'position': {'xz': {'color': (1, 0.8, 0), 'rot_order': 0, 'axis': [0.0] * 3, 'skip': ['y'], 'key_at': ['tx', 'ty', 'tz']}, 'y': {'color': (1, 0.8, 0), 'rot_order': 0, 'axis': [0.0] * 3, 'skip': ['x', 'z'], 'key_at': ['tx', 'ty', 'tz']}, 'xyz': {'color': (1, 0.8, 0), 'rot_order': 0, 'axis': [0.0] * 3, 'skip': [], 'key_at': ['tx', 'ty', 'tz']}}}
        self.groups = {'main': 'overlap_grp', 'editable': 'editable_loc_grp', 'origin': 'origin_loc_grp', 'result': 'result_loc_grp'}
        self.loc_names = {'follow': '_loc_follow', 'result': '_loc_result', 'animate': '_loc_animate', 'origin': '_loc_origin'}
        self.del_prefix()
        self.prefix = _r._PREFIX
        self.groups = dict(_r._GROUPS)

    def del_prefix(self):
        _r.clear_transients()

    def set_locator_hierarchy(self, loc_follow, loc_dest, loc_nucleus):
        _r.require_active()
        [cmds.group(n=self.groups[i], em=1) for i in list(self.groups) if not cmds.objExists(self.groups[i])]
        [cmds.setAttr(self.groups[i] + '.translate', lock=1) for i in list(self.groups) if cmds.objExists(self.groups[i])]
        [cmds.setAttr(self.groups[i] + '.rotate', lock=1) for i in list(self.groups) if cmds.objExists(self.groups[i])]
        [cmds.setAttr(self.groups[i] + '.scale', lock=1) for i in list(self.groups) if cmds.objExists(self.groups[i])]
        [cmds.parent(self.groups[i], self.groups['main']) for i in list(self.groups) if not i == 'main' and (not cmds.listRelatives(self.groups[i], ap=1) != None)]
        cmds.parent(loc_follow, self.groups['result'])
        cmds.parent(loc_dest, self.groups['origin'])
        cmds.parent(loc_nucleus, self.groups['editable'])
        self.update_groups()

    def remove_locator_hierarchy(self, obj):
        _r.require_active()
        del_ls = cmds.ls([_r.helper_name(obj, self.loc_names['animate']), _r.helper_name(obj, self.loc_names['follow']), _r.helper_name(obj, self.loc_names['result']), _r.helper_name(obj, self.loc_names['origin'])])
        cmds.delete(del_ls)

    def update_groups(self):
        _r.require_active()
        sub_groups = [self.groups[i] for i in self.groups if i != 'main']
        for grp in sub_groups:
            if cmds.listRelatives(grp, children=1) == None:
                cmds.delete(grp)
        if cmds.listRelatives(self.groups['main'], children=1) == None:
            cmds.delete(self.groups['main'])

    @_r.business_bridge('create')
    def kf_overlap(self, param):
        """
        :param param: ui parameter
        :return: overlap
        """
        self.del_prefix()
        is_playing = cmds.play(q=1, st=1)
        if is_playing:
            cmds.play(st=0)
        param['select_ls'] = [i for i in param['select_ls'] if not self.groups['main'] in i]
        cur_time = cmds.currentTime(q=1)
        timeline = scene.get_timeline()
        min_time, max_time = [timeline[0] - self.pre_post_roll, timeline[0] + self.pre_post_roll]
        cmds.currentTime(timeline[0])
        at = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        axis_name = param['mode_name'].split('_')[-1][:-1]
        mode_name = 'rotation' if 'aim_' in param['mode_name'] else 'position'
        mode_param = self.modes['rotation'] if 'aim_' in param['mode_name'] else self.modes['position']
        mode_param = mode_param[axis_name]
        direction = [i * param['distance'] for i in mode_param['axis']]
        axis = mode_param['axis']
        if param['aim_invert']:
            direction = [i * -1 for i in direction]
            axis = [i * -1 for i in axis]
        for obj in param['select_ls']:
            short_name = obj
            for n in self.loc_names:
                if cmds.objExists(_r.helper_name(short_name, self.loc_names[n])):
                    cmds.delete(_r.helper_name(short_name, self.loc_names[n]))
            loc_follow = util.get_space_locator(name=_r.helper_name(short_name, self.loc_names['follow']))
            loc_scale = [abs(i) for i in direction] if mode_name == 'rotation' else util.get_object_size(obj)
            loc_dest = util.get_space_locator(name=_r.helper_name(short_name, self.loc_names['origin']), color=[0.07, 0.07, 0.07], scale=loc_scale)
            loc_result = util.get_space_locator(name=_r.helper_name(short_name, self.loc_names['result']), color=mode_param['color'], scale=loc_scale, position=direction)
            cmds.setAttr(loc_follow + '.rotateOrder', mode_param['rot_order'])
            cmds.setAttr(loc_result + '.rotateOrder', mode_param['rot_order'])
            cmds.setAttr(loc_result + '.displayLocalAxis', 1)
            cmds.parent(loc_dest, loc_follow)
            cmds.parent(loc_result, loc_follow)
            if mode_name == 'rotation':
                util.match_transform(loc_follow, obj)
            elif mode_name == 'position':
                util.match_transform(loc_follow, obj, is_rot=False)
            if mode_name == 'rotation':
                follow_con = cmds.parentConstraint(obj, loc_follow, mo=0)[0]
                cmds.setAttr(follow_con + '.interpType', 0)
            elif mode_name == 'position':
                follow_con = cmds.pointConstraint(obj, loc_follow, mo=0)[0]
            if mode_name == 'rotation':
                cmds.xform(loc_dest, t=direction, r=1)
                cmds.parent(loc_dest, world=1)
            elif mode_name == 'position':
                cmds.parent(loc_dest, world=1)
            if mode_name == 'rotation':
                dest_con = cmds.parentConstraint(loc_follow, loc_dest, mo=1)[0]
                cmds.setAttr(dest_con + '.interpType', 0)
            elif mode_name == 'position':
                dest_con = cmds.pointConstraint(loc_follow, loc_dest, mo=0)[0]
            cmds.refresh(suspend=1)
            cmds.bakeResults(loc_dest, simulation=1, sampleBy=1, disableImplicitControl=1, preserveOutsideKeys=0, sparseAnimCurveBake=0, t=(timeline[0] - self.pre_post_roll, timeline[-1] + self.pre_post_roll), at=at, minimizeRotation=1)
            cmds.refresh(suspend=0)
            cmds.delete([dest_con])
            goal_weight = 1.0 - param['dynamic'] / 5.0 * 0.5
            print('convert dynamic {} to weight {}'.format(param['dynamic'], goal_weight))
            loc_nucleus_scale = [max(loc_scale) * 0.1] * 3 if mode_name == 'rotation' else loc_scale
            loc_nucleus = util.get_space_locator(name=_r.helper_name(short_name, self.loc_names['animate']), color=[1.0, 0.0, 0.0], scale=loc_nucleus_scale)
            n_particle = cmds.particle(name=self.prefix + '_particle', p=[(0, 0, 0)])[0]
            util.match_transform(n_particle, loc_dest)
            util.match_transform(loc_nucleus, loc_dest)
            n_goal = cmds.particle(name=self.prefix + '_loc_goal')[0]
            cmds.goal(n_particle, w=goal_weight, utr=0, g=loc_dest)
            n_particle_shp = cmds.listRelatives(n_particle, shapes=1, f=1)[0]
            cmds.connectAttr(n_particle_shp + '.worldCentroid', loc_nucleus + '.translate', force=1)
            fps = scene.get_fps()
            goal_smoothness = 3.2 if param['smoothness'] else 2.7
            cmds.setAttr(n_particle_shp + '.goalSmoothness', goal_smoothness)
            cmds.setAttr(n_particle_shp + '.startFrame', timeline[0])
            bake_sample = max(1, round(2.0 * (fps / 24.0)) if param['smoothness'] else round(1.0 * (fps / 24.0)))
            print('simulation result fps: {}, goal_sm: {}, sample: {}'.format(fps, goal_smoothness, bake_sample))
            cmds.refresh(suspend=1)
            cmds.bakeResults(loc_nucleus, simulation=1, sampleBy=bake_sample, disableImplicitControl=1, preserveOutsideKeys=0, sparseAnimCurveBake=0, t=(timeline[0] - self.pre_post_roll, timeline[-1] + self.pre_post_roll), at=at, oversamplingRate=1, minimizeRotation=1)
            cmds.refresh(suspend=0)
            cmds.delete(cmds.ls([self.prefix + '_particle' + '*', self.prefix + '_loc_goal' + '*']))
            if mode_name == 'rotation':
                cmds.keyframe(loc_nucleus, e=1, iub=1, r=1, o='over', tc=param['offset'])
            elif mode_name == 'position':
                cmds.keyframe(loc_nucleus, e=1, iub=1, r=1, o='over', tc=param['offset'], at=['t' + i for i in ['x', 'y', 'z'] if i not in mode_param['skip']])
            if mode_name == 'rotation':
                result_con = cmds.aimConstraint(loc_nucleus, loc_result, mo=1, aimVector=axis, worldUpType='object')[0]
            elif mode_name == 'position':
                result_con = cmds.pointConstraint(loc_nucleus, loc_result, mo=0, skip=mode_param['skip'])[0]
            cmds.refresh(suspend=1)
            cmds.bakeResults(loc_follow, simulation=1, sampleBy=1, disableImplicitControl=1, preserveOutsideKeys=0, sparseAnimCurveBake=0, t=(timeline[0] - self.pre_post_roll, timeline[-1] + self.pre_post_roll), at=at, oversamplingRate=1, minimizeRotation=1)
            cmds.refresh(suspend=0)
            cmds.delete(cmds.ls([follow_con]))
            for t in [timeline[1], timeline[0]]:
                cmds.currentTime(t)
                if mode_name == 'rotation':
                    cmds.setKeyframe(obj, t=(t,), at=mode_param['key_at'])
                elif mode_name == 'position':
                    cmds.setKeyframe(obj, t=(t,), at=mode_param['key_at'])
            exists_con = cmds.listRelatives(obj, typ='constraint')
            if exists_con != None:
                cmds.delete(exists_con)
            if mode_name == 'rotation':
                obj_con = cmds.orientConstraint(loc_result, obj, mo=0, skip=mode_param['skip'])[0]
                cmds.setAttr(obj_con + '.interpType', 0)
            elif mode_name == 'position':
                obj_con = cmds.pointConstraint(loc_result, obj, mo=0, skip=mode_param['skip'])[0]
            self.set_locator_hierarchy(loc_follow, loc_dest, loc_nucleus)
            self.update_groups()
        '----------------'
        '----------------'
        cmds.select(param['select_ls'])
        cmds.currentTime(cur_time)
        if is_playing:
            cmds.play(st=1)

    @_r.business_bridge('bake')
    def kf_bake_animation(self, param):

        def get_attr_tc(ac_ls, timeline):
            data = {}
            for ac in ac_ls:
                tc = cmds.keyframe(ac, q=1, tc=1)
                if tc == None:
                    tc = timeline
                else:
                    tc = [timeline[0]] + [i for i in tc if i > timeline[0] and i < timeline[1]] + [timeline[1]]
                tc = sorted(list(set([float(i) for i in tc])))
                data[ac] = tc
            return data
        if param['select_ls'] == []:
            return None
        sn_ls = [cmds.ls(i, sn=1)[0] for i in param['select_ls']]
        sn_ls = [i for i in sn_ls if cmds.objExists(_r.helper_name(i, self.loc_names['follow']))]
        "\n        # attributes is selected by modes\n        at = []\n        if cmds.listRelatives(sn_ls, typ='orientConstraint', f=0) != None:\n            at += ['rx', 'ry', 'rz']\n        if cmds.listRelatives(sn_ls, typ='pointConstraint', f=0) != None:\n            at += ['tx', 'ty', 'tz']\n        "
        rot_at_ls, pos_at_ls = [[], []]
        for sn in sn_ls:
            for at in ['rx', 'ry', 'rz']:
                rot_at_ls += [sn + '.' + at] if cmds.listConnections(sn + '.' + at, type='pairBlend') != None else []
            for at in ['tx', 'ty', 'tz']:
                pos_at_ls += [sn + '.' + at] if cmds.listConnections(sn + '.' + at, type='pairBlend') != None else []
        rot_at_ls = list(set(rot_at_ls))
        pos_at_ls = list(set(pos_at_ls))
        at_ls = rot_at_ls + pos_at_ls
        timeline = scene.get_timeline()
        min_time, max_time = [timeline[0] - self.pre_post_roll, timeline[1] + self.pre_post_roll]
        ac_ls = cmds.keyframe(at_ls, q=1, n=1)
        orig_attr_tc = get_attr_tc(at_ls, timeline)
        cmds.refresh(suspend=1)
        cmds.bakeResults(at_ls, simulation=1, sampleBy=1, disableImplicitControl=1, preserveOutsideKeys=0, sparseAnimCurveBake=0, t=(timeline[0], timeline[1]), oversamplingRate=1, minimizeRotation=1)
        cmds.refresh(suspend=0)
        ac_ls = cmds.keyframe(at_ls, q=1, n=1)
        tc = []
        for i in orig_attr_tc:
            tc += orig_attr_tc[i]
        tc = sorted(list(set(tc)))
        for obj in sn_ls:
            self.remove_locator_hierarchy(obj)
            self.update_groups()
        fps = scene.get_fps()
        sample_target = 3 * (fps / 24)
        for ac in ac_ls:
            key_total = max(tc) - min(tc) + 1.0
            key_n = int(round(key_total / sample_target)) - len(tc)
            print(ac, key_total, key_n)
            self.keyframe_optimizer(ac, tc, key_n)

    def keyframe_optimizer(self, ac, tc, n, breakdown=False):
        _r.require_active()

        def linspace(start, stop, num):
            if num - 1 == 0.0:
                step = 0.0
            else:
                step = (stop - start) / (num - 1)
            return [start + step * i for i in range(num)]
        tc_orig = tc
        tc = sorted([int(round(i)) for i in tc])

        def get_imp_between(tc):
            tc_window_ls = [tc[i:i + 2] for i in range(len(tc)) if len(tc[i:i + 2]) == 2]
            diff_win_ls = []
            len_win_ls = []
            tc_win_pass_ls = []
            for tc_win in list(tc_window_ls):
                if len(tc_window_ls) == len(tc_win_pass_ls):
                    tc_win_pass_ls = []
                if not tc_win in tc_win_pass_ls:
                    tc_win_pass_ls += [tc_win]
                else:
                    continue
                tc_ls = range(tc_win[0], tc_win[1] + 1)
                vc_ls = [round(cmds.keyframe(ac, q=1, eval=1, t=(i,))[0], 4) for i in tc_ls]
                len_win_ls.append(len(tc_ls))
                lin_vc_ls = linspace(vc_ls[0], vc_ls[-1], len(vc_ls))
                diff_vc_ls = [abs(vc_ls[i] - lin_vc_ls[i]) for i in range(len(tc_ls))]
                max_idx = diff_vc_ls.index(max(diff_vc_ls))
                diff_win_ls.append([diff_vc_ls[max_idx], tc_ls[max_idx]])
            diff_win_ls = sorted(diff_win_ls)
            data = {'error': round(diff_win_ls[-1][0], 3), 'frame': diff_win_ls[-1][1], 'win_avg': round(sum(len_win_ls) / float(len(len_win_ls)), 2), 'tc_length': len(tc)}
            return data
        for i in range(n):
            new_breakdown = get_imp_between(tc)
            if i == max(range(n)):
                print(i, new_breakdown)
            tc.append(new_breakdown['frame'])
            tc = sorted(tc)
        print(tc)
        tc_ls = range(tc[0], tc[-1] + 1)
        cmds.keyframe(ac, e=1, breakdown=1)
        [cmds.cutKey(ac, t=(i,)) for i in tc_ls if not i in tc]
        [cmds.keyframe(ac, e=1, breakdown=0, t=(i,)) for i in tc_ls if i in tc_orig]
        if not breakdown:
            cmds.keyframe(ac, e=1, breakdown=0)

class kf_overlap:

    def __init__(self):
        self.version = 2.0
        self.win_id = 'KF_OVERLAP'
        self.dock_id = self.win_id + '_DOCK'
        self.win_width = 280
        self.win_title = 'KF Overlap  -  v.{} ( alpha )'.format(self.version)
        self.color = {'bg': (0.21, 0.21, 0.21), 'red': (0.98, 0.374, 0), 'green': (0.7067, 1, 0), 'blue': (0.1, 0.6, 0.9), 'yellow': (1, 0.8, 0), 'shadow': (0.15, 0.15, 0.15), 'highlight': (0.3, 0.3, 0.3)}
        self.element = {}
        self.user_original, self.user_latest = ['$usr_orig$', None]
        import getpass
        if 'usr_orig' in self.user_original:
            self.user_original = getpass.getuser()
        self.user_latest = getpass.getuser()
        self.usr_data = None
        self.is_connected = False
        self.mode_bt_dict = {'aim_xb': ['aimxb_st', 'red'], 'aim_yb': ['aimyb_st', 'green'], 'aim_zb': ['aimzb_st', 'blue'], 'aim_ib': ['aimib_st', 'yellow'], 'pos_xzb': ['posxzb_st', 'yellow'], 'pos_yb': ['posyb_st', 'yellow'], 'pos_xyzb': ['posxyzb_st', 'yellow']}
        self.mode_current = list(self.mode_bt_dict)[0]
        self.is_aim_invert = False
        self.is_smoothness = True
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.update_usr_cfg()
        self.support()
        self.preset_dir = self.base_path + os.sep + 'presets'
        self.lds = _r.UIBridge()
        self.win_id = 'mtbKeyframeOverlap'
        self.dock_id = self.win_id + '_DOCK'
    '======================='
    '======================='

    def get_captured_param(self):
        data = {}
        data['smoothness'] = self.is_smoothness
        data['mode_name'] = self.mode_current
        data['aim_invert'] = self.is_aim_invert
        try:
            data['mode_transform'] = cmds.optionMenu(self.element['mode_om'], q=1, v=1)
            data['distance'] = round(cmds.floatSlider(self.element['distance_fs'], q=1, v=1), 3)
            data['dynamic'] = cmds.floatSlider(self.element['dynamic_fs'], q=1, v=1)
            data['offset'] = round(cmds.floatSlider(self.element['offset_fs'], q=1, v=1), 3)
        except:
            data['mode_transform'] = 'Rotation'
            data['distance'] = 3.0
            data['dynamic'] = 3
            data['offset'] = 0.0
        return data

    def save_preset(self):
        return _r.preset(self, 'save_preset')

    def load_preset(self):
        return _r.preset(self, 'load_preset')

    def rename_preset(self):
        return _r.preset(self, 'rename_preset')

    def delete_preset(self):
        return _r.preset(self, 'delete_preset')

    def field_to_slider(self):
        distance_v = cmds.floatField(self.element['distance_ff'], q=1, v=1)
        dynamic_v = cmds.floatField(self.element['dynamic_ff'], q=1, v=1)
        offset_v = cmds.floatField(self.element['offset_ff'], q=1, v=1)
        cmds.floatSlider(self.element['distance_fs'], e=1, v=distance_v)
        cmds.floatSlider(self.element['dynamic_fs'], e=1, v=dynamic_v)
        cmds.floatSlider(self.element['offset_fs'], e=1, v=offset_v)

    def exec_script(self, exec_name=''):
        param = self.get_captured_param()
        param['select_ls'] = cmds.ls(long=True, selection=True) or []
        return self.lds.kf_overlap(param) if exec_name == 'overlap' else self.lds.kf_bake_animation(param)
    '======================='
    '======================='

    def update_usr_cfg(self):
        self.cfg_data = self.get_captured_param()
        self.usr_data = {'user_orig': self.user_original, 'user_last': self.user_latest}
        self._presets = getattr(self, '_presets', {})

    def support(self):
        self.is_connected = False
    '======================='
    '======================='

    def init_win(self):
        if cmds.window(self.win_id, exists=1):
            cmds.deleteUI(self.win_id)
        cmds.window(self.win_id, t=self.win_title, menuBar=1, rtf=1, nde=1, w=self.win_width, sizeable=1, h=10, retain=0, bgc=self.color['bg'])

    def win_layout(self):

        def divider_block(text, al_idx=1):
            cmds.text(l='', fn='smallPlainLabelFont', al='center', h=10, w=self.win_width)
            cmds.text(l=' {} '.format(text), fn='smallPlainLabelFont', al=['left', 'center', 'right'][al_idx], w=self.win_width, bgc=self.color['highlight'])
            cmds.text(l='', fn='smallPlainLabelFont', al='center', h=10, w=self.win_width)
        "\n        cmds.menuBarLayout()\n        cmds.menu(label='Menu')\n        cmds.menuItem(divider=1, dividerLabel='selection')\n        cmds.menuItem(label='Latest selections', c='')\n        cmds.menuItem(label='All overlaped objects', c='')\n        cmds.menuItem(divider=1, dividerLabel='automation')\n        cmds.menuItem(label='Save selected instant overlap', c='')\n        cmds.menuItem(divider=1, dividerLabel='clean up scene')\n        cmds.menuItem(label='Cleanup', c='')\n        cmds.menuItem(divider=1, dividerLabel='about')\n        cmds.menuItem(label='Update version', c='')\n        licenseMItem = cmds.menuItem(label='Activate license key')\n        "
        cmds.columnLayout(adj=1, w=self.win_width)
        cmds.text(l='{}'.format(self.win_title), al='center', fn='boldLabelFont', bgc=self.color['yellow'], h=15)
        divider_block('PRESET', 1)
        self.element['preset_col'] = cmds.columnLayout(adj=1, w=self.win_width)
        self.element['preset_om'] = cmds.optionMenu(label='  Preset : ', bgc=self.color['shadow'], h=20)
        cmds.menuItem(label='preset_item')
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfColumns=3, w=self.win_width)
        self.element['save_ps_bt'] = cmds.button(label='Save', bgc=self.color['bg'], w=self.win_width * 0.33, c=lambda arg: util.return_none_func())
        self.element['rename_ps_bt'] = cmds.button(label='Rename', bgc=self.color['bg'], w=self.win_width * 0.33, c=lambda arg: util.return_none_func())
        self.element['del_ps_bt'] = cmds.button(label='Delete', bgc=self.color['bg'], w=self.win_width * 0.33, c=lambda arg: util.return_none_func())
        cmds.setParent('..')
        divider_block('QUICK OVERLAPING', 1)
        self.element['mode_om'] = cmds.optionMenu(label='  Mode : ', bgc=self.color['shadow'])
        cmds.menuItem(label='Rotation')
        cmds.menuItem(label='Position')
        cmds.text(l='', al='center', fn='boldLabelFont', bgc=self.color['bg'], h=5)
        self.element['mode_bt_grid'] = cmds.gridLayout(cellHeight=23)
        cmds.setParent('..')
        self.element['mode_vis_grid'] = cmds.gridLayout(cellHeight=4)
        cmds.setParent('..')
        cmds.text(l='', al='center', fn='boldLabelFont', bgc=self.color['bg'], h=7)
        cmds.rowColumnLayout(numberOfColumns=3, w=self.win_width)
        cmds.text(l='Farness :', w=self.win_width * 0.25, fn='smallFixedWidthFont', al='right')
        self.element['distance_ff'] = cmds.floatField(editable=True, value=1, pre=1, max=500, w=self.win_width * 0.14)
        cmds.columnLayout()
        cmds.text(l='{0} {2}  {1}'.format('Near', 'Far', ' ' * 5), fn='smallFixedWidthFont', w=self.win_width * 0.6, h=12)
        self.element['distance_fs'] = cmds.floatSlider(min=0, max=500, value=2, w=self.win_width * 0.56)
        cmds.setParent('..')
        cmds.text(l='Dynamic :', w=self.win_width * 0.25, fn='smallFixedWidthFont', al='right')
        self.element['dynamic_ff'] = cmds.floatField(editable=1, value=3, pre=2, w=self.win_width * 0.14)
        cmds.columnLayout()
        cmds.text(l='{0}  {2}  {1}'.format('Stedy', 'Sway', ' ' * 5), fn='smallFixedWidthFont', w=self.win_width * 0.6, h=12)
        self.element['dynamic_fs'] = cmds.floatSlider(minValue=0, maxValue=6, value=3, w=self.win_width * 0.56)
        cmds.setParent('..')
        cmds.text(l='Shift :', w=self.win_width * 0.25, fn='smallFixedWidthFont', al='right')
        self.element['offset_ff'] = cmds.floatField(editable=1, value=0, pre=1, min=-10, max=10, w=self.win_width * 0.14)
        cmds.columnLayout()
        cmds.text(l='{0}  {2}  {1}'.format('Lead', 'Follow', ' ' * 4), fn='smallFixedWidthFont', w=self.win_width * 0.6, h=12)
        self.element['offset_fs'] = cmds.floatSlider(minValue=-5, maxValue=5, value=0, w=self.win_width * 0.56)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfColumns=3, w=self.win_width)
        cmds.text(l='Smooth :', w=self.win_width * 0.25, fn='smallFixedWidthFont', al='right')
        self.element['sm_if'] = cmds.intField(editable=0, value=0, min=0, max=1, w=self.win_width * 0.1, vis=0)
        cmds.rowColumnLayout(numberOfColumns=3)
        cmds.text(l='', w=self.win_width * 0.07)
        self.element['sm_bt'] = cmds.button(label='True', bgc=self.color['bg'], w=self.win_width * 0.1, h=20)
        cmds.text(l='  Smoothness', fn='smallFixedWidthFont', w=self.win_width * 0.4, al='left')
        cmds.setParent('..')
        cmds.text(l='Frame R :', w=self.win_width * 0.25, fn='smallFixedWidthFont', al='right')
        self.element['fps_ff'] = cmds.floatField(editable=0, value=0, w=self.win_width * 0.1, vis=0)
        self.element['fps_tx'] = cmds.text(l='24', bgc=self.color['bg'], w=self.win_width * 0.6, h=20)
        cmds.setParent('..')
        cmds.text(l='', al='center', fn='boldLabelFont', bgc=self.color['bg'], h=10)
        self.element['overlap_bt'] = cmds.button(label='Create Overlap', bgc=self.color['bg'], w=self.win_width * 0.6, h=20, c=lambda arg: util.return_none_func())
        divider_block('BAKE ANIMATION', 1)
        self.element['bake_anim_bt'] = cmds.button(label='Bake Keyframe', bgc=self.color['bg'], w=self.win_width * 0.6, h=20, c=lambda arg: util.return_none_func())
        cmds.text(l='', al='center', fn='boldLabelFont', bgc=self.color['shadow'], h=5)
        cmds.text(l='(c) dex3d.gumroad.com', al='center', fn='smallPlainLabelFont', bgc=self.color['bg'], h=15)
        '======================='
        '======================='
        "\n        for c in list(self.color):\n            cmds.text(l='', fn='smallPlainLabelFont', al='center', h=5, w=10, bgc=self.color[c])\n        "
        '======================='
        '======================='
        if cmds.about(connected=1) or self.user_original == self.user_latest:
            self.init_layout_func()

    def init_layout_func(self):
        cmds.optionMenu(self.element['preset_om'], e=1, cc=lambda arg: self.load_preset())
        cmds.optionMenu(self.element['mode_om'], e=1, cc=lambda arg: self.update_ui())
        cmds.button(self.element['bake_anim_bt'], e=1, bgc=self.color['yellow'])
        cmds.button(self.element['overlap_bt'], e=1, bgc=self.color['yellow'])
        cmds.button(self.element['save_ps_bt'], e=1, c=lambda arg: self.save_preset())
        cmds.button(self.element['rename_ps_bt'], e=1, c=lambda arg: self.rename_preset())
        cmds.button(self.element['del_ps_bt'], e=1, c=lambda arg: self.delete_preset())
        cmds.floatSlider(self.element['distance_fs'], e=1, dc=lambda arg: self.update_ui(slider=True))
        cmds.floatSlider(self.element['dynamic_fs'], e=1, dc=lambda arg: self.update_ui(slider=True))
        cmds.floatSlider(self.element['offset_fs'], e=1, dc=lambda arg: self.update_ui(slider=True))
        cmds.floatField(self.element['distance_ff'], e=1, cc=lambda arg: self.field_to_slider())
        cmds.floatField(self.element['dynamic_ff'], e=1, cc=lambda arg: self.field_to_slider())
        cmds.floatField(self.element['offset_ff'], e=1, cc=lambda arg: self.field_to_slider())
        cmds.button(self.element['overlap_bt'], e=1, c=lambda arg: self.exec_script(exec_name='overlap'))
        cmds.button(self.element['bake_anim_bt'], e=1, c=lambda arg: self.exec_script(exec_name='bake_anim'))

    def show_win(self):
        cmds.showWindow(self.win_id)

    def init_dock(self):
        if cmds.dockControl(self.dock_id, q=1, ex=1):
            cmds.deleteUI(self.dock_id)
        cmds.dockControl(self.dock_id, area='left', fl=1, content=self.win_id, allowedArea=['left', 'right'], sizeable=0, width=self.win_width, label=self.win_title)

    def show_ui(self):
        self.init_win()
        self.win_layout()
        self.show_win()
        self.init_dock()
        self.update_ui()
        self.update_ui(slider=True)
        if self.user_original != self.user_latest:
            cmds.deleteUI(self.win_id)

    def update_ui(self, slider=False):

        def slider_to_field():
            distance_v = cmds.floatSlider(self.element['distance_fs'], q=1, v=1)
            dynamic_v = cmds.floatSlider(self.element['dynamic_fs'], q=1, v=1)
            offset_v = cmds.floatSlider(self.element['offset_fs'], q=1, v=1)
            cmds.floatField(self.element['distance_ff'], e=1, v=distance_v)
            cmds.floatField(self.element['dynamic_ff'], e=1, v=dynamic_v)
            cmds.floatField(self.element['offset_ff'], e=1, v=offset_v)

        def reload_preset_name():
            preset_name = cmds.optionMenu(self.element['preset_om'], q=True, v=True)
            for item in cmds.optionMenu(self.element['preset_om'], q=True, ils=True) or []:
                cmds.deleteUI(item)
            cmds.menuItem(parent=self.element['preset_om'], label='Defualt')
            for name in sorted(self._presets):
                cmds.menuItem(parent=self.element['preset_om'], label=name)
            if preset_name in self._presets:
                cmds.optionMenu(self.element['preset_om'], e=True, v=preset_name)

        def toggle_smoothness():
            self.is_smoothness = not self.is_smoothness
            smooth_bt_ui()

        def toggle_aim_invert():
            self.is_aim_invert = not self.is_aim_invert
            mode_ui()

        def set_mode_current(mode_name):
            self.mode_current = mode_name
            mode_ui()

        def fps_ui():
            cmds.text(self.element['fps_tx'], e=1, l=str(scene.get_fps()))
            fps = float(cmds.text(self.element['fps_tx'], q=1, l=1))
            cmds.floatField(self.element['fps_ff'], e=1, v=fps)

        def smooth_bt_ui():
            if self.is_smoothness:
                cmds.button(self.element['sm_bt'], e=1, l='', bgc=self.color['green'])
            else:
                cmds.button(self.element['sm_bt'], e=1, l='', bgc=self.color['shadow'])
            cmds.button(self.element['sm_bt'], e=1, c=lambda arg: toggle_smoothness())
            cmds.intField(self.element['sm_if'], e=1, value=int(self.is_smoothness))

        def mode_ui():
            if cmds.optionMenu(self.element['mode_om'], q=1, v=1) == 'Rotation':
                self.mode_current = 'aim_yb' if not 'aim' in self.mode_current else self.mode_current
            elif cmds.optionMenu(self.element['mode_om'], q=1, v=1) == 'Position':
                self.mode_current = 'pos_xyzb' if not 'pos' in self.mode_current else self.mode_current
            for n in cmds.gridLayout(self.element['mode_bt_grid'], q=1, ca=1) or []:
                cmds.deleteUI(n)
            cmds.setParent(self.element['mode_bt_grid'])
            if cmds.optionMenu(self.element['mode_om'], q=1, v=1) == 'Rotation':
                cmds.gridLayout(self.element['mode_bt_grid'], e=1, numberOfColumns=4, cellWidth=self.win_width / 4)
                self.element['aim_xb'] = cmds.button(l='X', c=lambda arg: set_mode_current('aim_xb'), bgc=self.color['highlight'])
                self.element['aim_yb'] = cmds.button(l='Y', c=lambda arg: set_mode_current('aim_yb'), bgc=self.color['highlight'])
                self.element['aim_zb'] = cmds.button(l='Z', c=lambda arg: set_mode_current('aim_zb'), bgc=self.color['highlight'])
                self.element['aim_ib'] = cmds.button(l='Invert', c=lambda arg: toggle_aim_invert(), bgc=self.color['highlight'])
            elif cmds.optionMenu(self.element['mode_om'], q=1, v=1) == 'Position':
                cmds.gridLayout(self.element['mode_bt_grid'], e=1, numberOfColumns=3, cellWidth=self.win_width / 3)
                self.element['pos_xzb'] = cmds.button(l='XZ', c=lambda arg: set_mode_current('pos_xzb'), bgc=self.color['highlight'])
                self.element['pos_yb'] = cmds.button(l='Y', c=lambda arg: set_mode_current('pos_yb'), bgc=self.color['highlight'])
                self.element['pos_xyzb'] = cmds.button(l='XYZ', c=lambda arg: set_mode_current('pos_xyzb'), bgc=self.color['highlight'])
            for n in cmds.gridLayout(self.element['mode_vis_grid'], q=1, ca=1) or []:
                cmds.deleteUI(n)
            cmds.setParent(self.element['mode_vis_grid'])
            if cmds.optionMenu(self.element['mode_om'], q=1, v=1) == 'Rotation':
                cmds.gridLayout(self.element['mode_vis_grid'], e=1, numberOfColumns=4, cellWidth=self.win_width / 4)
                self.element['aimxb_st'] = cmds.text(l='', bgc=self.color['shadow'])
                self.element['aimyb_st'] = cmds.text(l='', bgc=self.color['shadow'])
                self.element['aimzb_st'] = cmds.text(l='', bgc=self.color['shadow'])
                self.element['aimib_st'] = cmds.text(l='', bgc=self.color['shadow'])
            elif cmds.optionMenu(self.element['mode_om'], q=1, v=1) == 'Position':
                cmds.gridLayout(self.element['mode_vis_grid'], e=1, numberOfColumns=3, cellWidth=self.win_width / 3)
                self.element['posxzb_st'] = cmds.text(l='', bgc=self.color['shadow'])
                self.element['posyb_st'] = cmds.text(l='', bgc=self.color['shadow'])
                self.element['posxyzb_st'] = cmds.text(l='', bgc=self.color['shadow'])
            for n in list(self.mode_bt_dict):
                if self.mode_current == n and cmds.button(self.element[n], q=1, ex=1):
                    cmds.text(self.element[self.mode_bt_dict[n][0]], e=1, bgc=self.color[self.mode_bt_dict[n][1]])
                    cmds.button(self.element[n], e=1, bgc=self.color['shadow'])
                    break
            if self.is_aim_invert and cmds.button(self.element['aim_ib'], q=1, ex=1):
                cmds.text(self.element[self.mode_bt_dict['aim_ib'][0]], e=1, bgc=self.color[self.mode_bt_dict['aim_ib'][1]])
                cmds.button(self.element['aim_ib'], e=1, bgc=self.color['shadow'])
        if slider:
            slider_to_field()
        else:
            mode_ui()
            fps_ui()
            smooth_bt_ui()
            reload_preset_name()
