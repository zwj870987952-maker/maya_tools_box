import os #line:1
import json #line:2
import ctypes #line:3
import logging #line:4
from PySide2 import QtCore ,QtWidgets ,QtGui #line:6
from shiboken2 import wrapInstance ,isValid #line:8
from maya import cmds #line:9
from maya .OpenMayaUI import MQtUtil #line:10
from maya .api import OpenMayaUI as omui ,OpenMaya as om #line:11
from uuid import getnode as get_mac #line:12
from pymel import versions #line:14
try :#line:17
	long #line:18
	PY =2 #line:19
except NameError :#line:20
	long =int #line:21
	PY =3 #line:22
log =logging .getLogger ("MayaTabs")#line:24
mayaTabsSerialWindowName ='mayaTabsSerial'#line:27
mayaTabsMainWindowName ='mayaTabsMain'#line:28
scriptPath =os .path .expanduser ("~/maya/plug-ins/Maya-Tabs_Files")#line:31
scriptPath23 =os .path .expanduser ("~/Documents/maya/plug-ins/Maya-Tabs_Files")#line:33
if os .path .exists (scriptPath23 ):#line:34
	scriptPath =scriptPath23 #line:35
mayaTabslogo =scriptPath +'/'+'Maya-Tabs.jpg'#line:38
mayaTabsIcon =scriptPath +'/'+'Maya-Tabs_icon.png'#line:39
mayaTabsIconSave =scriptPath +'/'+'icon_save.png'#line:40
mayaTabsIconOpen =scriptPath +'/'+'icon_open.png'#line:41
mayaTabsIconAdd =scriptPath +'/'+'icon_add.png'#line:42
mayaTabsThemesDir =scriptPath +'/'+'Themes'#line:44
mayaTabsSerialFile =scriptPath +'/'+'serial.cfg'#line:47
mayaTabsSerialConfigFile =scriptPath +'/'+'mayatabs_51x56.config'#line:48
mayaTabsSettingsFile =scriptPath +'/'+'Maya-Tabs.ini'#line:49
__ =type ("This",(object ,),{})()#line:52
__ .callbacks =[]#line:53
__ .settings_fname =mayaTabsSettingsFile #line:55
__ .new_tab =lambda O0OO0O0O0OOO000O0 :{"name":O0OO0O0O0OOO000O0 ,"fname":"","autosave":False ,"active":False ,"thumbnail":"",}#line:72
__ .default_style ={"width":"200","height":"25","tabColor":"#707070","tabColorActive":"#058888","tabColorHasFile":"#566f6f",}#line:80
__ .settings ={"version":"1.1.0","animated":True ,"tooltipDelay":10 ,"tabs":[__ .new_tab ("Tab-%d"%O00O0O00O0O0OO00O )for O00O0O00O0O0OO00O in range (8 )],"currentTabIndex":0 ,"lastSaveDir":os .path .expanduser ("~"),"style":dict (__ .default_style )}#line:104
__ .style ="""

Tab {
	min-width: %(width)s;
	min-height: %(height)s;
	margin-right: 5px;
	padding: 5px;
	border: 1px solid transparent;
	background: %(tabColor)s;
}

Tab[hasFile=true] {
	background: %(tabColorHasFile)s;
}

Tab[active=true] {
	background: %(tabColorActive)s;
	border: 1px solid #666666;
}

Tab[autosave=true][active=true] {
	background: #ff0000;
	border: 1px solid #ff5555;
}

Tab[autosave=true][active=false] {
	background: #8d1414;
	border: 1px solid transparent;
}

Tooltip {
	background: %(tabColorHasFile)s;
	padding: 5px;
}

"""#line:140
def _OOO00OO0O00000OO0 ():#line:143
	OO0OOO0OOOOOOOOOO =__ .settings_fname #line:144
	with open (OO0OOO0OOOOOOOOOO ,"w")as O00000OO0000O0000 :#line:145
		json .dump (__ .settings ,O00000OO0000O0000 ,sort_keys =True ,indent =4 )#line:146
def _OO0O000O0OO0O000O ():#line:149
	OO0OO00OO00O0O000 =__ .settings_fname #line:150
	try :#line:152
		log .info ("Reading settings for MayaTabs @ %s"%OO0OO00OO00O0O000 )#line:153
		with open (OO0OO00OO00O0O000 )as O0O00000OO0O00OO0 :#line:155
			__ .settings .update (json .load (O0O00000OO0O00OO0 ))#line:156
	except Exception :#line:158
		log .info ("Creating new settings for MayaTabs @ %s"%OO0OO00OO00O0O000 )#line:159
		with open (OO0OO00OO00O0O000 ,"w")as O0O00000OO0O00OO0 :#line:161
			json .dump (__ .settings ,O0O00000OO0O00OO0 ,sort_keys =True ,indent =4 )#line:162
__ .save =_OOO00OO0O00000OO0 #line:165
__ .load =_OO0O000O0OO0O000O #line:166
class Tab (QtWidgets .QPushButton ):#line:169
	entered =QtCore .Signal ()#line:170
	exited =QtCore .Signal ()#line:171
	ctrl_clicked =QtCore .Signal ()#line:172
	cleared =QtCore .Signal ()#line:173
	delete =QtCore .Signal ()#line:174
	open_folder =QtCore .Signal ()#line:175
	def mouseReleaseEvent (O00000OOOO0O0OOO0 ,OO0O00OOO0O00OO0O ):#line:177
		if OO0O00OOO0O00OO0O .button ()==QtCore .Qt .MiddleButton :#line:178
			O00000OOOO0O0OOO0 .cleared .emit ()#line:179
		if OO0O00OOO0O00OO0O .button ()==QtCore .Qt .LeftButton :#line:181
			if OO0O00OOO0O00OO0O .modifiers ()&QtCore .Qt .ControlModifier :#line:182
				O00000OOOO0O0OOO0 .ctrl_clicked .emit ()#line:183
				OO0O00OOO0O00OO0O .accept ()#line:184
		return super (Tab ,O00000OOOO0O0OOO0 ).mouseReleaseEvent (OO0O00OOO0O00OO0O )#line:186
	def enterEvent (O0000O00000OOO0O0 ,O000O00O000OOOO00 ):#line:188
		O0000O00000OOO0O0 .entered .emit ()#line:189
	def leaveEvent (O00OOO0O0OOO0O00O ,O0000O0OO0O000O0O ):#line:191
		O00OOO0O0OOO0O00O .exited .emit ()#line:192
	def contextMenuEvent (OO000OO00O0OO0OOO ,O00OOOOO0O000OOO0 ):#line:194
		OOOO00O0OOO00O0OO =QtWidgets .QMenu ()#line:195
		OOOOO000OO00000O0 =OOOO00O0OOO00O0OO .addAction ("Delete tab")#line:197
		O0O0O0OO0OOOO00O0 =OOOO00O0OOO00O0OO .addAction ("Clear tab")#line:198
		O0O0O00OOOOOO0O00 =OOOO00O0OOO00O0OO .addSeparator ()#line:199
		O000OOOOOOOOO00O0 =OOOO00O0OOO00O0OO .addAction ("Open Folder...")#line:200
		OOOOO000OO00000O0 .triggered .connect (OO000OO00O0OO0OOO .delete .emit )#line:202
		O0O0O0OO0OOOO00O0 .triggered .connect (OO000OO00O0OO0OOO .cleared .emit )#line:203
		O000OOOOOOOOO00O0 .triggered .connect (OO000OO00O0OO0OOO .open_folder .emit )#line:204
		OOOO00O0OOO00O0OO .move (QtGui .QCursor .pos ())#line:207
		OOOO00O0OOO00O0OO .exec_ ()#line:208
class Tooltip (QtWidgets .QLabel ):#line:211
	def __init__ (OOOOO0000OOO0O000 ,parent =None ):#line:212
		super (Tooltip ,OOOOO0000OOO0O000 ).__init__ (parent ,QtCore .Qt .ToolTip )#line:213
		OOOOO0000OOO0O000 .setScaledContents (True )#line:214
