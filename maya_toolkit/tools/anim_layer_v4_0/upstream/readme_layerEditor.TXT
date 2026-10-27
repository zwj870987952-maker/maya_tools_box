put scripts in a folder C:\Users\<username>\Documents\maya\2018\scripts
and restart Maya

create_and_select_anim_layer(1); - creates a layer with the ability to choose a way to accumulate rotates (0 or 1)

create_anim_layer_from_channelbox_attrib(1); - create animLayer with selected channels in channelBox

extract_to_additive_layer(); - extract selected object to additive layer relatively current frame or framerange


setKeyframe -breakdown 0 -id -itt plateau  -ott plateau -dd true -hierarchy none -controlPoints 0 -shape 0;
- set 0 layer key


select_best_layer(); - select best layer for selected objects

select_object_in_selected_layers(); - select all objects contained in selected layers

anim_layer_util_menue() - recall menue with fastSmartBake, SmartExtractToOverride and other tools