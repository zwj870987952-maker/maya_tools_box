"""Record an existing commit and next tool without inventing commit identities."""
import argparse
import datetime
import json
import subprocess
import scan_pool


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--completed", required=True)
    parser.add_argument("--next-tool")
    parser.add_argument("--five-hour-used", type=float)
    parser.add_argument("--weekly-used", type=float)
    args = parser.parse_args()
    manifest_path = scan_pool.RUN / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(scan_pool.ROOT), text=True).strip()
    completed = next(item for item in manifest["tools"] if item["source_path"] == args.completed)
    if completed["status"] not in ("prepared_verified_offline", "prepared_unverified") or not completed["candidate_complete"]:
        raise ValueError("Completed item has no complete prepared candidate")
    completed["source_commit"] = commit
    if args.next_tool:
        following = next(item for item in manifest["tools"] if item["source_path"] == args.next_tool)
        following["status"] = "working"
        manifest["execution"]["current_tool"] = args.next_tool
    if args.five_hour_used is not None and args.weekly_used is not None:
        if not all(0 <= value <= 100 for value in (args.five_hour_used, args.weekly_used)):
            raise ValueError("Usage percentages must be between 0 and 100")
        manifest["execution"]["last_usage"] = {"five_hour_used_percent": args.five_hour_used, "weekly_used_percent": args.weekly_used, "recorded_at": datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(), "note": "Caller supplied actual read; reread on next run"}
    scan_pool.dump(manifest_path, manifest)
    print(json.dumps({"completed": args.completed, "source_commit": commit, "next_tool": args.next_tool}))


if __name__ == "__main__":
    main()
