from .ray import *
from numpy import *
import matplotlib.pyplot as plt

""" A group of rays kept as a list, to be used as a starting
point (i.e. an object) or as a cumulative detector (i.e. at an image
or output plane) for ImagingPath, MatrixGroup or any tracing function.
Subclasses can provide a computed ray for Monte Carlo simulation.
"""

class Rays:
    def __init__(self, rays=[]):
        self.rays = rays
        self.iteration = 0

        # We cache these because they can be lengthy to calculate
        self._yValues = None
        self._thetaValues = None
        self._intensityValues = None
        self._yHistogram = None
        self._intensityBinEdges = None
        self._thetaHistogram = None
        self._directionBinEdges = None

    @property
    def yValues(self):
        if self._yValues is None:
            self._yValues = list(map(lambda x : x.y, self))

        return self._yValues

    @property
    def thetaValues(self):
        if self._thetaValues is None:
            self._thetaValues = list(map(lambda x : x.theta, self))

        return self._thetaValues

    @property
    def intensityValues(self):
        if self._intensityValues is None:
            self._intensityValues = list(map(lambda x : x.intensity, self))

        return self._intensityValues

    
    def rayCountHistogram(self, binCount=None, minValue=None, maxValue=None):
        if self._yHistogram is None:
            if binCount is None:
                binCount = 40

            if minValue is None:
                minValue = min(self.yValues)

            if maxValue is None:
                maxValue = max(self.yValues)

            (self._yHistogram, binEdges) = histogram(self.yValues, 
                                bins=binCount, 
                                range=(minValue, maxValue))
            self._yHistogram = list(self._yHistogram)
            xValues = []
            for i in range(len(binEdges)-1):
                xValues.append((binEdges[i] + binEdges[i+1])/2 )

        return (xValues, self._yHistogram)


    def rayAnglesHistogram(self, binCount=None, minValue=None, maxValue=None):
        if self._thetaHistogram is None:
            if binCount is None:
                binCount = 40

            if minValue is None:
                minValue = min(self.thetaValues)

            if maxValue is None:
                maxValue = max(self.thetaValues)

            (self._thetaHistogram, binEdges) = histogram(self.thetaValues, bins=binCount, range=(minValue, maxValue))
            self._thetaHistogram = list(self._thetaHistogram)
            xValues = []
            for i in range(len(binEdges)-1):
                xValues.append((binEdges[i] + binEdges[i+1])/2 )

        return (xValues, self._thetaHistogram)

    def display(self, title="Intensity profile", showTheta=True):
        plt.ioff()
        fig = plt.figure()
        axis1 = fig.add_subplot()
        (x,y) = self.rayCountHistogram()
        axis1.plot(x,y,'k-',label="Intensity")
        plt.xlabel("Distance")
        plt.ylim([0, max(y)*1.1])

        if showTheta:
            (x,y) = self.rayAnglesHistogram()
            axis2 = axis1.twiny()
            axis2.plot(x,y,'k--',label="Orientation profile")
            plt.xlabel("Angles [rad]")
            plt.xlim([-pi/2,pi/2])
            plt.ylim([0, max(y)*1.1])
        
#        legend = axis1.legend(loc='upper right', shadow=True, fontsize='x-large')

        plt.ylabel("Ray count")
        plt.title(title)
        plt.show()
    
    def displayAngles(self, title="Angular profile"):
        plt.ioff()
        plt.plot(x,y,'k.')
        plt.ylim(bottom = 0)
        plt.xlabel("Distance")
        plt.ylabel("Angle")
        plt.title(title)
        plt.show()

    def __len__(self) -> int:
        if self.rays is not None:
            return len(self.rays)
        else:
            return 0

    def __iter__(self):
        self.iteration = 0
        return self

    def __next__(self) -> Ray :
        if self.rays is None:
            raise StopIteration

        if self.iteration < len(self.rays):
            ray = self.rays[self.iteration]
            self.iteration += 1
            return ray

        raise StopIteration

    def append(self, ray):
        if self.rays is not None:
            self.rays.append(ray)

        # Invalidate cached values
        self._yValues = None
        self._thetaValues = None
        self._intensityValues = None            
        self._yHistogram = None
        self._intensityBinEdges = None
        self._thetaHistogram = None
        self._directionBinEdges = None

    def whichBin(self, value):
        if value <= self.min:
            return 0
        elif value >= self.max:
            return len(self.distribution)-1
        
        return int((value - self.min)/self.delta)


    # For 2D histogram:
    # https://en.wikipedia.org/wiki/Xiaolin_Wu's_line_algorithm
    # and https://stackoverflow.com/questions/3122049/drawing-an-anti-aliased-line-with-thepython-imaging-library

    # @property
    # def intensityError(self):
    #     return list(map(lambda x : sqrt(x), self.distribution))

    # @property
    # def normalizedIntensity(self):
    #     maxValue = max(self.values)
    #     return list(map(lambda x : x/maxValue, self.distribution))

    # @property
    # def normalizedIntensityError(self):
    #     maxValue = max(self.distribution)
    #     return list(map(lambda x : x/maxValue, self.error))


