# -*- coding: utf-8 -*-
"""
================================================================================
Maya 外部 FBX 资产深度比对与差异同步工具 (向后兼容转发接口)
Backward-compatible forwarder module.
推荐使用新工具入口脚本: compare_and_sync_fbx_assets.py
================================================================================
"""
from compare_and_sync_fbx_assets import *
import compare_and_sync_fbx_assets as _canonical_module

if __name__ == "__main__":
    _canonical_module.show_ui()
