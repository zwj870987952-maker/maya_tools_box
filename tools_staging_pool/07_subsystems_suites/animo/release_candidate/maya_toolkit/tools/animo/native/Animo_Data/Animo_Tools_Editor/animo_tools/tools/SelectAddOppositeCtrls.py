import maya.cmds as cmds
import re


SIDE_TOKEN_GROUPS = [
    ("left", "right"),
    ("lft", "rgt"),
    ("lt", "rt"),
    ("lf", "rf"),
    ("lf", "rt"),
    ("lhs", "rhs"),
    ("lh", "rh"),
    ("l", "r"),
]

SIDE_TOKEN_PARTNERS = {}
for _leftToken, _rightToken in SIDE_TOKEN_GROUPS:
    SIDE_TOKEN_PARTNERS.setdefault(_leftToken, set()).add(_rightToken)
    SIDE_TOKEN_PARTNERS.setdefault(_rightToken, set()).add(_leftToken)

TOKEN_PATTERN = re.compile(r'[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|\d+')


def strip_namespace(obj):
    if ":" in obj:
        ns, name = obj.rsplit(":", 1)
        return ns + ":", name
    return "", obj


def tokenize_with_spans(name):
    return [(m.start(), m.end(), m.group(0)) for m in TOKEN_PATTERN.finditer(name)]


def match_token_case(sample, word):
    if sample.isupper():
        return word.upper()
    if sample[:1].isupper():
        return word.capitalize()
    return word.lower()


def learn_scene_side_tokens():
    scene_objects = cmds.ls(dag=True, long=False) or []
    learned = {}
    for obj in scene_objects:
        _, name = strip_namespace(obj)
        for _, _, text in tokenize_with_spans(name):
            lowerText = text.lower()
            if lowerText in SIDE_TOKEN_PARTNERS or len(lowerText) > 4:
                continue
            hasL = "l" in lowerText
            hasR = "r" in lowerText
            if hasL and not hasR:
                opposite = lowerText.replace("l", "r")
            elif hasR and not hasL:
                opposite = lowerText.replace("r", "l")
            else:
                continue
            learned.setdefault(lowerText, set()).add(opposite)
            learned.setdefault(opposite, set()).add(lowerText)
    return learned


def build_side_partners():
    partners = {}
    for token, opposites in SIDE_TOKEN_PARTNERS.items():
        partners.setdefault(token, set()).update(opposites)
    for token, opposites in learn_scene_side_tokens().items():
        partners.setdefault(token, set()).update(opposites)
    return partners


def find_opposite_name(name, sidePartners):
    for start, end, text in tokenize_with_spans(name):
        opposites = sidePartners.get(text.lower())
        if not opposites:
            continue
        for opposite in opposites:
            replacement = match_token_case(text, opposite)
            yield name[:start] + replacement + name[end:]


def select_add_opposite():
    selected_ctrls = cmds.ls(selection=True)
    if not selected_ctrls:
        cmds.warning("No controls selected.")
        return

    sidePartners = build_side_partners()
    opposites = []

    for ctrl in selected_ctrls:
        namespace, short_name = strip_namespace(ctrl)
        found = None
        for candidate in find_opposite_name(short_name, sidePartners):
            opposite_full = namespace + candidate
            if opposite_full != ctrl and cmds.objExists(opposite_full):
                found = opposite_full
                break
        if found:
            opposites.append(found)

    if opposites:
        cmds.select(opposites, add=True)
    else:
        cmds.warning("No matching opposites found for selected controls.")


select_add_opposite()