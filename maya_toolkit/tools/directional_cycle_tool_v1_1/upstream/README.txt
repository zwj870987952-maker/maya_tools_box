Directional Cycle Tool - v1.1
By Baptiste COLIN (FallingNT0)

Do not hesitate to contact me if you spot any problems!

For PERSONAL and COMMERCIAL USES.
This work is licensed under CC BY-SA 4.0


### DESCRIPTION ###

Automatically generate left, right, and backward animations from your forward cycle.
- Bake results on a dedicated animation layer
- Customize feet angle 
- Supports any rig



### INSTALLATION ###

- Put the "DirectionalCycleTool" folder in your maya's script directory ("[...]\Documents\maya\scripts")
- In maya's script editor, put the command:
#
import importlib
import DirectionalCycleTool
importlib.reload(DirectionalCycleTool)
#
- Feel free to create a shelf button for it.


### HOW TO USE ###

- Select the controllers required by the script (in correct order!) and save them:
	- Master: the parent ctrl of all your controllers
	- Feet: the IK ctrls of the feet. Selection depends on the number you insert in the option "Feet Number"
	- Main Body: the ctrl that drives the body
	- Upperbody: the ctrl for the upper body (better result if in IK)
	- Head: the ctrl for the head
- Choose the angle the body angle will have relative to the forward direction. Affects the feet rotations too (only applies to left and right).
- Launch the side you want


### OPTIONS ###

- "Bake to layers": Will bake the result into an animation layer. If not, the controls will remain constrained to the locators.
- If you don't bake to layers, correction locators will be created and visible for each foot. You can move these locators to adjust the feet's overall position. 
- "Preserve feet position relative to body": The final positions of the feet will be based on the body rotation (body angle). Great if the offsets of the feet are too strong and break the pose. Recommended for non-biped characters. 


### BACKLOG ###

v1.1
- Add: Non-biped characters support
- Add: Correction locators when not baking to layers
- Add: Preserve feet position relative to body

v1.0
- Initial release