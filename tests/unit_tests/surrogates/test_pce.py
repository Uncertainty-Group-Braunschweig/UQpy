import pytest

from UQpy.distributions import JointIndependent, Normal
from UQpy.sampling import MonteCarloSampling
from UQpy.distributions import Uniform
from UQpy.sensitivity.PceSensitivity import PceSensitivity
from UQpy.surrogates import *
import numpy as np

from UQpy.surrogates.polynomial_chaos.polynomials.TotalDegreeBasis import TotalDegreeBasis
from UQpy.surrogates.polynomial_chaos.polynomials.TensorProductBasis import TensorProductBasis

np.random.seed(1)
max_degree, n_samples = 2, 10
dist = Uniform(loc=0, scale=10)


def func(x):
    return x * np.sin(x) / 10


x = dist.rvs(n_samples)
x_test = dist.rvs(n_samples)
y = func(x)


# Unit tests
def test_1():
    """
    Test td basis
    """
    polynomials = TotalDegreeBasis(dist, max_degree).polynomials
    value = polynomials[1].evaluate(x)[0]
    assert round(value, 4) == -0.2874


def test_2():
    """
    Test tp basis
    """
    polynomial_basis = TensorProductBasis(distributions=dist,
                                                                   max_degree=max_degree).polynomials
    value = polynomial_basis[1].evaluate(x)[0]
    assert round(value, 4) == -0.2874


def test_3():
    """
    Test PCE coefficients w/ lasso
    """
    polynomial_basis = TensorProductBasis(dist, max_degree)
    lasso = LassoRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=lasso)
    pce.fit(x, y)
    assert round(pce.coefficients[0][0], 4) == 0.0004


#
def test_4():
    """
    Test PCE coefficients w/ ridge
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    ridge = RidgeRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=ridge)
    pce.fit(x, y)
    assert round(pce.coefficients[0][0], 4) == 0.0276


#
def test_5():
    """
    Test PCE coefficients w/ lstsq
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    least_squares = LeastSquareRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pce.fit(x, y)
    assert round(pce.coefficients[0][0], 4) == 0.2175


#
def test_6():
    """
    Test PCE prediction
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    least_squares = LeastSquareRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pce.fit(x, y)
    y_test = pce.predict(x_test)
    assert round(y_test[0][0], 4) == -0.1607


#
def test_7():
    """
    Test Sobol indices
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    least_squares = LeastSquareRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pce.fit(x, y)
    pce_sensitivity = PceSensitivity(pce)
    first_order_sobol = pce_sensitivity.calculate_first_order_indices()
    assert round(first_order_sobol[0][0], 3) == 1.0


#
def test_8():
    """
    Test Sobol indices
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    least_squares = LeastSquareRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pce.fit(x, y)
    pce_sensitivity = PceSensitivity(pce)

    total_order_sobol = pce_sensitivity.calculate_total_order_indices()
    assert round(total_order_sobol[0][0], 3) == 1.0


#
def test_9():
    """
    Test Sobol indices
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    least_squares = LeastSquareRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pce.fit(x, y)
    pce_sensitivity = PceSensitivity(pce)


#
def test_10():
    """
    Test Sobol indices
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    least_squares = LeastSquareRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pce.fit(x, y)
    pce_sensitivity = PceSensitivity(pce)
    with pytest.raises(ValueError):
        generalized_total_order_sobol = pce_sensitivity.calculate_generalized_total_order_indices()


#
def test_11():
    """
    PCE mean
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    least_squares = LeastSquareRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pce.fit(x, y)
    mean, _ = pce.get_moments()
    assert round(mean, 3) == 0.218