class MayaTabs (QtWidgets .QToolBar ):#line:217
	instance =None #line:218
	def __init__ (OOOOOO00OOO0O000O ,parent =None ):#line:220
		super (MayaTabs ,OOOOOO00OOO0O000O ).__init__ (parent )#line:221
		OOOOOO00OOO0O000O .setAttribute (QtCore .Qt .WA_StyledBackground )#line:222
		OOOOOO00OOO0O000O .setAttribute (QtCore .Qt .WA_DeleteOnClose )#line:223
		OOOOOO00OOO0O000O .setWindowTitle ("Maya Tabs")#line:224
		OOOO0OO0O0O0000OO =OOOOOO00OOO0O000O .addAction (QtGui .QIcon (mayaTabsIcon ),"Maya Tabs")#line:226
		O00O0OOOOO00OO000 =OOOOOO00OOO0O000O .addAction (QtGui .QIcon (mayaTabsIconOpen ),"Load")#line:227
		OOOO000OOOOO0O000 =OOOOOO00OOO0O000O .addAction (QtGui .QIcon (mayaTabsIconSave ),"Save")#line:228
		OO00O0O00000O0000 =OOOOOO00OOO0O000O .addAction (QtGui .QIcon (mayaTabsIconAdd ),"+")#line:229
		OOOO0OO0O0O0000OO .triggered .connect (OOOOOO00OOO0O000O .on_logo_session )#line:239
		O00O0OOOOO00OO000 .triggered .connect (OOOOOO00OOO0O000O .on_load_session )#line:240
		OOOO000OOOOO0O000 .triggered .connect (OOOOOO00OOO0O000O .on_save_session )#line:241
		OO00O0O00000O0000 .triggered .connect (OOOOOO00OOO0O000O .on_new_tab )#line:242
		O00O0OOOOO00OO000 .setToolTip ("Load a Maya Tabs session from disk")#line:244
		OOOO000OOOOO0O000 .setToolTip ("Save a Maya Tabs session to disk")#line:245
		OO00O0O00000O0000 .setToolTip ("Add a new tab")#line:246
		MayaTabs .instance =OOOOOO00OOO0O000O #line:249
		O0OOOO0O000000O0O =Tooltip (OOOOOO00OOO0O000O )#line:251
		O0OOOO0O000000O0O .hide ()#line:252
		OOOOOO00OOO0O000O ._tooltip =O0OOOO0O000000O0O #line:254
		OOOOOO00OOO0O000O ._slots =[]#line:255
		OOOOOO00OOO0O000O ._current_slot =None #line:256
		O000OO0O0OO0O00O0 =QtCore .QPropertyAnimation (O0OOOO0O000000O0O ,b"pos")#line:258
		O000OO0O0OO0O00O0 .setDuration (200 )#line:259
		O000OO0O0OO0O00O0 .setEasingCurve (QtCore .QEasingCurve .OutQuart )#line:260
		OOOOOO00OOO0O000O ._tooltip_anim =O000OO0O0OO0O00O0 #line:261
		OOOOOO00OOO0O000O ._tooltip_anim_firsttime =True #line:262
		OOOOOO00OOO0O000O .load_settings ()#line:264
		OOOOOO00OOO0O000O .refresh ()#line:265
	def on_new_tab (O0000000O00000O00 ):#line:267
		O00OOOO0000O0OOO0 =__ .new_tab ("New Tab")#line:268
		__ .settings ["tabs"]+=[O00OOOO0000O0OOO0 ]#line:269
		O0000000O00000O00 .save_settings ()#line:271
		O0000000O00000O00 .load_settings ()#line:272
	def on_logo_session (O0O000OO0OOO0000O ):#line:274
		guiMayaTabs ()#line:275
	def on_load_session (OO00OOOOOO0OO0000 ):#line:277
		O00O0000O00O00O00 ,O000OO0000O000O0O =QtWidgets .QFileDialog .getOpenFileName (OO00OOOOOO0OO0000 ,"Open Maya Tabs session",__ .settings ["lastSaveDir"],"Session files (*.tabs-session)")#line:283
		if not O00O0000O00O00O00 :#line:285
			return log .warning ("Cancelled")#line:286
		try :#line:288
			O000OO00O00OO0O00 =open (O00O0000O00O00O00 )#line:289
			OO00O000O0OO00000 =json .load (O000OO00O00OO0O00 )#line:290
		except Exception :#line:292
			import traceback #line:293
			traceback .print_exc ()#line:294
			return log .warning ("Couldn't load %s, ensure it is " "a valid Maya Tabs session"%O00O0000O00O00O00 )#line:298
		finally :#line:300
			O000OO00O00OO0O00 .close ()#line:301
		__ .settings ["lastSaveDir"]=os .path .dirname (O00O0000O00O00O00 )#line:304
		__ .settings ["tabs"]=OO00O000O0OO00000 #line:305
		__ .save ()#line:306
		OO00OOOOOO0OO0000 .load_settings ()#line:308
		for O0O00000O0000O0OO in OO00O000O0OO00000 :#line:310
			log .info ("Saving tab %s"%O0O00000O0000O0OO ["fname"])#line:311
		log .info ("Successfully loaded Maya Tabs session from %s"%O00O0000O00O00O00 )#line:313
	def on_save_session (O0O000OOOO0OO0O0O ):#line:315
		OO00000OO00O0OO00 ,O00O0000O00OO00O0 =QtWidgets .QFileDialog .getSaveFileName (O0O000OOOO0OO0O0O ,"Save Maya Tabs session",__ .settings ["lastSaveDir"],"Session files (*.tabs-session)")#line:321
		if OO00000OO00O0OO00 :#line:323
			OO0OO0O0OO0O0OOOO =__ .settings ["tabs"]#line:324
			with open (OO00000OO00O0OO00 ,"w")as OOO00OOO000O0000O :#line:325
				json .dump (OO0OO0O0OO0O0OOOO ,OOO00OOO000O0000O ,indent =4 ,sort_keys =True )#line:326
			for OOOO0O00O0OOOOOO0 in OO0OO0O0OO0O0OOOO :#line:328
				log .info ("Saving tab %s"%OOOO0O00O0OOOOOO0 ["name"])#line:329
			log .info ("Successfully saved Maya Tabs session to %s"%OO00000OO00O0OO00 )#line:331
		else :#line:332
			print ('No file selected')#line:333
	def on_slot_entered (OO00OOOO0O0000000 ):#line:335
		""#line:336
		O0O00OO00000O0O0O =OO00OOOO0O0000000 .sender ()#line:337
		OO00OOOO0O0000000 ._tooltip .hide ()#line:338
		OOOOO00000OOOO00O =O0O00OO00000O0O0O .property ("thumbnail")#line:340
		if not O0O00OO00000O0O0O .property ("active")and OOOOO00000OOOO00O :#line:342
			OO00OOOO0O0000000 ._tooltip .setPixmap (OOOOO00000OOOO00O )#line:343
			OO00000000O0O0O0O =float (OOOOO00000OOOO00O .height ())/OOOOO00000OOOO00O .width ()#line:346
			O0OO0O00O000OO00O =QtCore .QSize (O0O00OO00000O0O0O .width (),O0O00OO00000O0O0O .width ()*OO00000000O0O0O0O )#line:347
			OO000O0O0O00000OO =O0O00OO00000O0O0O .mapToGlobal (QtCore .QPoint (0 ,0 ))#line:348
			OO000O0O0O00000OO -=QtCore .QPoint (0 ,O0OO0O00O000OO00O .height ())#line:349
			OO000O0O0O00000OO -=QtCore .QPoint (0 ,5 )#line:350
			if OO00OOOO0O0000000 ._tooltip_anim_firsttime :#line:352
				OO00OOOO0O0000000 ._tooltip .move (OO000O0O0O00000OO +QtCore .QPoint (0 ,100 ))#line:353
				OO00OOOO0O0000000 ._tooltip_anim_firsttime =False #line:354
			if __ .settings .get ("animated"):#line:356
				OO00OOOO0O0000000 ._tooltip_anim .setEndValue (OO000O0O0O00000OO )#line:357
				OO00OOOO0O0000000 ._tooltip_anim .start ()#line:358
			else :#line:359
				OO00OOOO0O0000000 ._tooltip .move (OO000O0O0O00000OO )#line:360
			OO00OOOO0O0000000 ._tooltip .resize (O0OO0O00O000OO00O )#line:362
			QtCore .QTimer .singleShot (__ .settings .get ("tooltipDelay",10 ),OO00OOOO0O0000000 ._tooltip .show )#line:367
	def on_slot_exited (O0O00O0O0OO0O00OO ):#line:369
		""#line:370
		O0O00O0O0OO0O00OO ._tooltip .hide ()#line:371
	def refresh (O00O0000000OO0O00 ):#line:373
		O00O0000000OO0O00 ._tooltip .hide ()#line:374
		for OOOOO000OO0OOO0OO in O00O0000000OO0O00 ._slots :#line:376
			OOO00OOO0OO0O000O =OOOOO000OO0OOO0OO .property ("fname")#line:377
			O00OOO00O00O0OOO0 =os .path .basename (str (OOO00OOO0OO0O000O ))#line:378
			O00OOO00O00O0OOO0 =O00OOO00O00O0OOO0 .replace ('.mb','')#line:379
			OOOOO000OO0OOO0OO .setText (O00OOO00O00O0OOO0 or OOOOO000OO0OOO0OO .property ("name"))#line:380
			OOOOO000OO0OOO0OO .setToolTip (OOO00OOO0OO0O000O )#line:381
			OOOOO000OO0OOO0OO .setProperty ("active",OOOOO000OO0OOO0OO ==O00O0000000OO0O00 ._current_slot )#line:383
			OOOOO000OO0OOO0OO .setProperty ("autosave",OOOOO000OO0OOO0OO .property ("autosave"))#line:384
			OOOOO000OO0OOO0OO .setProperty ("hasFile",OOO00OOO0OO0O000O !="")#line:385
		OOOOO000O00O00OOO =__ .style %__ .settings .get ("style",__ .default_style )#line:387
		O00O0000000OO0O00 .setStyleSheet (OOOOO000O00O00OOO )#line:388
	def _save (O00000O00O0000O0O ):#line:390
		if not O00000O00O0000O0O .has_current_slot ():#line:391
			return #line:392
		O00O0000O00OOOO0O =O00000O00O0000O0O ._current_slot .property ("fname")#line:394
		if not O00O0000O00OOOO0O :#line:396
			O00OO00OOOO000OOO =("Maya Files (*.ma *.mb);;" "Maya ASCII (*.ma);;" "Maya Binary (*.mb);;" "All Files (*.*)")#line:402
			O00O0000O00OOOO0O =cmds .fileDialog2 (fileFilter =O00OO00OOOO000OOO ,dialogStyle =2 )#line:407
			if O00O0000O00OOOO0O :#line:409
				O00O0000O00OOOO0O =O00O0000O00OOOO0O [0 ]#line:410
			else :#line:411
				return log .warning ("Cancelled")#line:412
		cmds .file (rename =O00O0000O00OOOO0O )#line:414
		cmds .file (save =True ,force =True )#line:415
		return True #line:417
	def on_clear_clicked (O0OO0O00O0OOOOO00 ):#line:419
		OO0000OO0OOO0O000 =O0OO0O00O0OOOOO00 .sender ()#line:420
		if not OO0000OO0OOO0O000 .property ("fname"):#line:422
			O0OO0O00O0OOOOO00 .on_delete_clicked ()#line:423
			return #line:424
		OOO0O00OOOO0OOO00 =QtWidgets .QMessageBox (O0OO0O00O0OOOOO00 )#line:426
		OOO0O00OOOO0OOO00 .setStandardButtons (QtWidgets .QMessageBox .Ok |QtWidgets .QMessageBox .Cancel )#line:429
		OOO0O00OOOO0OOO00 .setWindowTitle ("Clear")#line:431
		OOO0O00OOOO0OOO00 .setText ("Clear tab %s"%(OO0000OO0OOO0O000 .property ("index")+1 ))#line:432
		if OOO0O00OOOO0OOO00 .exec_ ()==QtWidgets .QMessageBox .Cancel :#line:434
			return log .warning ("Cancelled")#line:435
		log .info ("Clearing %s"%OO0000OO0OOO0O000 .property ("name"))#line:437
		OO0000OO0OOO0O000 .setProperty ("fname","")#line:439
		OO0000OO0OOO0O000 .setProperty ("thumbnail","")#line:440
		OO0000OO0OOO0O000 .setProperty ("autosave",False )#line:441
		if OO0000OO0OOO0O000 ==O0OO0O00O0OOOOO00 ._current_slot :#line:443
			cmds .file (new =True ,force =True )#line:444
		O0OO0O00O0OOOOO00 .save_settings ()#line:446
		O0OO0O00O0OOOOO00 .refresh ()#line:447
	def on_ctrl_open_clicked (OO0OOOOOO0OOO0O00 ):#line:449
		O0O0OO0OO0OO00O0O =QtWidgets .QMessageBox (OO0OOOOOO0OOO0O00 )#line:450
		O0O0OO0OO0OO00O0O .setStandardButtons (QtWidgets .QMessageBox .Ok |QtWidgets .QMessageBox .Cancel )#line:453
		O0O0OO0OO0OO00O0O .setWindowTitle ("Maya Tabs Auto-Save")#line:455
		O00000O0O00OO0000 =OO0OOOOOO0OOO0O00 .sender ()#line:457
		if O00000O0O00OO0000 .property ("autosave"):#line:458
			O0O0OO0OO0OO00O0O .setText ("Disable auto-save?")#line:459
		else :#line:460
			O0O0OO0OO0OO00O0O .setText ("Enable auto-save?")#line:461
		if O0O0OO0OO0OO00O0O .exec_ ()==QtWidgets .QMessageBox .Ok :#line:463
			O00000O0O00OO0000 .setProperty ("autosave",not O00000O0O00OO0000 .property ("autosave"))#line:464
			OO0OOOOOO0OOO0O00 .save_settings ()#line:465
			OO0OOOOOO0OOO0O00 .on_open_clicked ()#line:466
		else :#line:467
			log .info ("Cancelled")#line:468
		OO0OOOOOO0OOO0O00 .refresh ()#line:470
	def has_current_slot (OOOO00OOOO0OOOOOO ):#line:472
		return OOOO00OOOO0OOOOOO ._current_slot is not None and isValid (OOOO00OOOO0OOOOOO ._current_slot )#line:473
	def on_open_clicked (OOOO0O00O0O0000O0 ):#line:475
		O000O0OOO0O000O0O =OOOO0O00O0O0000O0 .sender ()#line:476
		if O000O0OOO0O000O0O ==OOOO0O00O0O0000O0 ._current_slot :#line:478
			return #line:479
		O000OOOOOOO000O00 =O000O0OOO0O000O0O .property ("fname")#line:481
		OO0O00OOO00O00OO0 =O000O0OOO0O000O0O .property ("index")#line:482
		OOOO0O0OO000OOOOO =cmds .file (query =True ,modified =True )#line:484
		if OOOO0O0OO000OOOOO and OOOO0O00O0O0000O0 .has_current_slot ():#line:486
			if OOOO0O00O0O0000O0 ._current_slot .property ("autosave"):#line:487
				if not OOOO0O00O0O0000O0 ._save ():#line:488
					return #line:489
			else :#line:491
				OOOOOO0000OO0O0O0 =QtWidgets .QMessageBox (OOOO0O00O0O0000O0 )#line:492
				OOOOOO0000OO0O0O0 .setStandardButtons (QtWidgets .QMessageBox .Save |QtWidgets .QMessageBox .Discard |QtWidgets .QMessageBox .Cancel )#line:497
				O0OO0O000OOO00O00 =OOOO0O00O0O0000O0 ._current_slot .property ("fname")#line:499
				OOOOOO0000OO0O0O0 .setWindowTitle ("Warning: Scene not saved")#line:500
				OOOOOO0000OO0O0O0 .setText ("Save changes to %s?"%(O0OO0O000OOO00O00 or "untitled scene"))#line:502
				OO0OO0O0O00O0000O =OOOOOO0000OO0O0O0 .exec_ ()#line:504
				if OO0OO0O0O00O0000O ==QtWidgets .QMessageBox .Save :#line:506
					if not OOOO0O00O0O0000O0 ._save ():#line:507
						return #line:508
				elif OO0OO0O0O00O0000O ==QtWidgets .QMessageBox .Cancel :#line:510
					return log .warning ("Cancelled")#line:511
		if O000OOOOOOO000O00 :#line:513
			log .info ("Opening %s.."%O000OOOOOOO000O00 )#line:514
			cmds .file (O000OOOOOOO000O00 ,open =True ,force =True ,ignoreVersion =True )#line:515
		else :#line:517
			log .info ("Starting new scene @ slot %d"%(OO0O00OOO00O00OO0 +1 ))#line:518
			cmds .file (new =True ,force =True )#line:519
		OOOO0O00O0O0000O0 ._current_slot =O000O0OOO0O000O0O #line:521
		OOOO0O00O0O0000O0 .refresh ()#line:522
	def on_new (O0O0OO000OOO00OOO ):#line:524
		if not O0O0OO000OOO00OOO .has_current_slot ():#line:525
			return #line:526
		log .info ("New tab")#line:528
		O0O0OO000OOO00OOO ._current_slot .setProperty ("fname","")#line:530
		O0O0OO000OOO00OOO ._current_slot .setProperty ("thumbnail","")#line:531
		O0O0OO000OOO00OOO .save_settings ()#line:533
		O0O0OO000OOO00OOO .refresh ()#line:534
	def on_open (OOOOOO00O0OOOO000 ,O0OO00O0OO0O0O000 ):#line:536
		if not OOOOOO00O0OOOO000 .has_current_slot ():#line:537
			return #line:538
		log .info ("Opening tab %s"%O0OO00O0OO0O0O000 )#line:540
		OOOOOO00O0OOOO000 ._current_slot .setProperty ("fname",O0OO00O0OO0O0O000 )#line:542
		OOO0000O00OO0O0O0 =OOOOOO00O0OOOO000 ._view_to_pixmap ()#line:544
		OOOOOO00O0OOOO000 ._current_slot .setProperty ("thumbnail",OOO0000O00OO0O0O0 )#line:545
		OOOOOO00O0OOOO000 .save_settings ()#line:547
		OOOOOO00O0OOOO000 .refresh ()#line:548
	def on_save (O0O0OOO0OOOOO0OOO ,O0000OO00O000O0O0 ):#line:550
		if not O0O0OOO0OOOOO0OOO .has_current_slot ():#line:551
			return #line:552
		log .info ("Saving tab %s"%O0000OO00O000O0O0 )#line:554
		O0O0OOO0OOOOO0OOO ._current_slot .setProperty ("fname",O0000OO00O000O0O0 )#line:556
		O0000OOO0OO0O00O0 =O0O0OOO0OOOOO0OOO ._view_to_pixmap ()#line:558
		O0O0OOO0OOOOO0OOO ._current_slot .setProperty ("thumbnail",O0000OOO0OO0O00O0 )#line:559
		O0O0OOO0OOOOO0OOO .save_settings ()#line:561
		O0O0OOO0OOOOO0OOO .refresh ()#line:562
	def on_delete_clicked (O00O00O0O000000OO ):#line:564
		O0OOO00O00O00OO00 =O00O00O0O000000OO .sender ()#line:565
		OO00OOOOO0O0OOOO0 ="Nothing"#line:567
		for OO0OOO0O000O00O0O in list (O00O00O0O000000OO ._slots ):#line:569
			if OO0OOO0O000O00O0O !=O0OOO00O00O00OO00 :#line:570
				continue #line:571
			OO0000O0OOOO0O000 =OO0OOO0O000O00O0O .property ("index")#line:573
			OO00000O0O0O0O00O =__ .settings ["tabs"].pop (OO0000O0OOOO0O000 )#line:574
			OO00OOOOO0O0OOOO0 =O0OOO00O00O00OO00 .property ("fname")#line:576
			O00O00O0O000000OO ._slots .remove (O0OOO00O00O00OO00 )#line:577
			log .info ("Deleted %s"%OO00000O0O0O0O00O ["fname"])#line:578
			if O0OOO00O00O00OO00 ==O00O00O0O000000OO ._current_slot :#line:580
				O00O00O0O000000OO ._current_slot =None #line:581
			O0OOO00O00O00OO00 .deleteLater ()#line:583
		O00O00O0O000000OO .save_settings ()#line:585
		O00O00O0O000000OO .load_settings ()#line:586
	def on_open_folder (O00OO0OOOOOOO00O0 ):#line:589
		O000OO0O00000O000 =O00OO0OOOOOOO00O0 .sender ()#line:590
		O0O0OOOOO000OO0OO =O000OO0O00000O000 .property ("fname")#line:591
		OO0O0O0OOO000O0OO =os .path .dirname (O0O0OOOOO000OO0OO )#line:592
		if OO0O0O0OOO000O0OO :#line:593
			os .startfile (OO0O0O0OOO000O0OO )#line:594
	def load_settings (OO0OOOO0OO0O0O0OO ):#line:598
		""#line:599
		__ .load ()#line:600
		for O00O0OO0OO0O0000O in OO0OOOO0OO0O0O0OO ._slots :#line:602
			O00O0OO0OO0O0000O .deleteLater ()#line:603
		OO0OOOO0OO0O0O0OO ._slots [:]=[]#line:605
		O0OOOOO000000000O =cmds .file (query =True ,sceneName =True )#line:607
		for O0O0OO0O00O0OO0OO ,OOOOOOOOO0OO00OOO in enumerate (__ .settings ["tabs"]):#line:609
			O00O0OO0OO0O0000O =Tab ()#line:610
			O00O0OO0OO0O0000O .setProperty ("name",OOOOOOOOO0OO00OOO ["name"])#line:611
			O00O0OO0OO0O0000O .setProperty ("index",O0O0OO0O00O0OO0OO )#line:612
			O00O0OO0OO0O0000O .clicked .connect (OO0OOOO0OO0O0O0OO .on_open_clicked )#line:614
			O00O0OO0OO0O0000O .cleared .connect (OO0OOOO0OO0O0O0OO .on_clear_clicked )#line:615
			O00O0OO0OO0O0000O .open_folder .connect (OO0OOOO0OO0O0O0OO .on_open_folder )#line:616
			O00O0OO0OO0O0000O .ctrl_clicked .connect (OO0OOOO0OO0O0O0OO .on_ctrl_open_clicked )#line:617
			O00O0OO0OO0O0000O .delete .connect (OO0OOOO0OO0O0O0OO .on_delete_clicked )#line:618
			O00O0OO0OO0O0000O .entered .connect (OO0OOOO0OO0O0O0OO .on_slot_entered )#line:621
			O00O0OO0OO0O0000O .exited .connect (OO0OOOO0OO0O0O0OO .on_slot_exited )#line:622
			OO0OOOO0OO0O0O0OO .addWidget (O00O0OO0OO0O0000O )#line:624
			OO0OOOO0OO0O0O0OO ._slots .append (O00O0OO0OO0O0000O )#line:625
			O0000O000O0O0OO00 =os .path .basename (OOOOOOOOO0OO00OOO ["fname"])or OOOOOOOOO0OO00OOO ["name"]#line:627
			O00O0OO0OO0O0000O .setText (O0000O000O0O0OO00 )#line:628
			O00O0OO0OO0O0000O .setProperty ("fname",OOOOOOOOO0OO00OOO ["fname"])#line:629
			O00O0OO0OO0O0000O .setProperty ("hasFile",OOOOOOOOO0OO00OOO ["fname"]!="")#line:630
			O00O0OO0OO0O0000O .setProperty ("autosave",OOOOOOOOO0OO00OOO ["autosave"])#line:631
			O00O0OO0OO0O0000O .setProperty ("active",all ([OOOOOOOOO0OO00OOO ["fname"]==O0OOOOO000000000O ,O0OOOOO000000000O ,]))#line:639
			if OOOOOOOOO0OO00OOO ["fname"]!=""and "thumbnail"in OOOOOOOOO0OO00OOO and OOOOOOOOO0OO00OOO ["thumbnail"]:#line:641
				try :#line:642
					O0OOO000O0000OOO0 =OOOOOOOOO0OO00OOO ["thumbnail"].encode ()#line:643
					O0O0000O0O00O0000 =QtCore .QByteArray .fromBase64 (O0OOO000O0000OOO0 )#line:644
					O0O00OO000000OOOO =QtGui .QPixmap ()#line:645
					O0O00OO000000OOOO .loadFromData (O0O0000O0O00O0000 )#line:646
					O00O0OO0OO0O0000O .setProperty ("thumbnail",O0O00OO000000OOOO )#line:647
				except Exception :#line:649
					import traceback #line:650
					traceback .print_exc ()#line:651
					log .info ("Unable to load thumbnail for %s"%OOOOOOOOO0OO00OOO ["fname"])#line:652
			if O00O0OO0OO0O0000O .property ("active"):#line:654
				OO0OOOO0OO0O0O0OO ._current_slot =O00O0OO0OO0O0000O #line:655
		OO0OOOO0OO0O0O0OO .refresh ()#line:657
	def save_settings (OOO0OOO0000OO0O00 ):#line:659
		""#line:660
		for OOOO00OOO000OO0OO ,O0O0O00OOO0OOO0OO in enumerate (OOO0OOO0000OO0O00 ._slots ):#line:662
			O0OO000OO0O00OOO0 =__ .settings ["tabs"][OOOO00OOO000OO0OO ]#line:663
			O0OO000OO0O00OOO0 ["fname"]=O0O0O00OOO0OOO0OO .property ("fname")#line:664
			O0OO000OO0O00OOO0 ["autosave"]=O0O0O00OOO0OOO0OO .property ("autosave")#line:665
			OOO00OO0000O0OOOO =O0O0O00OOO0OOO0OO .property ("thumbnail")#line:666
			if OOO00OO0000O0OOOO :#line:668
				O0OO000OO0O00OOO0 ["thumbnail"]=OOO0OOO0000OO0O00 ._serialise_thumnail (OOO00OO0000O0OOOO )#line:669
		if OOO0OOO0000OO0O00 .has_current_slot ():#line:671
			O000OOO00OOOO00OO =OOO0OOO0000OO0O00 ._current_slot .property ("index")#line:672
			__ .settings ["currentTabIndex"]=O000OOO00OOOO00OO #line:673
		__ .save ()#line:675
		with open (__ .settings_fname ,"w")as OO0O0OOOO000OOO00 :#line:676
			json .dump (__ .settings ,OO0O0OOOO000OOO00 ,sort_keys =True ,indent =4 )#line:677
	def _serialise_thumnail (O000O00O0O0O00O0O ,OOO0O00OOO00OO0OO ):#line:679
		""#line:680
		O00O0OOO0000OOO00 =QtCore .QByteArray ()#line:681
		OOOOOOO0OOOOO0O00 =QtCore .QBuffer (O00O0OOO0000OOO00 )#line:682
		OOOOOOO0OOOOO0O00 .open (QtCore .QIODevice .WriteOnly )#line:684
		OOO0O00OOO00OO0OO .save (OOOOOOO0OOOOO0O00 ,"png")#line:685
		if PY ==2 :#line:687
			return str (O00O0OOO0000OOO00 .toBase64 ())#line:688
		else :#line:689
			return str (O00O0OOO0000OOO00 .toBase64 (),"utf-8")#line:691
	def _view_to_pixmap (O0OO0OOOO0OOO0O00 ):#line:693
		""#line:694
		O0O000O000OO0O0OO =om .MImage ()#line:696
		O00O00O0000O0OO0O =omui .M3dView .active3dView ()#line:697
		O00O00O0000O0OO0O .readColorBuffer (O0O000O000OO0O0OO ,True )#line:698
		O0O000O000OO0O0OO .verticalFlip ()#line:701
		O00O00O000O0000OO =O0O000O000OO0O0OO .getSize ()#line:703
		OOOO000O00O000O0O =ctypes .c_ubyte *O00O00O000O0000OO [0 ]*O00O00O000O0000OO [1 ]#line:704
		OOOO000O00O000O0O =OOOO000O00O000O0O .from_address (long (O0O000O000OO0O0OO .pixels ()))#line:705
		O00OOO0OO0OOO0000 =QtGui .QImage (OOOO000O00O000O0O ,O00O00O000O0000OO [0 ],O00O00O000O0000OO [1 ],QtGui .QImage .Format_RGB32 ).rgbSwapped ()#line:709
		return QtGui .QPixmap .fromImage (O00OOO0OO0OOO0000 ).scaled (512 ,256 ,QtCore .Qt .KeepAspectRatio ,QtCore .Qt .SmoothTransformation )#line:713
