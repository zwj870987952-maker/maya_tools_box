# Robert Joosten Timeline Marker 2.0.2; GPL-3.0-or-later. Adapted for Maya Toolkit. See upstream/LICENSE.
from .. import gui_bridge as bridge
import json
from maya import OpenMaya, OpenMayaUI, cmds, mel
from . import utils
global TIMELINE_MARKER
TIMELINE_MARKER = None

class TimelineMarker(utils.QWidget):

    def __init__(self):
        utils.QWidget.__init__(self)
        self.setObjectName('mtkTimelineMarkerCandidate')
        self.start = None
        self.end = None
        self.total = None
        self.step = None
        self.frames = []
        self.colors = []
        self.comments = []
        self.newID = None
        self.openID = None
        self._range = None
        self.menu = TimelineMarkerMenu(self)
        try:
            self.readFromCurrentScene()
            self.addCallbacks()
        except Exception:
            self.removeCallbacks()
            self.menu.deleteLater()
            raise

    def readFromCurrentScene(self, *args):
        return bridge.read(self)

    def saveToCurrentScene(self):
        return bridge.write(self, action='set', frames=self.frames, colors=self.colors, comments=self.comments)

    def getDataFromFrame(self, frame):
        """
        Get data from frame, this includes the index within the lists, the
        color and comment.

        :param int frame: Frame to get data from
        :return: index, frame, color, comment
        :rtype: tuple
        """
        if frame in self.frames:
            index = self.frames.index(frame)
            color = self.colors[index]
            comment = self.comments[index]
            return (index, frame, color, comment)
        return (-1, frame, None, None)

    def paintEvent(self, event):
        self.draw()

    def event(self, event):
        if self.total is None or not self.step or self.start is None:
            return utils.QWidget.event(self, event)
        '\n        Subclass the event function in order to capture the ToolTip event. \n        The hovered frame is calculated and checked to see if it is marked \n        and commented, if so the toolTip will show.\n        '
        if event.type() == utils.QEvent.ToolTip:
            utils.QToolTip.hideText()
            frame = int((event.x() - self.total * 0.005) / self.step + self.start)
            _, _, _, comment = self.getDataFromFrame(frame)
            utils.QToolTip.showText(event.globalPos(), comment or '', self)
        return utils.QWidget.event(self, event)

    def addFromUI(self):
        frames = utils.getTimelineRange()
        if not frames:
            return
        result = bridge.write(self, action='add', frames=frames, color=list(self.menu.colorA.property('rgb')), comment=self.menu.commentL.text())
        self.menu.commentL.setText('')
        return result

    def add(self, frame, color, comment):
        return bridge.write(self, action='add', frames=[frame], color=color, comment=comment)

    def removeFromUI(self):
        frames = utils.getTimelineRange()
        if frames:
            return bridge.write(self, action='remove', frames=frames)

    def remove(self, frame):
        return bridge.write(self, action='remove', frames=[frame])

    def clear(self):
        return bridge.write(self, action='clear')

    def pressCommand(self, *args):
        self._range = None
        '\n        Press callback on the timeline, this callback registers the current\n        selected frames, if the user settings determine that the frame range\n        is not important ( no automated shifting of markers ), no range will \n        be stored.\n        '
        timeline = utils.getMayaTimeline()
        cmds.timeControl(timeline, edit=True, beginScrub=True)
        rangeVisible = cmds.timeControl(timeline, q=True, rangeVisible=True)
        if not rangeVisible or not self.menu.moveA.isChecked():
            return
        self._range = utils.getTimelineRange()

    def releaseCommand(self, *args):
        return bridge.release(self)

    def draw(self):
        """
        Take all the marker information and fill in the utils.QWidget covering the
        timeline. This function will be called by the update and paintEvent
        function.
        """
        self.start = cmds.playbackOptions(query=True, min=True)
        self.end = cmds.playbackOptions(query=True, max=True)
        self.total = self.width()
        self.step = (self.total - self.total * 0.01) / (self.end - self.start + 1)
        if not self.frames or not self.colors:
            return
        painter = utils.QPainter(self)
        pen = utils.QPen()
        pen.setWidthF(self.step)
        for f, c in zip(self.frames, self.colors):
            pen.setColor(utils.QColor(c[0], c[1], c[2], 50))
            pos = (f - self.start + 0.5) * self.step + self.total * 0.005
            line = utils.QLineF(utils.QPointF(pos, 0), utils.QPointF(pos, 100))
            painter.setPen(pen)
            painter.drawLine(line)

    def addCallbacks(self):
        return bridge.add_callbacks(self)

    def removeCallbacks(self):
        return bridge.remove_callbacks(self)

    def update(self):
        return utils.QWidget.update(self)

    def deleteLater(self):
        self.removeCallbacks()
        self.menu.deleteLater()
        return utils.QWidget.deleteLater(self)

