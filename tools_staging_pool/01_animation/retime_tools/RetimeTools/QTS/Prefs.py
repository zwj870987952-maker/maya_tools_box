
#
#       _      _         _          
#      | |    | |       | |         
#  ___ | |__  | |  __ _ | |__   ___ 
# / _ \| '_ \ | | / _` || '_ \ / __|
#|  __/| |_) || || (_| || |_) |\__ \
# \___||_.__/ |_| \__,_||_.__/ |___/
# 
# eblabs, hybrid version handler        
import sys

# determine python version
version_info = sys.version_info
python_version = int('{0}{1}'.format(version_info[0], version_info[1]))

        
    
if python_version == 311:
    from .Prefs_311 import *
                
                
    
if python_version == 310:
    from .Prefs_310 import *
                
                
    
if python_version == 39:
    from .Prefs_39 import *
                
                
    
if python_version == 37:
    from .Prefs_37 import *
                
                
    
if python_version == 27:
    from .Prefs_27 import *
                
                