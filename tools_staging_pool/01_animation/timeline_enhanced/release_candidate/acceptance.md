# 时间轴方块工具人工验收（not_run）

1. 备份场景与临时JSON；加载 launch_candidate.py 的 load_tool，默认inspect、各纯动作/文件的dry_run后核对场景节点/键/selection/时间/播放/Undo不变。
2. 分别启动基础/增强UI，检查所有菜单、起始负帧/范围、1000帧水平滚动、刷新后布局仍在scroll里。检查Qt5/Qt6窗口焦点与Script Editor。
3. 基础随机色、默认点击拖拽落下；增强六方块类型、属性颜色/标签名称、Ctrl多选、单选/取消、复制相对时距粘贴/边界裁剪、同帧移动/已占帧替换取消/确认、删除/清空全部检查。场景真正key位置应保持不变。
4. 模式选择/添加/删除、reset默认拖拽、fit最小8px滚动、菜单与Ctrl+A/C/V/Delete/Escape检查；文本字段编辑焦点有冲突时记录。local Ctrl+Z/Redo恢复规划文档，Maya Undo不当作窗口内存Undo。
5. 保存新临时JSON，现有JSON默认保护，明确覆盖后旧字节备份存在；坏JSON/重复键/异常颜色/超体积加载拒绝且旧文档不变。换显示范围后隐藏方块仍保留，关闭前先保存。
6. sync只读Maya整数播放范围，负帧正确，超过1000/小数范围拒绝；当前帧按钮和真实play/stop正常，确实影响播放而非key重定时。不注册全局热键、无用户目录/源目录隐式写入。
7. 检查GUI帮助/关于及原说明（其中example/hotkey文件本池缺失，使用本候选窗口快捷键）。所有问题记录真实Maya版本/traceback，修复候选复验；未通过不转正。通过后使用 promotion.json 的预制晋级动作。
