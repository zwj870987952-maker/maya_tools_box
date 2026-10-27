"""No shell execution or overwriting existing files; independent of Maya."""
import hashlib
import os
from pathlib import Path
import re
import shlex
import shutil
import tempfile

_scratch = None


def checked_path(value):
    p = Path(value).absolute()
    if os.name == 'nt':
        for component in p.parts[1:]:
            if ':' in component or component.rstrip(' .') != component or re.match(r'(?i)^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\.|$)', component):
                raise ValueError('Unsafe Windows filename')
    for ancestor in [p]+list(p.parents):
        if ancestor.is_symlink() or getattr(ancestor, 'is_junction', lambda: False)():
            raise ValueError('Symlink/junction paths rejected')
    if not p.parent.is_dir():
        raise ValueError('Existing parent directory required')
    return p


def new_output(value):
    p = checked_path(value)
    if p.exists():
        raise FileExistsError('Existing file protected: '+str(p))
    return p


def reserve(value):
    p = new_output(value)
    if p.suffix.lower() != '.bb' and not inside_scratch(p):
        raise ValueError('Native writes limited to new .bb settings or owned scratch XML')
    with p.open('xb'):
        pass
    return str(p)


def copy_file(source, target, move=False):
    src, dst = checked_path(source), new_output(target)
    if not src.is_file() or src.resolve() == dst.resolve():
        raise ValueError('Existing distinct source file required')
    source_hash = hashlib.sha256(src.read_bytes()).hexdigest()
    created = False
    try:
        with src.open('rb') as incoming, dst.open('xb') as outgoing:
            created = True
            shutil.copyfileobj(incoming, outgoing)
        if hashlib.sha256(dst.read_bytes()).hexdigest() != source_hash:
            raise RuntimeError('Copied bytes changed')
        if move:
            if hashlib.sha256(src.read_bytes()).hexdigest() != source_hash:
                raise RuntimeError('Source changed; retained both files')
            src.unlink()
    except Exception:
        # Preserve a completed copy if original changed or removal failed.
        if created and dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest() != source_hash:
            dst.unlink()
        raise
    return str(dst)


def scratch():
    global _scratch
    if _scratch is None:
        _scratch = Path(tempfile.mkdtemp(prefix='bb_tools_session_')).resolve()
    return _scratch


def inside_scratch(path):
    return _scratch is not None and Path(path).resolve().is_relative_to(_scratch)


def delete_scratch(value):
    p = checked_path(value)
    if not inside_scratch(p) or p.suffix.lower() != '.xml' or not p.name.startswith('bb_skin2Deform_weight'):
        raise ValueError('Deletion limited to owned weight XML')
    if p.exists():
        p.unlink()
    return 1


def system_request(command):
    # Original FTM uses only quoted md/mkdir/copy/cp/move/mv commands.
    # Parse those requests; never pass any text to a shell.
    args = shlex.split(command.replace('\\', '/'), posix=True)
    if len(args) == 2 and args[0] in ('md', 'mkdir'):
        path = new_output(args[1])
        path.mkdir()
        return str(path)
    if len(args) == 3 and args[0] in ('copy', 'cp', 'move', 'mv'):
        return copy_file(args[1], args[2], move=args[0] in ('move', 'mv'))
    raise ValueError('Unsupported native system request')


CHECKBOXES = {'bb_QC_'+x for x in ('renamePlyCB', 'renameSurfCB', 'renameCurvesCB', 'renameJointCB', 'suffixNumCB', 'smoothConCB')}
TEXTFIELDS = {'bb_QC_'+x for x in ('modleSuffixTF', 'camTF', 'smoothSuffixTF', 'ctrlSuffixTF')}
LISTS = {'bb_QC_ctrlAttrTSL', 'bb_QC_extraCtrlTSL'}


def parse_qc_line(line):
    if not isinstance(line, str) or len(line) > 8192:
        raise ValueError('Bounded QC setting line required')
    line = line.strip()
    if not line:
        return None
    if not line.endswith(';'):
        raise ValueError('Single terminated QC setting required')
    parts = shlex.split(line[:-1], posix=True)
    if len(parts) == 5 and parts[:3] == ['checkBox', '-e', '-v'] and parts[3] in ('0', '1') and parts[4] in CHECKBOXES:
        return ('checkbox', parts[4], int(parts[3]))
    if len(parts) == 5 and parts[:3] == ['textField', '-e', '-tx'] and parts[4] in TEXTFIELDS:
        return ('text', parts[4], parts[3])
    if len(parts) == 4 and parts[:3] == ['textScrollList', '-e', '-removeAll'] and parts[3] in LISTS:
        return ('clear_list', parts[3], None)
    if len(parts) == 5 and parts[:3] == ['textScrollList', '-e', '-append'] and parts[4] in LISTS:
        return ('append_list', parts[4], parts[3])
    raise ValueError('QC settings accept only known UI values; executable MEL rejected')
