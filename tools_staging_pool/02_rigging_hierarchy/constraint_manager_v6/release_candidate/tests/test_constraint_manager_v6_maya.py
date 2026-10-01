import json
import os
from pathlib import Path
import runpy
import sys
import tempfile
import unittest
if os.environ.get('STAGING_ISOLATED_MAYAPY') != '1':
    raise RuntimeError('Only isolated temporary Maya')
import maya.standalone
maya.standalone.initialize(name='python')
from maya import cmds
RC = Path(__file__).resolve().parents[1]
TOOL = runpy.run_path(str(RC/'launch_candidate.py'))['load_tool']()
mod = sys.modules[TOOL.__class__.__module__]
engine = __import__(mod.__package__+'.engine', fromlist=['engine'])


def state():
    return (sorted(cmds.ls(long=True)), cmds.currentTime(query=True), cmds.ls(selection=True, long=True), cmds.autoKeyframe(query=True, state=True), cmds.namespaceInfo(currentNamespace=True), cmds.undoInfo(query=True, undoName=True))


def scene(kind='parentConstraint'):
    cmds.namespace(add='rig')
    drivers = [cmds.createNode('transform', name='rig:driverW_'+str(i)) for i in range(2)]
    child = cmds.createNode('transform', name='rig:driven')
    cmds.setAttr(drivers[0]+'.tx', 4.)
    cmds.setAttr(drivers[1]+'.tx', 8.)
    cmds.setAttr(child+'.tx', 6.)
    constraint = getattr(cmds, kind)(drivers, child, maintainOffset=True)[0]
    return drivers, child, constraint


