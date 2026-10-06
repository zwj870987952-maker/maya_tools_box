import maya.cmds as cmds
import json
MAIN_NODE = "esnSelectionSets"
GROUPS_NODE = "esnSelectionGroups"
GROUP_NODE_PREFIX = "esnGroup_"
ALL_CTRLS_NAMES = ["esn_All_Ctrls", "All_Ctrls", "all_controls", "All_Controls", "All+", "All +"]
PREFER_SMALLEST_SET = True
def _read_json(plug, default):
    if not cmds.objExists(plug):
        return default
    try:
        raw = cmds.getAttr(plug)
    except Exception:
        return default
    if not raw:
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default
def _group_node_name(group_name):
    safe = "".join(c for c in group_name if c.isalnum() or c in ("_", "-"))
    return GROUP_NODE_PREFIX + safe.strip().replace(" ", "_")
def _group_nodes():
    pairs = []
    used = set()
    groups_data = _read_json(GROUPS_NODE + ".groups", {})
    if isinstance(groups_data, dict):
        for group in groups_data.get("groups") or []:
            node = _group_node_name(group)
            if cmds.objExists(node) and node not in used:
                pairs.append((group, node))
                used.add(node)
    if not pairs:
        try:
            orphans = cmds.ls(GROUP_NODE_PREFIX + "*", type="network") or []
        except Exception:
            orphans = []
        for node in orphans:
            if node not in used:
                pairs.append((node.split(":")[-1][len(GROUP_NODE_PREFIX):], node))
                used.add(node)
    return pairs
def get_all_sets():
    entries = []
    for group, node in _group_nodes():
        sets_data = _read_json(node + ".selectionSets", {})
        metadata = _read_json(node + ".setMetadata", {})
        if not isinstance(sets_data, dict):
            continue
        if not isinstance(metadata, dict):
            metadata = {}
        order = metadata.get("set_order")
        names = [n for n in order if n in sets_data] if isinstance(order, list) else []
        names += [n for n in sets_data if n not in names]
        for name in names:
            info = metadata.get(name)
            disabled = bool(info.get("hotkey_disabled")) if isinstance(info, dict) else False
            entries.append({
                "name": name,
                "group": group,
                "objects": list(sets_data.get(name) or []),
                "disabled": disabled,
            })
    if not entries:
        sets_data = _read_json(MAIN_NODE + ".selectionSets", {})
        if isinstance(sets_data, dict):
            for name, objects in sets_data.items():
                entries.append({
                    "name": name,
                    "group": "",
                    "objects": list(objects or []),
                    "disabled": False,
                })
    disabled_names = set()
    disabled_contents = set()
    for entry in entries:
        if entry["disabled"]:
            disabled_names.add(entry["name"])
            if entry["objects"]:
                disabled_contents.add(frozenset(_base_name(o) for o in entry["objects"]))
    if disabled_names or disabled_contents:
        for entry in entries:
            if entry["disabled"]:
                continue
            if entry["name"] in disabled_names:
                entry["disabled"] = True
            elif entry["objects"] and frozenset(_base_name(o) for o in entry["objects"]) in disabled_contents:
                entry["disabled"] = True
    return entries
def _label(entry):
    return "{0}/{1}".format(entry["group"], entry["name"]) if entry["group"] else entry["name"]
def _short_name(obj):
    return obj.split("|")[-1]
def _base_name(obj):
    return _short_name(obj).rsplit(":", 1)[-1]
def _namespace_of(obj):
    short = _short_name(obj)
    return short.rsplit(":", 1)[0] if ":" in short else ""
def current_namespaces():
    namespaces = []
    for obj in cmds.ls(selection=True, long=True) or []:
        ns = _namespace_of(obj)
        if ns not in namespaces:
            namespaces.append(ns)
    return namespaces
def _ls(pattern):
    try:
        return cmds.ls(pattern, long=True) or []
    except Exception:
        return []
def _pick(candidates, preferred_namespaces):
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    for ns in preferred_namespaces:
        for candidate in candidates:
            if _namespace_of(candidate) == ns:
                return candidate
    return candidates[0]
def resolve_object(stored, preferred_namespaces):
    if cmds.objExists(stored):
        found = _pick(_ls(stored), preferred_namespaces)
        if found:
            return found
    short = _short_name(stored)
    if short != stored:
        found = _pick(_ls(short), preferred_namespaces)
        if found:
            return found
    base = _base_name(stored)
    candidates = []
    for pattern in (base, "*:" + base, "*:*:" + base):
        for name in _ls(pattern):
            if name not in candidates:
                candidates.append(name)
    if not candidates:
        try:
            candidates = cmds.ls(base, long=True, recursive=True) or []
        except Exception:
            candidates = []
    return _pick(candidates, preferred_namespaces)
def resolve_set_objects(objects, preferred_namespaces=None):
    if preferred_namespaces is None:
        preferred_namespaces = current_namespaces()
    resolved = []
    seen = set()
    for stored in objects:
        found = resolve_object(stored, preferred_namespaces)
        if found and found not in seen:
            resolved.append(found)
            seen.add(found)
    return resolved
