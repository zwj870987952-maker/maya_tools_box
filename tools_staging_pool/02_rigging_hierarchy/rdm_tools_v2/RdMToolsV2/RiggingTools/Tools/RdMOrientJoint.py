from maya import cmds

def OrientJoints(oj = "xzy", sao = "zup", *args):
    cmds.undoInfo(openChunk=True)    

    cmds.makeIdentity(a=1,t=1,r=1,s=1, n=0,pn=1)      
    cmds.joint(e= True, zso=True, oj= oj, sao = sao)
    
    cmds.undoInfo(closeChunk=True)    

    print 'Orient joint'