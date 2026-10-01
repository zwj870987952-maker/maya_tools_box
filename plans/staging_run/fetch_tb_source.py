"""Download the original upstream snapshot, never install or execute it."""
import hashlib
import json
from pathlib import Path
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
COMMIT = 'eb8ede026c61f3cf5e38bafbc709d3bbed4d90c1'
DEST = ROOT / 'tools_staging_pool/01_animation/tb_anim_tools/release_candidate/maya_toolkit/tools/tb_anim_tools/upstream'
URL = 'https://codeload.github.com/tb-animator/tbAnimTools/zip/' + COMMIT

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    path = DEST / ('tbAnimTools-' + COMMIT + '.zip')
    if not path.exists():
        request = urllib.request.Request(URL, headers={'User-Agent': 'maya-tools-staging-local-preparation'})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read(120 * 1024 * 1024 + 1)
        if len(data) > 120 * 1024 * 1024:
            raise ValueError('Archive download exceeds 120 MiB')
        path.write_bytes(data)
    with zipfile.ZipFile(path) as archive:
        rows = archive.infolist()
        result = {'commit': COMMIT, 'url': URL, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size, 'members': len(rows), 'uncompressed_bytes': sum(x.file_size for x in rows)}
        (DEST / 'snapshot.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
        print(json.dumps(result))
        for name in ['tbtoolsInstaller.py', 'module_startup.py', 'userSetup.py', '__init__.py', 'LICENSE']:
            entry = next(x for x in rows if x.filename == 'tbAnimTools-' + COMMIT + '/' + name)
            print('\nFILE ' + name + '\n' + archive.read(entry).decode('utf-8', errors='replace')[:28000])

if __name__ == '__main__':
    main()