def m2mLoadSettings (setting ='',settingsFile ='settings'):#line:715
	OO00O00O0OO0000OO =''#line:716
	if settingsFile =='settings':#line:717
		OO00O00O0OO0000OO =m2mSettingsFile #line:718
	if settingsFile =='ser':#line:719
		OO00O00O0OO0000OO =m2mSerialFile #line:720
	try :#line:721
		with open (OO00O00O0OO0000OO ,'r')as O0O00O00O0OO00O0O :#line:722
			OO0OO0000OO0O000O =O0O00O00O0OO00O0O .readlines ()#line:723
			for OOOO00O000OO0O0O0 in OO0OO0000OO0O000O :#line:724
				if setting in OOOO00O000OO0O0O0 :#line:725
					O000OO0O0OOOOOO00 =OOOO00O000OO0O0O0 .split ('=')#line:726
					return O000OO0O0OOOOOO00 [1 ].rstrip ('\n')#line:727
	except :#line:728
		print ('error loading settings')#line:729
srl =None #line:731
try :#line:732
	srl =m2mLoadSettings ('Serial','ser').rstrip ('\n')#line:733
except :#line:734
	srl =None #line:735
	print ("Serial Load Error")#line:736
def addToClipBoard (OO0OOOOOO0OOO0OO0 ):#line:738
	O0O00OO00OOO00000 ='echo '+OO0OOOOOO0OOO0OO0 .strip (' \t\n\r')+'| clip'#line:739
	os .system (O0O00OO00OOO00000 )#line:740
