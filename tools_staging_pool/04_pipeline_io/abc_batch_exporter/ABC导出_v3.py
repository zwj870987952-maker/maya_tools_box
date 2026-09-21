######新增新建材质功能，修改界面UI##############
import maya.mel as mel
import maya.cmds as cm
import os
import shutil
import random
import maya.cmds as py


def load_mesh():
    cm.select(hi=True)
    get_all_mesh = cm.ls(sl=True, shapes=True)
    get_all_mesh_string = ""
    for one_check_mesh in get_all_mesh:
        if cm.nodeType(one_check_mesh) == "mesh":
            temp_trans = cm.listRelatives(one_check_mesh, f=True, p=True)
            get_all_mesh_string += '"' + temp_trans[0] + '",'
            continue
    if len(get_all_mesh_string) != 0:
        cm.textScrollList("the_mod_list", e=True, ra=True)
        exec 'cm.textScrollList("the_mod_list",e=True,append=(' + get_all_mesh_string[
            0:-1
        ] + "))"


def remove_mesh():
    cm.textScrollList("the_mod_list", e=True, ra=True)


def set_path_output():
    get_path = cm.fileDialog2(
        fileMode=3, caption="设置输出位置"
    )
    if str(get_path) != "None":
        get_path_arr = str(get_path).split("'")
        cm.textField("thePath_to_out", e=True, tx=get_path_arr[1] + "/")


def set_path_load():
    get_path = cm.fileDialog2(
        fileMode=1, caption="设置输出位置"
    )
    if str(get_path) != "None":
        get_path_arr = str(get_path).split("'")
        cm.textScrollList("the_Ref_list", e=True, a=get_path_arr[1])


def set_path_remove():
    cm.textScrollList("the_Ref_list", e=True, ra=True)


def LR_set_path_output():
    get_path = cm.fileDialog2(
        fileMode=3, caption="设置输出位置"
    )
    if str(get_path) != "None":
        get_path_arr = str(get_path).split("'")
        cm.textField("LR_thePath_to_out", e=True, tx=get_path_arr[1] + "/")


def open_path_output():
    get_tx_path = cm.textField("thePath_to_out", q=True, tx=True)
    get_tx_path.replace("\\", "/")
    if get_tx_path[-1] != "/":
        get_tx_path = get_tx_path + "/"
    os.startfile(get_tx_path)


def open_LR_path_output():
    get_LR_path = cm.textField("LR_thePath_to_out", q=True, tx=True)
    get_LR_path.replace("\\", "/")
    if get_LR_path[-1] != "/":
        get_LR_path = get_LR_path + "/"
    os.startfile(get_LR_path)


def ABC_set_path_output():
    mf = "Alembic(*.abc);;All Files (*.*)"
    get_path = cm.fileDialog2(
        ff=mf, fileMode=0, caption="设置输出位置"
    )
    if str(get_path) != "None":
        get_path_arr = str(get_path).split("'")
        cm.textField("ABC_thePath_to_out", e=True, tx=get_path_arr[1])


def ABC_start():
    get_frame_start = cm.intField("the_ST_ABC", q=True, v=True)
    get_frame_end = cm.intField("the_ET_ABC", q=True, v=True)
    get_the_step = cm.floatField("the_EVA_every", q=True, v=True)
    get_final_out_path = cm.textField("ABC_thePath_to_out", q=True, tx=True)
    ifUV = int(cm.checkBox("if_write_UV", q=True, v=True))
    ifWP = int(cm.checkBox("if_world_Space", q=True, v=True))
    ifWUVset = int(cm.checkBox("if_write_UVset", q=True, v=True))
    ifWF = int(cm.checkBox("if_write_Faceset", q=True, v=True))
    ifWV = int(cm.checkBox("if_write_Visibility", q=True, v=True))
    ifRNS = int(cm.checkBox("if_remove_NS", q=True, v=True))
    all_need_to_abc = cm.textScrollList("the_mod_list", q=True, ai=True)
    write_UV = ["", "-uvWrite"]
    world_Space = ["", "-worldSpace"]
    write_UVset = ["", "-writeUVSets"]
    write_Faceset = ["", "-writeFaceSets"]
    write_Visibility = ["", "-writeVisibility"]
    remove_NS = ["", "-stripNamespaces"]
    all_need_to_abc_string = ""
    for one_abc in all_need_to_abc:
        all_need_to_abc_string += " -root " + one_abc
    cm.AbcExport(
        j="-frameRange "
        + str(get_frame_start)
        + " "
        + str(get_frame_end)
        + " "
        + "-step "
        + str(get_the_step)
        + " "
        + write_UV[ifUV]
        + " "
        + write_UVset[ifWUVset]
        + " "
        + write_Faceset[ifWF]
        + " " 
        + write_Visibility[ifWV]
        + " " 
        + remove_NS[ifRNS]
        + " " 
        + world_Space[ifWP]
        + all_need_to_abc_string
        + " -file "
        + get_final_out_path
    )


