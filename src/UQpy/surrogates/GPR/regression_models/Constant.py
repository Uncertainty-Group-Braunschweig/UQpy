import numpy as np
from UQpy.surrogates.gpr.regression_models.baseclass.Regression import Regression


class Constant(Regression):
    def r(self, s):
        s = np.atleast_2d(s)
        fx = np.ones([np.size(s, 0), 1])
        jf = np.zeros([np.size(s, 0), np.size(s, 1), 1])
        return fx, jf
