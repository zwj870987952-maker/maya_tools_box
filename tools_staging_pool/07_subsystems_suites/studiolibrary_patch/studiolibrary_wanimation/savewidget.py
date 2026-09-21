"""WAnimation save widget that reuses thumbnail playblast evaluation."""

from __future__ import absolute_import

import studioqt

from studiolibrarymaya import basesavewidget

from .worldanimation import WorldAnimationCollector, _long_names


def _initialize_with_base_save_ui(widget, initializer, *args, **kwargs):
    """Run BaseSaveWidget init while resolving its own upstream UI file.

    StudioQt normally derives the .ui filename from ``widget.__class__``.
    For this subclass that incorrectly resolves to WAnimationSaveWidget.ui,
    which does not exist. Redirect only this widget's first implicit loadUi
    call to the installed Studio Library BaseSaveWidget.ui. Nested widgets and
    explicit UI paths continue through untouched.
    """
    original_load_ui = studioqt.loadUi

    def load_ui(current, path=None, cls=None):
        if current is widget and path is None and cls is None:
            cls = basesavewidget.BaseSaveWidget
        return original_load_ui(current, path=path, cls=cls)

    studioqt.loadUi = load_ui
    try:
        return initializer(*args, **kwargs)
    finally:
        studioqt.loadUi = original_load_ui


class WAnimationSaveWidget(basesavewidget.BaseSaveWidget):
    """Collect world transforms while the normal image sequence is captured."""

    def __init__(self, *args, **kwargs):
        self._world_animation = None
        self._world_signature = None
        _initialize_with_base_save_ui(
            self,
            super(WAnimationSaveWidget, self).__init__,
            *args,
            **kwargs
        )

    def _current_signature(self):
        values = self.formWidget().values()
        objects = tuple(_long_names(values.get("objects") or []))
        frame_range = values.get("frameRange") or (0, 0)
        return objects, float(frame_range[0]), float(frame_range[1]), 1.0

    def selectionChanged(self):
        self._world_animation = None
        self._world_signature = None
        super(WAnimationSaveWidget, self).selectionChanged()

    def thumbnailCapture(self, show=False):
        # The expanded framing dialog captures asynchronously after this method
        # returns, so use the normal fallback sampling for that uncommon path.
        if show:
            self._world_animation = None
            self._world_signature = None
            return super(WAnimationSaveWidget, self).thumbnailCapture(show=show)

        values = self.formWidget().values()
        collector = WorldAnimationCollector(
            values.get("objects") or [],
            values.get("frameRange") or (0, 0),
            sample_by=1.0,
        )
        collector.start()
        try:
            result = super(WAnimationSaveWidget, self).thumbnailCapture(show=show)
        finally:
            collector.stop()

        if collector.is_complete():
            self._world_animation = collector.world_animation()
            self._world_signature = collector.signature()
        else:
            self._world_animation = None
            self._world_signature = None
        return result

    def save(self, path, thumbnail):
        kwargs = self.formWidget().values()
        sequence_path = self.ui.thumbnailButton.dirname()
        world_data = None
        if (self._world_animation is not None and
                self._world_signature == self._current_signature()):
            world_data = self._world_animation.data

        item = self.item()
        item.setPath(path)
        item.safeSave(
            thumbnail=thumbnail,
            sequencePath=sequence_path,
            worldAnimationData=world_data,
            **kwargs
        )
        self.close()
