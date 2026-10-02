import os
from pathlib import Path
import tempfile
def save_output(target):
    from maya import cmds
    import shutil
    target = Path(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mtb_replaced_', dir=str(target.parent)) as directory:
        generated = Path(directory) / ('scene' + target.suffix)
        cmds.file(rename=str(generated))
        cmds.file(save=True, type='mayaBinary' if target.suffix.lower() == '.mb' else 'mayaAscii', force=True)
        owned = False
        try:
            with target.open('xb') as writer:
                owned = True
                with generated.open('rb') as reader:
                    shutil.copyfileobj(reader, writer)
                writer.flush()
                os.fsync(writer.fileno())
        except Exception:
            if owned:
                target.unlink(missing_ok=True)
            raise
    return {'path': str(target), 'bytes': target.stat().st_size}
