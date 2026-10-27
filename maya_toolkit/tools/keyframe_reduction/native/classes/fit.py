import math
from .vector import Vector2D
from .keyframe import Keyframe
from ..utils import EPSILON

class FitBezier(object):
    """
    Ported from Paper.js - The Swiss Army Knife of Vector Graphics Scripting.
    http://paperjs.org/
    """

    def __init__(self, points, error=2.5, weightedTangents=True):
        """
        :param list points:
        :param int/float error:
        :param bool weightedTangents:
        """
        self._keyframes = []
        self._points = points
        self._error = error
        self._weightedTangents = weightedTangents

    def __repr__(self):
        return '< BezierFitter object | points: {} | error: {} | weighted-tangents: {} >'.format(len(self.points), self.error, self.weightedTangents)

    @property
    def points(self):
        """
        :return: Vector2Ds
        :rtype: list
        """
        return self._points

    @property
    def error(self):
        """
        :return: Maximum error
        :rtype: int/float
        """
        return self._error

    @property
    def weightedTangents(self):
        """
        :return: Weighted tangents
        :rtype: bool
        """
        return self._weightedTangents

    @property
    def keyframes(self):
        """
        :return: Keyframes
        :rtype: list
        """
        return self._keyframes

    @keyframes.setter
    def keyframes(self, s):
        """
        :param list s:
        """
        self._keyframes = s

    def fit(self):
        """
        Fit bezier curves to the points based on the provided maximum error
        value and the bezier weighted tangents.

        :return: Keyframes
        :rtype: list
        """
        length = len(self.points)
        if length == 0:
            return
        self.keyframes = []
        self.keyframes.append(Keyframe(self.points[0]))
        if length == 1:
            return self.keyframes
        tan1 = (self.points[1] - self.points[0]).normal()
        tan2 = (self.points[length - 2] - self.points[length - 1]).normal()
        self.fitCubic(0, length - 1, tan1, tan2)
        return self.keyframes

    def fitCubic(self, first, last, tan1, tan2):
        """
        But a cubic bezier points between the provided first and last index
        and it's tangents. Based in the weighted tangent settings the
        iterations will be adjusted to gain speed. If a curve can be matched
        the curve will be added to the keyframes, if not the curve will be
        split at the point of max error and the function will be called
        again.

        :param int first:
        :param int last:
        :param Vector2D tan1:
        :param Vector2D tan2:
        """
        if last - first == 1:
            pt1 = self.points[first]
            pt2 = self.points[last]
            dist = pt1.distanceBetween(pt2) / 3
            self.addCurve(pt1, pt1 + tan1 * dist, pt2 + tan2 * dist, pt2)
            return
        uPrime = self.chordLengthParameterize(first, last)
        errorThreshold = max(self.error, self.error * 4)
        iterations = 4 if self.weightedTangents else 1
        for i in range(iterations):
            curve = self.generateBezier(first, last, uPrime, tan1, tan2)
            maxError, maxIndex = self.findMaxError(first, last, curve, uPrime)
            if maxError < self.error:
                self.addCurve(*curve)
                return
            if maxError >= errorThreshold:
                break
            self.reparameterize(first, last, uPrime, curve)
            errorThreshold = maxError
        tanCenter = (self.points[maxIndex - 1] - self.points[maxIndex + 1]).normal()
        self.fitCubic(first, maxIndex, tan1, tanCenter)
        self.fitCubic(maxIndex, last, tanCenter * -1, tan2)

    def addCurve(self, pt1, tan1, tan2, pt2):
        """
        :param Vector2D pt1:
        :param Vector2D tan1:
        :param Vector2D tan2:
        :param Vector2D pt2:
        """
        prev = self.keyframes[len(self.keyframes) - 1]
        prev.outHandle = Vector2D(tan1 - pt1)
        keyframe = Keyframe(pt2, Vector2D(tan2 - pt2))
        self.keyframes.append(keyframe)

    def generateBezier(self, first, last, uPrime, tan1, tan2):
        """
        Based on the weighted tangent setting either use a least-squares
        method to find Bezier controls points for a region or use Wu/Barsky
        heuristic.

        :param int first:
        :param int last:
        :param dict uPrime:
        :param Vector2D tan1:
        :param Vector2D tan2:
        """
        epsilon = EPSILON
        pt1 = self.points[first]
        pt2 = self.points[last]
        alpha1 = alpha2 = 0
        handle1 = handle2 = None
        if self.weightedTangents:
            C = [[0, 0], [0, 0]]
            X = [0, 0]
            for i in range(last - first + 1):
                u = uPrime[i]
                t = 1 - u
                b = 3 * u * t
                b0 = t * t * t
                b1 = b * t
                b2 = b * u
                b3 = u * u * u
                a1 = tan1 * b1
                a2 = tan2 * b2
                tmp = self.points[first + i] - pt1 * (b0 + b1) - pt2 * (b2 + b3)
                C[0][0] += a1 * a1
                C[0][1] += a1 * a2
                C[1][0] = C[0][1]
                C[1][1] += a2 * a2
                X[0] += a1 * tmp
                X[1] += a2 * tmp
            detC0C1 = C[0][0] * C[1][1] - C[1][0] * C[0][1]
            if abs(detC0C1) > epsilon:
                detC0X = C[0][0] * X[1] - C[1][0] * X[0]
                detXC1 = X[0] * C[1][1] - X[1] * C[0][1]
                alpha1 = detXC1 / detC0C1
                alpha2 = detC0X / detC0C1
            else:
                c0 = C[0][0] + C[0][1]
                c1 = C[1][0] + C[1][1]
                if abs(c0) > epsilon:
                    alpha1 = alpha2 = X[0] / c0
                elif abs(c1) > epsilon:
                    alpha1 = alpha2 = X[1] / c1
        segLength = pt2.distanceBetween(pt1)
        epsilon *= segLength
        if alpha1 < epsilon or alpha2 < epsilon:
            alpha1 = alpha2 = segLength / 3
        else:
            line = pt2 - pt1
            handle1 = tan1 * alpha1
            handle2 = tan2 * alpha2
            if handle1 * line - handle2 * line > segLength * segLength:
                alpha1 = alpha2 = segLength / 3
                handle1 = handle2 = None
        return [pt1, pt1 + (handle1 or tan1 * alpha1), pt2 + (handle2 or tan2 * alpha2), pt2]

    def reparameterize(self, first, last, u, curve):
        """
        Given set of points and their parameterization, try to find a better
        parameterization.

        :param int first:
        :param int last:
        :param dict u:
        :param list curve:
        """
        for i in range(first, last + 1):
            u[i - first] = self.findRoot(curve, self.points[i], u[i - first])

    def findRoot(self, curve, point, u):
        """
        Use Newton-Raphson iteration to find better root.

        :param list curve:
        :param Vector2D point:
        :param Vector2D u:
        :return: New root point
        :rtype: Vector2D
        """
        curve1 = [(curve[i + 1] - curve[i]) * 3 for i in range(3)]
        curve2 = [(curve1[i + 1] - curve1[i]) * 2 for i in range(2)]
        pt = self.evaluate(3, curve, u)
        pt1 = self.evaluate(2, curve1, u)
        pt2 = self.evaluate(1, curve2, u)
        diff = pt - point
        df = pt1 * pt1 + diff * pt2
        if abs(df) < EPSILON:
            return u
        return u - diff * pt1 / df

    def evaluate(self, degree, curve, t):
        """
        Evaluate a bezier curve at a particular parameter value.

        :param int degree:
        :param list curve:
        :param float t:
        :return: Point on curve
        :rtype: Vector2D
        """
        tmp = curve[:]
        for i in range(1, degree + 1):
            for j in range(degree - i + 1):
                tmp[j] = tmp[j] * (1 - t) + tmp[j + 1] * t
        return tmp[0]

    def chordLengthParameterize(self, first, last):
        """
        Assign parameter values to digitized points using relative distances
        between points.

        :param int first:
        :param int last:
        :return: Chord length parameterization
        :rtype: dict
        """
        u = {0: 0}
        for i in range(first + 1, last + 1):
            u[i - first] = u[i - first - 1] + self.points[i].distanceBetween(self.points[i - 1])
        m = last - first
        for i in range(1, m + 1):
            u[i] /= u[m]
        return u

    def findMaxError(self, first, last, curve, u):
        """
        Find the maximum squared distance of digitized points to fitted
        curve.

        :param int first:
        :param int last:
        :param list curve:
        :param dict u:
        :return: Max distance and max index
        :rtype: tuple
        """
        maxDist = 0
        maxIndex = math.floor((last - first + 1) / 2)
        for i in range(first + 1, last):
            P = self.evaluate(3, curve, u[i - first])
            dist = (P - self.points[i]).length()
            if dist >= maxDist:
                maxDist = dist
                maxIndex = i
        return (maxDist, maxIndex)
