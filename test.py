from raytracing import *

lens = Lens(f=5)
path = MatrixGroup()
path.append(lens)
path.append(Space(3))
path.append(lens)
path.append(Space(0.1))
path.append(lens)
path.append(Space(3))

print("EFL", path.effectiveFocalLengths())
print("PP1 PP2", path.principalPlanePositions(z=0))
print("BFL", path.backFocalLength())
print("FFL", path.frontFocalLength())
print("V1", path.frontVertex)
print("V2", path.backVertex)



obj = LUMPLFL40X()
print("EFL", obj.effectiveFocalLengths())
print("PP1 PP2" , obj.principalPlanePositions(z=0))
print("BFL", obj.backFocalLength())
print("FFL", obj.frontFocalLength())

