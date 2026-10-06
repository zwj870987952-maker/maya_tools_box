# Quick-menu wrapper: assigns the currently selected camera for Spacify's
# "Camera Space", the same way the "Assign" button does in the full UI.
# spacify_actions.assign_camera() writes the camera's short name into a
# text-field widget for display purposes -- since there is no visible field
# on the toolbar menu, a tiny stand-in object is passed instead. The camera
# itself is still stored in SPACIFY_STATE and saved to the scene network,
# so "Camera Space" (and the full Spacify UI, if opened afterwards) will
# pick it up normally.
import spacify_actions


class _NoDisplayField(object):
    def setText(self, text):
        pass


spacify_actions.assign_camera(_NoDisplayField())