def chkSrl (OO0000O0O000O0OOO ):#line:742
	O000O0OO0O000O0OO =get_mac ()#line:743
	OO0O0O00OO00OO000 =str (O000O0OO0O000O0OO )[2 :4 ]#line:745
	O0O0OO00OOOOO0O0O =str (O000O0OO0O000O0OO )[6 :8 ]#line:746
	OO00OOOOO00000OO0 =str (O000O0OO0O000O0OO )[1 :3 ]#line:747
	OO0OOOOOO0000O0O0 =OO0000O0O000O0OOO [3 :5 ]#line:749
	O0O00OO0OOO00O00O =OO0000O0O000O0OOO [6 :8 ]#line:750
	OOOOOO00OOO0000O0 =OO0000O0O000O0OOO [10 :12 ]#line:751
	OOO00OOOOOOOO00O0 ='xxx'#line:753
	OOO00OO0OO0OO0O0O ='x'#line:754
	O00OOOO00O000000O ='xx'#line:755
	O000000OO0O0O00O0 ='xxx'+OO00OOOOO00000OO0 +'x'+OO0O0O00OO00OO000 +'xx'+O0O0OO00OOOOO0O0O #line:757
	if OO0OOOOOO0000O0O0 ==OO00OOOOO00000OO0 and O0O00OO0OOO00O00O ==OO0O0O00OO00OO000 and OOOOOO00OOO0000O0 ==O0O0OO00OOOOO0O0O :#line:759
		return True #line:760
	else :#line:761
		return False #line:762
