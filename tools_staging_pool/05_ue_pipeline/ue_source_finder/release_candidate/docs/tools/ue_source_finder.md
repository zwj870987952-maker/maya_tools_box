# UE 源文件追溯复制候选

完整保留原选中资产→import_data源文件→按UE文件夹分类→复制并以资产名重命名→成功/缺失/失败日志与名单→汇总→打开目录功能。原无UI单文件SHA归档，import取消桌面打印与立即复制。native UE独立包，无Maya继承/注册，Schema/validate/execute/run结构化success/data/errors。dry_run默认True/action默认inspect，读选区/importmetadata/源SHA但不mkdir/复制/log/Explorer。

```python
from engine_toolkit.tools import ue_source_finder as t
preview = t.run(action='copy_sources', output_dir=r'D:/SourceCollect', session_name='Review01')
result = t.run(dry_run=False, action='copy_sources', output_dir=r'D:/SourceCollect', session_name='Review01')
```

output_dir必须现存，默认桌面；session_name缺省时间+随机后缀，预检显示自己的会话路径，下次执行可能分配新路径，需传相同session_name复核路径。新会话目录必须不存在，独占mkdir，不复用桌面旧目录；保存Game/Plugin mount完整父文件夹层级，防原仅末级目录分类合并不同UE路径。原第一源filename行为default source_mode=first保留，all额外源按_src2/3后缀，文件basename为asset_name+原extension，不改变UE资产名或importdata。source metadata读取复用第89项reviewed reader，代码独立复制source_paths.py，自包含，不依赖别候选。raw/相对路径绝不按cwd猜，missing记录；missing可有完整成功查询结果，不表示复制了全部资产，应检查total_missing。

整批碰撞/路径遍历/Windows保留名/selection<=10000预检；每源SHA/size执行前再核对，独占xb分块copy、目标SHA核对、copystat；失败只删除自己创建的部分文件，保留成功outputs与失败日志；进程中断/目录或日志异常可留下partial session。既有源不修改/删除，UE资产元数据不写，外部输出不受UE Undo。读大源计算SHA有IO成本，远程路径/源在copy时变化可能导致该项失败，不能保证生产者同时改写的snapshot。

每文件夹按需保存原4种TXT（成功复制/名单/源文件缺失/处理失败），多字段保留asset path/source/target/renamed/error，并summary.json结构化计数/完整folder_logs/生成路径。open_folders默认False（原自动弹资源管理器改显式True），Windows以参数数组explorer.exe调用，无shell命令拼接；仅打开本次组路径，非Windows或失败warnings如实记录。show_ui仅Output Log预检（原无窗口）；复制后log简短汇总，不开UE事务。原覆盖copy2改独占的新会话输出，明确行为变化与路径层级调整。

可衔接PrintSourcePaths查询、人工定位缺失源或重新生成FBX配置；只复制导入源文件不复制uasset、不修改reimport绑定，不承诺重新导入配置就正确。真实UE资产类型/multi-source/TXT/Explorer/跨版本均not_run；离线真实临时文件复制测试不替代UE验收。promotion.json仅engine/docs/tests预制路径，runtime_version/current SHA/人工验收后晋级，依旧不改Maya正式库。