class TimelineMarkerMenu(object):

    def __init__(self, parent):
        self.menu = utils.getTimelineMenu()
        self._buttons = []
        self.separatorA1 = self.addSeparator()
        pText = 'marker comment'
        self.commentA, self.commentL = self.addCommentField(pText)
        self.colorA = self.addColorPicker()
        self.separatorA2 = self.addSeparator()
        aText = 'Add Marker'
        rText = 'Delete Selected Marker'
        cText = 'Delete All Markers'
        self.addA = self.addButton(aText, parent.addFromUI)
        self.removeA = self.addButton(rText, parent.removeFromUI)
        self.clearA = self.addButton(cText, parent.clear)
        self.separatorA3 = self.addSeparator()
        self.moveA = self.addButton('Move With Time Control')
        self.moveA.setCheckable(True)
        self.moveA.setChecked(False)

    @property
    def buttons(self):
        """
        List all marker related QActions from the timeline menu.

        :return: Buttons
        :rtype: list
        """
        return self._buttons

    def addCommentField(self, placeholderText):
        """
        Add comment field QAction to the menu.

        :param str placeholderText: Placeholder text
        :return: QAction, QLineEdit
        :rtype: tuple
        """
        edit = utils.QLineEdit(self.menu)
        edit.setPlaceholderText(placeholderText)
        button = utils.QWidgetAction(self.menu)
        button.setDefaultWidget(edit)
        self.menu.addAction(button)
        self.buttons.append(button)
        return (button, edit)

    def addColorPicker(self):
        """
        Add color picker QAction to the menu.

        :return: Color picker
        :rtype: QAction
        """
        button = self.addButton('Pick Color', self.picker)
        button.setProperty('rgb', [0, 255, 0])
        pixmap = utils.QPixmap(12, 12)
        pixmap.fill(utils.QColor(0, 255, 0))
        button.setIcon(utils.QIcon(pixmap))
        return button

    def addSeparator(self):
        """
        Add separator QAction to the menu.

        :return: Separator
        :rtype: QAction
        """
        separator = utils.QAction(self.menu)
        separator.setSeparator(True)
        self.menu.addAction(separator)
        self.buttons.append(separator)
        return separator

    def addButton(self, text, command=None):
        """
        Add button QAction to the menu.

        :param str text: Button text
        :param func command: Function to call when button is released.
        :return: Button
        :rtype: QAction
        """
        button = utils.QAction(self.menu)
        button.setText(text)
        if command:
            button.triggered.connect(command)
        self.menu.addAction(button)
        self.buttons.append(button)
        return button

    def picker(self):
        """
        The picker will change the color of the button and will store the
        rgb values in a property, this property will be read when a marker is
        added via the menu.
        """
        rgbL = self.colorA.property('rgb')
        rgbQt = utils.QColor(rgbL[0], rgbL[1], rgbL[2])
        dialog = utils.QColorDialog.getColor(rgbQt, self.menu)
        if not dialog.isValid():
            return
        rgb = [dialog.red(), dialog.green(), dialog.blue()]
        pixmap = utils.QPixmap(12, 12)
        pixmap.fill(utils.QColor(rgb[0], rgb[1], rgb[2]))
        self.colorA.setProperty('rgb', rgb)
        self.colorA.setIcon(utils.QIcon(pixmap))

    def deleteLater(self):
        return bridge.delete_menu(self)

def install():
    import sys
    return bridge.install(sys.modules[__name__])

def uninstall():
    import sys
    return bridge.uninstall(sys.modules[__name__])
