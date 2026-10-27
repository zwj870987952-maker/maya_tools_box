import  maya.cmds as cmd
sel = cmd.ls(sl = 1)
attributes = []
if sel:
	#For every object selected, find ordered attributes in channel box
	for obj in sel:
		allAttrs = cmd.listAttr(obj)
		cbAttrs = cmd.listAnimatable(obj)
		if allAttrs and cbAttrs:
			orderedAttrs = [attr for attr in allAttrs for cb in cbAttrs if cb.endswith(attr)]
			if u'visibility' in orderedAttrs:
				orderedAttrs.remove(u'visibility')
				orderedAttrs.append(u'visibility')
			attributes.extend(orderedAttrs)
for i in attributes:
    print i


