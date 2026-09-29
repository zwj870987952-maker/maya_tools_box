# SpeedLine Creator
# Version : v1.5
# Creation Date : 2021 / 06 / 25
# Last Updated : 2023 / 09 / 21
# Written By : Hao-Yu(Andy),Tung
# Email : aandy1208@gmail.com
# Website : https://hypercreative3d.blogspot.com/


----------


Usage :
Just place the tool under :
"C:\Users\YourUserName\Documents\maya\scripts"
Then run the code in Maya's script editor(python tab):

Maya 2020 -
import SpeedLine_Creator_v1_5_2020
SpeedLine_Creator_v1_5_2020.run()

Maya 2022 -
import SpeedLine_Creator_v1_5_2022
SpeedLine_Creator_v1_5_2022.run()

Maya 2023 -
import SpeedLine_Creator_v1_5_2023
SpeedLine_Creator_v1_5_2023.run()

Maya 2024 -
import SpeedLine_Creator_v1_5_2024
SpeedLine_Creator_v1_5_2024.run()

----------


Notice 1 : Considering the size of your scene, it will not automatically show the texture. You have to press 6 or click on the show texture button to see the SpeedLines after created.


Notice 2 : If you use the [Switch Target] or [Match + Switch] function, all the deformers and their attributes will be removed. You will need to create a new one for each of them to your own mesh if needed.(Return to Default button will bring all them back)


Notice 3 : This tool is initially designed for Layout use, which is mainly preview only, but in some cases would be great if it is possible for rendering. However, if some of the attribute values aren't in the proper range, it will cause a render warning, such as the Blur Attribute here. It can lead to rendering artifacts and numeric instability if in a weird value. It should be increased above 0.009 to avoid a render warning(NaN/inf) if the value causes a problem but is still needed for the result. Please notice that Gamma values(Blur attr here) typically range between 1.0(Default) and 2.2.

If there is no render required, just for playblast and preview use, then the value doesn't matter. It still can be rendered, but will always appear the warning. If you have a good solution for this mathematical issue, welcome to DM me.


----------


Tools Changing Log :

v1.0 :
• First Version Release

v1.1 :
• Added : Mask func

v1.2 :
• Added : Switch Target func
• Added : Match + Switch Target func
• Added : Assign Target func

v1.3 :
• Added : Attribute Selection func
• Added : Rig Groups Selection func
• Fixed : Assigning materials Bug

v1.4 :
• Added : Auto load plugins to avoid errors
• Added : Check target if skinned
• Edited : UI updated

v1.4.1 :
• Edited : Backend code edit (No difference to main functions)

v1.5 (Current Version) :
• Added : Twist func
• Added : Wave func
• Added : Amplitude func
• Added : Distortion attrs func
• Added : Invert Mask func
• Added : Mask Wave func
• Added : Mask Noise func
• Added : SpeedLine visibility func
• Added : Batch selections in list func
• Added : Return to Default func
• Added : Batch set all attrs to default func
• Added : Batch Copy-Paste attrs
• Added : Mesh Ctrl
• Edited : UI updated
• Edited : Mask Start / End value func
• Edited : Switch / Match / Assign method
• Edited : NoiseU Max range limitation
• Edited : Deformer's center position
• Edited : Main attr ctrl auto position
• Fixed : Now Rendable for all render engine
• Fixed : Bend attr issue when scene unit is meter
• Removed : Select button

