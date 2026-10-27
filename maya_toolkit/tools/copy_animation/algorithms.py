from maya import cmds
from .runtime import require_active, record_warning
_warning = record_warning
TRANSFORM_CHANNELS = ('translate', 'rotate', 'scale')
CHANNEL_LABELS = {'translate': '位移', 'rotate': '旋转', 'scale': '缩放', 'other': '其他属性'}

def _object_exists(node):
    return bool(node and cmds.objExists(node))

class ChannelAlgorithms:

    def _attribute_has_key(self, node, attribute, frame):
        require_active()
        plug = '{}.{}'.format(node, attribute)
        if not cmds.objExists(plug):
            return False
        return bool(cmds.keyframe(plug, query=True, time=(frame, frame), keyframeCount=True))

    def _channel_has_key(self, node, channel, frame):
        require_active()
        attributes = ['{}{}'.format(channel, axis) for axis in ('X', 'Y', 'Z')]
        return any((self._attribute_has_key(node, attribute, frame) for attribute in attributes))

    def _match_and_key(self, target, target_locator, channel, frame):
        require_active()
        if not _object_exists(target_locator):
            raise RuntimeError('辅助定位器不存在，请重新生成定位器。')
        cmds.currentTime(frame, edit=True)
        match_flags = {'translate': {'pos': True}, 'rotate': {'rot': True}, 'scale': {'scl': True}}
        cmds.matchTransform(target, target_locator, **match_flags[channel])
        cmds.setKeyframe(target, attribute=channel, time=frame)

    def apply_channel_modes(self, source, target, target_locator, modes, start_time, end_time):
        require_active()
        for frame in range(start_time, end_time + 1):
            for channel in TRANSFORM_CHANNELS:
                mode = modes.get(channel, 'none')
                if mode == 'frame':
                    if self._channel_has_key(source, channel, frame):
                        try:
                            self._match_and_key(target, target_locator, channel, frame)
                        except Exception as error:
                            _warning('{} 在第 {} 帧的{}对齐失败：{}'.format(target, frame, CHANNEL_LABELS[channel], error))
                elif mode == 'numeric':
                    self.copy_numeric_values(source, target, channel, frame)
            if modes.get('other') == 'numeric':
                self.copy_numeric_values(source, target, 'other', frame)

    def _numeric_attributes(self, node, channel):
        require_active()
        if channel == 'other':
            attributes = cmds.listAttr(node, keyable=True, userDefined=True) or []
        else:
            attributes = ['{}{}'.format(channel, axis) for axis in ('X', 'Y', 'Z')]
        return attributes

    def copy_numeric_values(self, source, target, channel, frame):
        require_active()
        for attribute in self._numeric_attributes(source, channel):
            source_plug = '{}.{}'.format(source, attribute)
            target_plug = '{}.{}'.format(target, attribute)
            if not cmds.objExists(target_plug):
                continue
            try:
                if not cmds.getAttr(target_plug, settable=True):
                    continue
                value = cmds.getAttr(source_plug, time=frame)
                if isinstance(value, (list, tuple)):
                    if len(value) == 1 and isinstance(value[0], (list, tuple)):
                        value = value[0]
                    if len(value) != 1:
                        _warning('跳过非标量属性 {}。'.format(source_plug))
                        continue
                    value = value[0]
                if not isinstance(value, (int, float, bool)):
                    continue
                cmds.setKeyframe(target, time=frame, attribute=attribute, value=value)
            except Exception as error:
                _warning('{} 在第 {} 帧复制失败：{}'.format(target_plug, frame, error))
