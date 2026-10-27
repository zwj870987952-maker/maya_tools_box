# -*- coding: utf-8 -*-
"""Undo-guarded live preview; never disables Undo or undoes unrelated edits."""
from __future__ import absolute_import, division, print_function

import uuid
from maya_toolkit.core import UndoChunkContext


class PreviewSession(object):
    def __init__(self, tool, cmds):
        self.tool = tool
        self.cmds = cmds
        self.token = None
        self.arguments = None
        self.result = None

    @property
    def active(self):
        return self.token is not None

    def cancel(self):
        if not self.active:
            return
        if not self.cmds.undoInfo(query=True, state=True) or self.cmds.undoInfo(query=True, undoName=True) != self.token:
            raise RuntimeError("Preview is not the latest Undo operation; no unrelated edits were undone. Use Apply to keep current result, or manually Undo intervening edits first.")
        self.cmds.undo()
        self.token = None
        self.result = None
        self.arguments = None

    def update(self, arguments=None, buffer=False):
        previous_arguments = self.arguments
        if self.active:
            self.cancel()
        arguments = arguments if arguments is not None else previous_arguments or {}
        validation = self.tool.validate(**arguments)
        if not validation.success:
            return validation
        self.arguments = dict(arguments)
        self.arguments["anim_curves"] = validation.data["anim_curves"]
        self.arguments["time_range"] = validation.data["time_range"]
        token = "AnimFiltersPreview_" + uuid.uuid4().hex
        with UndoChunkContext(chunk_name=token):
            if buffer:
                self.cmds.bufferCurve(self.arguments["anim_curves"], animation="objects", overwrite=True)
            result = self.tool.run(**self.arguments)
        # Retain the token on partial failures so Cancel can undo the partial write.
        if self.cmds.undoInfo(query=True, undoName=True) == token:
            self.token = token
        self.result = result
        return result

    def apply(self):
        result = self.result
        self.token = None
        self.arguments = None
        self.result = None
        return result
