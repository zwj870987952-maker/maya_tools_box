import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma

WINDOW_NAME = "WeightTransferListUI"


# -------------------------------------------------
# 基础工具
# -------------------------------------------------
def short_name(path):
    if not path:
        return ""
    return path.split("|")[-1]


def get_full_path(node_name):
    if not node_name or not cmds.objExists(node_name):
        return None
    try:
        result = cmds.ls(node_name, long=True) or []
        return result[0] if result else node_name
    except:
        return node_name


def resolve_to_full_path(name):
    if not name:
        return None
    matches = cmds.ls(name, long=True) or []
    if not matches:
        return None
    return matches[0]


def get_mobject(node_name):
    sel = om.MSelectionList()
    sel.add(node_name)
    return sel.getDependNode(0)


def get_dagpath(node_name):
    sel = om.MSelectionList()
    sel.add(node_name)
    return sel.getDagPath(0)


def get_skin_clusters_from_mesh(mesh):
    history = cmds.listHistory(mesh, pruneDagObjects=True) or []
    return cmds.ls(history, type='skinCluster') or []


def get_meshes_from_source_joint(source_joint):
    history = cmds.listHistory(source_joint, pruneDagObjects=True) or []
    skin_clusters = cmds.ls(history, type='skinCluster') or []

    meshes = []
    for sc in skin_clusters:
        geo = cmds.skinCluster(sc, query=True, geometry=True) or []
        meshes.extend(geo)

    uniq = []
    for m in meshes:
        if m not in uniq:
            uniq.append(m)
    return uniq


def find_influence_index(influence_paths, full_path, short):
    for i, p in enumerate(influence_paths):
        full_name = p.fullPathName()
        partial_name = p.partialPathName()
        short_name_value = full_name.split("|")[-1]

        if full_path and full_path in (full_name, partial_name):
            return i, p
        if short and short == short_name_value:
            return i, p
    return None, None


def normalize_meshes(meshes):
    result = []
    for m in meshes:
        full = resolve_to_full_path(m)
        if full and full not in result:
            result.append(full)
    return result


# -------------------------------------------------
# 权重转移
# -------------------------------------------------
def transfer_joint_weights_fast(source_joint, target_joint, mesh):
    skin_clusters = get_skin_clusters_from_mesh(mesh)
    if not skin_clusters:
        raise RuntimeError("模型 {} 没有找到 skinCluster".format(short_name(mesh)))

    skin_cluster_name = skin_clusters[0]
    skin_cluster_obj = get_mobject(skin_cluster_name)
    skin_fn = oma.MFnSkinCluster(skin_cluster_obj)

    mesh_path = get_dagpath(mesh)
    influence_paths = skin_fn.influenceObjects()

    source_index, _ = find_influence_index(
        influence_paths, get_full_path(source_joint), short_name(source_joint)
    )
    target_index, _ = find_influence_index(
        influence_paths, get_full_path(target_joint), short_name(target_joint)
    )

    if source_index is None:
        raise RuntimeError("源骨骼不在 skinCluster 影响列表中: {}".format(short_name(source_joint)))
    if target_index is None:
        raise RuntimeError("目标骨骼不在 skinCluster 影响列表中: {}".format(short_name(target_joint)))

    mesh_fn = om.MFnMesh(mesh_path)
    vertex_count = mesh_fn.numVertices

    comp_fn = om.MFnSingleIndexedComponent()
    vtx_comp = comp_fn.create(om.MFn.kMeshVertComponent)
    comp_fn.addElements(range(vertex_count))

    weights, inf_count = skin_fn.getWeights(mesh_path, vtx_comp)
    weights = list(weights)

    for v in range(vertex_count):
        base = v * inf_count
        sw = weights[base + source_index]
        tw = weights[base + target_index]

        weights[base + target_index] = tw + sw
        weights[base + source_index] = 0.0

    influence_indices = om.MIntArray(range(inf_count))
    weight_array = om.MDoubleArray(weights)

    skin_fn.setWeights(mesh_path, vtx_comp, influence_indices, weight_array, False)
    cmds.skinCluster(skin_cluster_name, edit=True, forceNormalizeWeights=True)


