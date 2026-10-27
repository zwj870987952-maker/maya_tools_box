################
### Overview ###
################

AnimPolish is a set of deformation tools that can be used on any polygon geometry in Maya 2015+,
whether or not it's animated. Some of the tools can also be used on nurbs curves. The tools are
intended to be used as a final step on finished animation. However, depending on your workflow,
you may still be able to update animation after working in the polish step. Hover over any UI
element to see summarized instructions about each tool.


​
####################
### Installation ###
####################

Installing AnimPolish is extremely simple since it does not use any plug-ins. This also means
you can install at most studios and schools, as well as at home. To install, simply unzip the
download and copy the "animPolish" directory into "maya/scripts". The end result should be
"maya/scripts/animPolish". The "maya" directory is usually found on your home drive or in
"Documents" on Windows. On Mac OS it is usually found in "Library/preferences/autodesk/maya/scripts".

In a fresh Maya session, copy/paste the following code into a Python tab of the script editor
and either run it or middle-mouse drag it to a shelf to make a button:


import animPolish.ui
try:
	from importlib import reload
except:
	pass
reload (animPolish.ui)
animPolish.ui.ui (dock = 1)


Or, if you find that you see UI bugs such as double buttons, try the following instead (running
this way will prevent docking):


import animPolish.ui
try:
	from importlib import reload
except:
	pass
reload (animPolish.ui)
animPolish.ui.ui (dock = 0)



##################################
### Note On Shared Directories ###
##################################

Dear TD: If multiple users run this tool from a shared directory, you might want to fill in the
custom "user_data_directory" variable at the top of "animPolish_ui.py". I'd recommend writing
some custom code above it to query the current user and concatenate a final path. If you don't,
the "Save/Load Settings" and "Copy/Paste Attrs" tools will end up overwriting eachother between
users.



#############
### Links ###
#############

Documentation:
https://docs.google.com/document/d/1wZ9YK99o3FRZpzjEoPXzcpPmpGOSfbl__VPGC60qM4Y/edit?usp=sharing

Contact:
https://www.friggingawesome.com/support