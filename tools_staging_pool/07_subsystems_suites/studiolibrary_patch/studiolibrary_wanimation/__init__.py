"""Studio Library PlusPatch extension package."""

from .wanimationitem import WAnimationItem
from .wposeitem import WPoseItem
from .integration import install as install_integration
from .startup import schedule_cache_repair

__all__ = ["WAnimationItem", "WPoseItem"]
__version__ = "2.2.2"

install_integration()
schedule_cache_repair()