def versionCheck ():#line:764
	print ("Version check...")#line:765
	O0O0000O0O00OOOOO =str (versions .current ())#line:766
	print (O0O0000O0O00OOOOO )#line:767
	O0OOO0OOOOOO00O0O =['2014','2015','2016','2017','2018','2019','2020','2022']#line:768
	for OO0OOOOOO0OO0OO00 in O0OOO0OOOOOO00O0O :#line:769
		if OO0OOOOOO0OO0OO00 in O0O0000O0O00OOOOO :#line:770
			print ("Maya Tabs: Supported Version")#line:771
			return True #line:772
	O00O0OO0OOOO00000 ="Maya Version not Supported. Please visit www.3DtoAll.com"#line:774
	cmds .confirmDialog (title ='Maya Tabs',message =O00O0OO0OOOO00000 ,button =['Ok'],defaultButton ='Yes',cancelButton ='No',dismissString ='No')#line:775
	return False #line:776
def guiSerial ():#line:778
	def OO0OO0OO0O00O0000 ():#line:781
		OOOOOO00O0OO0O00O =get_mac ()#line:782
		OO0O0O00OO000O00O =str (OOOOOO00O0OO0O00O )[2 :4 ]#line:783
		O0OOOOO00O0O000OO =str (OOOOOO00O0OO0O00O )[6 :8 ]#line:784
		O0O0OOOO0O0O0O00O =str (OOOOOO00O0OO0O00O )[1 :3 ]#line:785
		O0OOOOO00OOOO0OOO ='MTB'#line:786
		O00000OOO000O00OO ='V1Y'#line:787
		OOO000OO00O0000O0 ='TAB'#line:788
		O0OOOOO0O0OO0OO00 ='09H'#line:789
		OO000O0OOO000O000 =O0OOOOO00OOOO0OOO +OO0O0O00OO000O00O +O00000OOO000O00OO +O0OOOOO00O0O000OO +OOO000OO00O0000O0 +O0O0OOOO0O0O0O00O #line:791
		return OO000O0OOO000O000 #line:793
	def OOO0O0OO0OO00O00O ():#line:795
		O0O0000O000OO0OOO =cmds .textField ("txtFieldCode",query =True ,text =True )#line:796
		addToClipBoard (O0O0000O000OO0OOO )#line:797
	def OOO0OO000OO000OOO ():#line:799
		cmds .launch (web ="http://www.3dtoall.com/register")#line:800
	def O0OO00OOO0OO0OO00 ():#line:802
		O0O00OO0O00OO0O00 =cmds .textField (O0000OO000O0O0000 ,q =True ,tx =True )#line:803
		O0O00OO0O00OO0O00 =O0O00OO0O00OO0O00 .replace (' ','')#line:804
		if chkSrl (O0O00OO0O00OO0O00 )==True :#line:806
			with open (mayaTabsSerialFile ,'w')as OO00OO000OOO0000O :#line:807
				OO00OO000OOO0000O .write ('Serial='+O0O00OO0O00OO0O00 +'\n')#line:808
			with open (mayaTabsSerialConfigFile ,'w')as OO00OO000OOO0000O :#line:810
				OO00OO000OOO0000O .write ('Serial='+O0O00OO0O00OO0O00 +'\n')#line:811
			print ('- Maya Tabs Activated -')#line:813
			try :#line:815
				cmds .deleteUI (mayaTabsSerialWindowName )#line:816
			except :#line:817
				pass #line:818
			install_toolbar ()#line:819
			install_callbacks ()#line:820
		else :#line:821
			cmds .confirmDialog (title ='Maya Tabs',message ='Activation Problem. Please try again or contact support.',button =['Ok'],defaultButton ='Yes',cancelButton ='No',dismissString ='No')#line:822
	try :#line:828
		O0OO000O0OO0O0000 =cmds .window ("mayatabsSerial",query =True ,title =True )#line:829
	except :#line:830
		pass #line:831
	try :#line:832
		cmds .deleteUI (mainWindowName )#line:833
	except Exception as OO0OOOOO0O00O00O0 :#line:834
		pass #line:835
	try :#line:836
		cmds .deleteUI (mayaTabsSerialWindowName )#line:837
	except Exception as OO0OOOOO0O00O00O0 :#line:838
		pass #line:839
	O0O0OOO000000O00O =cmds .window (mayaTabsSerialWindowName ,toolbox =True ,maximizeButton =False ,minimizeButton =False ,sizeable =False ,title ="Maya Tabs",widthHeight =(343 ,310 ))#line:841
	OOO00OOO0000OOOO0 =cmds .formLayout (numberOfDivisions =100 )#line:842
	OO00000O0O0OO0000 =cmds .image (image =mayaTabslogo ,backgroundColor =(0.392157 ,0.862745 ,1 ),w =343 ,h =88 )#line:844
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(OO00000O0O0OO0000 ,'top',0 ),(OO00000O0O0OO0000 ,'left',0 )])#line:845
	OO00000O0O0OO0000 =cmds .text (label ="Your Code:",w =115 ,h =21 )#line:847
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(OO00000O0O0OO0000 ,'top',90 ),(OO00000O0O0OO0000 ,'left',115 )])#line:848
	OOOOO00O000OOOO00 =cmds .textField ("txtFieldCode",tx =OO0OO0OO0O00O0000 (),font ='boldLabelFont',editable =False ,width =150 )#line:850
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(OOOOO00O000OOOO00 ,'top',115 ),(OOOOO00O000OOOO00 ,'left',50 )])#line:851
	OO00000O00O0O0OO0 =cmds .button (label ='Copy to Clipboard',width =120 ,c =lambda *O00O0O0OOOO0000O0 :OOO0O0OO0OO00O00O (),height =20 )#line:853
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(OO00000O00O0O0OO0 ,'top',115 ),(OO00000O00O0O0OO0 ,'left',175 )])#line:854
	OO000OOO00000OO0O =cmds .button (label ='Get Activation Serial',width =260 ,c =lambda *OO00OO00OO00OO0OO :OOO0OO000OO000OOO (),height =25 )#line:856
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(OO000OOO00000OO0O ,'top',142 ),(OO000OOO00000OO0O ,'left',45 )])#line:857
	OO00000O0O0OO0000 =cmds .separator (style ='in',w =325 ,h =6 )#line:859
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(OO00000O0O0OO0000 ,'top',175 ),(OO00000O0O0OO0000 ,'left',10 )])#line:860
	O00OO0O0O0O0OOO0O =cmds .text (label ='Enter your Maya Tabs serial here:')#line:862
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(O00OO0O0O0O0OOO0O ,'top',188 ),(O00OO0O0O0O0OOO0O ,'left',85 )])#line:863
	O0000OO000O0O0000 =cmds .textField ("txtFieldSerialEnter",tx ="",width =210 )#line:865
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(O0000OO000O0O0000 ,'top',206 ),(O0000OO000O0O0000 ,'left',70 )])#line:866
	OO00O0O0O000O0000 =cmds .button (label ='ACTIVATE',command =lambda *OO00O0OO0000O00O0 :O0OO00OOO0OO0OO00 (),height =40 ,width =210 )#line:868
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(OO00O0O0O000O0000 ,'top',232 ),(OO00O0O0O000O0000 ,'left',70 )])#line:869
	OO00000O0O0OO0000 =cmds .separator (style ='in',w =325 ,h =6 )#line:871
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(OO00000O0O0OO0000 ,'top',280 ),(OO00000O0O0OO0000 ,'left',10 )])#line:872
	OO0O00O0OOO00O0O0 =cmds .text (label ='(c) 2022 3DtoAll. All Rights Reserved.')#line:874
	cmds .formLayout (OOO00OOO0000OOOO0 ,edit =True ,attachForm =[(OO0O00O0OOO00O0O0 ,'top',290 ),(OO0O00O0OOO00O0O0 ,'left',85 )])#line:875
	cmds .showWindow (O0O0OOO000000O00O )#line:877
	cmds .window (O0O0OOO000000O00O ,e =True ,width =335 ,height =312 )#line:878
