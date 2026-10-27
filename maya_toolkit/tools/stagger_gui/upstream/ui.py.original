#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Stagger is a tool to automate staggers

Usage:
import stagger
try:
	from importlib import reload
except:
	pass
stagger.ui()
"""

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as Opm
import os


__author__ = 'Animation Creation'
__copyright__ = '2022, animationcreation.com'
__version__ = '1.1.0'
__status__ = 'Production'


# Constant variables
images_path = os.path.join(os.path.dirname(__file__), 'images')


# Commander
def commander(fn, *args, **kwargs):
	def commanded(*_, **__):
		fn(*args, **kwargs)
	return commanded


def stagger_it():
	# Get the start frame
	start_frame = cmds.intField('sf', query=True, value=True)
	# Get the end_frame
	end_frame = cmds.intField('ef', query=True, value=True)
	# Get the slider value
	sv = cmds.floatSlider('fl', query=True, value=True)
	# Get the selected objects
	selection = cmds.ls(selection=True)
	# Is the end frame greater than the start frame?
	if end_frame > start_frame:
		# Need a minimum of 4 frames
		if end_frame > start_frame + 2:
			# Is anything selected?
			if selection:
				# Get the window height
				window_height = cmds.window('stagger_window', query=True, height=True)
				# Expand the window for the progress bar
				cmds.window('stagger_window', edit=True, height=window_height + 20)
				# Get the animation curves
				anim_curves = cmds.keyframe(query=True, time=(':',), name=True)
				if anim_curves:
					for i in range(0, len(anim_curves)):
						amount = 100 * (float(i + 1) / len(anim_curves))
						cmds.progressBar('pb', edit=True, progress=amount, visible=True)
						# Insert keyframes on start_frame and end_frame to preserve animation outside the stagger range
						cmds.setKeyframe(anim_curves[i], time=start_frame, insert=True)
						cmds.setKeyframe(anim_curves[i], time=end_frame, insert=True)
						# Is there animation on the curves?
						values = cmds.keyframe(anim_curves[i], query=True, time=(start_frame, end_frame), valueChange=True)
						value = cmds.keyframe(anim_curves[i], query=True, valueChange=True)[0]
						if not all(item == value for item in values):
							key_values = []
							for f in range(start_frame, end_frame, 2):
								# Get the stagger values
								if f < end_frame - 3:
									# Offset values
									key_values.append(cmds.keyframe(anim_curves[i], query=True, eval=True, time=(f+sv, f+sv))[0])
									# Normal values
									key_values.append(cmds.keyframe(anim_curves[i], query=True, eval=True, time=(f+2, f+2))[0])
							# If the frame count is odd, pull value .5 frames before the end. There's got to be a better way than this
							if (end_frame - start_frame) & 1 == 1:
								key_values.append(cmds.keyframe(
									anim_curves[i],
									query=True,
									eval=True,
									time=(end_frame - .5, end_frame - .5))[0])
							# Ease into the last frame
							cmds.setKeyframe(anim_curves[i], time=end_frame - 1, insert=True)
							# Create the keyframes
							for frame, key_value in enumerate(key_values, start=1):
								cmds.setKeyframe(anim_curves[i], time=start_frame + frame, value=key_value)
					# Hide the progress bar
					cmds.progressBar('pb', edit=True, endProgress=True, visible=False)
					# Return the window to its previous size
					cmds.window('stagger_window', edit=True, height=window_height)
					Opm.MGlobal.displayInfo('Success!')
				else:
					Opm.MGlobal.displayWarning('No animation exists')
			else:
				Opm.MGlobal.displayWarning('Select something first')
		else:
			Opm.MGlobal.displayWarning('A minimum of 4 frames is needed for a stagger')
	else:
		Opm.MGlobal.displayWarning('The end frame must be later than the start frame')


def get_frame(f):
	# Check to see if a frame range is selected
	playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
	sf_ef = cmds.timeControl(playback_slider, query=True, rangeArray=True)
	if sf_ef[1] - sf_ef[0] == 1:
		# Return the value of the first frame into the frame field
		cmds.intField(f, edit=True, value=sf_ef[0])
	else:
		# Return the values of the range into the sf and ef field
		cmds.intField('sf', edit=True, value=sf_ef[0])
		cmds.intField('ef', edit=True, value=(sf_ef[1]-1))


def adjust_height():
	vertical_size = cmds.floatSlider('fl', query=True, value=True)
	cmds.window('stagger_window', edit=True, height=110+((vertical_size-3.1)*20))
	cmds.iconTextButton(
		'stagger_amount',
		edit=True,
		height=50+((vertical_size-3.1)*20),
	)
	cmds.formLayout('form', edit=True, attachForm=[('stagger_it', 'top', (vertical_size - 3.1)*10)])


def win():
	if cmds.window('stagger_window', exists=True):
		cmds.deleteUI('stagger_window', window=True)
	# Create the window
	cmds.window(
		'stagger_window',
		title="Stagger",
		toolbox=True,
		minimizeButton=False,
		maximizeButton=False,
		sizeable=False
	)
	# Create padding for the ui elements
	pad = 3
	# Create the column layout
	cmds.columnLayout(columnAttach=('both', 5), rowSpacing=2, adjustableColumn=True)
	cmds.separator(height=pad, style='none')
	# Create the start/end frame row
	cmds.rowLayout(
		numberOfColumns=4,
		columnWidth4=(45, 40, 40, 35),
		# columnAlign=(1, 'right'),
		columnAttach=[(1, 'right', 0), (2, 'both', 0), (3, 'both', 0), (4, 'left', 0)]
		)
	# Start frame
	cmds.iconTextButton(
		'start_frame',
		style='iconAndTextVertical',
		image=os.path.join(images_path, 'start.svg'),
		highlightImage=os.path.join(images_path, 'start_h.svg'),
		scaleIcon=True,
		width=45,
		height=25,
		command=commander(get_frame, 'sf')
	)
	cmds.intField('sf', value=00)
	# End frame
	cmds.intField('ef', value=00)
	cmds.iconTextButton(
		'end_frame',
		style='iconAndTextVertical',
		image=os.path.join(images_path, 'end.svg'),
		highlightImage=os.path.join(images_path, 'end_h.svg'),
		scaleIcon=True,
		width=35,
		height=25,
		command=commander(get_frame, 'ef')
	)
	cmds.setParent('..')
	# Stagger amount slider
	cmds.floatSlider('fl', min=2.2, max=4, value=3.1, dragCommand=commander(adjust_height))
	cmds.setParent('..')
	# Create a form layout to overlay graphics
	cmds.formLayout('form', numberOfDivisions=100)
	# Create the amount image
	cmds.iconTextButton(
		'stagger_amount',
		style='iconAndTextVertical',
		image=os.path.join(images_path, 'amount.svg'),
		scaleIcon=True,
		width=170,
		height=50,
		flat=True
	)
	# Create the stagger it button
	cmds.iconTextButton(
		'stagger_it',
		style='iconAndTextVertical',
		image=os.path.join(images_path, 'stagger_it.svg'),
		highlightImage=os.path.join(images_path, 'stagger_it_h.svg'),
		scaleIcon=True,
		width=170,
		height=50,
		command=commander(stagger_it)
	)
	# Progress bar
	cmds.separator(height=pad, style='none')
	cmds.progressBar('pb', highlightColor=[0.475, 0.761, 0.404], width=170, visible=False)
	cmds.formLayout('form', edit=True, attachControl=[('pb', 'top', pad, 'stagger_amount')])
	# Show the window
	cmds.window('stagger_window', edit=True, widthHeight=(180, 110))
	cmds.showWindow('stagger_window')
