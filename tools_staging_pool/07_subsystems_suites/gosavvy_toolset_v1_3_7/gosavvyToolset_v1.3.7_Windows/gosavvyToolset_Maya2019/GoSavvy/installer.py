import platform
import maya.cmds as cmds
import os
import shutil
import distutils
import ctypes
import sys
import subprocess

class Installer:
	
	mayaVer= cmds.about(version=True)
	userPath= os.path.expanduser('~')
	
	if platform.system()=='Windows':
		defaultPluginPath= r'C:\Program Files\Autodesk\Maya'+mayaVer+r'\plug-ins'
		pluginExt= '.mll'
		userPath.replace('/','\\')
		prefPath= os.path.join(userPath, 'maya', mayaVer)
		
	else:
		defaultPluginPath= '/usr/autodesk/maya'+mayaVer+'/plug-ins'
		pluginExt= '.so'
		prefPath= os.path.join(userPath, 'maya', mayaVer)
		
	def installerGUI(self):
		if cmds.window('gosavvyInstaller', exists=True):
			cmds.deleteUI('gosavvyInstaller')
		cmds.window('gosavvyInstaller', t='Install / Update GoSavvy Toolset', s=False, bgc=[0.1,0.1,0.11])
		cmds.window('gosavvyInstaller', e=True, w=600, h=100)
		cmds.columnLayout('cl', adj=True)
		cmds.rowColumnLayout(nc=2, cw=[(1,200), (2, 400)], cs=(5,5), p='cl')
		cmds.button(label='Browse Downloaded GoSavvy Folder', c='gosavvyInstaller.browseGoSavvyFolder()')
		cmds.textFieldGrp('gosavvyFolderTF', text='', editable=False, adj=1)
		cmds.button(label='Browse Installation Folder', c='gosavvyInstaller.browseInstallationFolder()')
		cmds.textFieldGrp('installationFolderTF', text='', editable=False, adj=1)
		cmds.text(l='')
		cmds.checkBox('startupCB', l='Start GoSavvy Toolset on Maya Startup', v=True)
		cmds.separator(h=10, st='in')
		cmds.separator(h=10, st='in')
		cmds.button(label='Update', c= 'gosavvyInstaller.install(fresh=False)', bgc=[0.25,0.09,0.1])
		cmds.button(label='Fresh Install (Removes Existing Toolset If Found)', c='gosavvyInstaller.install(fresh=True)', bgc=[0.1,0.2,0.22])
		cmds.separator(h=10, st='in', p='cl')
		cmds.showWindow()

	def update(self):
		install(fresh=False)
	
	def freshInstall(self):
		install(fresh=True)
	
	def browseGoSavvyFolder(self):
		path= cmds.fileDialog2(cap='Browse GoSavvy Folder Containing New Tools', fm=2, okc='Select GoSavvy Folder')
		if path != None:
			path= path[0]
			if platform.system()=='Windows':
				path= path.replace('/','\\')
			cmds.textFieldGrp('gosavvyFolderTF', e=True, text=path)
			
	def browseInstallationFolder(self):
		path= cmds.fileDialog2(cap='Browse Plugin Installation Folder', fm=2, okc='Select Installation Folder', dir=self.defaultPluginPath)
		if path != None:
			path= path[0]
			if platform.system()=='Windows':
				path= path.replace('/','\\')
			cmds.textFieldGrp('installationFolderTF', e=True, text=path)
			
	def mayaAdminModeWindow(self):
		if platform.system()=='Windows':
			adminMode= ctypes.windll.shell32.IsUserAnAdmin()
		else:
			if os.getuid()==0:
				adminMode= True
			else:
				adminMode= False
		if adminMode == False:
			if cmds.window('adminModePermissionWin', exists=True):
				cmds.deleteUI('adminModePermissionWin')
			cmds.window('adminModePermissionWin', t='Require Admin Rights', s=False)
			cmds.window('adminModePermissionWin', e=True, w=300, h=50)
			cmds.columnLayout('adminModeCl1', adj=True)
			cmds.text(l='')
			cmds.text(l='Launch Maya in Admin Mode?')
			cmds.text(l='')
			if platform.system()=='Windows':
				if sys.version[0]=='3':
					cm= 'cmds.deleteUI("adminModePermissionWin")\n'+'ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)'
				else:
					cm= 'cmds.deleteUI("adminModePermissionWin")\n'+'ctypes.windll.shell32.ShellExecuteW(None, u"runas", unicode(sys.executable), unicode(" ".join(sys.argv)), None, 1)'
			else:
				cm= 'cmds.deleteUI("adminModePermissionWin")\n'+'os.execvp("sudo", ["sudo","'+sys.executable+'"])'
			cmds.button(l='OK', c= cm)
			cmds.showWindow()
		else:
			msg= 'GoSavvy package cannot be installed.\n'
			msg= msg + 'Try again or Change the directory or try manual install.\n'
			msg= msg + 'Check README.txt for manual installation instructions.'
			cmds.confirmDialog(t='Write Access Denied!', m=msg, db='OK')
			
				
	def install(self, fresh=True):
		taskList=[]
		gosavvyFolder= cmds.textFieldGrp('gosavvyFolderTF', q=True, text=True)
		installationFolder= cmds.textFieldGrp('installationFolderTF', q=True, text=True)
		if installationFolder != '':
			if installationFolder[-7:]=='GoSavvy':
				installationFolder= installationFolder[:-8]
		if gosavvyFolder != '' and installationFolder != '':
			if gosavvyFolder[-7:]!='GoSavvy':
				cmds.confirmDialog(t='Wrong Folder!', m='Installation Unsuccessful!\nSelect GoSavvy Folder containing the tools.')
			else:
				gosavvyPluginsPath= os.path.join(installationFolder, 'GoSavvy')
				updateFailed= False
				writeFailed= False
				if fresh == True:
					if os.path.exists(gosavvyPluginsPath):
						onlyFiles = [f for f in os.listdir(gosavvyPluginsPath) if os.path.isfile(os.path.join(gosavvyPluginsPath, f))]
						for fl in onlyFiles:
							if self.pluginExt in fl:
								if cmds.pluginInfo(fl, q=True, l=True):
									cmds.unloadPlugin(fl, f=True)
									print(fl+' Unloaded')
						try:		
							shutil.rmtree(gosavvyPluginsPath)
							os.mkdir(os.path.join(installationFolder, 'GoSavvy'))
							os.mkdir(os.path.join(installationFolder, 'GoSavvy', 'icons'))
							os.mkdir(os.path.join(installationFolder, 'GoSavvy', 'customTools'))
							os.mkdir(os.path.join(installationFolder, 'GoSavvy', 'customTools', 'icons'))
						except Exception as e:
							writeFailed= True
							print(e)
							self.mayaAdminModeWindow()
					else:
						try:
							os.mkdir(os.path.join(installationFolder, 'GoSavvy'))
							os.mkdir(os.path.join(installationFolder, 'GoSavvy', 'icons'))
							os.mkdir(os.path.join(installationFolder, 'GoSavvy', 'customTools'))
							os.mkdir(os.path.join(installationFolder, 'GoSavvy', 'customTools', 'icons'))
						except Exception as e:
							writeFailed= True
							print(e)
							self.mayaAdminModeWindow()
				else:
					if os.path.exists(gosavvyPluginsPath):
						onlyFiles = [f for f in os.listdir(gosavvyPluginsPath) if os.path.isfile(os.path.join(gosavvyPluginsPath, f))]
						for fl in onlyFiles:
							if self.pluginExt in fl:
								if cmds.pluginInfo(fl, q=True, l=True):
									cmds.unloadPlugin(fl, f=True)
									print(fl+' Unloaded')
					else:
						updateFailed= True
						cmds.confirmDialog(t='Update Failed!', m='GoSavvy Toolset is not installed in this location.\nTry Fresh Install.')
						
				if updateFailed== False and writeFailed==False:
					try:
						if  os.path.exists(os.path.join(gosavvyPluginsPath, 'userID'+self.pluginExt)):
							os.remove(os.path.join(gosavvyPluginsPath, 'userID'+self.pluginExt))
						if  os.path.exists(os.path.join(gosavvyPluginsPath, 'icons', 'userIDIcon.png')):
							os.remove(os.path.join(gosavvyPluginsPath, 'icons', 'userIDIcon.png'))
						distutils.dir_util.copy_tree(gosavvyFolder, os.path.join(installationFolder, 'GoSavvy'))
						if fresh==True:
							taskList.append('GoSavvy Toolset Package successfully installed.')
						else:
							taskList.append('GoSavvy Toolset Package successfully updated.')
						try:
							cmds.loadPlugin('gosavvyToolset'+self.pluginExt)
						except:
							pass
					except:
						writeFailed= True
						self.mayaAdminModeWindow()
						
				envCmdAlreadyExist= False
				if fresh==False:
					envCmdAlreadyExist= True
				if fresh==True and writeFailed==False and updateFailed==False:
					mayaEnvPath= os.path.join(self.prefPath, 'Maya.env')			
					if os.path.exists(self.prefPath)==False:
						path= cmds.fileDialog2(cap='Browse Maya.env', fm=1, okc='Select', ff='env File (*.env)')
						if path != None:
							mayaEnvPath= path[0]
							self.prefPath= mayaEnvPath[:-9]
						else:
							cmds.confirmDialog(t='Maya.env not found!', m='Installation Unsuccessful!\nNeed Maya.env file to run GoSavvy Toolset.')
					
					if os.path.exists(self.prefPath):
						envLine= '\nMAYA_PLUG_IN_PATH = '+gosavvyPluginsPath+'\n'
						if os.path.exists(mayaEnvPath):
							envFile= open(mayaEnvPath, 'r')
							envData= envFile.read()
							envFile.close()
							if envLine not in envData:
								envFile= open(mayaEnvPath, 'a')
								envFile.write(envLine)
								envFile.close()
								taskList.append('GoSavvy Plugins Path added to Maya.env')
							else:
								envCmdAlreadyExist= True
						else:
							envFile= open(mayaEnvPath, 'w')
							envFile.write(envLine)
							envFile.close()
							taskList.append('GoSavvy Plugins Path added to Maya.env')
				
				if writeFailed==False and updateFailed==False:			
					startupSetup= cmds.checkBox('startupCB', q=True, v=True)
					if startupSetup == True:
						startupFile= os.path.join(self.prefPath, 'scripts', 'gosavvyToolsetStartup.py')
						if not os.path.exists(startupFile):
							line= 'import maya.cmds as cmds\n'
							line= line + 'def start():\n'
							line= line + '\tif not cmds.pluginInfo("gosavvyToolset'+self.pluginExt+'", q=True, l=True):'
							line= line + 'cmds.loadPlugin("gosavvyToolset'+self.pluginExt+'")\n'
							line= line + '\tcmds.gosavvyToolset()'
							f= open(startupFile, 'w')
							f.write(line)
							f.close()
						userSetupFile= os.path.join(self.prefPath, 'scripts', 'userSetup.py')
						line1= 'import maya.utils\n'
						line2= 'import gosavvyToolsetStartup\n'
						line2= line2+ 'maya.utils.executeDeferred("gosavvyToolsetStartup.start()")\n'
						if not os.path.exists(userSetupFile):
							f= open(userSetupFile, 'w')
							f.write(line1+line2)
							f.close()
							taskList.append('Auto-run on startup is activated.')
						else:
							f= open(userSetupFile, 'r')
							userSetupData= f.read()
							f.close()
							f= open(userSetupFile, 'a')
							if line1 not in userSetupData:
								f.write(line1)
							if line2 not in userSetupData:
								f.write(line2)
							f.close()
							taskList.append('Auto-run on startup is activated.')
				
				if envCmdAlreadyExist== True and writeFailed==False and updateFailed==False:
					cmds.gosavvyToolset()
					taskList.append('\nCommand to run GoSavvy Toolset:\nMEL -> gosavvyToolset;\nPython -> maya.cmds.gosavvyToolset()')
				elif envCmdAlreadyExist== False and writeFailed==False and updateFailed==False:
					taskList.append('Restart Maya To View GoSavvy Toolset')
					taskList.append('\nCommand to run GoSavvy Toolset:\nMEL -> gosavvyToolset;\nPython -> maya.cmds.gosavvyToolset()')
				if len(taskList) > 0:
					msg=''
					for task in taskList:
						msg= msg + task + '\n'
					msg= msg[:-1]
					if fresh==True:
						cmds.confirmDialog(t='Successfully Installed', m=msg)
					else:
						cmds.confirmDialog(t='Successfully Updated', m=msg)
							
gosavvyInstaller= Installer()
gosavvyInstaller.installerGUI()