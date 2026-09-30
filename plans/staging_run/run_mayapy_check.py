"""Run candidate tests with disposable Maya preferences and a bounded timeout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile


def python_fingerprint(source_root):
    digest = hashlib.sha256()
    for path in sorted(source_root.rglob("*.py")):
        if "__pycache__" not in path.parts:
            digest.update(path.relative_to(source_root).as_posix().encode("utf-8") + b"\0" + path.read_bytes())
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("test")
    parser.add_argument("--mayapy", default=r"C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe")
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    test_path = Path(args.test).resolve()
    source_root = test_path.parents[1]
    source_hash = python_fingerprint(source_root)
    with tempfile.TemporaryDirectory(prefix="staging_maya_") as directory:
        env = os.environ.copy()
        env.update({"MAYA_APP_DIR": directory, "QT_QPA_PLATFORM": "offscreen", "MAYA_DISABLE_CIP": "1", "MAYA_DISABLE_CER": "1", "STAGING_ISOLATED_MAYAPY": "1", "PYTHONDONTWRITEBYTECODE": "1"})
        try:
            result = subprocess.run([args.mayapy, str(Path(args.test).resolve())], env=env, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=args.timeout)
            report = {"kind": "mayapy_standalone", "executable": args.mayapy, "test": args.test, "returncode": result.returncode, "passed": result.returncode == 0, "output": result.stdout.decode("utf-8", errors="replace"), "gui_acceptance": False}
        except subprocess.TimeoutExpired as error:
            output = error.stdout or b""
            report = {"kind": "mayapy_standalone", "executable": args.mayapy, "passed": False, "timeout_seconds": args.timeout, "output": output.decode("utf-8", errors="replace"), "gui_acceptance": False}
        report["python_source_sha256"] = source_hash
        Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in report.items() if key != "output"}, ensure_ascii=True))


if __name__ == "__main__":
    main()
