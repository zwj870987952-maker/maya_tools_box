"""Only explicit legacy reload actions and exclusive task-scoped exports."""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import os

_export = ContextVar('rdm_candidate_export', default=None)


def bundled_scripts_dir(**kwargs):
    return (Path(__file__).parent / 'native').as_posix() + '/'


def legacy_reload(module):
    # Definitions are already loaded without side effects. Original reload
    # callbacks explicitly run retained script logic instead of importing twice.
    module.run_script()
    return module


def export_path(value):
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError('Explicit absolute new export file required')
    path = Path(value)
    if not path.parent.is_dir() or path.exists() or os.path.lexists(path):
        raise ValueError('Existing export or missing parent directory rejected')
    if any(p.is_symlink() or getattr(p, 'is_junction', lambda: False)() for p in [path.parent] + list(path.parent.parents)):
        raise ValueError('Export parent links/junctions rejected')
    if path.suffix.lower() not in ('.json', '.py'):
        raise ValueError('Original export supports .json or .py')
    return path


def checked_output():
    context = _export.get()
    if context is None:
        raise RuntimeError('Explicit export API context required; original hardcoded path disabled')
    path = export_path(context['output_path'])
    return path.open('x', encoding='utf-8', newline='\n')


def explicit_ui_input():
    context = _export.get()
    if context is None or not context.get('input_ui'):
        raise RuntimeError('Explicit .ui input required')
    path = Path(context['input_ui'])
    if not path.is_absolute() or not path.is_file() or path.suffix.lower() != '.ui':
        raise ValueError('Existing absolute .ui file required')
    return str(path)


@contextmanager
def export_context(p):
    token = _export.set(p)
    try:
        yield
    finally:
        _export.reset(token)
