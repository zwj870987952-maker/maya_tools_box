"""Run bounded offline checks and record candidate evidence into the manifest."""
import argparse
import ast
import datetime
import json
from pathlib import Path
import subprocess
import sys

import scan_pool
from run_mayapy_check import python_fingerprint


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tool", required=True)
    parser.add_argument("--test", required=True)
    parser.add_argument("--mayapy-report")
    args = parser.parse_args()
    candidate = scan_pool.POOL / args.tool / "release_candidate"
    description = json.loads((candidate / "promotion.json").read_text(encoding="utf-8"))
    checks = []
    errors = []
    for path in sorted(candidate.rglob("*.py")):
        try:
            ast.parse(path.read_bytes(), filename=str(path))
        except Exception as error:
            errors.append(str(error))
    checks.append({"kind": "python_static_parse", "passed": not errors, "errors": errors})
    commands = [([sys.executable, str(candidate / args.test)], "isolated_unittest"), ([sys.executable, str(scan_pool.RUN / "promote_candidate.py"), "--candidate", str(candidate)], "promotion_preview")]
    preview = None
    for command, kind in commands:
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=45)
            output = result.stdout.decode("utf-8", errors="replace")
            checks.append({"kind": kind, "passed": result.returncode == 0, "returncode": result.returncode, "output": output})
            if kind == "promotion_preview" and result.returncode == 0:
                preview = json.loads(output)
        except subprocess.TimeoutExpired:
            checks.append({"kind": kind, "passed": False, "reason": "timeout after 45 seconds"})
    if args.mayapy_report:
        report = json.loads(Path(args.mayapy_report).read_text(encoding="utf-8"))
        checks.append(report)
        checks.append({"kind": "mayapy_report_matches_candidate", "passed": report.get("python_source_sha256") == python_fingerprint(candidate)})
    manifest = json.loads((scan_pool.RUN / "manifest.json").read_text(encoding="utf-8"))
    item = next(item for item in manifest["tools"] if item["source_path"] == args.tool)
    complete = bool(preview) and (candidate / "acceptance.md").is_file()
    limitations = ["Real Maya GUI acceptance pending", "Other Maya/Python versions unverified"] + description.get("verification_limitations", [])
    item.update({"status": "prepared_verified_offline" if all(check["passed"] for check in checks) else "prepared_unverified", "candidate_path": candidate.relative_to(scan_pool.ROOT).as_posix(), "candidate_complete": complete, "offline_checks": checks, "acceptance_instructions": (candidate / "acceptance.md").relative_to(scan_pool.ROOT).as_posix(), "promotion": preview, "resources": description.get("resources", []), "external_dependencies": description.get("dependencies", []), "source_preserved": True, "change_summary": description.get("change_summary", "See candidate knowledge document for behavior and safety changes."), "issues": limitations, "prepared_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()})
    manifest["execution"].update({"state": "working", "heartbeat_transition_verified": True, "heartbeat_verified": False, "heartbeat_status": "PAUSED", "last_completed_tool": args.tool})
    scan_pool.dump(scan_pool.RUN / "manifest.json", manifest)
    print(json.dumps({"tool": args.tool, "status": item["status"], "candidate_complete": item["candidate_complete"], "checks": [{"kind": check["kind"], "passed": check["passed"]} for check in checks]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
