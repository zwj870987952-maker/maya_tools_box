"""
Licensing and Trial Handling (date limited use)
## tool specific version
"""

# Built Ins

# 3rd Party

# Local
from ...UXFramework.scripts import LicenseManager

# maya

# compatibility
#https://python-future.org/compatible_idioms.html#long-integers
try:
    from past.builtins import long
except:
    pass

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

# BEGIN CONFIGURABLE

__TRIALMODE__ = False
__TRIALDATE__ = [2023, 4, 29]

# END CONFIGURABLE

class Edit(LicenseManager.Edit):
    pass

class Query(LicenseManager.Query):
    pass



