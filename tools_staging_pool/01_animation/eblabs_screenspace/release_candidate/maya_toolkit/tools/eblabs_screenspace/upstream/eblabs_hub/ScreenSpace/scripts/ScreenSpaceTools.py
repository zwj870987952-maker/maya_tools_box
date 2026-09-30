"""
Screen Space Tools Launcher
"""


# Built Ins
import inspect
import os

# 3rd Party


# Local
# from . import LicenseManager
from ..data import PackageData
package_data =  PackageData.get_data()

# maya
from maya import mel

# compatibility
#https://python-future.org/compatible_idioms.html#long-integers
try:
    from past.builtins import long
except:
    pass

__author__ = "Eric Bates, eblabs.com"
__copyright__ = "Copyright 2021, Eric Bates"
__credits__ = ["Eric Bates"]
__maintainer__ = "Eric Bates"
__email__ = "info@eblabs.com"
__status__ = "Production"
__version__ = package_data.get('version', '')
__date__ = '2021.11.18'

# https://python-future.org/_modules/future/utils.html
# https://python-future.org/compatible_idioms.html
def iteritems(obj, **kwargs):
    """Use this only if compatibility with Python versions before 2.7 is
    required. Otherwise, prefer viewitems().
    """
    func = getattr(obj, "iteritems", None)
    if not func:
        func = obj.items
    return func(**kwargs)

'''
install_path = 'S:/Git/eblabs-hub/'
package_id = 'ScreenSpace'

import os
import sys
if not install_path in sys.path:
    sys.path.insert(0, install_path)

import eblabs_hub.ScreenSpace.scripts.ScreenSpaceTools as tool

tool.Tool.launch()
'''


class Tool():

    @classmethod
    def get_self_path(cls):
        '''
        make sure to leave this method in each plugin's iconProvider
        '''
        #current_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        #current_path = os.path.abspath(inspect.getfile(inspect.currentframe()))
        current_path = os.path.dirname(os.path.abspath(inspect.getfile(cls)))
        return current_path

    @classmethod
    def launch(cls):
        # check license manager
        # license_safe_check = LicenseManager.Query.LicenseSafeCheck()
        # if not license_safe_check:
        #     return

        # get path
        path = cls.get_self_path()
        melCommand = os.path.normpath(os.path.join(path, 'eblabs_screenSpace.mel'))
        melCommand = melCommand.replace('\\', '\\\\')

        # launch
        mel.eval('source \"{0}\"'.format(melCommand))
        mel.eval('ebLabs_screenSpace;')


'''
install_path = 'S:/Git/eblabs-hub'
package_id = 'ScreenSpace'

import os
from maya import mel


melCommand = os.path.normpath(os.path.join(install_path, 'eblabs_hub', 'ScreenSpace', 'scripts', 'eblabs_screenSpace.mel'))
melCommand = melCommand.replace('\\','\\\\')
mel.eval('source \"{0}\"'.format(melCommand))
mel.eval('ebLabs_screenSpace;')
'''


