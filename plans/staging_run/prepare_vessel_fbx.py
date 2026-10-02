"""Self-contained native FBX and exclusive scene save implementations."""
import ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PKG=ROOT/'tools_staging_pool/04_pipeline_io/vessel_fbx_exporter/release_candidate/maya_toolkit/tools/vessel_fbx_exporter'
src=ROOT/'tools_staging_pool/04_pipeline_io/fbx_batch_exporter_v7/release_candidate/maya_toolkit/tools/fbx_batch_exporter_v7/tool.py'
tree=ast.parse(src.read_text(encoding='utf8')); nodes=[]
for n in tree.body:
    if isinstance(n,(ast.Import,ast.ImportFrom)) and not (isinstance(n,ast.ImportFrom) and n.module=='maya_toolkit.framework'): nodes.append(n)
    elif isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('FLAGS','DEFAULTS') for t in n.targets): nodes.append(n)
    elif isinstance(n,ast.FunctionDef) and n.name in ('safe_name','preserve_session','mel_string','fbx_settings','export'): nodes.append(n)
code='"""Complete native FBX settings restoration; no staging dependency."""\n'+ '\n\n'.join(ast.unparse(n) for n in nodes)+"\nFLAGS.update(blend_shapes='FBXExportShapes',include_children='FBXExportIncludeChildren')\nDEFAULTS.update(blend_shapes=True,include_children=True)\n"
(PKG/'fbx_io.py').write_text(code,encoding='utf8',newline='\n')
src=ROOT/'tools_staging_pool/04_pipeline_io/replace_references/release_candidate/maya_toolkit/tools/replace_references/tool.py'
tree=ast.parse(src.read_text(encoding='utf8')); fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='save_output')
(PKG/'scene_io.py').write_text('import os\nfrom pathlib import Path\nimport tempfile\n'+ast.unparse(fn)+'\n',encoding='utf8',newline='\n')
print('Full original set pipeline with self-contained FBX and scene IO prepared')
