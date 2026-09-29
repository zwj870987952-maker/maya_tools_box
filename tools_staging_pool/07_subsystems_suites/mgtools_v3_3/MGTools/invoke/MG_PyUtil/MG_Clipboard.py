from . import mg_pysideutils


class Clipboard(object):
    Clipboard = None

    @classmethod
    def _initClipboard(cls):
        if not cls.Clipboard:
            if mg_pysideutils.isPySide2Available():
                from PySide2 import QtGui

                cls.Clipboard = QtGui.QClipboard()

            elif mg_pysideutils.isPySideAvailable():
                from PySide import QtGui

                cls.Clipboard = QtGui.QClipboard()
            else:
                return False
        return True

    @classmethod
    def copy(cls, txt, rep=True):
        if not cls._initClipboard():
            return False if not rep else \
                "!Copy to clipboard feature is only avaiable in Maya2014+, you need to select the text and Ctrl+C to manually copy it."

        cls.Clipboard.setText(txt)
        return True if not rep else ("The text '%s' has been copied to clipboard" % txt)

    @classmethod
    def text(cls):
        if not cls._initClipboard():
            return ''

        return cls.Clipboard.text()