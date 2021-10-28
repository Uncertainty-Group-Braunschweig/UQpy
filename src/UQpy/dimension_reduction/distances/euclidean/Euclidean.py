from typing import Union
import numpy as np
from scipy.spatial.distance import pdist

from UQpy import Numpy2DFloatArray
from UQpy.utilities import DistanceMetric


class Euclidean:
    def __init__(self, metric: DistanceMetric):
        """
        A class that calculates the Euclidean distance between points.
        :param metric: Enumeration of type DistanceMetric that defines
        the type of distance to be used.

        """
        metric_str = str(metric.name).lower()
        self.distance_function = lambda x: pdist(x, metric=metric_str)

    def compute_distance(self, points: Numpy2DFloatArray) -> Union[float, np.ndarray]:
        """

        :param numpy.ndarray points: Array holding the coordinates of the points
        :return float or numpy.ndarray: Euclidean Distance
        :rtype float or numpy.ndarray
        """
        d = self.distance_function(points)
        return d
