Shift_animation tool  

Author: Pavel Barnev pavel_barnev2000@mail.ru 

Installation: 

Quick Installation:

    unzip the file into a directory of choice

    Start Maya. 

    Drag file: 
	drag_and_drop_THIS_FILE_on_maya_window_for_install_Shift_animation_tool.mel 
	into a MAYA window. The script icon will appear on Custom tab on the Shelf Editor
 
This tool is for: 
	Most effective - working with motion capture
	Correction of moving animation without feet sliding
	Shifting animation without feet sliding
	Recalculating the animation from a different pose
	Rotating the animation without feet sliding

	
Basic principle of operation. 
	MATCH algorithm
	The script looks at which animation layer is selected.
	Determines what objects are in it.
	Determines how the objects moved with that layer, 
	and how they moved without it
	Based on this data, calculates the shift using its own algorithm
	The script works through the acceleration analysis algorithm. 
	In other words, the motion of the objects is distributed in such a way 
	so that the additional displacement in the layer will occur in the areas 
	when the object moves in the original animation.
	AUTOPATH algorithm
	The script looks at which animation layer is allocated.
	Determines what objects are in it.
	Determines how the objects moved with that layer, 
	and how they moved without it
	Determines the object against which the curve is plotted,
	and then recalculates all other objects along the curve.
	Records the result in a separate layer.
	MANUAL mode of operation does the same thing, but with the possibility to set the shape of the curve yourself.
Usage:
	Run the script
	select legs, main control and pelvis. 
	(depending on the task - it can be other objects)
	place them in a separate animation layer 
	(the script will process the objects in this animation layer).
	and in the layer move the objects as you like
	select the layer
	Click the "MATCH from animLayer" button.
	The script will recalculate the shift into the same animation layer.
	
Application Features.
	The more shifting of the legs will be in the animation 
	and the longer the animation - the better and smoother the result
	
	If you need to animation and shift and rotate at the same time 
	- it is better to do it in 2 times. 
	Separately shift, calculate, then in a new layer rotate, calculate.
	
	If you need to shift animation with hands 
	(for example, running on all fours, or jumping over an obstacle with the support of the hand)
	then in the initial layer put the hand as well.
	
	You can also make several shifts in a layer
	The script will analyze the gaps between the keys and calculate the shift.
	Attention! For the MATCH Algorithm, the tangents of the curves do not matter - only the values of the keys. 
	The shift between them is calculated linearly
	Try not to make these keys too often - it doesn't make sense
	
