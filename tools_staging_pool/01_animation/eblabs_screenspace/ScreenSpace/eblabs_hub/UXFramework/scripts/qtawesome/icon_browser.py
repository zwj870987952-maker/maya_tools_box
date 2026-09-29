
import sys
import traceback

from . import Qt

from .. import qtawesome

'''
try:
    from .. import qtawesome
except Exception as e:
    print(Exception)
    print(traceback.format_exc())
'''

# TODO: Set icon colour and copy code with color kwarg

VIEW_COLUMNS = 5
AUTO_SEARCH_TIMEOUT = 500
ALL_COLLECTIONS = 'All'

#
class IconBrowser(Qt.QtWidgets.QMainWindow):
    """
    A small browser window that allows the user to search through all icons from
    the available version of QtAwesome.  You can also copy the name and python
    code for the currently selected icon.
    """

    def __init__(self, parent):
        super(IconBrowser, self).__init__(parent)
        self.setMinimumSize(400, 300)
        self.setWindowTitle('QtAwesome Icon Browser')

        '''
        self.setWindowFlags(

            Qt.QtCore.Qt.CustomizeWindowHint |
            Qt.QtCore.Qt.WindowTitleHint |
            Qt.QtCore.Qt.WindowCloseButtonHint |
            Qt.QtCore.Qt.Tool
            )
        '''

        qtawesome._instance()
        fontMaps = qtawesome._resource['iconic'].charmap

        iconNames = []
        for fontCollection, fontData in fontMaps.items():
            for iconName in fontData:
                iconNames.append('%s.%s' % (fontCollection, iconName))

        self._filterTimer = Qt.QtCore.QTimer(self)
        self._filterTimer.setSingleShot(True)
        self._filterTimer.setInterval(AUTO_SEARCH_TIMEOUT)
        self._filterTimer.timeout.connect(self._updateFilter)

        model = IconModel()
        model.setStringList(sorted(iconNames))

        self._proxyModel = Qt.QtCore.QSortFilterProxyModel()
        self._proxyModel.setSourceModel(model)
        self._proxyModel.setFilterCaseSensitivity(Qt.QtCore.Qt.CaseInsensitive)

        self._listView = IconListView(self)
        self._listView.setUniformItemSizes(True)
        self._listView.setViewMode(Qt.QtWidgets.QListView.IconMode)
        self._listView.setModel(self._proxyModel)
        self._listView.setContextMenuPolicy(Qt.QtCore.Qt.CustomContextMenu)
        self._listView.doubleClicked.connect(self._copyIconText)
        self._listView.selectionModel().selectionChanged.connect(self._updateNameField)

        self._lineEdit = Qt.QtWidgets.QLineEdit(self)
        self._lineEdit.setAlignment(Qt.QtCore.Qt.AlignCenter)
        self._lineEdit.textChanged.connect(self._triggerDelayedUpdate)
        self._lineEdit.returnPressed.connect(self._triggerImmediateUpdate)

        self._comboBox = Qt.QtWidgets.QComboBox(self)
        self._comboBox.setMinimumWidth(75)
        self._comboBox.currentIndexChanged.connect(self._triggerImmediateUpdate)
        self._comboBox.addItems([ALL_COLLECTIONS] + sorted(fontMaps.keys()))

        lyt = Qt.QtWidgets.QHBoxLayout()
        lyt.setContentsMargins(0, 0, 0, 0)
        lyt.addWidget(self._comboBox)
        lyt.addWidget(self._lineEdit)
        '''
        self._combo_style = Qt.QtWidgets.QComboBox(self)
        self._combo_style.addItems([
            qtawesome.styles.DEFAULT_DARK_PALETTE,
            qtawesome.styles.DEFAULT_LIGHT_PALETTE])
        self._combo_style.currentTextChanged.connect(self._updateStyle)
        lyt.addWidget(self._combo_style)
        '''

        searchBarFrame = Qt.QtWidgets.QFrame(self)
        searchBarFrame.setLayout(lyt)

        self._nameField = Qt.QtWidgets.QLineEdit(self)
        self._nameField.setAlignment(Qt.QtCore.Qt.AlignCenter)
        self._nameField.setReadOnly(True)

        self._copyButton = Qt.QtWidgets.QPushButton('Copy Name', self)
        self._copyButton.clicked.connect(self._copyIconText)

        lyt = Qt.QtWidgets.QVBoxLayout()
        lyt.addWidget(searchBarFrame)
        lyt.addWidget(self._listView)
        lyt.addWidget(self._nameField)
        lyt.addWidget(self._copyButton)

        frame = Qt.QtWidgets.QFrame(self)
        frame.setLayout(lyt)

        self.setCentralWidget(frame)
        #self.setMainWidget(frame)

        self.setTabOrder(self._comboBox, self._lineEdit)
        #self.setTabOrder(self._lineEdit, self._combo_style)
        self.setTabOrder(self._lineEdit, self._listView)
        self.setTabOrder(self._listView, self._nameField)
        self.setTabOrder(self._nameField, self._copyButton)
        self.setTabOrder(self._copyButton, self._comboBox)

        Qt.QtWidgets.QShortcut(
            Qt.QtGui.QKeySequence(Qt.QtCore.Qt.Key_Return),
            self,
            self._copyIconText,
        )
        Qt.QtWidgets.QShortcut(
            Qt.QtGui.QKeySequence("Ctrl+F"),
            self,
            self._lineEdit.setFocus,
        )

        self._lineEdit.setFocus()

        geo = self.geometry()

        # QApplication.desktop() has been removed in Qt 6.
        # Instead, QGuiApplication.screenAt(QPoint) is supported
        # in Qt 5.10 or later.
        try:
            screen = Qt.QtGui.QGuiApplication.screenAt(Qt.QtGui.QCursor.pos())
            centerPoint = screen.geometry().center()
        except AttributeError:
            desktop = Qt.QtWidgets.QApplication.desktop()
            screen = desktop.screenNumber(desktop.cursor().pos())
            centerPoint = desktop.screenGeometry(screen).center()

        geo.moveCenter(centerPoint)
        self.setGeometry(geo)

    def _updateStyle(self, text):
        _app = Qt.QtWidgets.QApplication
        if text == qtawesome.styles.DEFAULT_DARK_PALETTE:
            qtawesome.reset_cache()
            qtawesome.dark(_app)
        else:
            qtawesome.reset_cache()
            qtawesome.light(_app)

    def _updateFilter(self):
        """
        Update the string used for filtering in the proxy model with the
        current text from the line edit.
        """
        reString = ""

        group = self._comboBox.currentText()
        if group != ALL_COLLECTIONS:
            reString += r"^%s\." % group

        searchTerm = self._lineEdit.text()
        if searchTerm:
            reString += ".*%s.*$" % searchTerm

        # QSortFilterProxyModel.setFilterRegExp has been removed in Qt 6.
        # Instead, QSortFilterProxyModel.setFilterRegularExpression is
        # supported in Qt 5.12 or later.
        try:
            self._proxyModel.setFilterRegularExpression(reString)
        except AttributeError:
            self._proxyModel.setFilterRegExp(reString)

    def _triggerDelayedUpdate(self):
        """
        Reset the timer used for committing the search term to the proxy model.
        """
        self._filterTimer.stop()
        self._filterTimer.start()

    def _triggerImmediateUpdate(self):
        """
        Stop the timer used for committing the search term and update the
        proxy model immediately.
        """
        self._filterTimer.stop()
        self._updateFilter()

    def _copyIconText(self):
        """
        Copy the name of the currently selected icon to the clipboard.
        """
        indexes = self._listView.selectedIndexes()
        if not indexes:
            return

        clipboard = Qt.QtWidgets.QApplication.clipboard()
        clipboard.setText(indexes[0].data())

    def _updateNameField(self):
        """
        Update field to the name of the currently selected icon.
        """
        indexes = self._listView.selectedIndexes()
        if not indexes:
            self._nameField.setText("")
        else:
            self._nameField.setText(indexes[0].data())


