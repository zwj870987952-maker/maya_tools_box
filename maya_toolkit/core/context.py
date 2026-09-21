# -*- coding: utf-8 -*-
"""
上下文管理模块：提供 Maya 原生 Undo Chunk 封装、视口刷新抑制、性能计时等能力。
"""
from __future__ import absolute_import, division, print_function

import time
import functools
from contextlib import contextmanager

try:
    import maya.cmds as cmds
    MAYA_AVAILABLE = True
except ImportError:
    cmds = None
    MAYA_AVAILABLE = False


class UndoChunkContext(object):
    """
    上下文管理器：将代码块安全包裹在单个 Maya 原生 Undo Chunk 中。
    支持在异常时正确关闭 Chunk，确保通过 Ctrl+Z 可以一键撤销完整操作。
    """

    def __init__(self, chunk_name="MayaToolkitOperation"):
        self.chunk_name = str(chunk_name)
        self._is_open = False

    def __enter__(self):
        if MAYA_AVAILABLE and cmds:
            try:
                cmds.undoInfo(openChunk=True, chunkName=self.chunk_name)
                self._is_open = True
            except Exception:
                self._is_open = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if MAYA_AVAILABLE and cmds and self._is_open:
            try:
                cmds.undoInfo(closeChunk=True)
            except Exception:
                pass
            self._is_open = False
        # 返回 False 允许异常正常向上抛出
        return False


def undo_chunk(chunk_name=None):
    """
    装饰器：将函数执行过程包裹在单个 Maya Undo Chunk 中。
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = chunk_name or func.__name__
            with UndoChunkContext(chunk_name=name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class SuspendRefreshContext(object):
    """
    上下文管理器：在执行大批量操作期间临时挂起视口渲染刷新，
    并在退出时恢复，从而带来 5~10 倍的性能提速。
    """

    def __init__(self):
        self._suspended = False

    def __enter__(self):
        if MAYA_AVAILABLE and cmds:
            try:
                cmds.refresh(suspend=True)
                self._suspended = True
            except Exception:
                self._suspended = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if MAYA_AVAILABLE and cmds and self._suspended:
            try:
                cmds.refresh(suspend=False)
                cmds.refresh()
            except Exception:
                pass
            self._suspended = False
        return False


@contextmanager
def execution_timer(operation_name="Operation"):
    """
    计时上下文管理器，记录代码执行耗时并返回带有耗时的字典或信息。
    """
    start_time = time.time()
    timing_info = {"elapsed_seconds": 0.0, "name": operation_name}
    try:
        yield timing_info
    finally:
        timing_info["elapsed_seconds"] = round(time.time() - start_time, 4)
