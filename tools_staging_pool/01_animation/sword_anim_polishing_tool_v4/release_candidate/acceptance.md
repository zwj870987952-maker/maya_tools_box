# Sword Anim Polishing Maya 验收

真实 GUI、Parent In/Aim/Sword/Reverse、完整Arc均not_run。本机隔离Maya只验证完整过程编译、数值权重、native Bake/Euler、motionPath子过程、UUID与Undo，不冒充完整交互通过。原许可不许修改或分发，完整九文件原字节保留。

1. 备份武器rig，确认本地原包使用授权，candidate launcher load_tool().show_ui()打开。检查所有原工作方式、group快选、knots/show source/size/start/end、帮助文本及重开。不同原MEL版本必须重启；不同时开启原UI/另一候选会话。若显式原UI对照，使用备份prefs，原入口会改matrixNodes autoload。
2. 对weapon或多控制器Parent In，比较原版外部locator与最后对象层级动画、帧区间、约束回源和Euler。dry_run不改节点/键/选择/时间/Undo；引用/锁/同短名/共享或外部driver应拒绝。
3. Aim创建每对象Top/Side后分别移动远离pivot且非共线，点击finish_setup，检查真实末端旋转控制和bake回源，source/top/side/all快选。取消选择不能自动运行原scriptJob。begin和finish各Undo组；移动自身也需正常Maya Undo。
4. Sword依次weapon/(optional wrist)/hand，Reverse同顺序；完整原特殊locator/joint/pivot/相对腕部位移、jointOrient和双向约束，对照原备份；不能只检查helper出现就标通过。Reverse调整Pivot/Top/Side，候选finish，测试地面插剑/双手武器；Top/Side共线拒绝。
5. Arc选真实timeline范围或本对象至少两键，knots2/3/20、show source开关。检查完整motionTrail/smooth curve/cluster control/source curve/逐帧motionPath uValue/Curve_trajectory和pairBlend渐入渐出。存在外部motionTrail时其nodeState在finally恢复，MT Update应拒操作外部trail。matrixNodes/decomposeMatrix未就绪应先加载已安装Maya插件再预检，不能自动下载。
6. 每种系统选source，Bake与Layer Bake，比较源world姿态/关键帧/区间外属性/Euler winding。Layer BakedAnim重名拒绝。原bake内部吞错，必须人工看结果，API返回不能当最终验收。确认后Delete仅自有helpers：pairBlend input1烘焙输出应接回，曲线/新layer保留；外部child/下游或无独立烘焙拒删除。一次Undo/Redo恢复所有阶段，不删其他工具资源。
7. 替换输入/locator名字，保存重开，Status与group依UUID正确，finish或删除不使用旧名；Undo后重复调用应与网络元数据一致，多个session显式选定。
8. 在备份上注入native路径错误或其他失败：已观测原Undo opens须闭合，外层整组Undo有效；时间、对象/键选择、autokey、units、eval/cache、Move模式、viewport/timeline恢复；failed状态阻止未Undo后续写入。拒将失败描述为自动回滚。原UI未受此适配保护。
9. 附属帮助.mel实际是文本，不能source；安装器会建Shelf，本次不运行。记录真实Maya/Python版本、所有上述结果与未通过问题，才执行promotion预览及经用户确认的apply。正式库此前不动。
