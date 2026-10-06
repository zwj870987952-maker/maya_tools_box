# Quick-menu wrapper: opens the same color picker as the "Color" swatch in
# the full Spacify UI and applies the chosen color to the selected controls.
from spacify_core import QtWidgets
import spacify_actions

_color = QtWidgets.QColorDialog.getColor()
if _color.isValid():
    _rgb = (_color.redF(), _color.greenF(), _color.blueF())
    spacify_actions.apply_color_to_objects(_rgb)