def guiMayaTabs ():#line:881
	def O00OOOOO00OO0OOO0 (OOOO00OOO00O000O0 ):#line:882
		OO000000000O0O0OO =[]#line:883
		for O00O0O0OOO000OOO0 in (0 ,2 ,4 ):#line:884
			O0000000O000O0O00 =int (OOOO00OOO00O000O0 [O00O0O0OOO000OOO0 :O00O0O0OOO000OOO0 +2 ],16 )#line:885
			OO000000000O0O0OO .append (O0000000O000O0O00 )#line:886
		return tuple (OO000000000O0O0OO )#line:888
	def O0OO0OOO0O000O000 (OOOO0O0000O00O000 ):#line:890
		OO00OO000OOO0OO00 =int (OOOO0O0000O00O000 [0 ]*255 )#line:891
		OOO000000OO0O0O0O =int (OOOO0O0000O00O000 [1 ]*255 )#line:892
		O0OO0O000OO0O000O =int (OOOO0O0000O00O000 [2 ]*255 )#line:893
		print ("--------------")#line:895
		return '#%02x%02x%02x'%(OO00OO000OOO0OO00 ,OOO000000OO0O0O0O ,O0OO0O000OO0O000O )#line:896
	def OOOO0OO0OO00O0000 ():#line:898
		import json #line:899
		O0000OOO000000000 =open (mayaTabsSettingsFile ,"r")#line:901
		OO0OO000OO00OO0O0 =json .loads (O0000OOO000000000 .read ())#line:904
		O00OO0OO00O0O0OO0 =OO0OO000OO00OO0O0 ['style']['height']#line:907
		O0000000O0O0O0O0O =OO0OO000OO00OO0O0 ['style']['width']#line:908
		if O00OO0OO00O0O0OO0 =="20":cmds .optionMenu ("menuTabsHeight",e =True ,sl =1 )#line:910
		if O00OO0OO00O0O0OO0 =="35":cmds .optionMenu ("menuTabsHeight",e =True ,sl =2 )#line:911
		if O00OO0OO00O0O0OO0 =="60":cmds .optionMenu ("menuTabsHeight",e =True ,sl =3 )#line:912
		if O0000000O0O0O0O0O =="10":cmds .optionMenu ("menuTabsWidth",e =True ,sl =1 )#line:914
		if O0000000O0O0O0O0O =="50":cmds .optionMenu ("menuTabsWidth",e =True ,sl =2 )#line:915
		if O0000000O0O0O0O0O =="100":cmds .optionMenu ("menuTabsWidth",e =True ,sl =3 )#line:916
		if O0000000O0O0O0O0O =="150":cmds .optionMenu ("menuTabsWidth",e =True ,sl =4 )#line:917
		if O0000000O0O0O0O0O =="200":cmds .optionMenu ("menuTabsWidth",e =True ,sl =5 )#line:918
		O000000OOO0OO0O00 =OO0OO000OO00OO0O0 ['style']['tabColorActive']#line:920
		O0OOO0OOOO0OOOOO0 =O00OOOOO00OO0OOO0 (O000000OOO0OO0O00 .lstrip ('#'))#line:921
		cmds .button (OOOO000OOO0000OOO ,edit =True ,bgc =[O0OOO0OOOO0OOOOO0 [0 ]/255 ,O0OOO0OOOO0OOOOO0 [1 ]/255 ,O0OOO0OOOO0OOOOO0 [2 ]/255 ])#line:922
		O000000OOO0OO0O00 =OO0OO000OO00OO0O0 ['style']['tabColorHasFile']#line:924
		O0OOO0OOOO0OOOOO0 =O00OOOOO00OO0OOO0 (O000000OOO0OO0O00 .lstrip ('#'))#line:925
		cmds .button (O00OOOOOO0OO0OO00 ,edit =True ,bgc =[O0OOO0OOOO0OOOOO0 [0 ]/255 ,O0OOO0OOOO0OOOOO0 [1 ]/255 ,O0OOO0OOOO0OOOOO0 [2 ]/255 ])#line:926
		O000000OOO0OO0O00 =OO0OO000OO00OO0O0 ['style']['tabColor']#line:928
		O0OOO0OOOO0OOOOO0 =O00OOOOO00OO0OOO0 (O000000OOO0OO0O00 .lstrip ('#'))#line:929
		cmds .button (O0OOOOO00OOO0O000 ,edit =True ,bgc =[O0OOO0OOOO0OOOOO0 [0 ]/255 ,O0OOO0OOOO0OOOOO0 [1 ]/255 ,O0OOO0OOOO0OOOOO0 [2 ]/255 ])#line:930
		O0000OOO000000000 .close ()#line:933
	def O00000000OO0000O0 ():#line:937
		O0OOO00000O000000 =open (mayaTabsSettingsFile ,"r")#line:939
		OO0OOOOO0O00O0000 =json .load (O0OOO00000O000000 )#line:940
		O0OOO00000O000000 .close ()#line:941
		OOO00OOOO00OOOOOO =cmds .optionMenu (O0000O000O0O00O0O ,query =True ,value =True )#line:943
		O0O0OOO00OO0000OO =cmds .optionMenu (O0O0OO00OOO000OOO ,query =True ,value =True )#line:944
		O00O0O000OOOO0000 =O0OO0OOO0O000O000 (cmds .button (OOOO000OOO0000OOO ,query =True ,bgc =True ))#line:945
		O00OO0O0O0OO00OOO =O0OO0OOO0O000O000 (cmds .button (O00OOOOOO0OO0OO00 ,query =True ,bgc =True ))#line:946
		O000O000000000OOO =O0OO0OOO0O000O000 (cmds .button (O0OOOOO00OOO0O000 ,query =True ,bgc =True ))#line:947
		OO0OOOOO0O00O0000 ['style']['height']=OOO00OOOO00OOOOOO #line:951
		OO0OOOOO0O00O0000 ['style']['width']=O0O0OOO00OO0000OO #line:952
		OO0OOOOO0O00O0000 ['style']['tabColorActive']=O00O0O000OOOO0000 #line:953
		OO0OOOOO0O00O0000 ['style']['tabColorHasFile']=O00OO0O0O0OO00OOO #line:954
		OO0OOOOO0O00O0000 ['style']['tabColor']=O000O000000000OOO #line:955
		O0OOO00000O000000 =open (mayaTabsSettingsFile ,"w+")#line:958
		O0OOO00000O000000 .write (json .dumps (OO0OOOOO0O00O0000 ))#line:959
		O0OOO00000O000000 .close ()#line:960
		uninstall_toolbar ()#line:963
		install_toolbar ()#line:964
	def OOO0OO00OOO0OO000 ():#line:966
		O0OOOO000OO0O000O =cmds .button (OOOO000OOO0000OOO ,query =True ,bgc =True )#line:967
		cmds .colorEditor (rgbValue =[O0OOOO000OO0O000O [0 ],O0OOOO000OO0O000O [1 ],O0OOOO000OO0O000O [2 ]])#line:968
		if cmds .colorEditor (query =True ,result =True ):#line:969
			OO00OOOO0O000O00O =cmds .colorEditor (query =True ,rgb =True )#line:970
			cmds .button (OOOO000OOO0000OOO ,edit =True ,bgc =[OO00OOOO0O000O00O [0 ],OO00OOOO0O000O00O [1 ],OO00OOOO0O000O00O [2 ]])#line:971
			O00000000OO0000O0 ()#line:972
		else :#line:973
			print ('Editor was dismissed')#line:974
	def O0O000O0O00O0O0OO ():#line:976
		OOOOOO00000OO0O0O =cmds .button (O00OOOOOO0OO0OO00 ,query =True ,bgc =True )#line:977
		cmds .colorEditor (rgbValue =[OOOOOO00000OO0O0O [0 ],OOOOOO00000OO0O0O [1 ],OOOOOO00000OO0O0O [2 ]])#line:978
		if cmds .colorEditor (query =True ,result =True ):#line:979
			O0000O00O0000000O =cmds .colorEditor (query =True ,rgb =True )#line:980
			cmds .button (O00OOOOOO0OO0OO00 ,edit =True ,bgc =[O0000O00O0000000O [0 ],O0000O00O0000000O [1 ],O0000O00O0000000O [2 ]])#line:981
			O00000000OO0000O0 ()#line:982
		else :#line:983
			print ('Editor was dismissed')#line:984
	def O0OO00O00O0O00O00 ():#line:987
		OO00O00OOO0OO0000 =cmds .button (O0OOOOO00OOO0O000 ,query =True ,bgc =True )#line:988
		cmds .colorEditor (rgbValue =[OO00O00OOO0OO0000 [0 ],OO00O00OOO0OO0000 [1 ],OO00O00OOO0OO0000 [2 ]])#line:989
		if cmds .colorEditor (query =True ,result =True ):#line:990
			O0O0OOO0OOO0O000O =cmds .colorEditor (query =True ,rgb =True )#line:991
			cmds .button (O0OOOOO00OOO0O000 ,edit =True ,bgc =[O0O0OOO0OOO0O000O [0 ],O0O0OOO0OOO0O000O [1 ],O0O0OOO0OOO0O000O [2 ]])#line:992
			O00000000OO0000O0 ()#line:993
		else :#line:994
			print ('Editor was dismissed')#line:995
	def O0OOO000000O0OO00 ():#line:998
		O0O000O0O0O0O0O0O =cmds .button (btnTabBorderColor ,query =True ,bgc =True )#line:999
		cmds .colorEditor (rgbValue =[O0O000O0O0O0O0O0O [0 ],O0O000O0O0O0O0O0O [1 ],O0O000O0O0O0O0O0O [2 ]])#line:1000
		if cmds .colorEditor (query =True ,result =True ):#line:1001
			OO0O0OOO0OOOOOOO0 =cmds .colorEditor (query =True ,rgb =True )#line:1002
			cmds .button (btnTabBorderColor ,edit =True ,bgc =[OO0O0OOO0OOOOOOO0 [0 ],OO0O0OOO0OOOOOOO0 [1 ],OO0O0OOO0OOOOOOO0 [2 ]])#line:1003
			O00000000OO0000O0 ()#line:1004
		else :#line:1005
			print ('Editor was dismissed')#line:1006
	def O0OO0O0O00OO0O00O ():#line:1009
		OO0OO0O0O0O0OOO0O =None #line:1010
		OO0O0OO0OOO00O00O ,O0O000OOO000OO00O =QtWidgets .QFileDialog .getSaveFileName (None ,"Save Maya Tabs Theme",mayaTabsThemesDir ,"Theme (*.mttheme)")#line:1016
		if OO0O0OO0OOO00O00O :#line:1019
			try :#line:1020
				O00O0OOOO00O000O0 =O0OO0OOO0O000O000 (cmds .button (OOOO000OOO0000OOO ,query =True ,bgc =True ))#line:1021
				O00OO0000OO0000OO =O0OO0OOO0O000O000 (cmds .button (O00OOOOOO0OO0OO00 ,query =True ,bgc =True ))#line:1022
				OOOO0000O0O000000 =O0OO0OOO0O000O000 (cmds .button (O0OOOOO00OOO0O000 ,query =True ,bgc =True ))#line:1023
				O00OOOO0OO0000OO0 ={}#line:1026
				OOO0OO0O00O000OOO ="100"#line:1029
				if cmds .optionMenu ("menuTabsWidth",query =True ,sl =True )==1 :OOO0OO0O00O000OOO ="10"#line:1030
				if cmds .optionMenu ("menuTabsWidth",query =True ,sl =True )==2 :OOO0OO0O00O000OOO ="50"#line:1031
				if cmds .optionMenu ("menuTabsWidth",query =True ,sl =True )==3 :OOO0OO0O00O000OOO ="100"#line:1032
				if cmds .optionMenu ("menuTabsWidth",query =True ,sl =True )==4 :OOO0OO0O00O000OOO ="150"#line:1033
				if cmds .optionMenu ("menuTabsWidth",query =True ,sl =True )==5 :OOO0OO0O00O000OOO ="200"#line:1034
				O000O00O00O0OO00O ="20"#line:1035
				if cmds .optionMenu ("menuTabsHeight",query =True ,sl =True )==1 :O000O00O00O0OO00O ="20"#line:1036
				if cmds .optionMenu ("menuTabsHeight",query =True ,sl =True )==2 :O000O00O00O0OO00O ="35"#line:1037
				if cmds .optionMenu ("menuTabsHeight",query =True ,sl =True )==3 :O000O00O00O0OO00O ="60"#line:1038
				O00OOOO0OO0000OO0 ['size']={'height':O000O00O00O0OO00O ,'width':OOO0OO0O00O000OOO }#line:1040
				O00OOOO0OO0000OO0 ['style']={'active':O00O0OOOO00O000O0 ,'inactive':O00OO0000OO0000OO ,"empty":OOOO0000O0O000000 }#line:1041
				with open (OO0O0OO0OOO00O00O ,'w')as O000000OO00O0O0OO :#line:1043
					json .dump (O00OOOO0OO0000OO0 ,O000000OO00O0O0OO )#line:1044
			except :#line:1045
				print ('Error saving Theme File')#line:1046
	def OO0OO00OOOOO0O0OO ():#line:1048
		OOOOOO0O0000O0OO0 ,O0000O0OOOO00OOOO =QtWidgets .QFileDialog .getOpenFileName (None ,"Load Maya Tabs Theme",mayaTabsThemesDir ,"Theme (*.mttheme)")#line:1054
		if OOOOOO0O0000O0OO0 :#line:1055
			try :#line:1056
				O0000OOOO000O00O0 =open (OOOOOO0O0000O0OO0 )#line:1057
				O0OO000O0OO0OO00O =json .load (O0000OOOO000O00O0 )#line:1058
				O00OO0O00OOO0O000 =O0OO000O0OO0OO00O ['size']['height']#line:1060
				OOO0OO0O0OO0O000O =O0OO000O0OO0OO00O ['size']['width']#line:1061
				O0000OOOO000O00O0 .close ()#line:1064
				print ('=='*50 )#line:1067
				print ('readTabHeight',O00OO0O00OOO0O000 )#line:1068
				print ('readTabWidth',OOO0OO0O0OO0O000O )#line:1069
				print ('=='*50 )#line:1070
				if O00OO0O00OOO0O000 =="20":cmds .optionMenu ("menuTabsHeight",e =True ,sl =1 )#line:1072
				if O00OO0O00OOO0O000 =="35":cmds .optionMenu ("menuTabsHeight",e =True ,sl =2 )#line:1073
				if O00OO0O00OOO0O000 =="60":cmds .optionMenu ("menuTabsHeight",e =True ,sl =3 )#line:1074
				if OOO0OO0O0OO0O000O =="10":cmds .optionMenu ("menuTabsWidth",e =True ,sl =1 )#line:1076
				if OOO0OO0O0OO0O000O =="50":cmds .optionMenu ("menuTabsWidth",e =True ,sl =2 )#line:1077
				if OOO0OO0O0OO0O000O =="100":cmds .optionMenu ("menuTabsWidth",e =True ,sl =3 )#line:1078
				if OOO0OO0O0OO0O000O =="150":cmds .optionMenu ("menuTabsWidth",e =True ,sl =4 )#line:1079
				if OOO0OO0O0OO0O000O =="200":cmds .optionMenu ("menuTabsWidth",e =True ,sl =5 )#line:1080
				OO000O0O0OO000000 =O0OO000O0OO0OO00O ['style']['active']#line:1082
				OO00OO0O0O00O000O =O00OOOOO00OO0OOO0 (OO000O0O0OO000000 .lstrip ('#'))#line:1083
				cmds .button (OOOO000OOO0000OOO ,edit =True ,bgc =[OO00OO0O0O00O000O [0 ]/255 ,OO00OO0O0O00O000O [1 ]/255 ,OO00OO0O0O00O000O [2 ]/255 ])#line:1084
				OO000O0O0OO000000 =O0OO000O0OO0OO00O ['style']['inactive']#line:1086
				OO00OO0O0O00O000O =O00OOOOO00OO0OOO0 (OO000O0O0OO000000 .lstrip ('#'))#line:1087
				cmds .button (O00OOOOOO0OO0OO00 ,edit =True ,bgc =[OO00OO0O0O00O000O [0 ]/255 ,OO00OO0O0O00O000O [1 ]/255 ,OO00OO0O0O00O000O [2 ]/255 ])#line:1088
				OO000O0O0OO000000 =O0OO000O0OO0OO00O ['style']['empty']#line:1090
				OO00OO0O0O00O000O =O00OOOOO00OO0OOO0 (OO000O0O0OO000000 .lstrip ('#'))#line:1091
				cmds .button (O0OOOOO00OOO0O000 ,edit =True ,bgc =[OO00OO0O0O00O000O [0 ]/255 ,OO00OO0O0O00O000O [1 ]/255 ,OO00OO0O0O00O000O [2 ]/255 ])#line:1092
				O00000000OO0000O0 ()#line:1094
				print ("finished")#line:1095
			except :#line:1096
				print ('Error reading Theme File')#line:1097
	def OOO0O0O00OOO0OO00 ():#line:1099
		try :#line:1100
			OO00O0OO0O000OO00 ="#4c8758"#line:1101
			O0OO0O00000OOO000 =O00OOOOO00OO0OOO0 (OO00O0OO0O000OO00 .lstrip ('#'))#line:1102
			cmds .button (OOOO000OOO0000OOO ,edit =True ,bgc =[O0OO0O00000OOO000 [0 ]/255 ,O0OO0O00000OOO000 [1 ]/255 ,O0OO0O00000OOO000 [2 ]/255 ])#line:1103
			OO00O0OO0O000OO00 ="#3e6170"#line:1105
			O0OO0O00000OOO000 =O00OOOOO00OO0OOO0 (OO00O0OO0O000OO00 .lstrip ('#'))#line:1106
			cmds .button (O00OOOOOO0OO0OO00 ,edit =True ,bgc =[O0OO0O00000OOO000 [0 ]/255 ,O0OO0O00000OOO000 [1 ]/255 ,O0OO0O00000OOO000 [2 ]/255 ])#line:1107
			OO00O0OO0O000OO00 ="#212324"#line:1109
			O0OO0O00000OOO000 =O00OOOOO00OO0OOO0 (OO00O0OO0O000OO00 .lstrip ('#'))#line:1110
			cmds .button (O0OOOOO00OOO0O000 ,edit =True ,bgc =[O0OO0O00000OOO000 [0 ]/255 ,O0OO0O00000OOO000 [1 ]/255 ,O0OO0O00000OOO000 [2 ]/255 ])#line:1111
			cmds .optionMenu ("menuTabsHeight",e =True ,sl =1 )#line:1113
			cmds .optionMenu ("menuTabsWidth",e =True ,sl =4 )#line:1114
			O00000000OO0000O0 ()#line:1116
		except :#line:1117
			print ("Can't load Defaults")#line:1118
	def O000O000OO0OOO00O (O0000OOO0OO000O00 ):#line:1121
		O00000000OO0000O0 ()#line:1122
	def O0000O0OOOO000OOO ():#line:1125
		cmds .launch (web ="http://www.3dtoall.com")#line:1126
	def OO000OO00OO00OOOO ():#line:1128
		try :#line:1129
			cmds .deleteUI (mayaTabsMainWindowName )#line:1130
		except :#line:1131
			print ("can't close")#line:1132
	try :#line:1137
		O0OOOOOOOOOO0O0OO =cmds .window ("mayatabsMain",query =True ,title =True )#line:1138
	except :#line:1139
		pass #line:1140
	try :#line:1141
		cmds .deleteUI (mainWindowName )#line:1142
	except Exception as OO0O0OO0O00O0O0O0 :#line:1143
		pass #line:1144
	try :#line:1145
		cmds .deleteUI (mayaTabsMainWindowName )#line:1146
	except Exception as OO0O0OO0O00O0O0O0 :#line:1147
		pass #line:1148
	O0O000O000OOOO000 =cmds .window (mayaTabsMainWindowName ,toolbox =True ,maximizeButton =False ,minimizeButton =False ,sizeable =False ,title ="Maya Tabs",widthHeight =(343 ,340 ))#line:1150
	OOO0O0000O0O00000 =cmds .formLayout (numberOfDivisions =100 )#line:1151
	O000O0OOOO00O0OOO =cmds .image (image =mayaTabslogo ,backgroundColor =(0.392157 ,0.862745 ,1 ),w =343 ,h =88 )#line:1154
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(O000O0OOOO00O0OOO ,'top',0 ),(O000O0OOOO00O0OOO ,'left',0 )])#line:1155
	OO0O0OOO0OOOO00O0 =cmds .text (label ='Theme Editor:')#line:1158
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(OO0O0OOO0OOOO00O0 ,'top',100 ),(OO0O0OOO0OOOO00O0 ,'left',25 )])#line:1159
	O000O0OOOO00O0OOO =cmds .separator (style ='in',w =220 ,h =6 )#line:1161
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(O000O0OOOO00O0OOO ,'top',105 ),(O000O0OOOO00O0OOO ,'left',105 )])#line:1162
	OO000OOOO0000OO00 =20 #line:1164
	OOOO00OOO00OO0OOO =5 #line:1165
	OOOO000OOO0000OOO =cmds .button (label ='Active',width =60 ,c =lambda *OOOOO0000O00OO0OO :OOO0OO00OOO0OO000 (),height =25 )#line:1167
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(OOOO000OOO0000OOO ,'top',120 +OOOO00OOO00OO0OOO ),(OOOO000OOO0000OOO ,'left',162 +OO000OOOO0000OO00 )])#line:1168
	O00OOOOOO0OO0OO00 =cmds .button (label ='Inactive',width =60 ,c =lambda *OO0000O0O0OO000O0 :O0O000O0O00O0O0OO (),height =25 )#line:1170
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(O00OOOOOO0OO0OO00 ,'top',120 +OOOO00OOO00OO0OOO ),(O00OOOOOO0OO0OO00 ,'left',226 +OO000OOOO0000OO00 )])#line:1171
	O0OOOOO00OOO0O000 =cmds .button (label ='Empty',width =124 ,c =lambda *O0OO0OO0000O0OOO0 :O0OO00O00O0O00O00 (),height =25 )#line:1173
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(O0OOOOO00OOO0O000 ,'top',149 +OOOO00OOO00OO0OOO ),(O0OOOOO00OOO0O000 ,'left',162 +OO000OOOO0000OO00 )])#line:1174
	O0O0OO00OOO000OOO =cmds .optionMenu ("menuTabsWidth",w =120 ,label ="Tabs Width: ",changeCommand =O000O000OO0OOO00O )#line:1180
	cmds .menuItem (O0O0OO00OOO000OOO ,label ="10")#line:1181
	cmds .menuItem (O0O0OO00OOO000OOO ,label ="50")#line:1182
	cmds .menuItem (O0O0OO00OOO000OOO ,label ="100")#line:1183
	cmds .menuItem (O0O0OO00OOO000OOO ,label ="150")#line:1184
	cmds .menuItem (O0O0OO00OOO000OOO ,label ="200")#line:1185
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(O0O0OO00OOO000OOO ,'top',121 +OOOO00OOO00OO0OOO ),(O0O0OO00OOO000OOO ,'left',20 +OO000OOOO0000OO00 )])#line:1186
	O0000O000O0O00O0O =cmds .optionMenu ("menuTabsHeight",w =120 ,label ="Tabs Height:",changeCommand =O000O000OO0OOO00O )#line:1188
	cmds .menuItem (O0O0OO00OOO000OOO ,label ="20")#line:1189
	cmds .menuItem (O0O0OO00OOO000OOO ,label ="35")#line:1190
	cmds .menuItem (O0O0OO00OOO000OOO ,label ="60")#line:1191
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(O0000O000O0O00O0O ,'top',150 +OOOO00OOO00OO0OOO ),(O0000O000O0O00O0O ,'left',20 +OO000OOOO0000OO00 )])#line:1192
	OOOO00OOO00OO0OOO =-60 #line:1202
	OO00O000OO0OOO00O =cmds .button (label ='Load Theme...',width =90 ,c =lambda *O0O0OOOO000O0OO00 :OO0OO00OOOOO0O0OO (),height =25 )#line:1203
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(OO00O000OO0OOO00O ,'top',256 +OOOO00OOO00OO0OOO ),(OO00O000OO0OOO00O ,'left',27 )])#line:1204
	OO00000OOO00OO000 =cmds .button (label ='Save Theme...',width =90 ,c =lambda *O000OOO0OOOO000OO :O0OO0O0O00OO0O00O (),height =25 )#line:1206
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(OO00000OOO00OO000 ,'top',256 +OOOO00OOO00OO0OOO ),(OO00000OOO00OO000 ,'left',123 )])#line:1207
	OO0OOOO000O000O00 =cmds .button (label ='Reset',width =85 ,c =lambda *O0O0O0O00OO00O000 :OOO0O0O00OOO0OO00 (),height =25 )#line:1209
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(OO0OOOO000O000O00 ,'top',256 +OOOO00OOO00OO0OOO ),(OO0OOOO000O000O00 ,'left',219 )])#line:1210
	O000O0OOOO00O0OOO =cmds .separator (style ='in',w =315 ,h =6 )#line:1214
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(O000O0OOOO00O0OOO ,'top',288 +OOOO00OOO00OO0OOO ),(O000O0OOOO00O0OOO ,'left',10 )])#line:1215
	OO0O00OO00O0O000O =cmds .button (label ='Ok',command =lambda *OO0000O0OOO00O00O :OO000OO00OO00OOOO (),height =40 ,width =146 )#line:1217
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(OO0O00OO00O0O000O ,'top',305 +OOOO00OOO00OO0OOO ),(OO0O00OO00O0O000O ,'left',176 -5 )])#line:1218
	OOOO0O0000O00O0O0 =cmds .button (label ='Visit 3dtoall.com...',command =lambda *O00OOO00O000OO0O0 :O0000O0OOOO000OOO (),height =40 ,width =146 )#line:1220
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(OOOO0O0000O00O0O0 ,'top',305 +OOOO00OOO00OO0OOO ),(OOOO0O0000O00O0O0 ,'left',24 -5 )])#line:1221
	O000O0OOOO00O0OOO =cmds .separator (style ='in',w =315 ,h =6 )#line:1223
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(O000O0OOOO00O0OOO ,'top',353 +OOOO00OOO00OO0OOO ),(O000O0OOOO00O0OOO ,'left',10 )])#line:1224
	O0OOOO0O00OOO00O0 =cmds .text (label ='(c) 2021 3DtoAll. All Rights Reserved.')#line:1226
	cmds .formLayout (OOO0O0000O0O00000 ,edit =True ,attachForm =[(O0OOOO0O00OOO00O0 ,'top',366 +OOOO00OOO00OO0OOO ),(O0OOOO0O00OOO00O0 ,'left',85 )])#line:1227
	cmds .showWindow (O0O000O000OOOO000 )#line:1229
	cmds .window (O0O000O000OOOO000 ,e =True ,width =335 ,height =330 )#line:1230
	print ("START FORM!")#line:1232
	OOOO0OO0OO00O0000 ()#line:1233
