from __future__ import absolute_import
import os

_ROOTDIR_ = os.path.dirname(__file__)

## Yes. My "License"-detection is just looking for a file.
## It's not difficult break, but that's also not the point.
## Feel free to cheat it.
_TRIAL_ = 1
if os.path.exists(os.path.join(_ROOTDIR_, 'license.txt')):
    _TRIAL_ = 0


_TITLE_ = 'KS_NodeOutliner'
_URL_ = 'www.kimstrandli.com'
_URL_TOOL_ = 'www.kimstrandli.com/script-nodeoutliner/'
_VERSION_ = 'v2.2'

_CONFIG_USER_ = os.path.join(_ROOTDIR_, 'ksNodeOutliner_filterData.json').replace('\\', '/')
_ICON_DIR_ = os.path.join(_ROOTDIR_, 'filterData', '').replace('\\', '/')
_SF_ROOTPACKAGE_ = 'ks_nodeOutliner.SCRIPTFILTERS'
