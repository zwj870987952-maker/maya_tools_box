import maya.cmds as cmds
path= cmds.pluginInfo('gosavvyToolset.mll', q=True, p=True)
ind= path.rfind('/gosavvy')
path= path[:ind+1]+'customTools/'
msg= 'Install custom python scripts from HELP menu -> Custom Tools Installer\n\n'
msg= msg + 'OR\n\n' 
msg= msg + 'Add custom python scripts here:\n'+ path
cmds.confirmDialog(t='Add Custom Scripts', m= msg)
