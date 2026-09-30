import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / 'tools_staging_pool/01_animation/dof_control_v1_0'
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/dof_control_v1_0'


def main():
    PACKAGE.mkdir(parents=True, exist_ok=True)
    resources = []
    for name in ('dofControl.mel', 'dofControl.xpm'):
        source = UNIT / name
        target = PACKAGE / 'upstream' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        resources.append({'path': 'upstream/' + name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
    (UNIT / '.gitattributes').write_text('dofControl.* -text\n', encoding='utf-8', newline='\n')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    (PACKAGE / 'upstream/.gitattributes').write_text('* -text\n', encoding='utf-8', newline='\n')
    original = (UNIT / 'dofControl.mel').read_text(encoding='utf-8-sig')
    text = original.replace('global proc dofControl ()', 'global proc string[] mtbDOF_build (string $objList[], string $prefix)')
    text = text.replace('string $objList[] = `ls -sl -ca -dag`;', 'python("from maya_toolkit.tools.dof_control_v1_0.runtime import require_active; require_active()");\n    string $result[];')
    text = text.replace('return;', 'return $result;')
    text = text.replace('$camTransNode[0] + "dofArea#"', '$prefix + "Area#"')
    text = text.replace('// parent polyCube to camera', 'string $cubeShape[] = `listRelatives -shapes -fullPath $cube[0]`;\n\t\t// parent polyCube to camera')
    # Render switches exist on actual shape; resolve before setting them.
    text = text.replace('setAttr ( $cube[0] + ".castsShadows" )', 'string $cubeShape[] = `listRelatives -shapes -fullPath $cube[0]`;\n\t\tsetAttr ( $cubeShape[0] + ".castsShadows" )')
    text = text.replace('string $cubeShape[] = `listRelatives -shapes -fullPath $cube[0]`;\n\t\t// parent', '// parent')
    for attr in ('primaryVisibility', 'visibleInReflections', 'visibleInRefractions'):
        text = text.replace('$cube[0] + ".' + attr + '"', '$cubeShape[0] + ".' + attr + '"')
    text = text.replace('createNode "reverse"', 'createNode -name ($prefix + "Reverse#") "reverse"')
    text = text.replace('createNode "addDoubleLinear"', 'createNode -name ($prefix + "Add#") "addDoubleLinear"')
    text = text.replace('connectAttr -f ', 'connectAttr ')
    text = text.replace('\t}\n}\n', '\t\t$result[size($result)] = $cube[0];\n\t\t$result[size($result)] = $revNode;\n\t\t$result[size($result)] = $addNode;\n\t}\n    return $result;\n}\n')
    text = '\n'.join(line.rstrip() for line in text.splitlines()) + '\n'
    (PACKAGE / 'runtime.mel').write_text(text, encoding='utf-8', newline='\n')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'dof_control_changes.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True), text.splitlines(True), fromfile='upstream/dofControl.mel', tofile='runtime.mel')), encoding='utf-8', newline='\n')
    catalog = {'tool_id': 'dof_control_v1_0', 'original_procedures': ['dofControl'], 'runtime_procedures': ['mtbDOF_build'], 'raw_files': resources, 'license': 'Original header: freely distributed; modify at own risk; Dirk Bialluch, 2000', 'changes': ['Explicit camera shape array and private guarded MEL procedure', 'Unique helpers, actual shape render flags, no forced connection overwrite', 'Owned UUID/message records and cleanup/restore', 'Original reverse(add(tz,1)) and fStop/negative XY scales preserved', 'Native source has no UI; lightweight standard action UI added']}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    descriptor = {'tool_id': 'dof_control_v1_0', 'registration': {'module': 'dof_control_v1_0', 'class_name': 'DofControlTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': ['upstream/dofControl.mel', 'upstream/dofControl.xpm', 'runtime.mel', 'catalog.json'], 'dependencies': ['Maya cmds/MEL polyCube/reverse/addDoubleLinear and implicit unitConversion', 'Existing framework/core Undo'], 'source': '../dofControl.mel', 'change_summary': 'Full original DOF cube/node graph and XPM, explicit camera preflight, owned persistent cleanup restoring old focus/fStop, standard UI/Schema/Undo.', 'verification_limitations': ['Real viewport/template and render engine DOF pending', 'DepthOfField remains unchanged; scaleZ is fStop, not physical focus range', 'Camera units/scale and render-engine interpretation require manual check'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(descriptor, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'resources': len(resources), 'procedures': ['mtbDOF_build']}))


if __name__ == '__main__':
    main()
