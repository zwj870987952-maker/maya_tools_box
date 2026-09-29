# Embedded file name: S:\Git\eblabs-hub\eblabs_hub\UXFramework\scripts\LicenseManager.py
r"""
Licensing and Trial Handling (date limited use)

import sys
import sys
import importlib
sys.path.insert(0, 'S:\Git\eblabs-hub\')
import eblabs_hub
import eblabs_hub.UXFramework.scripts.LicenseManager as tool

is_trial_mode = eblabs_hub.UXFramework.scripts.LicenseManager.Query.IsTrialMode()
eblabs_hub.UXFramework.scripts.LicenseManager.Edit.SetTrialMode(True)
"""
import datetime
import os
import inspect
import re
import copy
from . import Prefs
from ...UXFramework.scripts import BasicTool_Widgets
from ...UXFramework.scripts import Qt
from maya import cmds
try:
    from past.builtins import long
except:
    pass

def iteritems(obj, **kwargs):
    """Use this only if compatibility with Python versions before 2.7 is
    required. Otherwise, prefer viewitems().
    """
    func = getattr(obj, 'iteritems', None)
    if not func:
        func = obj.items
    return func(**kwargs)


__TRIALMODE__ = False
__TRIALDATE__ = [2023, 4, 29]

class Edit(object):

    @classmethod
    def get_self_path(cls):
        """
        make sure to leave this method in each plugin's iconProvider
        """
        current_path = os.path.dirname(os.path.abspath(inspect.getfile(cls)))
        return current_path

    @classmethod
    def SetTrialMode(cls, trial_mode = False, path = None):
        if not path or not os.path.isfile(path):
            print ('License Manager Warning: file not found: ', path)
            return
        else:
            sourceLines = None
            with open(path, 'r') as f:
                sourceLines = f.readlines()
            tag = 'CONFIGURABLE'
            startTag = '# BEGIN {0}'.format(tag)
            endTag = '# END {0}'.format(tag)
            new_lines = []
            editible = False
            for i, line in enumerate(sourceLines):
                if line.find(startTag) == 0:
                    editible = True
                if editible:
                    if cls.are_all_strings_in_string(line, ['__TRIALMODE__', '=']):
                        value = True if trial_mode else False
                        line = '__TRIALMODE__ = {0}\n'.format(value)
                    if cls.are_all_strings_in_string(line, ['__TRIALDATE__', '=']):
                        date_time_today = datetime.datetime.today() + datetime.timedelta(days=14)
                        value = [date_time_today.year, date_time_today.month, date_time_today.day]
                        line = '__TRIALDATE__ = {0}\n'.format(value)
                if line.find(endTag) == 0:
                    editible = False
                new_lines.append(line)

            with open(path, 'w') as f:
                f.writelines(new_lines)
            return

    @classmethod
    def are_all_strings_in_string(cls, str_item, str_list):
        re_string = '.*'.join(str_list)
        return bool(re.match('.*{0}.*'.format(re_string), str_item))


class Query(object):

    @classmethod
    def LicenseSafeCheck(cls, displayMessage = True):
        """
        return true or false
        optionally, display a message if in a trial, or if a trial has expired
        """
        if not cls.is_trial_mode():
            return True
        days_left = cls.get_remaining_days()
        do_display = False
        first_time_today = cls.is_first_check_today()
        if displayMessage:
            if days_left <= 0:
                do_display = True
            elif first_time_today:
                do_display = True
        cmds.warning(InfoDialog.get_simple_message())
        if do_display:
            InfoDialog.launch()
        return days_left >= 0

    @classmethod
    def is_trial_mode(cls):
        return __TRIALMODE__

    @classmethod
    def is_first_check_today(cls):
        last_check_date = Prefs.PrefsManager.getProperty('last_license_check_date', None)
        date_time_today = datetime.datetime.today()
        today_check_date = [date_time_today.year, date_time_today.month, date_time_today.day]
        if last_check_date != today_check_date:
            Prefs.PrefsManager.setProperty('last_license_check_date', today_check_date)
            return True
        else:
            return False

    @classmethod
    def get_remaining_days(cls):
        today = datetime.datetime.today()
        today.replace(tzinfo=None)
        end_date = datetime.datetime(*__TRIALDATE__)
        delta = (end_date - today).days + 2
        return delta