def install ():#line:1238
	def O0OOO0O0OO0O0O00O ():#line:1239
		O0OO00000OOO0OO0O =str (versions .current ())#line:1240
		OO000000OO0OO000O =['2014','2015','2016','2017','2018','2019','2020','2022','2023']#line:1241
		for O00O000O00OO000OO in OO000000OO0OO000O :#line:1242
			if O00O000O00OO000OO in O0OO00000OOO0OO0O :#line:1243
				return True #line:1244
		OO0OO0OOO00O00O00 ="Maya Version not Supported. Please visit www.3DtoAll.com"#line:1246
		cmds .confirmDialog (title ="Maya-Tabs",message =OO0OO0OOO00O00O00 ,button =['Ok'],defaultButton ='Yes',cancelButton ='No',dismissString ='No')#line:1247
		return False #line:1248
	if O0OOO0O0OO0O0O00O ()==True :#line:1250
		if os .path .exists (mayaTabsSerialConfigFile )==True :#line:1251
			install_toolbar ()#line:1252
			install_callbacks ()#line:1253
		else :#line:1254
			if srl !=None and O0OOO0O0OO0O0O00O ()==True :#line:1255
				if chkSrl (srl )==True :#line:1256
					install_toolbar ()#line:1257
					install_callbacks ()#line:1258
				else :#line:1259
					guiSerial ()#line:1260
			if srl ==None or chkSrl ==False :#line:1261
				guiSerial ()#line:1262
