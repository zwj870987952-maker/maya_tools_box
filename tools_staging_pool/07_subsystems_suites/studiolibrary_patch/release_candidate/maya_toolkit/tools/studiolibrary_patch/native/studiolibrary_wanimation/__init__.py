"""Explicit activation only: importing this package never hooks or repairs caches."""
__version__='2.2.2-mtb'
__all__=['WAnimationItem','WPoseItem']
def __getattr__(name):
    if name=='WAnimationItem':
        from .wanimationitem import WAnimationItem
        return WAnimationItem
    if name=='WPoseItem':
        from .wposeitem import WPoseItem
        return WPoseItem
    raise AttributeError(name)