class MayaChecks(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        cmds.autoKeyframe(state=False)
        engine._snapshots.clear()

    def test_real_aliases_order_key_values_all_modes_and_preflight(self):
        drivers, child, constraint = scene()
        data = engine.info(constraint)
        attrs = [x['weight_plug'] for x in data['targets']]
        self.assertEqual([engine.node(x) for x in drivers], [x['node'] for x in data['targets']])
        before = state()
        dry = TOOL.run(dry_run=True, action='weights', selected_weights=[attrs[0]], all_weights=attrs, mode='selected_one')
        self.assertTrue(dry.success, dry.message)
        self.assertEqual(before, state())
        cmds.setKeyframe(attrs[0], time=1, value=.25)
        cmds.setKeyframe(attrs[0], time=9, value=.75)
        cmds.currentTime(5)
        result = TOOL.run(action='weights', selected_weights=[attrs[0]], all_weights=attrs, mode='selected_one')
        self.assertTrue(result.success, result.message)
        self.assertEqual([1.], cmds.keyframe(attrs[0], query=True, time=(5, 5), valueChange=True))
        self.assertEqual([0.], cmds.keyframe(attrs[1], query=True, time=(5, 5), valueChange=True))
        cmds.undo()
        self.assertEqual([1., 9.], cmds.keyframe(attrs[0], query=True, timeChange=True))
        for mode, expected in (('zero', 0.), ('one', 1.), ('custom', .42)):
            result = TOOL.run(action='weights', selected_weights=[attrs[0]], mode=mode, value=.42)
            self.assertTrue(result.success, result.message)
            self.assertAlmostEqual(expected, cmds.getAttr(attrs[0]))
        cmds.setAttr(attrs[1], lock=True)
        cmds.select(constraint)
        before = state()
        self.assertFalse(TOOL.run(action='weights', selected_weights=attrs, mode='zero').success)
        self.assertFalse(TOOL.run(action='delete', constraints=[]).success)
        self.assertEqual(before, state())

    def test_disconnect_restore_preserves_uuid_animation_offsets_and_protects_new_driver(self):
        drivers, child, constraint = scene()
        d = engine.info(constraint)
        attr = d['targets'][0]['weight_plug']
        cmds.setKeyframe(attr, time=1, value=.2)
        cmds.setKeyframe(attr, time=9, value=.8)
        offsets = [cmds.getAttr(d['node']+'.target['+str(x['index'])+'].targetOffsetTranslate') for x in d['targets']]
        before = state()
        result = TOOL.run(action='disconnect', constraints=[constraint])
        self.assertTrue(result.success, result.message)
        self.assertTrue(cmds.objExists(constraint))
        self.assertEqual([], engine.info(constraint)['outputs'])
        self.assertEqual([1., 9.], cmds.keyframe(attr, query=True, timeChange=True))
        restored = TOOL.run(action='restore', constraints=[constraint])
        self.assertTrue(restored.success, restored.message)
        self.assertEqual(d['uuid'], engine.info(constraint)['uuid'])
        self.assertEqual(offsets, [cmds.getAttr(d['node']+'.target['+str(x['index'])+'].targetOffsetTranslate') for x in d['targets']])
        cmds.undo()
        self.assertEqual([], engine.info(constraint)['outputs'])
        cmds.undo()
        self.assertEqual(before[:5], state()[:5])
        TOOL.run(action='disconnect', constraints=[constraint])
        unrelated = cmds.createNode('transform', name='newDriver')
        cmds.connectAttr(unrelated+'.tx', child+'.tx')
        self.assertFalse(TOOL.run(action='restore', constraints=[constraint]).success)
        self.assertTrue(cmds.isConnected(unrelated+'.tx', child+'.tx'))

    def test_inverse_is_actual_direction_each_target_restore_and_cycle_guard(self):
        drivers, child, constraint = scene('pointConstraint')
        result = TOOL.run(action='reverse', constraints=[constraint])
        self.assertTrue(result.success, result.message)
        ids = result.data['results'][0]['reverse_uuids']
        self.assertEqual(2, len(ids))
        for identity in ids:
            data = engine.info(identity)
            self.assertEqual(engine.identity(child), data['targets'][0]['uuid'])
            self.assertIn(data['constrained_uuid'], [engine.identity(x) for x in drivers])
        cmds.setAttr(child+'.ty', 3.)
        self.assertTrue(all(abs(cmds.getAttr(x+'.ty')-3.) < .001 for x in drivers))
        restored = TOOL.run(action='restore', constraints=[constraint])
        self.assertTrue(restored.success, restored.message)
        self.assertTrue(all(not cmds.ls(x) for x in ids))
        self.assertTrue(engine.info(constraint)['outputs'])
        cmds.undo()
        self.assertEqual(2, len([x for x in ids if cmds.ls(x)]))
        cmds.undo()
        cmds.undo()
        self.assertTrue(engine.info(constraint)['outputs'])
        # Existing animated drivers are protected before any original disconnection.
        cmds.setKeyframe(drivers[0]+'.ty', time=1, value=0.)
        before = state()
        self.assertFalse(TOOL.run(action='reverse', constraints=[constraint]).success)
        self.assertEqual(before, state())

    def test_rebuild_real_node_retains_offsets_skip_custom_attribute_and_input_keys(self):
        drivers, child, constraint = scene()
        data = engine.info(constraint)
        attr = data['targets'][0]['weight_plug']
        cmds.setKeyframe(attr, time=1, value=.3)
        cmds.setKeyframe(attr, time=7, value=.7)
        cmds.addAttr(constraint, longName='userNote', dataType='string')
        cmds.setAttr(constraint+'.userNote', 'preserve', type='string')
        cmds.setAttr(constraint+'.interpType', 2)
        offsets = [cmds.getAttr(data['node']+'.target['+str(t['index'])+'].targetOffsetTranslate') for t in data['targets']]
        curves = cmds.listConnections(attr, source=True, destination=False)
        result = TOOL.run(action='rebuild', constraints=[constraint])
        self.assertTrue(result.success, result.message)
        new = result.data['results'][0]['new']
        self.assertNotEqual(data['uuid'], engine.identity(new))
        self.assertEqual('preserve', cmds.getAttr(new+'.userNote'))
        self.assertEqual(2, cmds.getAttr(new+'.interpType'))
        self.assertEqual(offsets, [cmds.getAttr(new+'.target['+str(t['index'])+'].targetOffsetTranslate') for t in engine.info(new)['targets']])
        new_attr = engine.info(new)['targets'][0]['weight_plug']
        self.assertEqual(curves, cmds.listConnections(new_attr, source=True, destination=False))
        self.assertEqual([1., 7.], cmds.keyframe(new_attr, query=True, timeChange=True))
        cmds.undo()
        self.assertEqual(data['uuid'], engine.identity(constraint))

    def test_remove_exact_target_alias_and_saved_list_json_file_snapshot(self):
        drivers, child, constraint = scene('pointConstraint')
        data = engine.info(constraint)
        result = TOOL.run(action='remove_target', constraints=[constraint], selected_weights=[data['targets'][0]['weight_plug']], maintain_offset=True)
        self.assertTrue(result.success, result.message)
        self.assertEqual([engine.node(drivers[1])], [x['node'] for x in engine.info(constraint)['targets']])
        cmds.undo()
        items = [{'text': data['node']+'.'+data['targets'][0]['alias'], 'color': '#ff0000', 'constraint_node': data['node'], 'weight_attrs': [data['targets'][0]['weight_plug']]}]
        saved = TOOL.run(action='save_list', list_name='review', items=items)
        self.assertTrue(saved.success, saved.message)
        self.assertEqual(items, json.loads(cmds.getAttr(saved.data['locator']+'.notes'))['items'])
        self.assertFalse(TOOL.run(action='save_list', list_name='review', items=items).success)
        TOOL.run(action='disconnect', constraints=[constraint])
        with tempfile.TemporaryDirectory(prefix='constraint_json_test_') as root:
            path = str(Path(root)/'snapshot.json')
            exported = TOOL.run(action='export_snapshot', constraints=[constraint], path=path)
            self.assertTrue(exported.success, exported.message)
            original = Path(path).read_bytes()
            self.assertFalse(TOOL.run(action='export_snapshot', constraints=[constraint], path=path).success)
            self.assertEqual(original, Path(path).read_bytes())
            engine._snapshots.clear()
            bad = json.loads(original.decode('utf-8'))
            unrelated = cmds.createNode('transform', name='unrelatedRestoreTarget')
            bad['snapshots'][0]['outputs'][0]['destination']['uuid'] = engine.identity(unrelated)
            forged = Path(root)/'forged.json'
            forged.write_text(json.dumps(bad), encoding='utf-8')
            before = state()
            self.assertFalse(TOOL.run(action='import_snapshot', path=str(forged)).success)
            self.assertEqual(before, state())
            self.assertEqual({}, engine._snapshots)
            imported = TOOL.run(action='import_snapshot', path=path)
            self.assertTrue(imported.success, imported.message)
            self.assertTrue(TOOL.run(action='restore', constraints=[constraint]).success)
        self.assertFalse(TOOL.run(action='axis', constraints=[constraint]).success)

    def test_pairblend_original_animation_and_snapshot_restore_scope(self):
        drivers, child, original = scene()
        cmds.delete(original)
        cmds.setKeyframe(child+'.tx', time=1, value=6.)
        cmds.setKeyframe(child+'.tx', time=9, value=7.)
        constraint = cmds.parentConstraint(drivers[0], child, maintainOffset=True)[0]
        d = engine.info(constraint)
        self.assertTrue(any(cmds.nodeType(engine.node(e['destination']['uuid'])) == 'pairBlend' for e in d['outputs']))
        result = TOOL.run(action='disconnect', constraints=[constraint])
        self.assertTrue(result.success, result.message)
        restored = TOOL.run(action='restore', constraints=[constraint])
        self.assertTrue(restored.success, restored.message)
        self.assertEqual([1., 9.], cmds.keyframe(child+'.tx', query=True, timeChange=True))


if __name__ == '__main__':
    unittest.main()
