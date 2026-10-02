"""Owned stage recovery; preserve payload and old versions without collisions."""
from pathlib import Path
import shutil,uuid
from .guards import path
owned={}
def tree(p):
    p=path(str(p))
    if p.is_dir():
        for child in p.rglob('*'):
            if child.is_symlink():raise ValueError('Symlink in asset/history tree')
    return p
def install(module):
    original_stage=module.stage_existing_asset;original_commit=module.commit_stage
    def stage(asset,item):
        tree(asset);row=original_stage(asset,item)
        if row:owned[row['stage']]=dict(row)
        return row
    def checked(row):
        expected=owned.get(row.get('stage'))
        if expected is None or row!=expected:raise ValueError('Unowned history stage')
        root=tree(row['stage']);asset=tree(row['assetPath'])
        if root.parent!=asset.parent or not root.name.startswith('.studiolibrary_plus_history_'):raise ValueError('Invalid history stage')
        for key in ('snapshot','history'):
            if path(row[key]).parent!=root:raise ValueError('Invalid stage child')
        return root,asset
    def restore(row):
        if not row:return True
        root,asset=checked(row);snapshot=tree(row['snapshot']);history=tree(row['history'])
        if not snapshot.is_dir():return False
        # Build the whole recovery before moving a partially written target.
        recovery=root/'recovered';shutil.copytree(snapshot,recovery)
        if history.is_dir():shutil.copytree(history,recovery/'.history')
        elif (asset/'.history').is_dir():shutil.copytree(asset/'.history',recovery/'.history')
        displaced=root/'failed_asset'
        if asset.exists():shutil.move(str(asset),str(displaced))
        try:shutil.move(str(recovery),str(asset))
        except Exception:
            if displaced.exists() and not asset.exists():shutil.move(str(displaced),str(asset))
            raise
        # A failed partial asset is preserved for inspection, not discarded.
        owned.pop(row['stage'],None)
        return True
    def merge(source,dest):
        source=tree(source);dest=tree(dest)
        if not source.is_dir():return
        rows=list(source.iterdir())
        if any((dest/p.name).exists() for p in rows):raise FileExistsError('History collision; recovery stage preserved')
        dest.mkdir(exist_ok=True)
        for p in rows:shutil.move(str(p),str(dest/p.name))
    def commit(row,asset):
        checked(row);tree(asset)
        if path(asset)!=path(row['assetPath']):raise ValueError('Destination changed during save')
        result=original_commit(row,asset);owned.pop(row['stage'],None);return result
    module.stage_existing_asset=stage;module.restore_stage=restore;module._merge_history=merge;module.commit_stage=commit
