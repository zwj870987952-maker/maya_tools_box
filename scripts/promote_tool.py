import json
import os
import shutil
import sys
from pathlib import Path

def to_safe_path(p: Path) -> Path:
    s = str(p.resolve())
    if os.name == 'nt' and not s.startswith('\\\\?\\'):
        return Path('\\\\?\\' + s)
    return p

def promote(staging_rel_path: str):
    root = Path(__file__).resolve().parents[1]
    rc_dir = root / staging_rel_path / "release_candidate"
    promo_file = rc_dir / "promotion.json"
    if not promo_file.is_file():
        raise FileNotFoundError(f"Missing promotion.json at {promo_file}")

    data = json.loads(promo_file.read_text(encoding='utf-8'))
    tool_id = data['tool_id']
    files = data['files']

    print(f"Promoting tool: {tool_id} ({len(files)} files) from {rc_dir}")

    count = 0
    for item in files:
        src = to_safe_path(rc_dir / item['source'])
        dst = to_safe_path(root / item['target'])
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            content = src.read_bytes()
            dst.write_bytes(content)
            count += 1
            if count % 200 == 0:
                print(f"Copied {count}/{len(files)} files...")
        else:
            print(f"Warning: source file not found: {src}")

    print(f"Completed copying {count} files for {tool_id}.")
    return data

if __name__ == '__main__':
    if len(sys.argv) > 1:
        promote(sys.argv[1])