#
def test_12():
    """
    PCE variance
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    least_squares = LeastSquareRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pce.fit(x, y)
    _, variance = pce.get_moments()
    assert round(variance, 3) == 0.185


def function(x):
    # without square root
    u1 = x[:, 4] * np.cos(x[:, 0])
    u2 = x[:, 4] * np.cos(x[:, 0]) + x[:, 5] * np.cos(np.sum(x[:, :2], axis=1))
    u3 = x[:, 4] * np.cos(x[:, 0]) + x[:, 5] * np.cos(np.sum(x[:, :2], axis=1)) + x[:, 6] * np.cos(
        np.sum(x[:, :3], axis=1))
    u4 = x[:, 4] * np.cos(x[:, 0]) + x[:, 5] * np.cos(np.sum(x[:, :2], axis=1)) + x[:, 6] * np.cos(
        np.sum(x[:, :3], axis=1)) + x[:, 7] * np.cos(np.sum(x[:, :4], axis=1))

    v1 = x[:, 4] * np.sin(x[:, 0])
    v2 = x[:, 4] * np.sin(x[:, 0]) + x[:, 5] * np.sin(np.sum(x[:, :2], axis=1))
    v3 = x[:, 4] * np.sin(x[:, 0]) + x[:, 5] * np.sin(np.sum(x[:, :2], axis=1)) + x[:, 6] * np.sin(
        np.sum(x[:, :3], axis=1))
    v4 = x[:, 4] * np.sin(x[:, 0]) + x[:, 5] * np.sin(np.sum(x[:, :2], axis=1)) + x[:, 6] * np.sin(
        np.sum(x[:, :3], axis=1)) + x[:, 7] * np.sin(np.sum(x[:, :4], axis=1))

    return (u1 + u2 + u3 + u4) ** 2 + (v1 + v2 + v3 + v4) ** 2


dist_1 = Uniform(loc=0, scale=2 * np.pi)
dist_2 = Uniform(loc=0, scale=1)

marg = [dist_1] * 4
marg_1 = [dist_2] * 4
marg.extend(marg_1)

joint = JointIndependent(marginals=marg)

n_samples_2 = 10
mcs_2 = MonteCarloSampling(distributions=joint, nsamples=n_samples_2, random_state=0)
x_2 = mcs_2.samples
y_2 = function(x_2)

polynomial_basis = TotalDegreeBasis(joint, 2)
least_squares = LeastSquareRegression()
pce_2 = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
pce_2.fit(x_2, y_2)


def test_17():
    """
    Test Sobol indices for vector-valued quantity of interest on the random inputs
    """
    pce_sensitivity = PceSensitivity(pce_2)
    pce_sensitivity.run()
    generalized_first_sobol = pce_sensitivity.generalized_first_order_indices
    assert round(generalized_first_sobol[0], 4) == 0.0137


def test_18():
    """
    Test Sobol indices for vector-valued quantity of interest on the random inputs
    """
    pce_sensitivity = PceSensitivity(pce_2)
    pce_sensitivity.run()
    generalized_total_sobol = pce_sensitivity.generalized_total_order_indices
    assert round(generalized_total_sobol[0], 4) == 0.4281


def test_19():
    """
    Test Higher statistical moments on Uniform distribution (skewness=0, kurtosis=1.8 from definition)
    """
    polynomial_basis = TotalDegreeBasis(dist, max_degree)
    least_squares = LeastSquareRegression()
    pce = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pce.fit(x, x)
    mean, var, skew, kurtosis = pce.get_moments(True)

    assert round(kurtosis, 3) == 1.8 and round(skew, 3) == 0


def test_20():
    """
    Test Higher statistical moments on Gaussian distribution (skewness=0, kurtosis=3 from definition)
    """
    dist_Gauss = Normal(loc=0, scale=1)

    mcs = MonteCarloSampling(dist, nsamples=n_samples, random_state=1)

    polynomial_basis = TotalDegreeBasis(dist_Gauss, max_degree)
    least_squares = LeastSquareRegression()
    pceGauss = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
    pceGauss.fit(x, x)
    mean, var, skew, kurtosis = pceGauss.get_moments(True)

    assert round(kurtosis, 3) == 3 and round(skew, 3) == 0


def functionLAR(x):
    u1 = x[:, 0] ** 2 + x[:, 2] ** 2 + x[:, 3] ** 2

    return u1


n_samples_2 = 100
x_2 = joint.rvs(n_samples_2)
y_2 = functionLAR(x_2)

polynomial_basis = TotalDegreeBasis(joint, 6)
least_squares = LeastSquareRegression()
pce_2 = PolynomialChaosExpansion(polynomial_basis=polynomial_basis, regression_method=least_squares)
pce_2.fit(x_2, y_2)


def test_21():
    """
    Test Model Selection Algorithm based on Least Angle Regression (select only important basis functions from large set)
    """

    pce_lar = polynomial_chaos.regressions.LeastAngleRegression.model_selection(pce_2)
    pce2_lar_sens = PceSensitivity(pce_lar)

    assert all((np.argwhere(np.round(pce2_lar_sens.calculate_generalized_total_order_indices(), 3) > 0)
                == [[0], [2], [3]]))