class IconListView(Qt.QtWidgets.QListView):
    """
    A QListView that scales it's grid size to ensure the same number of
    columns are always drawn.
    """

    def __init__(self, parent=None):
        super(IconListView, super).__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.QtCore.Qt.ScrollBarAlwaysOn)

    def resizeEvent(self, event):
        """
        Re-implemented to re-calculate the grid size to provide scaling icons

        Parameters
        ----------
        event : Qt.QtCore.QEvent
        """
        width = self.viewport().width() - 30
        # The minus 30 above ensures we don't end up with an item width that
        # can't be drawn the expected number of times across the view without
        # being wrapped. Without this, the view can flicker during resize
        tileWidth = width / VIEW_COLUMNS
        iconWidth = int(tileWidth * 0.8)
        # tileWidth needs to be an integer for setGridSize
        tileWidth = int(tileWidth)

        self.setGridSize(Qt.QtCore.QSize(tileWidth, tileWidth))
        self.setIconSize(Qt.QtCore.QSize(iconWidth, iconWidth))

        return super(IconListView, self).resizeEvent(event)


class IconModel(Qt.QtCore.QStringListModel):

    def __init__(self):
        super(IconModel, self).__init__()

    def flags(self, index):
        return Qt.QtCore.Qt.ItemIsEnabled | Qt.QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        """
        Re-implemented to return the icon for the current index.

        Parameters
        ----------
        index : Qt.QtCore.QModelIndex
        role : int

        Returns
        -------
        Any
        """
        if role == Qt.QtCore.Qt.DecorationRole:
            iconString = self.data(index, role=Qt.QtCore.Qt.DisplayRole)
            return qtawesome.icon(iconString)
        return super(IconModel, self).data(index, role)


def run(parent):
    """
    Start the IconBrowser and block until the process exits.
    """
    # app = Qt.QtWidgets.QApplication([])
    #qtawesome.dark(app)

    browser = IconBrowser(parent)
    browser.show()

    #sys.exit(app.exec_())


if __name__ == '__main__':
    run()
