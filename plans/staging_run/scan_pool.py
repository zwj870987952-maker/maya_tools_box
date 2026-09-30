"""Read source inventory without importing or running tools; preserve progress."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POOL = ROOT / "tools_staging_pool"
RUN = Path(__file__).resolve().parent


def dump(path, data):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair-paths", action="store_true")
    args = parser.parse_args()
    catalog_path = POOL / "staging_catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
    previous = json.loads((RUN / "manifest.json").read_text(encoding="utf-8")) if (RUN / "manifest.json").exists() else {}
    old = {item["source_path"]: item for item in previous.get("tools", [])}
    folders = sorted(p.relative_to(POOL).as_posix() for category in POOL.iterdir() if category.is_dir() and category.name[:2].isdigit() for p in category.iterdir() if p.is_dir())
    records = {}
    duplicates = []
    for item in catalog:
        if item["folder"] in records:
            duplicates.append(item["folder"])
        records[item["folder"]] = item
    repairs = previous.get("entry_repairs", [])
    tools = []
    for folder in folders:
        unit = POOL / folder
        record = records.get(folder, {})
        files = sorted(p for p in unit.rglob("*") if p.is_file() and not {"release_candidate", "__pycache__"}.intersection(p.relative_to(unit).parts))
        entry = record.get("entry")
        exists = bool(entry and (unit / entry).is_file())
        matches = [p.relative_to(unit).as_posix() for p in files if entry and p.name.lower() == Path(entry).name.lower()]
        if args.repair_paths and not exists and len(matches) == 1:
            repairs.append({"folder": folder, "before": entry, "after": matches[0], "evidence": "Unique same filename found inside original unit; callable still requires source review."})
            entry = matches[0]
            record["entry"] = entry
            exists = True
        item = old.get(folder, {}).copy()
        digest = hashlib.sha256()
        for source in files:
            digest.update(source.relative_to(unit).as_posix().encode("utf-8") + b"\0")
            with source.open("rb") as stream:
                for chunk in iter(lambda: stream.read(65536), b""):
                    digest.update(chunk)
        tree_hash = digest.hexdigest()
        if item.get("source_tree_sha256") and item["source_tree_sha256"] != tree_hash and item.get("candidate_complete"):
            item["status"] = "pending"
            item["candidate_complete"] = False
            item.setdefault("issues", []).append("Original source/resources changed; candidate must be reviewed again")
        item["source_tree_sha256"] = tree_hash
        if item.get("candidate_complete") and item.get("promotion", {}).get("candidate_sha256"):
            from promote_candidate import fingerprint
            candidate = ROOT / item["candidate_path"]
            try:
                description = json.loads((candidate / "promotion.json").read_text(encoding="utf-8"))
                current_candidate_hash = fingerprint(candidate, description)
            except (OSError, ValueError, KeyError):
                current_candidate_hash = None
            if current_candidate_hash != item["promotion"]["candidate_sha256"]:
                item["status"] = "pending"
                item["candidate_complete"] = False
                item.setdefault("issues", []).append("Candidate changed or assets disappeared after checks; rerun verification")
        item.update({"source_path": folder, "name": record.get("name", unit.name), "category": record.get("category", folder.split("/")[0]), "entry": entry, "entry_exists": exists, "entry_candidates": matches, "source_file_count": len(files), "source_files": [p.relative_to(unit).as_posix() for p in files if p.suffix.lower() in (".py", ".mel", ".cpp", ".h", ".cs", ".uplugin")], "license_files": [p.relative_to(unit).as_posix() for p in files if "license" in p.name.lower() or "licence" in p.name.lower() or "copyright" in p.name.lower()]})
        if exists:
            new_hash = hashlib.sha256((unit / entry).read_bytes()).hexdigest()
            if item.get("entry_sha256") and item["entry_sha256"] != new_hash and item.get("candidate_complete"):
                item["status"] = "pending"
                item["candidate_complete"] = False
                item.setdefault("issues", []).append("Original entry changed since candidate preparation; review candidate again")
            item["entry_sha256"] = new_hash
        item.setdefault("status", "pending")
        item.setdefault("candidate_complete", False)
        item.setdefault("offline_checks", [])
        item.setdefault("maya_acceptance", {"status": "not_run", "versions": []})
        item.setdefault("issues", [])
        tools.append(item)
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    data = {"schema_version": 1, "updated_at": now, "scope": "tools_staging_pool only; rescan on resume", "execution": previous.get("execution", {"state": "preparing", "heartbeat_id": "automation", "heartbeat_status": "PAUSED", "heartbeat_verified": False, "reset_guard": "not_started_requires_authorization", "obsidian_sync": "disabled_for_this_run", "single_writer": "this_chat_only"}), "entry_repairs": repairs, "catalog_missing_folders": sorted(set(records) - set(folders)), "unlisted_folders": sorted(set(folders) - set(records)), "duplicate_catalog_folders": duplicates, "tools": tools}
    if args.repair_paths:
        dump(catalog_path, catalog)
    dump(RUN / "manifest.json", data)
    lines = ["# 待整理工具池执行进度", "", "更新时间：" + now, "", "离线检查不等于真实 Maya 验收。正式库尚未晋级。", "", "| 工具 | 状态 | 入口存在 | 候选完整 | Maya 验收 |", "| --- | --- | --- | --- | --- |"]
    for item in tools:
        lines.append("| `{}` | {} | {} | {} | {} |".format(item["source_path"], item["status"], item["entry_exists"], item["candidate_complete"], item["maya_acceptance"]["status"]))
    (RUN / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"physical": len(folders), "catalog": len(catalog), "entry_exists": sum(x["entry_exists"] for x in tools), "entry_unresolved": sum(not x["entry_exists"] for x in tools), "path_repairs": len(repairs)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
