# 视口显示（Viewport Display）

切换视口中的对象类型、辅助显示、灯光和遮罩。

- 状态：prepared_unverified，等待人工 Maya 直验。
- 输入：当前 Maya 选择、通道/Graph Editor 关键帧及时间区间；固定预设由下列脚本定义。
- 输出：候选 API 返回分派状态与操作后选择，不声称原算法已成功。
- 撤销：场景操作进入 Undo Chunk；外部文件、UI、插件、偏好不由 Maya Undo 撤回。

| operation ID | 原名称 | 执行源文件（相对 Animo_v10.6.0） | 具体用途/影响 |
| --- | --- | --- | --- |
| `viewport_display.toggle_blue_pencil_eda97f97` | Toggle Blue Pencil | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Blue Pencil.py` | 视口显示：Toggle Blue Pencil。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_cameras_439575d2` | Toggle Cameras | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Cameras.py` | 视口显示：Toggle Cameras。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_clip_ghosts_18c2f7cc` | Toggle Clip Ghosts | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Clip Ghosts.py` | 视口显示：Toggle Clip Ghosts。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_construction_planes_7d2db265` | Toggle Construction Planes | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Construction Planes.py` | 视口显示：Toggle Construction Planes。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_controllers_1a23f301` | Toggle Controllers | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Controllers.py` | 视口显示：Toggle Controllers。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_controls_display_d26a502c` | Toggle Controls Display | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Controls Display.py` | 视口显示：Toggle Controls Display。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_deformers_dd0f96e2` | Toggle Deformers | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Deformers.py` | 视口显示：Toggle Deformers。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_dimensions_05e30505` | Toggle Dimensions | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Dimensions.py` | 视口显示：Toggle Dimensions。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_dynamic_constraints_205cebef` | Toggle Dynamic Constraints | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Dynamic Constraints.py` | 视口显示：Toggle Dynamic Constraints。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_dynamics_d44bf8d3` | Toggle Dynamics | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Dynamics.py` | 视口显示：Toggle Dynamics。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_fluids_f7d3d656` | Toggle Fluids | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Fluids.py` | 视口显示：Toggle Fluids。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_follicles_c947832d` | Toggle Follicles | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Follicles.py` | 视口显示：Toggle Follicles。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_gpu_cache_6b39f983` | Toggle GPU Cache | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle GPU Cache.py` | 视口显示：Toggle GPU Cache。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_grid_209cf6bb` | Toggle Grid | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Grid.py` | 视口显示：Toggle Grid。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_hair_systems_8f2bca38` | Toggle Hair Systems | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Hair Systems.py` | 视口显示：Toggle Hair Systems。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_handles_673d5516` | Toggle Handles | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Handles.py` | 视口显示：Toggle Handles。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_hud_e53070b0` | Toggle HUD | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle HUD.py` | 视口显示：Toggle HUD。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_ik_handles_a3d8e729` | Toggle IK Handles | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle IK Handles.py` | 视口显示：Toggle IK Handles。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_image_planes_ff477169` | Toggle Image Planes | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Image Planes.py` | 视口显示：Toggle Image Planes。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_isolate_selections_7ec8c2c6` | Toggle Isolate Selections | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Isolate Selections.py` | 视口显示：Toggle Isolate Selections。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_joints_ffd75f0a` | Toggle Joints | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Joints.py` | 视口显示：Toggle Joints。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_lights_63caaa15` | Toggle Lights | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Lights.py` | 视口显示：Toggle Lights。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_locators_b9016f48` | Toggle Locators | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Locators.py` | 视口显示：Toggle Locators。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_manipulators_87291eba` | Toggle Manipulators | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Manipulators.py` | 视口显示：Toggle Manipulators。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_motion_trails_8ae91061` | Toggle Motion Trails | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Motion Trails.py` | 视口显示：Toggle Motion Trails。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_ncloths_d7686d23` | Toggle nCloths | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle nCloths.py` | 视口显示：Toggle nCloths。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_nparticles_f5ff0f8c` | Toggle nParticles | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle nParticles.py` | 视口显示：Toggle nParticles。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_nrigids_e4053640` | Toggle nRigids | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle nRigids.py` | 视口显示：Toggle nRigids。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_nurbs_curves_7afd9f9b` | Toggle Nurbs Curves | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Nurbs Curves.py` | 视口显示：Toggle Nurbs Curves。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_nurbs_cvs_b391178c` | Toggle Nurbs CVs | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Nurbs CVs.py` | 视口显示：Toggle Nurbs CVs。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_nurbs_hulls_b4d8d8f2` | Toggle Nurbs Hulls | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Nurbs Hulls.py` | 视口显示：Toggle Nurbs Hulls。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_nurbs_surfaces_a4c4cf76` | Toggle Nurbs Surfaces | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Nurbs Surfaces.py` | 视口显示：Toggle Nurbs Surfaces。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_particle_instancers_e9e3e693` | Toggle Particle Instancers | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Particle Instancers.py` | 视口显示：Toggle Particle Instancers。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_pivots_e6e56a0d` | Toggle Pivots | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Pivots.py` | 视口显示：Toggle Pivots。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_plugin_shapes_4d37ea36` | Toggle Plugin Shapes | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Plugin Shapes.py` | 视口显示：Toggle Plugin Shapes。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_polygons_62fb4162` | Toggle Polygons | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Polygons.py` | 视口显示：Toggle Polygons。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_selection_highlighting_ea275957` | Toggle Selection Highlighting | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Selection Highlighting.py` | 视口显示：Toggle Selection Highlighting。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_strokes_10a33979` | Toggle Strokes | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Strokes.py` | 视口显示：Toggle Strokes。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_subdivision_surfaces_ea3a2c1d` | Toggle Subdivision Surfaces | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Subdivision Surfaces.py` | 视口显示：Toggle Subdivision Surfaces。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_texture_placements_813da7ce` | Toggle Texture Placements | `Animo_Data/Animo_Tools_Editor/animo_tools/tools/Toggle Texture Placements.py` | 视口显示：Toggle Texture Placements。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |
| `viewport_display.toggle_xray_surfaces_d8c5154f` | Toggle Xray Surfaces | `Animo_Data/Animo_Tools_Editor/tools_library/Viewport Display/Toggle Xray Surfaces.py` | 视口显示：Toggle Xray Surfaces。切换视口中的对象类型、辅助显示、灯光和遮罩。；视口显示状态 |

## 调用

```python
tool.run(dry_run=True, action="invoke", operation_id='viewport_display.toggle_blue_pencil_eda97f97')
# 阅读预检结果后再执行：
# tool.run(action="invoke", operation_id='viewport_display.toggle_blue_pencil_eda97f97')
```

所有入口的函数签名、顶层固定调用值及原索引别名见候选 `operations.json`；这些是静态证据，不表示运行兼容。
