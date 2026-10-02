# UE 源文件追溯复制验收 not_run

备份UE项目，准备存在/缺失/无importdata/同名不同文件夹/多源资产、临时output_dir。import和dry_run不得建目录或开Explorer；核对路径清单和full Game父级分类；source_mode=first/all与_srcN命名、原asset名改名规则、Unicode/Windows保留名/同target碰撞/相对路径明确拒绝或missing。实际copy验证SHA/时间元数据/原源不变/UE importdata不变，新会话fourTXT+summary统计准确；existing session拒绝不覆盖，失败copy保留成功文件并删除自己partial、失败日志真实；纯missing生成missing日志不假计success。open_folders=True只打开自己的路径，无shell拼接。真实UE/Explorer/跨版本未验收，临时离线复制不算UE通过；通过后记录current candidate SHA/runtime_version/tool_id=ue_source_finder/accepted_by/date/passed=true，文件输出不能UE Undo撤回。
