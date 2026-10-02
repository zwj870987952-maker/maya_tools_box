# 浮动工具栏真实Maya验收 not_run

1. 原完整无边框可拖窗口、FlowLayout换行、10空按钮、编辑名称/完整多行Python/MEL语言、删除/clear。show不自动改shelf，enable/disable重复安装自有filter，Shift中键拖入与原Maya原生拖入现存名字；原left click/command/sourceType/dragCallback/mousePress无变化。close撤filter，不触其他工具。
2. 拖入Python import语句、多行与末尾分号、MEL无末尾分号均尊重源language；drop/load不执行，明确按钮或API confirm_execute才run，scene一次Undo但文件/UI影响另记。任意外部用户脚本先自己审阅，不在整理过程中运行真实shelf命令。
3. 图标Maya Qt资源/自选PNG保存内嵌JSON跨目录读取；不生成覆盖icon_i文件。坏最后按钮/坏PNG/非法Python不清原配置，新JSON已有文件拒绝覆盖，既有raw配置读兼容语言需显式检查。
4. 当前仅离线/Qt，真实MayaGUI/shelf/drag与实际command/cross-version实测逐项记；candidate_sha256/accepted_by/maya_version/date/passed=true后再promotion。
