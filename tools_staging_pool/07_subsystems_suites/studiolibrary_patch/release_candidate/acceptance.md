# Studio Library PlusPatch Maya GUI 验收 not_run

1. 新Maya会话用launch_candidate.show_ui选择备份资产root；原标准pose/anim/set/mirror与WPose/WAnimation菜单、完整Save/Load/采样/缩略图/sequence、namespace/名称替换/镜像选项，中文切换和Last Modified/历史显示均逐项响应。inspect/dry前后无Qt/hook/cache写入，只有主动启用才patch，不启动自动cache修复。
2. 备份rig层级变换/不同rotateOrder/约束/锁轴/缩放/world pose blend/additive/mirror，world animation replace/merge/insert非world custom attrs/多帧/采样bake与一次UndoRedo；最后无效或锁住对象应在首项写入前拒绝。原native report任何failed/cancelled不能记全成功。
3. 新.wpose/.wanim完整pose.json/anim.ma/worldJSON roundtrip；同名资产仅GUI明确覆盖，历史v####原payload与thumbnail/metadata精确保留，只读虚拟历史回读。模拟保存失败恢复原本体和.history；collision/损坏/symlink不静默删版本，保留stage/partial新资产供检查，外部文件不由Maya Undo撤回。
4. ModernDark原CSS所有token/DPI/字体图标实际显示；候选apply_theme只本窗口不写bundle文件。外部resource install先备份、重复install、uninstall还原，原CSS被另一工具改过拒绝restore而保留它；cache repair自有root限定/精确backup，无自动全局修复，QSettings语言/历史显式改变可反向恢复。
5. 重复install/uninstall无叠加；foreign后装wrapper/item registry变化拒绝强覆盖，关闭/重开窗口不操作其他库。Maya2025与所需旧版本真实核验；记录candidate_sha256/maya_version/accepted_by/date/passed=true后再promotion。当前任何离线/isolated mayapy/Qt均非真实GUI实测。
