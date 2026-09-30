"""Python 3 syntax audit only: never import or execute staging sources."""
import ast
import json
from pathlib import Path
import sys
import scan_pool


def main():
    manifest_path = scan_pool.RUN / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reports = []
    for item in manifest["tools"]:
        report = {"source_path": item["source_path"], "python_files": 0, "mel_files": 0, "parse_errors": [], "top_level_call_files": [], "runtime_verified": False}
        for relative in item["source_files"]:
            source = scan_pool.POOL / item["source_path"] / relative
            if source.suffix.lower() == ".mel":
                report["mel_files"] += 1
                continue
            if source.suffix.lower() != ".py":
                continue
            report["python_files"] += 1
            try:
                tree = ast.parse(source.read_bytes(), filename=relative)
                if any(isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) for node in tree.body):
                    report["top_level_call_files"].append(relative)
            except Exception as error:
                report["parse_errors"].append({"file": relative, "error": str(error)})
        item["source_parse_audit"] = {"interpreter": sys.version.split()[0], "python_files": report["python_files"], "mel_files": report["mel_files"], "parse_errors": len(report["parse_errors"]), "possible_top_level_calls": len(report["top_level_call_files"]), "note": "Python3 syntax scan only. Errors may be legacy Python2 syntax/encoding; top-level calls may be read-only. Not candidate verification or Maya acceptance."}
        reports.append(report)
    scan_pool.dump(scan_pool.RUN / "source_audit.json", {"python_version": sys.version, "reports": reports})
    scan_pool.dump(manifest_path, manifest)
    print(json.dumps({"units": len(reports), "python_files": sum(x["python_files"] for x in reports), "mel_files": sum(x["mel_files"] for x in reports), "units_with_python3_parse_errors": sum(bool(x["parse_errors"]) for x in reports)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