def remove_influence_from_mesh(source_joint, mesh):
    skin_clusters = get_skin_clusters_from_mesh(mesh)
    if not skin_clusters:
        raise RuntimeError("模型 {} 没有找到 skinCluster".format(short_name(mesh)))

    skin_cluster_name = skin_clusters[0]
    skin_cluster_influences = cmds.skinCluster(skin_cluster_name, query=True, influence=True) or []

    source_full = get_full_path(source_joint)
    source_short = short_name(source_joint)

    exists_influence = False
    for inf in skin_cluster_influences:
        if inf == source_joint or get_full_path(inf) == source_full or short_name(inf) == source_short:
            exists_influence = True
            break

    if not exists_influence:
        return False

    cmds.skinCluster(skin_cluster_name, edit=True, removeInfluence=source_joint)
    return True


# -------------------------------------------------
# 任务解析
# 格式：
# 源骨骼 => 目标骨骼 => 模型1,模型2 => DelSkin
# -------------------------------------------------
def parse_task_line(line):
    parts = [p.strip() for p in line.split("=>")]
    if len(parts) < 2:
        raise RuntimeError("任务行格式错误，应为：源骨骼 => 目标骨骼 => 模型1,模型2 => DelSkin")

    source_name = parts[0]
    target_name = parts[1]

    mesh_names = []
    del_skin = False

    if len(parts) >= 3 and parts[2].strip():
        mesh_names = [m.strip() for m in parts[2].split(",") if m.strip()]

    if len(parts) >= 4 and parts[3].strip().lower() == "delskin":
        del_skin = True

    return source_name, target_name, mesh_names, del_skin


# -------------------------------------------------
# UI 逻辑
# -------------------------------------------------
def load_selection_to_list(*args):
    sel = cmds.ls(selection=True, long=True) or []
    if len(sel) < 2:
        cmds.warning("请至少选择：源骨骼、目标骨骼")
        return

    source_full = sel[0]
    target_full = sel[1]
    mesh_fulls = sel[2:] if len(sel) > 2 else []

    line_display = "{} => {} => {}".format(
        short_name(source_full),
        short_name(target_full),
        ",".join([short_name(m) for m in mesh_fulls])
    )

    current = cmds.scrollField("wt_task_list", query=True, text=True)
    if current.strip():
        new_text = current.rstrip() + "\n" + line_display
    else:
        new_text = line_display

    cmds.scrollField("wt_task_list", edit=True, text=new_text)


