import unittest
import envtest  # modifies path  # fixme: requires path to /tests
# from raytracing import *
from raytracing.figureManager import FigureManager  # todo: append init
from raytracing.drawing import *

# FIXME: Temporary display tests


class TestFigureManager(unittest.TestCase):
    def testHandleDrawings(self):
        figure = FigureManager()
        figure.createFigure()

        components = [ArrowPatch(dy=5),
                      ArrowPatch(dy=-5),
                      StopPatch(y=5),
                      StopPatch(y=-5)]

        figure.add(Drawing(ArrowPatch(dy=5, color='b'), x=0, label="Object"))
        figure.add(Drawing(ArrowPatch(dy=-5, color='r'), x=7.6, label="Label 1"))
        figure.add(Drawing(ArrowPatch(dy=-5, color='r'), x=7.8, label="Label 2"))
        figure.add(Drawing(*components, x=8, label="Label 3"))

        figure.draw()

        figure.display()