def _match_score(entry, selected_shorts, selected_bases):
    shorts = set()
    bases = set()
    for obj in entry["objects"]:
        shorts.add(_short_name(obj))
        bases.add(_base_name(obj))
    if shorts & selected_shorts:
        return 2
    if bases & selected_bases:
        return 1
    return 0
def _looks_like_all_ctrls(name):
    lowered = name.lower()
    if name in ALL_CTRLS_NAMES:
        return True
    if "all" in lowered and ("ctrl" in lowered or "control" in lowered or "+" in lowered):
        return True
    return lowered in ("all", "todos", "full", "everything")
def get_all_controls_set(entries=None):
    if entries is None:
        entries = get_all_sets()
    for wanted in ALL_CTRLS_NAMES:
        for entry in entries:
            if entry["name"] == wanted:
                return entry
    for entry in entries:
        if _looks_like_all_ctrls(entry["name"]):
            return entry
    return None
def esnSelectNetworkSets():
    entries = get_all_sets()
    if not entries:
        cmds.warning("Pickify: nenhum selection set encontrado nesta cena.")
        return
    selection = cmds.ls(selection=True, long=True) or []
    if not selection:
        selectAllCtrls()
        return
    preferred = current_namespaces()
    selected_shorts = set(_short_name(o) for o in selection)
    selected_bases = set(_base_name(o) for o in selection)
    exact_matches = []
    loose_matches = []
    skipped = []
    for entry in entries:
        score = _match_score(entry, selected_shorts, selected_bases)
        if not score:
            continue
        if entry["disabled"]:
            skipped.append(_label(entry) + " (Disable Hotkey)")
            continue
        if _looks_like_all_ctrls(entry["name"]):
            skipped.append(_label(entry) + " (All Ctrls)")
            continue
        if score == 2:
            exact_matches.append(entry)
        else:
            loose_matches.append(entry)
    matching = exact_matches or loose_matches
    if not matching:
        if skipped:
            cmds.warning("Pickify: a selecao so aparece em sets ignorados: {0}".format(", ".join(skipped)))
        else:
            cmds.warning("Pickify: nenhum set contem os objetos selecionados. "
                         "Rode listAllSets() para ver os sets desta cena.")
        return
    if PREFER_SMALLEST_SET and len(matching) > 1:
        smallest = min(len(e["objects"]) for e in matching)
        matching = [e for e in matching if len(e["objects"]) == smallest]
    objects = []
    for entry in matching:
        objects.extend(entry["objects"])
    resolved = resolve_set_objects(objects, preferred)
    if not resolved:
        cmds.warning("Pickify: os objetos dos sets encontrados nao existem nesta cena.")
        return
    cmds.select(resolved, replace=True)
def selectSpecificSet(set_name, add=False):
    entries = get_all_sets()
    if not entries:
        cmds.warning("Pickify: nenhum selection set encontrado nesta cena.")
        return
    group_filter = None
    target = set_name
    if "/" in set_name:
        group_filter, target = set_name.split("/", 1)
    def _filter(test):
        return [e for e in entries
                if test(e) and (group_filter is None or e["group"] == group_filter)]
    matches = _filter(lambda e: e["name"] == target)
    if not matches:
        lowered = target.lower()
        matches = _filter(lambda e: e["name"].lower() == lowered)
    if not matches:
        available = ", ".join(_label(e) for e in entries)
        cmds.warning("Pickify: set '{0}' nao encontrado. Disponiveis: {1}".format(set_name, available))
        return
    if len(matches) > 1:
        cmds.warning("Pickify: '{0}' existe em mais de um grupo ({1}). Usando o primeiro - "
                     "use \"Grupo/{0}\" para escolher.".format(
                         target, ", ".join(e["group"] for e in matches)))
    entry = matches[0]
    resolved = resolve_set_objects(entry["objects"])
    if not resolved:
        cmds.warning("Pickify: nenhum objeto do set '{0}' existe nesta cena.".format(_label(entry)))
        return
    if add:
        cmds.select(resolved, add=True)
    else:
        cmds.select(resolved, replace=True)
def selectAllCtrls():
    entries = get_all_sets()
    all_ctrls = get_all_controls_set(entries)
    if all_ctrls is None:
        cmds.warning("Pickify: set de todos os controles nao encontrado. "
                     "Crie um com 'Create All Ctrls Set' no menu do Pickify.")
        return
    resolved = resolve_set_objects(all_ctrls["objects"])
    if not resolved:
        cmds.warning("Pickify: nenhum objeto de '{0}' existe nesta cena.".format(_label(all_ctrls)))
        return
    cmds.select(resolved, replace=True)
def listAllSets():
    entries = get_all_sets()
    if not entries:
        return
    preferred = current_namespaces()
    all_ctrls = get_all_controls_set(entries)
    for entry in entries:
        total = len(entry["objects"])
        resolved = len(resolve_set_objects(entry["objects"], preferred))
        if resolved == total:
            status = "OK"
        elif resolved > 0:
            status = "PARTIAL"
        else:
            status = "MISSING"
        flags = []
        if entry["disabled"]:
            flags.append("HOTKEY DESABILITADA")
        if all_ctrls is not None and entry is all_ctrls:
            flags.append("ALL CTRLS")
esnSelectNetworkSets()