import pymel.core as pm

# 按顺序选骨骼
joint_list = pm.selected()

# 按顺序选模型
mod_list = pm.selected()

for i,each in enumerate(joint_list):
    mod = mod_list[i]
    pm.select(each, mod)
    pm.skinCluster(tsb=1)