# Quick-menu wrapper: runs Spacify's "World" action directly, without
# opening the full Spacify UI. Triggered from the Spacify icon's
# right-click / left-click menu (see barMod.py -> ICON_DATA -> spacify_icon.png).
import spacify_actions

spacify_actions.execute_world()