class InfoDialog(BasicTool_Widgets.SimpleWidgetDialog):

    def __init__(self, *args, **kwargs):
        super(InfoDialog, self).__init__(*args, **kwargs)

    @classmethod
    def get_template_data(cls):
        data = BasicTool_Widgets.SimpleWidgetDialog.get_template_data()
        data['label'] = 'Trial Version'
        data['size'] = [BasicTool_Widgets.SharedSettings.Maya.get_dpi_scaled_value(400), BasicTool_Widgets.SharedSettings.Maya.get_dpi_scaled_value(200)]
        return copy.deepcopy(data)

    def create_contents_widgets(self):
        data = InfoText.get_template_data()
        data['label'] = self.get_message()
        w = InfoText(self, data=data)
        self.main_layout.addWidget(w, 1, 0, 1, 1)

    @classmethod
    def get_simple_message(cls):
        remaining_days = Query.get_remaining_days()
        remaining_days = max(0, remaining_days)
        message = '{0} day(s) remaining in trial. Thanks for trying out eblabs.com Animation Tools'.format(remaining_days)
        return message

    @classmethod
    def get_message(cls):
        remaining_days = Query.get_remaining_days()
        remaining_days = max(0, remaining_days)
        message = '\n<h2>Thanks for trying out <b>eblabs.com</b> Animation Tools</h2>\n<h3>You have <b>{0}</b> day(s) remaining</h3>\n        '.format(remaining_days)
        return message


class InfoText(BasicTool_Widgets.SimpleDataHandler, Qt.QtWidgets.QLabel):

    def __init__(self, *args, **kwargs):
        super(InfoText, self).__init__(*args, **kwargs)
        self.setMinimumSize(Qt.QtCore.QSize(0, 0))
        self.setMargin(0)
        self.setWordWrap(True)
        self.setSizePolicy(Qt.QtWidgets.QSizePolicy.Expanding, Qt.QtWidgets.QSizePolicy.Expanding)
        self.setAlignment(Qt.QtCore.Qt.AlignCenter)
        self.on_redraw()

    @classmethod
    def get_template_data(cls):
        data = BasicTool_Widgets.SimpleDataHandler.get_template_data()
        data['background'] = [0,
         0,
         0,
         0]
        data['text_color'] = BasicTool_Widgets.ColorPaletteManager.BasicColors.get_color_for_keyword('high_contrast').get_rgba()
        data['padding'] = BasicTool_Widgets.SharedSettings.get_padding_size()
        data['label'] = 'Unset Label'
        data['subscribe_to_palette_change'] = True
        return copy.deepcopy(data)

    def on_redraw_pre(self):
        self.data['background'] = [0,
         0,
         0,
         0]
        self.data['text_color'] = BasicTool_Widgets.ColorPaletteManager.BasicColors.get_color_for_keyword('high_contrast').get_rgba()

    def on_redraw(self):
        data = self.get_all_data()
        label = self.get_data_key('label', 'NOT SET')
        self.setText(label)
        color = BasicTool_Widgets.ColorModule.Color(data['background']).get_int_rgba_string()
        text_color = BasicTool_Widgets.ColorModule.Color(data['text_color']).get_int_rgba_string()
        padding = data['padding']
        stylesheet = '\n        InfoText {{\n            background-color: {0};\n            border: 0px solid rgba(0,0,0,0);\n            color: {1};\n            padding-left: {2}px;\n            padding-right: {2}px;\n\n            background-repeat: no-repeat;\n            background-position: center;\n\n        }}\n        '.format(color, text_color, padding)
        self.setStyleSheet(stylesheet)