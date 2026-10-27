import maya.cmds as mc

class exportImportJointsWeight:

    def loadFolder(self):
        folderPath = mc.fileDialog2(dialogStyle=2, fileMode=3)[0]
        mc.textFieldButtonGrp('folderPathField', edit=True, text=folderPath)

    def exportWeights(self, arg1):
        folderBasePath = mc.textFieldButtonGrp('folderPathField', query=True, text=True)
        objList = mc.ls(sl=True)
        for each in objList:
            mySel = mc.listRelatives(each, shapes=True)
            shapeHistory = mc.listHistory(mySel, levels=5)
            skinClus = mc.ls(shapeHistory, typ='skinCluster')
            jointsInfluence = mc.ls(shapeHistory, typ='joint')
            folderPath = folderBasePath + '/'
            filePath = folderPath + each + '.txt'
            with open(filePath, 'w') as f:
                for obj in jointsInfluence:
                    f.write(obj + '\n')
            mc.deformerWeights(each + '_sknCls.xml', deformer=skinClus[0], export=True, format='XML', path=folderPath)

    def importWeights(self, arg1):
        folderBasePath = mc.textFieldButtonGrp('folderPathField', query=True, text=True)
        postMethod = mc.checkBox('postCB', query=True, value=True)
        skinnedMesh = mc.checkBox('skinnedCB', query=True, value=True)
        objList = mc.ls(sl=True)
        for each in objList:
            nameObj = each
            folderPath = folderBasePath + '/'
            filePath = folderPath + nameObj + '.txt'
            with open(filePath, 'r') as f:
                jointNames = f.read().splitlines()
                jointList = mc.ls(jointNames)
            if postMethod == True:
                if skinnedMesh == True:
                    mySel = mc.listRelatives(each, shapes=True)
                    shapeHistory = mc.listHistory(mySel, levels=5)
                    newSkin = mc.ls(shapeHistory, typ='skinCluster')
                else:
                    newSkin = mc.skinCluster(jointList, each, tsb=True, nw=2)
                mc.deformerWeights(nameObj + '_sknCls.xml', path=folderPath, im=True, method='index', deformer=newSkin[0])
                mc.skinCluster(newSkin, edit=True)
            else:
                if skinnedMesh == True:
                    mySel = mc.listRelatives(each, shapes=True)
                    shapeHistory = mc.listHistory(mySel, levels=5)
                    newSkin = mc.ls(shapeHistory, typ='skinCluster')
                else:
                    newSkin = mc.skinCluster(jointList, each, tsb=True)
                mc.deformerWeights(nameObj + '_sknCls.xml', path=folderPath, im=True, method='index', deformer=newSkin[0])
                mc.skinCluster(newSkin, edit=True, fnw=True)

    def exportImportWeightsUI(self):
        if mc.window('ExportImportJointsWeight', exists=True):
            mc.deleteUI('ExportImportJointsWeight')
        mc.window('ExportImportJointsWeight', title='Timal Export-Import JointsWeights v 1.3 UI', widthHeight=(400, 120), rtf=True, sizeable=False)
        mc.columnLayout('mainColumn', adj=True)
        mc.frameLayout(label='Files Path Selection', w=400)
        mc.textFieldButtonGrp('folderPathField', label='Folder Path', buttonLabel='Select', columnWidth3=(80, 270, 50), buttonCommand=self.loadFolder)
        mc.frameLayout(label='Export', w=400)
        mc.rowLayout(numberOfColumns=2, columnWidth2=(300, 100))
        mc.text('select all skinned Geometries', align='left')
        mc.button(label='Export', w=100, command=self.exportWeights)
        mc.setParent('mainColumn')
        mc.frameLayout(label='Import', w=400)
        mc.rowLayout(numberOfColumns=2, columnWidth2=(300, 100))
        mc.text('select all the geometries to import skin', align='left')
        mc.button(label='Import', w=100, command=self.importWeights)
        mc.rowLayout(parent='mainColumn', numberOfColumns=3, columnWidth3=(110, 150, 20))
        mc.checkBox('postCB', label='Post Normalize', value=False)
        mc.checkBox('skinnedCB', label='Load only SkinCluster', value=False)
        mc.separator(height=30, style='none')
        mc.setParent('mainColumn')
        mc.separator(height=30, style='none')
        mc.text('script by Hugo Timal/Timal Studios', align='left')
        mc.showWindow('ExportImportJointsWeight')
