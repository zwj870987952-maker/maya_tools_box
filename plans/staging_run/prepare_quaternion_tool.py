import ast
import prepare_small_candidate as builder
unit=builder.ROOT/'tools_staging_pool/03_transforms_modeling/quaternion_tool'
tree=ast.parse((unit/'QuaternionTool_Maya.py').read_bytes())
tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
source=ast.unparse(tree)
source=source.replace('fromDirection.normalize()','fromDirection = om.MVector(fromDirection)\n        fromDirection.normalize()').replace('toDirection.normalize()','toDirection = om.MVector(toDirection)\n        toDirection.normalize()')
source=source.replace('axis.normalize()','axis = om.MVector(axis)\n            axis.normalize()',1)
# Axis-angle copies its caller-owned MVector; internal cross-product vectors
# in FromToRotation are temporary and need no additional copying.
source=source.replace('        axis.normalize()\n        sin_half', '        axis = om.MVector(axis)\n        axis.normalize()\n        sin_half')
source=source.replace('cosA = fromDirection * toDirection','cosA = clamp(fromDirection * toDirection, -1.0, 1.0)')
source=source.replace('theta_0 = math.acos(dot)','theta_0 = math.acos(clamp(dot, -1.0, 1.0))')
source=source.replace("cmds.button(label='应用旋转到选中物体', command=self.apply_to_selection)","cmds.button(label='预检应用旋转', command=self.preflight)\n        cmds.button(label='应用旋转到选中物体', command=self.apply_to_selection)")
builder.put(unit/'release_candidate/maya_toolkit/tools/quaternion_tool/native.py',source)
