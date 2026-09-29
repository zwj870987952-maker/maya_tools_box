Run installer.py inside Maya Python Script Editor and install easily.

For Windows Maya 2020 and above, install Visual Studio 2019 Redistributable 64bit from:
https://aka.ms/vs/16/release/VC_redist.x64.exe

OR

Manual Install Process:

Copy the entire GoSavvy folder to

Windows- C:\Program Files\Autodesk\Maya20##\plug-ins\
Linux- /usr/autoesk/maya20##/plug-ins/

or any other path you may like.



Open Maya.env file in text editor. It can be found here:

Windows- C:\Users\username\Documents\maya\20##\Maya.env
Linux- /home/username/maya/20##/Maya.env

Add following line to Maya.env:

MAYA_PLUG_IN_PATH = C:\Program Files\Autodesk\Maya20##\plug-ins\GoSavvy

(DO NOT FORGET TO REPLACE ## WITH MAYA VERSION IN THE ABOVE LINE)



In Maya go to Windows > Settings/Preferences > Plug-In Manager and load plugin gosavvyToolset.mll



In python script editor use the following code:

maya.cmds.gosavvyToolset()

OR

In MEL script editor type:

gosavvyToolset;

For Windows Maya 2020 and above, install Visual Studio 2019 Redistributable 64bit from:
https://aka.ms/vs/16/release/VC_redist.x64.exe