def uninstall ():#line:1267
	uninstall_callbacks ()#line:1268
	uninstall_toolbar ()#line:1269
def install_toolbar ():#line:1272
	uninstall_toolbar ()#line:1273
	OOO0O0O00O000O0OO =MayaTabs ()#line:1275
	OO00O000O00OOOO0O =MQtUtil .mainWindow ()#line:1278
	OO00O000O00OOOO0O =long (OO00O000O00OOOO0O )#line:1280
	O0O0O00000O0O0O00 =wrapInstance (OO00O000O00OOOO0O ,QtWidgets .QMainWindow )#line:1281
	O0O0O00000O0O0O00 .addToolBar (QtCore .Qt .BottomToolBarArea ,OOO0O0O00O000O0OO )#line:1282
	OOO0O0O00O000O0OO .show ()#line:1284
	OOO0O0O00O000O0OO .setFocus ()#line:1285
	return OOO0O0O00O000O0OO #line:1287
def uninstall_toolbar ():#line:1290
	if MayaTabs .instance is not None :#line:1291
		MayaTabs .instance .deleteLater ()#line:1292
		MayaTabs .instance =None #line:1293
def _O00OO0OO0O0O00OOO (*O0O0OO0000O0O0000 ):#line:1296
	O0OO0000OO0000O00 =MayaTabs .instance #line:1297
	O0OO0000OO0000O00 .on_new ()#line:1298
def _O000000OOO0O0O000 (*O00O00O0000OO0OOO ):#line:1301
	OOOOOOO0OOOO00O0O =MayaTabs .instance #line:1302
	OO00O000OO00O0O0O =cmds .file (query =True ,sceneName =True )#line:1303
	OOOOOOO0OOOO00O0O .on_save (OO00O000OO00O0O0O )#line:1304
def _O0O0OOO0O0OO0O000 (*OOO0OOO0OOO0OOO0O ):#line:1307
	OOO0OO000000O00OO =MayaTabs .instance #line:1308
	O0O0O0000O0O0OOOO =cmds .file (query =True ,sceneName =True )#line:1309
	OOO0OO000000O00OO .on_open (O0O0O0000O0O0OOOO )#line:1310
def install_callbacks ():#line:1313
	__ .callbacks .append (om .MSceneMessage .addCallback (om .MSceneMessage .kAfterSave ,lambda *O0OO0OOOOOO0O0OOO :cmds .evalDeferred (_O000000OOO0O0O000 )))#line:1317
	__ .callbacks .append (om .MSceneMessage .addCallback (om .MSceneMessage .kAfterOpen ,lambda *OOOO00OOOOOO00O0O :cmds .evalDeferred (_O0O0OOO0O0OO0O000 )))#line:1321
	__ .callbacks .append (om .MSceneMessage .addCallback (om .MSceneMessage .kAfterNew ,lambda *O0OO0O0OO0OO0000O :cmds .evalDeferred (_O00OO0OO0O0O00OOO )))#line:1325
def uninstall_callbacks ():#line:1328
	for O0OOO0O0O0O00O0OO in __ .callbacks :#line:1329
		om .MMessage .removeCallback (O0OOO0O0O0O00O0OO )#line:1330
	__ .callbacks [:]=[]#line:1331
def initializePlugin (O0O0000OO0O0O0O00 ):#line:1339
	install ()#line:1340
def uninitializePlugin (O00O0OO0O0OO00OOO ):#line:1343
	uninstall ()#line:1344
