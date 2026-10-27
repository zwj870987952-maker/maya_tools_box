import maya.cmds as cmds
flags_to_test = [
    {'format': 'image', 'compression': 'png'},
    {'clearCache': True},
    {'viewer': False},
    {'showOrnaments': False},
    {'framePadding': 4},
    {'percent': 100},
    {'forceOverwrite': True},
    {'sequenceTime': False},
    {'filename': 'test_fn'},
    {'completeFilename': 'C:/temp/test.png'}
]
for f in flags_to_test:
    try:
        kwargs = dict(startTime=1, endTime=2, width=320, height=240)
        kwargs.update(f)
        cmds.playblast(**kwargs)
        print("Flag passed:", list(f.keys()))
    except Exception as e:
        print("Flag failed:", list(f.keys()), "Error:", e)
