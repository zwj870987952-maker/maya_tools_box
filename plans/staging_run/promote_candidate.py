"""Prepare promotion without scene operations; --apply requires acceptance evidence."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def inside(path, parent):
    resolved = path.resolve()
    resolved.relative_to(parent.resolve())
    return resolved


def payload(candidate, description):
    pairs = []
    for item in description["files"]:
        if description.get('runtime') in ('unreal_editor', 'windows_standalone'):
            tool = description['tool_id']
            if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', tool):
                raise ValueError('Invalid external tool identifier')
            permitted = ('engine_toolkit/tools/' + tool + '/', 'docs/tools/' + tool, 'tests/test_' + tool)
            target_name = item['target'].replace('\\', '/')
            if item['source'] != item['target'] or not any(target_name.startswith(p) for p in permitted):
                raise ValueError('External tool payload must use its own engine/docs/tests namespace')
        source = inside(candidate / item["source"], candidate)
        target = inside(ROOT / item["target"], ROOT)
        if not source.is_file():
            raise ValueError("Missing candidate file: " + str(source))
        if target.exists():
            raise ValueError("Target already exists; review before promotion: " + str(target))
        pairs.append((source, target))
    return pairs


def fingerprint(candidate, description):
    digest = hashlib.sha256()
    for item in sorted(description["files"], key=lambda row: row["source"]):
        source = inside(candidate / item["source"], candidate)
        digest.update(item["source"].encode("utf-8") + b"\0" + source.read_bytes() + b"\0")
    digest.update(json.dumps(description, sort_keys=True).encode("utf-8"))
    return digest.hexdigest()


def registry_change(description):
    path = ROOT / "maya_toolkit/tools/__init__.py"
    original = path.read_bytes()
    source = original.decode("utf-8")
    source = source.replace("\r\n", "\n")
    registration = description["registration"]
    cls, module = registration["class_name"], registration["module"]
    for value in (cls, module):
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError("Invalid registration identifier")
    tree = ast.parse(source)
    assignments = {node.targets[0].id: node for node in tree.body if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)}
    changes = []
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    for name, expression in (("ALL_TOOL_CLASSES", cls), ("__all__", repr(cls))):
        node = assignments[name]
        if not isinstance(node.value, ast.List):
            raise ValueError("Registry is not the expected literal list")
        for element in node.value.elts:
            if (isinstance(element, ast.Name) and element.id == cls) or (isinstance(element, ast.Constant) and element.value == cls):
                raise ValueError("Class already registered: " + cls)
        insertion = offsets[node.value.end_lineno - 1] + node.value.end_col_offset - 1
        changes.append((insertion, "    " + expression + ",\n"))
    insertion = offsets[assignments["ALL_TOOL_CLASSES"].lineno - 1]
    changes.append((insertion, "from .{} import {}\n\n".format(module, cls)))
    for offset, addition in sorted(changes, reverse=True):
        source = source[:offset] + addition + source[offset:]
    ast.parse(source)
    if b"\r\n" in original:
        source = source.replace("\n", "\r\n")
    return path, original, source.encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--acceptance")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    candidate = inside(Path(args.candidate), ROOT / "tools_staging_pool")
    if candidate.name != "release_candidate":
        raise ValueError("Expected release_candidate directory")
    description = json.loads((candidate / "promotion.json").read_text(encoding="utf-8"))
    pairs = payload(candidate, description)
    external = description.get('runtime') in ('unreal_editor', 'windows_standalone')
    if external:
        if description.get('registration') is not None or not description.get('entry_module'):
            raise ValueError('External tool requires its own entry module and no Maya registration')
        registry, original, updated = None, None, None
    else:
        registry, original, updated = registry_change(description)
    candidate_hash = fingerprint(candidate, description)
    if args.apply:
        if not args.acceptance:
            raise ValueError("--apply requires a user-recorded --acceptance file")
        acceptance = json.loads(Path(args.acceptance).read_text(encoding="utf-8"))
        required = (acceptance.get("passed") is True, acceptance.get("tool_id") == description["tool_id"], acceptance.get("candidate_sha256") == candidate_hash, bool(acceptance.get("runtime_version" if external else "maya_version")), bool(acceptance.get("accepted_by")), bool(acceptance.get("date")))
        if not all(required):
            raise ValueError("Missing/stale human runtime acceptance; refusing promotion")
        for source, unused_target in pairs:
            if source.suffix == ".py":
                compile(source.read_bytes(), str(source), "exec")
        copied = []
        try:
            for source, target in pairs:
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    raise ValueError("Target appeared during promotion: " + str(target))
                # Exclusive creation avoids silently replacing another chat's file.
                with target.open("xb") as stream:
                    stream.write(source.read_bytes())
                copied.append(target)
            if registry is not None and registry.read_bytes() != original:
                raise ValueError("Registry changed during promotion")
            if registry is not None:
                registry.write_bytes(updated)
        except Exception:
            if registry is not None and registry.read_bytes() == updated:
                registry.write_bytes(original)
            for target in reversed(copied):
                target.unlink()
            raise
    print(json.dumps({"tool_id": description["tool_id"], "candidate_sha256": candidate_hash, "applied": args.apply, "files": [str(target.relative_to(ROOT)) for unused_source, target in pairs], "registry": str(registry.relative_to(ROOT)) if registry else None, "panel": description.get('panel', 'Native runtime entry') if external else "ToolRegistry discovery plus tool.show_ui", "maya_acceptance_required": not external, "runtime_acceptance_required": True, "runtime": description.get('runtime', 'maya')}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
