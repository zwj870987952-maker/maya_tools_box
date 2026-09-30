"""Apply source-reviewed entry corrections and fix exact README link targets."""
import json
from pathlib import Path
import scan_pool


def main():
    catalog_path = scan_pool.POOL / "staging_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
    audit = json.loads((scan_pool.RUN / "entry_audit.json").read_text(encoding="utf-8"))
    manifest_path = scan_pool.RUN / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    changes = []
    for correction in audit:
        record = next(row for row in catalog if row["folder"] == correction["folder"])
        source = (scan_pool.POOL / correction["folder"] / correction["entry"]).resolve()
        source.relative_to((scan_pool.POOL / correction["folder"]).resolve())
        if not source.is_file():
            raise ValueError("Missing reviewed source: " + str(source))
        if record["entry"] != correction["entry"]:
            change = {"folder": record["folder"], "before": record["entry"], "after": correction["entry"], "evidence": correction["evidence"]}
            changes.append(change)
            manifest["entry_repairs"].append(change)
        record.update({"entry": correction["entry"], "entry_kind": correction["entry_kind"], "entry_notes": correction["evidence"]})
        item = next(item for item in manifest["tools"] if item["source_path"] == record["folder"])
        item["entry_review"] = {"evidence": correction["evidence"], "kind": correction["entry_kind"], "real_execution_verified": False}
    readme = scan_pool.POOL / "README.md"
    text = readme.read_text(encoding="utf-8")
    for repair in manifest["entry_repairs"]:
        before = repair["folder"] + "/" + repair["before"]
        after = repair["folder"] + "/" + repair["after"]
        text = text.replace("](" + before + ")", "](<" + after + ">)")
    scan_pool.dump(catalog_path, catalog)
    scan_pool.dump(manifest_path, manifest)
    readme.write_text(text, encoding="utf-8")
    print(json.dumps({"source_reviewed_corrections": len(changes), "total_entry_repairs": len(manifest["entry_repairs"])}))


if __name__ == "__main__":
    main()
