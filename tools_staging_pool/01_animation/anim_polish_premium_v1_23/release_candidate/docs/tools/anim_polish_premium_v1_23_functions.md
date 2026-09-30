# AnimPolish 过程签名与覆盖目录

完整原始 suite 保留；user_* 的 2 个 run 和文件句柄辅助过程由 UI/状态层管理，不作为 JSON invoke。签名行号指向 upstream。

| 过程 | 参数 | 原行号 | JSON invoke |
| --- | --- | --- | --- |
| `assignColors.createMats` | `` | 30 | 是 |
| `assignColors.createMat` | `name, color` | 49 | 是 |
| `assignColors.assign_sel` | `color, mode` | 64 | 是 |
| `assignColors.assign` | `obj, color, mode` | 78 | 是 |
| `assignColors.random_sel` | `mode` | 86 | 是 |
| `assignColors.random` | `obj, mode` | 99 | 是 |
| `assignColors.printColor_sel` | `` | 108 | 是 |
| `assignColors.printColor` | `mat` | 116 | 是 |
| `caching.exp_cams` | `path, cams` | 32 | 是 |
| `caching.exp_geos` | `path, geos` | 54 | 是 |
| `caching.imp_cams` | `path` | 105 | 是 |
| `caching.imp_geos` | `path` | 113 | 是 |
| `caching.swap` | `path` | 192 | 是 |
| `caching.attach_sel` | `` | 220 | 是 |
| `caching.attach` | `` | 260 | 是 |
| `caching.attach2` | `chars` | 279 | 是 |
| `caching.delete` | `` | 326 | 是 |
| `copyPasteAttrs.copy` | `path='', k=0` | 31 | 是 |
| `copyPasteAttrs.paste` | `path=''` | 76 | 是 |
| `cycleCam.run` | `skipOrtho=0` | 26 | 是 |
| `growShrink.run_sel` | `hideData=1, smooth=3` | 34 | 是 |
| `growShrink.run` | `geo, dfrmverts=[], floodverts=[], cb='', hideData=1, smooth=3, its=3` | 75 | 是 |
| `growShrink.flood` | `verts, bs, smooth=3` | 147 | 是 |
| `iron.run_sel` | `hideData=1, smooth=3` | 36 | 是 |
| `iron.run` | `geo, dfrmverts=[], floodverts=[], cb='', hideData=1, smooth=3, its=3` | 77 | 是 |
| `iron.flood` | `verts, bs, smooth=3` | 162 | 是 |
| `quickBake.run_sel` | `` | 32 | 是 |
| `quickBake.run` | `objs` | 46 | 是 |
| `quickBake.rivet_sel` | `` | 57 | 是 |
| `quickBake.rivet` | `` | 74 | 是 |
| `quickBake.plane_sel` | `` | 88 | 是 |
| `quickBake.plane` | `` | 105 | 是 |
| `rivetStuff.rivet_sel` | `loc=0` | 33 | 是 |
| `rivetStuff.rivet` | `vtx, surf, outGeo='', loc=0` | 46 | 是 |
| `rivetStuff.stickyMod` | `surf, falloff=1` | 104 | 是 |
| `rivetStuff.run_sel` | `falloff=1, color=22, sphVis=1, smooth=3, lra=1, mode=1, scale=1` | 132 | 是 |
| `rivetStuff.run_vtx` | `vtx, surf, falloff=1, color=22, sphVis=1, lra=1, mode=1, scale=1` | 176 | 是 |
| `rivetStuff.run_cp` | `cp, surf, falloff=1, color=22, sphVis=1, lra=1, mode=1, scale=1` | 219 | 是 |
| `rivetStuff.finalize` | `sm, surf, color=22, sphVis=1, lra=1, mode=1, scale=1` | 273 | 是 |
| `rivetStuff.floodReplace` | `comps, sm_dfrm` | 448 | 是 |
| `rivetStuff.floodSmooth` | `comps, sm_dfrm, smooth=3` | 469 | 是 |
| `rivetStuff.addGeo_sel` | `` | 490 | 是 |
| `rivetStuff.addGeo` | `sm, geo` | 519 | 是 |
| `rivetStuff.removeGeo_sel` | `` | 540 | 是 |
| `rivetStuff.removeGeo` | `sm, geo` | 569 | 是 |
| `rivetStuff.breakRot_sel` | `` | 589 | 是 |
| `rivetStuff.breakRot` | `sm` | 605 | 是 |
| `rivetStuff.oriToWorld_sel` | `` | 630 | 是 |
| `rivetStuff.oriToWorld` | `sm` | 645 | 是 |
| `rivetStuff.aimAtObj_sel` | `` | 656 | 是 |
| `rivetStuff.aimAtObj` | `obj, sm` | 677 | 是 |
| `sculptPose.run_sel` | `lv=1, ihi=1` | 41 | 是 |
| `sculptPose.run` | `scu, geo, mode, lv=1, ihi=1` | 49 | 是 |
| `sculptPose.sculpt_sel` | `vis=1, shade=1, editMode=0` | 217 | 是 |
| `sculptPose.sculpt` | `geo, vis=1, shade=1, editMode=0` | 238 | 是 |
| `sculptPose.abortSculpt` | `` | 298 | 是 |
| `sculptPose.sculptFromZero_sel` | `vis=1, shade=1, lv=1, mode=1` | 321 | 是 |
| `sculptPose.sculptFromZero` | `geo, vis=1, shade=1, lv=1, mode=1` | 342 | 是 |
| `sculptPose.apply_sel` | `mode, lv=1, ihi=1` | 401 | 是 |
| `sculptPose.apply` | `scu, mode, lv=1, ihi=1` | 426 | 是 |
| `sculptPose.apply_1f_sel` | `` | 462 | 是 |
| `sculptPose.apply_1f` | `scu, lv=1, ihi=1` | 484 | 是 |
| `sculptPose.apply_p2p_sel` | `lv=1, ihi=1` | 512 | 是 |
| `sculptPose.apply_p2p` | `scu, lv=1, ihi=1` | 534 | 是 |
| `sculptPose.createP2PZero_sel` | `lv` | 579 | 是 |
| `sculptPose.createP2PZero` | `geo, lv` | 601 | 是 |
| `sculptPose.createP2PHold_sel` | `lv=1, ihi=1` | 674 | 是 |
| `sculptPose.createP2PHold` | `geo, lv=1, ihi=1` | 701 | 是 |
| `sculptPose.p2pPre` | `geo, lv` | 759 | 是 |
| `sculptPose.getAttrs` | `geo` | 820 | 是 |
| `sculptPose.sortCB` | `` | 834 | 是 |
| `sculptPose.sortKey` | `text` | 893 | 是 |
| `sculptPose.atoi` | `text` | 897 | 是 |
| `sculptPose.delete_sel` | `lv=1, allP2P=0` | 906 | 是 |
| `sculptPose.delete` | `geo, a, lv=1, allP2P=0` | 941 | 是 |
| `sculptPose.editSculpt_sel` | `vis=1, shade=1` | 1018 | 是 |
| `sculptPose.editSculpt` | `geo, vis=1, shade=1` | 1049 | 是 |
| `sculptPose.applyEdit_sel` | `lv=1, ihi=1` | 1067 | 是 |
| `sculptPose.applyEdit` | `geo, scu, drv, lv=1, ihi=1` | 1094 | 是 |
| `sculptPose.ui` | `` | 1126 | 是 |
| `sculptPose.ui_sculpt` | `` | 1194 | 是 |
| `sculptPose.ui_sculptFromZero` | `` | 1202 | 是 |
| `sculptPose.ui_apply` | `` | 1212 | 是 |
| `sculptPose.ui_apply_1f` | `` | 1220 | 是 |
| `sculptPose.ui_apply_p2p` | `` | 1226 | 是 |
| `sculptPose.ui_createP2PZero` | `` | 1234 | 是 |
| `sculptPose.ui_createP2PHold` | `` | 1241 | 是 |
| `sculptPose.ui_delete` | `allP2P=0` | 1249 | 是 |
| `sculptPose.ui_editSculpt` | `` | 1256 | 是 |
| `sculptPose.ui_applyEdit` | `` | 1264 | 是 |
| `sculptPose.selectSculpts` | `` | 1274 | 是 |
| `smoothPreview.run` | `div=2` | 30 | 是 |
| `subdue.run` | `rate=4, smooth=3` | 34 | 是 |
| `subdue.flood` | `verts, bs, smooth=3` | 184 | 是 |
| `ui.ui` | `dock=1` | 91 | 是 |
| `ui.scu_sculpt` | `` | 417 | 是 |
| `ui.scu_sculptFromZero` | `` | 423 | 是 |
| `ui.scu_abortSculpt` | `` | 431 | 是 |
| `ui.scu_apply` | `` | 435 | 是 |
| `ui.scu_apply_1f` | `` | 441 | 是 |
| `ui.scu_apply_p2p` | `` | 445 | 是 |
| `ui.scu_createP2PZero` | `` | 451 | 是 |
| `ui.scu_createP2PHold` | `` | 456 | 是 |
| `ui.scu_delete` | `allP2P=0` | 462 | 是 |
| `ui.scu_editSculpt` | `` | 467 | 是 |
| `ui.scu_applyEdit` | `` | 473 | 是 |
| `ui.wrap_loadVerts` | `` | 489 | 是 |
| `ui.wrap_clearVerts` | `` | 497 | 是 |
| `ui.wrap_wrapToMesh` | `` | 501 | 是 |
| `ui.wrap_wrapToWorld` | `` | 509 | 是 |
| `ui.subdue_run` | `` | 525 | 是 |
| `ui.growShrink_run` | `` | 540 | 是 |
| `ui.iron_run` | `` | 546 | 是 |
| `ui.misc_loadDfrmVerts` | `` | 552 | 是 |
| `ui.misc_clearDfrmVerts` | `` | 560 | 是 |
| `ui.misc_loadFloodVerts` | `` | 564 | 是 |
| `ui.misc_clearFloodVerts` | `` | 572 | 是 |
| `ui.deltaMush` | `` | 584 | 是 |
| `ui.sine` | `` | 588 | 是 |
| `ui.wave` | `` | 592 | 是 |
| `ui.cluster` | `` | 596 | 是 |
| `ui.ac_lambert1` | `` | 608 | 是 |
| `ui.assignColor` | `color` | 619 | 是 |
| `ui.randomColors` | `` | 628 | 是 |
| `ui.saveSettings_run` | `typ, name, flag, f` | 645 | 内部/旧状态脚本 |
| `ui.saveSettings` | `` | 654 | 是 |
| `ui.loadSettings` | `` | 747 | 是 |
| `ui.defaultSettings` | `` | 780 | 是 |
| `ui.toggleAnimEval` | `` | 796 | 是 |
| `ui.toggleAnimEval_2` | `` | 803 | 是 |
| `ui.fixViewport` | `` | 814 | 是 |
| `ui.floodSmooth` | `cnt` | 818 | 是 |
| `ui.pim` | `` | 828 | 是 |
| `ui.cache_launch` | `` | 848 | 是 |
| `ui.cache_createMeta` | `` | 852 | 是 |
| `ui.cache_refresh` | `create=1` | 862 | 是 |
| `ui.cache_refreshList` | `` | 886 | 是 |
| `ui.cache_fieldWrite` | `` | 906 | 是 |
| `ui.cache_resetDir` | `` | 930 | 是 |
| `ui.cache_browseDir` | `` | 943 | 是 |
| `ui.cache_exportGeo` | `` | 959 | 是 |
| `ui.cache_exportCams` | `` | 1009 | 是 |
| `ui.cache_loadGeo` | `` | 1026 | 是 |
| `ui.cache_loadCams` | `` | 1035 | 是 |
| `ui.cache_importGeo` | `` | 1044 | 是 |
| `ui.cache_importCams` | `` | 1071 | 是 |
| `ui.cache_attach` | `` | 1081 | 是 |
| `ui.cache_attach_sel` | `` | 1085 | 是 |
| `ui.cache_swap` | `` | 1089 | 是 |
| `ui.cache_delete` | `` | 1107 | 是 |
| `user_settings.run` | `` | 3 | 内部/旧状态脚本 |
| `user_settings_default.run` | `` | 9 | 内部/旧状态脚本 |
| `wrap.wrapToMesh_sel` | `verts=[], smooth=3, hideData=1` | 44 | 是 |
| `wrap.wrapToMesh` | `drvn, drvr, verts=[], smooth=3, hideData=1` | 77 | 是 |
| `wrap.wrapToWorld_sel` | `verts=[], smooth=3, hideData=1` | 126 | 是 |
| `wrap.wrapToWorld` | `drvn, verts=[], smooth=3, hideData=1` | 149 | 是 |
| `wrap.duplicate` | `obj, n='', grpPar=1` | 192 | 是 |
| `wrap.floodReplace` | `bs, verts` | 225 | 是 |
| `wrap.floodSmooth` | `bs, obj, smooth=3` | 248 | 是 |
| `wrap.extractFaces` | `` | 269 | 是 |
