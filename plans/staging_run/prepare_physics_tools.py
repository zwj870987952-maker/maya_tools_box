"""Retain all 109 MEL procedures, privately route original UI and isolate helpers."""
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
from review_physics_tools import SOURCE, procedures, tokenize

ROOT = Path(__file__).resolve().parents[2]
UNIT = SOURCE.parent
RC = UNIT / 'release_candidate'
PACKAGE = RC / 'maya_toolkit/tools/physics_tools'
PREFIX = 'mtkPTC_'


def guarded_deletes(body):
    tokens = tokenize(body)
    edits = []
    for i, token in enumerate(tokens):
        if token.group() not in ('delete', 'Delete', 'doDelete'):
            continue
        j = i + 1
        while j < len(tokens) and tokens[j].group() != ';':
            j += 1
        if j == len(tokens):
            raise ValueError('Unterminated delete command')
        args = body[token.end():tokens[j].start()].strip()
        mode = 1 if re.fullmatch(r'-\s*(?:cn|constraints)', args) else 0
        if args.startswith('-') and not mode:
            raise ValueError('Review unsupported delete flags: ' + args)
        if mode or not args:
            expression = '{}'
        elif args.startswith('`') and args.endswith('`'):
            expression = args
        else:
            # All original explicit deletes have one literal or one variable.
            if not re.fullmatch(r'"(?:\\.|[^"\\])*"|\$[A-Za-z_][A-Za-z_0-9]*|[A-Za-z_][A-Za-z_0-9]*', args):
                raise ValueError('Review delete operands: ' + args)
            if re.fullmatch('[A-Za-z_][A-Za-z_0-9]*', args):
                args = json.dumps(args)
            expression = '{' + args + '}'
        edits.append((token.start(), tokens[j].end(), PREFIX + 'Delete(' + expression + ', ' + str(mode) + ');'))
    for start, end, replacement in reversed(edits):
        body = body[:start] + replacement + body[end:]
    return body