def run_tasks(*args):
    text = cmds.scrollField("wt_task_list", query=True, text=True).strip()
    if not text:
        cmds.warning("任务列表为空")
        return

    lines = [l.strip() for l in text.splitlines() if l.strip()]

    success = 0
    failed = []

    for idx, line in enumerate(lines, start=1):
        try:
            source_name, target_name, mesh_names, del_skin = parse_task_line(line)

            source_full = resolve_to_full_path(source_name)
            target_full = resolve_to_full_path(target_name)

            if not source_full:
                raise RuntimeError("源骨骼不存在或无法解析: {}".format(source_name))
            if not target_full:
                raise RuntimeError("目标骨骼不存在或无法解析: {}".format(target_name))

            if not mesh_names:
                mesh_names = get_meshes_from_source_joint(source_full)
                if not mesh_names:
                    raise RuntimeError("未录入模型，且无法从源骨骼自动识别模型: {}".format(short_name(source_full)))

            mesh_fulls = normalize_meshes(mesh_names)

            any_done = False
            skipped = []

            for mesh_full in mesh_fulls:
                try:
                    skin_clusters = get_skin_clusters_from_mesh(mesh_full)
                    if not skin_clusters:
                        skipped.append("{}(无skinCluster)".format(short_name(mesh_full)))
                        continue

                    skin_cluster_name = skin_clusters[0]
                    skin_cluster_obj = get_mobject(skin_cluster_name)
                    skin_fn = oma.MFnSkinCluster(skin_cluster_obj)
                    influence_paths = skin_fn.influenceObjects()

                    source_index, _ = find_influence_index(
                        influence_paths, source_full, short_name(source_full)
                    )
                    target_index, _ = find_influence_index(
                        influence_paths, target_full, short_name(target_full)
                    )

                    if source_index is None or target_index is None:
                        skipped.append("{}(缺少骨骼)".format(short_name(mesh_full)))
                        continue

                    transfer_joint_weights_fast(source_full, target_full, mesh_full)

                    if del_skin:
                        try:
                            remove_influence_from_mesh(source_full, mesh_full)
                        except Exception as rm_e:
                            skipped.append("{}(移除影响失败:{})".format(short_name(mesh_full), rm_e))

                    any_done = True
                    print("第 {} 行完成：{} -> {} | {}".format(
                        idx, short_name(source_full), short_name(target_full), short_name(mesh_full)
                    ))

                except Exception as mesh_e:
                    skipped.append("{}({})".format(short_name(mesh_full), mesh_e))

            if not any_done:
                raise RuntimeError("第 {} 行没有任何模型成功执行，跳过原因：{}".format(idx, " | ".join(skipped)))

            success += 1

        except Exception as e:
            msg = "第 {} 行失败：{} | 原始行：{}".format(idx, e, line)
            failed.append(msg)
            cmds.warning(msg)

    print("执行完成：成功 {} 行，失败 {} 行".format(success, len(failed)))
    if failed:
        print("\n".join(failed))


# -------------------------------------------------
# UI
# -------------------------------------------------
def build_ui():
    if cmds.window(WINDOW_NAME, exists=True):
        cmds.deleteUI(WINDOW_NAME)

    win = cmds.window(
        WINDOW_NAME,
        title="骨骼权重批量转移工具",
        widthHeight=(1020, 560),
        sizeable=True
    )

    main_form = cmds.formLayout()

    info_text = cmds.text(
        parent=main_form,
        label="任务格式：源骨骼 => 目标骨骼 => 模型1,模型2 => DelSkin\n最后一列写 DelSkin 时，执行完成后会从模型中移除源骨骼影响；不写则不移除。",
        align="left"
    )

    task_list = cmds.scrollField(
        "wt_task_list",
        parent=main_form,
        editable=True,
        wordWrap=False,
        text=""
    )

    btn_col = cmds.columnLayout(
        parent=main_form,
        adjustableColumn=True,
        rowSpacing=6
    )

    btn1 = cmds.button(
        label="载入选择",
        height=36,
        command=load_selection_to_list
    )

    btn2 = cmds.button(
        label="执行",
        height=36,
        bgc=(0.3, 0.6, 0.3),
        command=run_tasks
    )

    cmds.formLayout(
        main_form,
        edit=True,
        attachForm=[
            (info_text, "top", 10),
            (info_text, "left", 10),
            (info_text, "right", 10),

            (task_list, "left", 10),
            (task_list, "right", 10),

            (btn_col, "left", 10),
            (btn_col, "right", 10),
            (btn_col, "bottom", 10),
        ],
        attachControl=[
            (task_list, "top", 10, info_text),
            (btn_col, "top", 10, task_list),
        ],
        attachPosition=[
            (task_list, "bottom", 0, 72),
        ]
    )

    cmds.columnLayout(btn_col, edit=True, adjustableColumn=True)
    cmds.button(btn1, edit=True, width=1)
    cmds.button(btn2, edit=True, width=1)

    cmds.showWindow(win)


build_ui()
