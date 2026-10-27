import json
from pathlib import Path

root = Path('.')
names = [
    'advanced_skeleton_mirror_session',
    'jop_retarget_anim_v09',
    'keyframe_overlap_v2_0',
    'maya_keyframe_reduction',
    'maya_timeline_marker',
    'mov_playblast_v11',
    'overslapper_v1_03'
]

for n in names:
    matches = list(root.glob(f'tools_staging_pool/**/{n}/release_candidate/promotion.json'))
    if matches:
        data = json.loads(matches[0].read_text(encoding='utf-8'))
        tool_id = data.get('tool_id')
        module = data.get('registration', {}).get('module')
        prod_exists = (root / f'maya_toolkit/tools/{module}').is_dir()
        print(f"{n} -> tool_id: {tool_id}, module: {module}, in_prod: {prod_exists}")
    else:
        print(f"{n} -> NO PROMOTION.JSON FOUND")
