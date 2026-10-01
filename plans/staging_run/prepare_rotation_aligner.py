import ast
import prepare_small_candidate as builder
unit=builder.ROOT/'tools_staging_pool/03_transforms_modeling/rotation_aligner'
tree=ast.parse(next(unit.glob('*.py')).read_bytes())
tree.body=[n for n in tree.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='create_alignment_window')]
source=ast.unparse(tree).replace("WINDOW_NAME = 'alignmentToolWindow'","WINDOW_NAME = 'mtbAlignmentToolWindow'")
source=source.replace("exec_btn = cmds.button(label='执行对齐'", "cmds.button(label='预检对齐', command=lambda *args: candidate_preflight())\n    exec_btn = cmds.button(label='执行对齐'")
builder.put(unit/'release_candidate/maya_toolkit/tools/rotation_aligner/native.py',source)
