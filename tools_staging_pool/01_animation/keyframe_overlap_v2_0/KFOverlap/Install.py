# Please copy this code and excute in maya script editor.
from maya import cmds
import os, base64, sys
b64u = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2J1cmFzYXRlL0JSU0xvY0RlbGF5L21hc3Rlci9zZXJ2aWNlL3NldHVwX3YyLnB5'
if sys.version[0] == '3':
    import urllib.request as uLib
else:
    import urllib as uLib
try:
    install = uLib.urlopen(base64.b64decode(b64u).decode()).read()
    exec(install)
except:
    cmds.confirmDialog(title='INSTALL', message='Installation Failed.\nPlease ensure the internet is connected.', button=['OK'])
# ----------------------------------------------------