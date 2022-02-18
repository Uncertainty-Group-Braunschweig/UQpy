from abc import abstractmethod

import numpy as np
import scipy.integrate as integrate
from beartype import beartype


class Polynomials:

    @beartype
    def __init__(self, distributions, degree):
        """
        Class for polynomials used for the polynomial_chaos method.

        :param distributions: Object from a distribution class.
        :param degree: Maximum degree of the polynomials.
        """
        self.distributions = distributions
        self.degree = degree + 1

    @staticmethod
    def standardize_normal(tensor, mean, std):
        """
        Static method: Standardize data based on the standard normal distribution :math:`\mathcal{N}(0,1)`.

        :param tensor: Input data generated from a normal distribution.
        :param mean: Mean value of the original normal distribution.
        :param std: Standard deviation of the original normal distribution.
        :return: Standardized data.
        """
        return (tensor - mean) / std

    @staticmethod
    def standardize_uniform(x, uniform):
        loc = uniform.get_parameters()['loc']  # loc = lower bound of uniform distribution
        scale = uniform.get_parameters()['scale']
        upper = loc + scale  # upper bound = loc + scale
        return (2 * x - loc - upper) / (upper - loc)

    @staticmethod
    def normalized(degree, samples, a, b, pdf_st, p):
        """
        Calculates design matrix and normalized polynomials.

        :param degree: polynomial degree
        :param samples:  Input samples.
        :param a: Left bound of the support the distribution.
        :param b: Right bound of the support of the distribution.
        :param pdf_st: Pdf function generated from :py:mod:`UQpy` distribution object.
        :param p: List containing the orthogonal polynomials generated with scipy.
        :return: Design matrix,normalized polynomials
        """
        pol_normed = []
        m = np.zeros((degree, degree))
        for i in range(degree):
            for j in range(degree):
                int_res = integrate.quad(
                    lambda k: p[i](k) * p[j](k) * pdf_st(k),
                    a,
                    b,
                    epsabs=1e-15,
                    epsrel=1e-15,
                )
                m[i, j] = int_res[0]
            pol_normed.append(p[i] / np.sqrt(m[i, i]))

        a = np.zeros((samples.shape[0], degree))
        for i in range(samples.shape[0]):
            for j in range(degree):
                a[i, j] = pol_normed[j](samples[i])

        return a, pol_normed

    def get_mean(self):
        """
        Returns a :any:`float` with the mean of the :py:mod:`UQpy` distribution object.
        """
        m = self.distributions.moments(moments2return="m")
        return m

    def get_std(self):
        """
        Returns a :any:`float` with the variance of the :py:mod:`UQpy` distribution object.
        """
        s = np.sqrt(self.distributions.moments(moments2return="v"))
        return s

    def location(self):
        """
        Returns a :any:`float` with the location of the :py:mod:`UQpy` distribution object.
        """
        m = self.distributions.__dict__["parameters"]["location"]
        return m

    def scale(self):
        """
        Returns a :any:`float` with the scale of the :py:mod:`UQpy` distribution object.
        """
        s = self.distributions.__dict__["parameters"]["scale"]
        return s

    @abstractmethod
    def evaluate(self, x):
        pass
        # """
        # Calculates the design matrix. Rows represent the input samples and
        # columns the multiplied polynomials whose degree must not exceed the
        # maximum degree of polynomials.
        #
        # :param x: `ndarray` containing the samples.
        # :return: Returns an array with the design matrix.
        # """
        # if not type(self.distributions) == JointIndependent:
        #     if type(self.distributions) == Normal:
        #         from UQpy.surrogates.polynomial_chaos.polynomials.Hermite import Hermite
        #
        #         return Hermite(self.degree, self.distributions).get_polys(x)[0]
        #         # design matrix (second_order_tensor x polynomials)
        #
        #     if type(self.distributions) == Uniform:
        #         from UQpy.surrogates.polynomial_chaos.polynomials.Legendre import (
        #             Legendre,
        #         )
        #
        #         return Legendre(self.degree, self.distributions).get_polys(x)[0]
        #
        #     else:
        #         raise TypeError("Warning: This distribution is not supported.")
        #
        # else:
        #
        #     a = []
        #     for i in range(len(self.distributions.marginals)):
        #
        #         if isinstance(self.distributions.marginals[i], Normal):
        #             from UQpy.surrogates.polynomial_chaos.polynomials.Hermite import (
        #                 Hermite,
        #             )
        #
        #             a.append(
        #                 Hermite(self.degree, self.distributions.marginals[i]).get_polys(
        #                     x[:, i]
        #                 )[0]
        #             )
        #
        #         elif isinstance(self.distributions.marginals[i], Uniform):
        #             from UQpy.surrogates.polynomial_chaos.polynomials.Legendre import (
        #                 Legendre,
        #             )
        #
        #             a.append(
        #                 Legendre(self.degree, self.distributions.marginals[i]).get_polys(
        #                     x[:, i]
        #                 )[0]
        #             )
        #
        #         else:
        #             raise TypeError("Warning: This distribution is not supported.")
        #
        #     # Compute all possible valid combinations
        #     m = len(a)  # number of variables
        #     p = self.degree  # maximum polynomial order
        #
        #     p_ = np.arange(0, p, 1).tolist()
        #     res = list(itertools.product(p_, repeat=m))
        #     # sum of poly orders
        #     sum_ = [int(math.fsum(res[i])) for i in range(len(res))]
        #     indices = sorted(range(len(sum_)), key=lambda k: sum_[k])
        #     res_new = [res[indices[i]] for i in range(len(res))]
        #     comb = [(0,) * m]
        #
        #     for i in range(m):
        #         t = [0] * m
        #         t[i] = 1
        #         comb.append(tuple(t))
        #
        #     for i in range(len(res_new)):
        #         if 1 < int(math.fsum(res_new[i])) <= p - 1:
        #             rev = res_new[i][::-1]
        #             comb.append(rev)
        #
        #     design = np.ones((x.shape[0], len(comb)))
        #     for i in range(len(comb)):
        #         for j in range(m):
        #             h = [a[j][k][comb[i][j]] for k in range(x.shape[0])]
        #             design[:, i] *= h
        #
        #     return design


