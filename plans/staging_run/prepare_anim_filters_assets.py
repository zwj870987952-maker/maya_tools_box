"""Preserve the complete upstream unit inside the candidate runtime package."""
from pathlib import Path
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
UNIT = ROOT / "tools_staging_pool/01_animation/anim_filters"
UPSTREAM = UNIT / "animFilters-v1.0-maya17"
PACKAGE = UNIT / "release_candidate/maya_toolkit/tools/anim_filters"

for source in UPSTREAM.rglob("*"):
    if source.is_file() and "__pycache__" not in source.parts:
        target = PACKAGE / "upstream" / source.relative_to(UPSTREAM)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(source), str(target))
license_path = PACKAGE / "LICENSE.txt"
if not license_path.exists():
    with urllib.request.urlopen("https://www.gnu.org/licenses/old-licenses/gpl-2.0.txt", timeout=20) as response:
        license_text = response.read(200000).decode("utf-8")
    if "GNU GENERAL PUBLIC LICENSE" not in license_text or "END OF TERMS AND CONDITIONS" not in license_text:
        raise ValueError("Unexpected GNU license response")
    license_path.write_text(license_text, encoding="utf-8")
print("Preserved upstream files and GPL v2 license")