class UniformRays(Rays):
    def __init__(self, yMax=1.0, yMin=None, thetaMax=pi/2, thetaMin=None, M=100, N=100):
        self.yMax = yMax
        self.yMin = yMin
        if self.yMin is None:
            self.yMin = -yMax
        self.thetaMax = thetaMax
        self.thetaMin = thetaMin
        if thetaMin is None:
            self.thetaMin = -thetaMax

        self.M = M
        self.N = N
        rays = []
        for y in linspace(self.yMin, self.yMax, self.M, endpoint=True):
            for theta in linspace(self.thetaMin, self.thetaMax, self.N, endpoint=True):
                rays.append(Ray(y,theta))
        super(UniformRays, self).__init__(rays=rays)

class LambertianRays(Rays):
    def __init__(self, yMax, yMin=None, M=100, N=100, I=100):
        self.yMax = yMax
        self.yMin = yMin
        if yMin is None:
            self.yMin = -yMax

        self.thetaMax = -pi/2
        self.thetaMin = pi/2
        self.M = M
        self.N = N
        self.I = I
        rays = []
        for theta in linspace(self.thetaMin, self.thetaMax, N, endpoint=True):
            intensity = int( I * cos(theta) )
            for y in linspace(self.yMin, self.yMax, M, endpoint=True):
                for k in range(intensity):
                    rays.append(Ray(y,theta, intensity))
        super(LambertianRays, self).__init__(rays=rays)

class RandomRays(Rays):
    def __init__(self, yMax=1.0, yMin=None, thetaMax=pi/2, thetaMin=None, maxCount=100000):
        self.maxCount = maxCount
        self.yMax = yMax
        self.yMin = yMin
        if self.yMin is None:
            self.yMin = -yMax
        self.thetaMax = thetaMax
        self.thetaMin = thetaMin
        if thetaMin is None:
            self.thetaMin = -thetaMax
        super(RandomRays, self).__init__(rays=None)

    def __len__(self) -> int:
        return self.maxCount

    def __next__(self) -> Ray :
        if self.iteration >= self.maxCount:
            raise StopIteration 
        self.iteration += 1
        return self.randomRay()

    def randomRay(self) -> Ray :
        raise NotImplemented("You must implement randomRay() is your subclass")

class RandomUniformRays(Rays):
    def __init__(self, yMax=1.0, yMin=None, thetaMax=pi/2, thetaMin=None, maxCount=100000):
        super(RandomUniformRays, self).__init__(rays=None, yMax=yMax, yMin=yMin, thetaMax=thetaMax, thetaMin=thetaMin, maxCount=maxCount)

    def randomRay(self) -> Ray :
        theta = self.thetaMin + random.random() * (self.thetaMax - self.thetaMin)
        y = self.yMin + random.random() * (self.yMax - self.yMin) 
        return Ray(y=y, theta=theta)

class RandomLambertianRays(RandomRays):
    def __init__(self, yMax, yMin=None, maxCount=10000):
        super(RandomLambertianRays, self).__init__(yMax=yMax, yMin=yMin, thetaMax=-pi/2, thetaMin=pi/2, maxCount=maxCount)

    def randomRay(self) -> Ray :
        theta = 0
        intensity = 1.0
        while (True):
            theta = self.thetaMin + random.random() * (self.thetaMax - self.thetaMin)
            intensity = cos(theta)
            seed = random.random()
            if seed < intensity:
                break

        y = self.yMin + random.random() * (self.yMax - self.yMin) 
        return Ray(y, theta)

  
