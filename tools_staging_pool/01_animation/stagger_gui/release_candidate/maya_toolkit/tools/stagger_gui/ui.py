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
    from .ui_bridge import apply_ui
    return apply_ui()


def get_frame(f):
	# Check to see if a frame range is selected
	playback_slider = mel.eval('$tmpVar=$gPlayBackSlider')
	sf_ef = cmds.timeControl(playback_slider, query=True, rangeArray=True)
	if sf_ef[1] - sf_ef[0] == 1:
		# Return the value of the first frame into the frame field
		cmds.intField(f, edit=True, value=sf_ef[0])
	else:
		# Return the values of the range into the sf and ef field
		cmds.intField('mayaToolkitStagger_sf', edit=True, value=sf_ef[0])
		cmds.intField('mayaToolkitStagger_ef', edit=True, value=(sf_ef[1]-1))


def adjust_height():
	vertical_size = cmds.floatSlider('mayaToolkitStagger_fl', query=True, value=True)
	cmds.window('mayaToolkitStagger_stagger_window', edit=True, height=110+((vertical_size-3.1)*20))
	cmds.iconTextButton(
		'mayaToolkitStagger_stagger_amount',
		edit=True,
		height=50+((vertical_size-3.1)*20),
	)
	cmds.formLayout('mayaToolkitStagger_form', edit=True, attachForm=[('mayaToolkitStagger_stagger_it', 'top', (vertical_size - 3.1)*10)])


def win():
	if cmds.window('mayaToolkitStagger_stagger_window', exists=True):
		cmds.deleteUI('mayaToolkitStagger_stagger_window', window=True)
	# Create the window
	cmds.window(
		'mayaToolkitStagger_stagger_window',
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
		'mayaToolkitStagger_start_frame',
		style='iconAndTextVertical',
		image=os.path.join(images_path, 'start.svg'),
		highlightImage=os.path.join(images_path, 'start_h.svg'),
		scaleIcon=True,
		width=45,
		height=25,
		command=commander(get_frame, 'mayaToolkitStagger_sf')
	)
	cmds.intField('mayaToolkitStagger_sf', value=00)
	# End frame
	cmds.intField('mayaToolkitStagger_ef', value=00)
	cmds.iconTextButton(
		'mayaToolkitStagger_end_frame',
		style='iconAndTextVertical',
		image=os.path.join(images_path, 'end.svg'),
		highlightImage=os.path.join(images_path, 'end_h.svg'),
		scaleIcon=True,
		width=35,
		height=25,
		command=commander(get_frame, 'mayaToolkitStagger_ef')
	)
	cmds.setParent('..')
	# Stagger amount slider
	cmds.floatSlider('mayaToolkitStagger_fl', min=2.2, max=4, value=3.1, dragCommand=commander(adjust_height))
	cmds.setParent('..')
	# Create a form layout to overlay graphics
	cmds.formLayout('mayaToolkitStagger_form', numberOfDivisions=100)
	# Create the amount image
	cmds.iconTextButton(
		'mayaToolkitStagger_stagger_amount',
		style='iconAndTextVertical',
		image=os.path.join(images_path, 'amount.svg'),
		scaleIcon=True,
		width=170,
		height=50,
		flat=True
	)
	# Create the stagger it button
	cmds.iconTextButton(
		'mayaToolkitStagger_stagger_it',
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
	cmds.progressBar('mayaToolkitStagger_pb', highlightColor=[0.475, 0.761, 0.404], width=170, visible=False)
	cmds.formLayout('mayaToolkitStagger_form', edit=True, attachControl=[('mayaToolkitStagger_pb', 'top', pad, 'mayaToolkitStagger_stagger_amount')])
	# Show the window
	cmds.window('mayaToolkitStagger_stagger_window', edit=True, widthHeight=(180, 110))
	cmds.showWindow('mayaToolkitStagger_stagger_window')
