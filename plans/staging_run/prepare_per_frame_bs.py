"""Self-contained native FBX helper copied from the validated V7 adapter."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
UNIT=ROOT/'tools_staging_pool/04_pipeline_io/per_frame_bs_fbx'
PKG=UNIT/'release_candidate/maya_toolkit/tools/per_frame_bs_fbx'
src=ROOT/'tools_staging_pool/04_pipeline_io/fbx_batch_exporter_v7/release_candidate/maya_toolkit/tools/fbx_batch_exporter_v7/tool.py'
tree=ast.parse(src.read_text(encoding='utf8'))
nodes=[]
for n in tree.body:
    if isinstance(n,(ast.Import,ast.ImportFrom)) and not (isinstance(n,ast.ImportFrom) and n.module=='maya_toolkit.framework'): nodes.append(n)
    elif isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('FLAGS','DEFAULTS') for t in n.targets): nodes.append(n)
    elif isinstance(n,ast.FunctionDef) and n.name in ('preserve_session','mel_string','fbx_settings','export'): nodes.append(n)
code='"""Packaged FBX export implementation; no dependency on staging paths."""\n'+ '\n\n'.join(ast.unparse(n) for n in nodes)+'\nFLAGS[\'blend_shapes\']=\'FBXExportShapes\'\nDEFAULTS[\'blend_shapes\']=True\n'
(PKG/'fbx_io.py').write_text(code,encoding='utf8',newline='\n')
print('Self-contained native FBX helper with shape/skin export and settings restoration')