def main():
    source = SOURCE.read_text(encoding='utf-8-sig')
    rows = procedures(source)
    names = [row['name'] for row in rows]
    controls = ['PhysicsToolsWin'] + re.findall(r'floatSliderGrp[^;]+\s(\w+)\s*;', rows[0]['body'])
    controls = sorted(set(controls))
    mapping = {name: PREFIX + name for name in names}
    mapping.update({name: PREFIX + name for name in controls})
    native = []
    removed_editor_commands = ('ConnectionEditor', 'connectWindowFillFromActiveList', 'nodeOutliner', 'connectWindowSetLeftLabel', 'nodeOutlinerOutputsCmd', 'connectWindowSetRightLabel', 'nodeOutlinerInputsCmd', 'getUIComponentDockControl', 'setupNParticleConnections', 'Goal', 'performDynamics')
    for row in rows:
        body = row['body']
        # Retain explicit particle connection/goal operation; original editor mirroring is redundant.
        if row['name'] != 'PhysicsToolsWin':
            lines = []
            for line in body.splitlines():
                s = line.strip()
                if any(re.match(re.escape(n) + r'\b', s) for n in removed_editor_commands) or s == 'deleteUI connectWindow;':
                    continue
                lines.append(line)
            body = '\n'.join(lines) + '\n'
        body = re.sub(r'diskCache\s+-ea\s+-da\s*;', PREFIX + 'ClearOwnCache();', body)
        body = re.sub(r'diskCache\s+-os\s+-ea\s+-ct\s+mcj\s+-sr\s+1\s+-enabledCachesOnly\s*;', PREFIX + 'CreateOwnCache();', body)
        body = re.sub(r'`floatSliderGrp\s+-q\s+-value\s+"([A-Za-z0-9_]+)"`', lambda m: '`' + PREFIX + 'Value("' + m[1] + '")`', body)
        # Original auto-generated names depend on target namespace; use exact UUID-derived leaf alias.
        body = re.sub(r'("(?:imLocator_|ProxyLocator_|imCube_|imSphere_)")\s*\+\s*\$node', lambda m: PREFIX + 'HelperName(' + m[1] + ', $node)', body)
        body = re.sub(r'\$node\s*\+\s*("_(?:Translations|Rotations|layer|Overlap)")', lambda m: PREFIX + 'HelperName(' + m[1] + ', $node)', body)
        body = guarded_deletes(body)
        # Maya may remove the now-empty set while deleting its helper graph.
        cleanup = re.compile(r'select PhysicsSets;\s*sets -remove "PhysicsSets";\s*select -r -ne PhysicsSets\s*;\s*mtkPTC_Delete\(\{\}, 0\);')
        body = cleanup.sub(lambda m: 'if (`objExists PhysicsSets`) {\n' + m[0] + '\n}', body)
        body = re.sub(r'doJiggle\s+1\s*\{[^}]+\}\s*;', PREFIX + 'CreateJiggle();', body)
        if row['name'] == 'PhysicsToolsWin':
            body = body.replace('scrollLayout scrollLayout;', 'scrollLayout ' + PREFIX + 'Scroll;\ncheckBox -label "Allow reference edits" -value false ' + PREFIX + 'AllowReferences;')
        # Compile private namespaces for procedure and UI names, including callback strings.
        pattern = re.compile(r'(?<![$A-Za-z0-9_])(' + '|'.join(sorted(map(re.escape, mapping), key=len, reverse=True)) + r')(?![A-Za-z0-9_])')
        body = pattern.sub(lambda m: mapping[m[1]], body)
        body = re.sub(r'\bpython\s*\(', PREFIX + 'Embedded(', body)
        # Multi-object unrolled source uses objExists(array[index]) out of bounds; gate count first.
        body = re.sub(r'if\s*\(\s*`objExists\s+\$naSelecao\[(\d+)\]`\s*\)', lambda m: 'if (size($naSelecao) > ' + m[1] + ' && `objExists $naSelecao[' + m[1] + ']`)', body)
        native.append('global proc ' + PREFIX + 'Native_' + row['name'] + '() {\npython("from maya_toolkit.tools.physics_tools.runtime import require_scope; require_scope()");\n' + body + '\n}\n')
    wrappers = []
    for name in names:
        wrappers.append('global proc ' + PREFIX + name + '() {\nif (`python("from maya_toolkit.tools.physics_tools.runtime import active; active()")`) {\n' + PREFIX + 'Native_' + name + '();\n} else {\npython("from maya_toolkit.tools.physics_tools.runtime import ui_call; ui_call(\'' + name + '\')");\n}\n}\n')
    helpers = r'''
global proc float mtkPTC_Value(string $control) {
    string $escaped = encodeString($control);
    return `python("from maya_toolkit.tools.physics_tools.runtime import value; value(\"" + $escaped + "\")")`;
}
global proc string mtkPTC_HelperName(string $prefix, string $node) {
    return `python("from maya_toolkit.tools.physics_tools.runtime import helper_name; helper_name(\"" + encodeString($prefix) + "\",\"" + encodeString($node) + "\")")`;
}
global proc mtkPTC_Embedded(string $code) {
    python("from maya_toolkit.tools.physics_tools.runtime import embedded; embedded(\"" + encodeString($code) + "\")");
}
global proc mtkPTC_ClearOwnCache() {
    python("from maya_toolkit.tools.physics_tools.runtime import cache; cache(False)");
}
global proc mtkPTC_CreateOwnCache() {
    python("from maya_toolkit.tools.physics_tools.runtime import cache; cache(True)");
}
global proc mtkPTC_CreateJiggle() {
    python("from maya_toolkit.tools.physics_tools.runtime import create_jiggle; create_jiggle()");
}
global proc mtkPTC_Delete(string $nodes[], int $constraints) {
    string $literal = "[";
    for ($i=0; $i<size($nodes); $i++) {
        if ($i) $literal += ",";
        $literal += "\"" + encodeString($nodes[$i]) + "\"";
    }
    $literal += "]";
    python("from maya_toolkit.tools.physics_tools.runtime import delete_owned; delete_owned(" + $literal + "," + $constraints + ")");
}
'''
    rendered = '// Version: 12/10/22\n// Autor: IURI MONTEIRO\n// modified by k31\n// Private local candidate; all 109 original procedure bodies retained with documented safety adaptations.\n' + helpers + ''.join(wrappers + native)
    # Trim inherited physical-line whitespace outside MEL literals only.
    literal_ranges = [(t.start(), t.end()) for t in tokenize(rendered) if t.group().startswith('"')]
    clean = []
    offset = 0
    for line in rendered.splitlines(True):
        content = line.rstrip('\r\n')
        trimmed = content.rstrip(' \t')
        start = offset + len(trimmed)
        inside_literal = any(a <= start < b for a, b in literal_ranges)
        clean.append((content if inside_literal else trimmed) + '\n')
        offset += len(line)
    rendered = ''.join(clean)
    PACKAGE.mkdir(parents=True, exist_ok=True)
    (PACKAGE / 'native.mel').write_text(rendered, encoding='utf-8', newline='\n')
    raw = PACKAGE / 'upstream/PhysicsTools_v1.8.mel'
    raw.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, raw)
    (PACKAGE / 'upstream/.gitattributes').write_text('* -text\n', encoding='utf-8')
    (UNIT / '.gitattributes').write_text('PhysicsTools_v1.8.mel -text\n', encoding='utf-8')
    (RC / '.gitattributes').write_text('* -text\n', encoding='utf-8')
    catalog = {'raw_files': [{'path': 'upstream/PhysicsTools_v1.8.mel', 'sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest()}], 'procedures': names, 'controls': controls, 'license': 'No independent redistribution/modification license supplied; personal local candidate, retain author and k31 attribution', 'native_sha256': hashlib.sha256(rendered.encode()).hexdigest()}
    (PACKAGE / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    docs = RC / 'docs/tools'
    docs.mkdir(parents=True, exist_ok=True)
    (docs / 'physics_tools_changes.diff').write_text(''.join(difflib.unified_diff(source.splitlines(True), rendered.splitlines(True), fromfile='upstream/PhysicsTools_v1.8.mel', tofile='native.mel')), encoding='utf-8', newline='\n')
    launcher = (ROOT / 'tools_staging_pool/01_animation/maya_keyframe_reduction/release_candidate/launch_candidate.py').read_text(encoding='utf-8').replace('keyframe_reduction', 'physics_tools').replace('KeyframeReductionTool', 'PhysicsToolsTool')
    (RC / 'launch_candidate.py').write_text(launcher, encoding='utf-8')
    payload = [p for folder in (RC / 'maya_toolkit', RC / 'docs', RC / 'tests') for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    data = {'tool_id': 'physics_tools', 'registration': {'module': 'physics_tools', 'class_name': 'PhysicsToolsTool'}, 'files': [{'source': p.relative_to(RC).as_posix(), 'target': p.relative_to(RC).as_posix()} for p in sorted(payload)], 'resources': ['native.mel', 'upstream/PhysicsTools_v1.8.mel', 'catalog.json'], 'dependencies': ['Maya MEL/cmds/legacy particle/jiggle/createHair procedures', 'Interactive Maya native UI for scene-independent editor utilities', 'Rivet/GhostSelected and related Maya runtime commands; source assets not supplied', 'BaseMayaTool/Undo'], 'source': '../PhysicsTools_v1.8.mel', 'change_summary': 'Full 109-procedure MEL suite and full original UI, particle/jiggle and advanced axis/local-space/proxy/tracking/curve/noise workflows retained; private globals/UI, checked API, isolated helper namespace and owned cache/delete protections.', 'verification_limitations': ['Full native interactive Maya suite and production rigs require human acceptance', 'Legacy Jiggle/hair/runtime-command behaviors may differ in Maya2025; individual failures recorded', 'Preview helper/session state needs explicit cleanup; external cache files cannot Maya Undo', 'No independent license supplied, local use only; do not publish', 'Guarded source still needs all original operation-specific Maya dependencies'], 'acceptance_required': True}
    (RC / 'promotion.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'procedures': len(names), 'controls': controls, 'source_sha256': catalog['raw_files'][0]['sha256']}))


if __name__ == '__main__':
    main()
