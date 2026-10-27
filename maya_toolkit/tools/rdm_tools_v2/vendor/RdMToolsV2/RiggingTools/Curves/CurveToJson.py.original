import json
import maya.OpenMaya as openmaya
dagIter = openmaya.MItDag(openmaya.MItDag.kDepthFirst, openmaya.MFn.kCurve)
output = []
# Iterate through all of the dag nodes and get the curves.
while not dagIter.isDone():
    curveIter = openmaya.MItCurveCV(dagIter.currentItem())
    curve = openmaya.MFnDagNode(dagIter.currentItem())
    dagIter.next()
    # Create an object to store the curve info.
    node = {"name": curve.name(), "points": []}
    # Iterate through all of the points in the curve and store it.
    while not curveIter.isDone():
        pos = curveIter.position()
        curveIter.next()
        node["points"].append([pos.x, pos.y, pos.z])
    # Add the object to the output
    output.append(node)
print output    

# Save as a json file (or switch this up to use another format)
with open("C:Users/Usuario/Desktop/Foot.json", mode="w") as fOut:
    json.dump(output, fOut)
    
    
    
    
    
    
    