def addnew_Shade():
    def material():
            sel=py.ls(sl=True)
            print sel
            if sel!=[]:
                for obj in sel:
                    myShade = py.shadingNode('lambert', asShader=True)
                    #print myShade
                    myShadeSG=py.sets( renderable=True,noSurfaceShader=True, name=(myShade+"SG"))
                    #print myShadeSG
                    py.connectAttr ((myShade+".outColor"),(myShadeSG+".surfaceShader"))
                    print obj
                    py.select(obj)
                    py.sets (forceElement=myShadeSG)
                    colorR1=random.random()
                    colorG1=random.random()
                    colorB1=random.random()
                    py.setAttr ((myShade+".color"),colorR1,colorG1,colorB1,type="double3" );
            else:
                py.inViewMessage( amg='please select object!', pos='midCenter', fade=True )
    
    material()



def window_TX():
    if cm.window("wit", ex=True):
        cm.deleteUI("wit")
    cm.window(
        "wit", title="ABC导出器", mb=1, widthHeight=(400, 400), sizeable=0
    )
    pro = "liulizhan"
    cm.frameLayout(
        bgc=[0, 0.3,0.6],
        label="选择加载需要转化的模型并载入",
    )
    cm.columnLayout()
    cm.rowColumnLayout(numberOfColumns=2, cw=[(1, 200), (2, 185)])
    cm.rowColumnLayout(numberOfColumns=1)
    cm.textScrollList("the_mod_list", w=200, h=220, bgc=(0, 0.3, 0.3))
    cm.setParent("..")
    cm.rowColumnLayout(numberOfColumns=1)
    cm.text(label="ABC导出设置")
    cm.rowColumnLayout(numberOfColumns=3, cw=[(1, 80), (2, 50), (3, 50)])
    cm.text(label="")
    cm.text(label="")
    cm.text(label="")
    cm.text(label="起始/结束")
    get_start_frame = cm.playbackOptions(q=True, min=True)
    get_end_frame = cm.playbackOptions(q=True, max=True)
    cm.intField("the_ST_ABC", v=get_start_frame)
    cm.intField("the_ET_ABC", v=get_end_frame)
    cm.text(label="步长")
    cm.floatField("the_EVA_every", v=1)
    cm.text(label="")
    cm.text(label="")
    cm.text(label="")
    cm.text(label="")
    cm.checkBox("if_write_UV", label="UV 写入", v=1)
    cm.text(label="")
    cm.text(label="")
    cm.checkBox("if_world_Space", label="世界空间", v=1)
    cm.text(label="")
    cm.text(label="")
    cm.checkBox("if_write_Visibility", label="写入可见性", value=True)
    cm.text(label="")
    cm.text(label="")
    cm.checkBox("if_write_UVset", label="写入UV集", value=True)
    cm.text(label="")
    cm.text(label="")
    cm.checkBox("if_remove_NS", label="去除空间名", value=False)
    cm.text(label="")
    cm.text(label="")
    cm.checkBox("if_write_Faceset", label="写入面集", value=True)
    cm.text(label="")
    cm.text(label="")
    cm.text(label="")
    cm.setParent("..")
    cm.rowColumnLayout(numberOfColumns=2, cw=[(1, 90), (2, 90)])
    cm.button(label="载入所选", h=30, c="load_mesh()")
    cm.button(label="清空列表", c="remove_mesh()")
    cm.setParent("..")
    cm.setParent("..")
    cm.setParent("..")
    cm.setParent("..")
    cm.frameLayout(
        cll=1,
        cl=0,
        bgc=[0, 0.3,0.6],
        label="ABC缓存输出",
    )
    cm.rowColumnLayout(numberOfColumns=3, cw=[(1, 90), (2, 230), (3, 60)])
    cm.text(fn="boldLabelFont", label="ABC缓存位置：")
    cm.textField("ABC_thePath_to_out", ed=False)
    cm.button(label="浏览...", c="ABC_set_path_output()")
    cm.setParent("..")
    cm.rowColumnLayout(numberOfColumns=4, cw=[(1, 50), (2, 150), (3, 30), (4, 150)])
    cm.text(label="")
    cm.button(label="输出ABC缓存", c="ABC_start()")
    cm.text(label="")
    cm.button(label="新建材质", c="addnew_Shade()",bgc=(0, 0.3, 0.3))
    cm.setParent("..")

   
    cm.showWindow("wit")


# 在这里调用 window_TX() 函数
window_TX()
