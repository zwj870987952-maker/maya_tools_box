# Maya记录点直验 not_run

备份scene真实GUI中：import/dry create/restore/clear/install不改scene/Undo队列或UI；原Qt面板全部create/name/多行状态/双击与选中/最新恢复/clear/视口提示运行。tx1→记录A→tx2→记录B→tx3，B恢复tx2，Redo标记与编辑回tx3，A恢复tx1，标记本身无场景节点；中文/引号名不能执行MEL。max_steps不足/target foreign/flush/有限历史截断/scene新建切换必须零步拒绝，不Undo无关编辑；manual Undo/Redo状态一致，clear/overwrite只列表，不清原Undo。调用必须外层chunk外；嵌套marker不可见如实失败，不能擅关caller chunk。异常/其他脚本插队停止且报告已撤步骤，refresh原状态恢复；不能恢复文件IO/非undo命令。实际四Shelf owned buttons点击/重复安装不重复、不改其他button、完整模块callback、退出后prefs是否保存取决用户，不自动写prefs。真实GUI/Shelf/跨版本未验，mayapy不算直验，通过后当前SHA/版本/操作者/日期再晋级。
