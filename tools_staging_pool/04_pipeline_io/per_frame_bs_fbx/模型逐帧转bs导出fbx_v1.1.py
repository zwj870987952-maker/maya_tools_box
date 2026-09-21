import pymel.core as pm
import maya.cmds as cmds

'''
1.复制脚本到maya  python标签栏中
2.设置好时间轴上的开始帧，结束帧
3.选中要导出的模型组
4.执行脚本
5.选中大纲中新生成的模型组导出fbx文件
'''

sel_mod_grp = pm.selected()[0]
start_time = pm.playbackOptions(q=1, min=1)
end_time = pm.playbackOptions(q=1, max=1)

try:
    sel_mod_grp_name = sel_mod_grp.split(':')[-1]
except:
    sel_mod_grp_name = '{}'.format(sel_mod_grp)

if not pm.objExists('{}_FbxExpGrp'.format(sel_mod_grp_name)):
    pm.select(cl=1)
    root_FbxExpGrp = pm.group(n='{}_FbxExpGrp'.format(sel_mod_grp_name))
    base_bs_grp = pm.duplicate(sel_mod_grp,n='{}_exp'.format(sel_mod_grp_name))[0]
    pm.select(base_bs_grp)
    base_bs_node = pm.blendShape(automatic=1,n='{}_ani_bs'.format(sel_mod_grp_name))[0]
    base_bs_node.origin.set(0)
    pm.parent(base_bs_grp, root_FbxExpGrp)
    pm.select(cl=1)
    root_joint = pm.joint(n='{}_ExpRootJoint'.format(sel_mod_grp_name))
    pm.parent(root_joint, root_FbxExpGrp)
    pm.select(root_joint, base_bs_grp)
    cmds.SmoothBindSkin()
    
time_num = end_time - start_time
# pm.modelEditor('modelPanel5', e=1, allObjects=0)
for each in range(int(time_num+1)):
    currentTime = start_time + each
    pm.setCurrentTime(currentTime)
    pm.setKeyframe(root_joint)
    temp_mod_grp = pm.duplicate(sel_mod_grp, n='{}_Frame_{}'.format(sel_mod_grp_name, start_time+each))[0]
    mel_cc = 'blendShape -e -t {} {} {} 1 {};'.format(base_bs_grp, each, temp_mod_grp, base_bs_node)
    pm.mel.eval(mel_cc)
    
    pm.setCurrentTime(currentTime-1)
    pm.PyNode('{}.{}'.format(base_bs_node, temp_mod_grp)).set(0)
    pm.setKeyframe('{}.{}'.format(base_bs_node, temp_mod_grp))
    pm.setCurrentTime(currentTime)
    pm.PyNode('{}.{}'.format(base_bs_node, temp_mod_grp)).set(1)
    pm.setKeyframe('{}.{}'.format(base_bs_node, temp_mod_grp))
    pm.setCurrentTime(currentTime+1)
    pm.PyNode('{}.{}'.format(base_bs_node, temp_mod_grp)).set(0)
    pm.setKeyframe('{}.{}'.format(base_bs_node, temp_mod_grp))
    pm.delete(temp_mod_grp)
    
# pm.modelEditor('modelPanel5', e=1, allObjects=1)



