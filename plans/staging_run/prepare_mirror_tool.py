from pathlib import Path
import ast
import prepare_small_candidate as builder
ROOT=builder.ROOT
unit=ROOT/'tools_staging_pool/03_transforms_modeling/mirror_tool'
source=(unit/'mirror_tool.py').read_text(encoding='utf8')
tree=ast.parse(source)
tree.body=[n for n in tree.body if not isinstance(n,ast.If)]
# Retain every original function/method/UI. The supported subclass redirects
# both mutation entries to BaseMayaTool; no automatic window invocation.
native=ast.unparse(tree)
native=native.replace("cmds.button(label='执行镜像', command=self.execute_mirror, height=40)","cmds.button(label='预检当前选择', command=self.preflight)\n        cmds.button(label='执行镜像', command=self.execute_mirror, height=40)")
builder.put(unit/'release_candidate/maya_toolkit/tools/mirror_tool/native.py',native)
