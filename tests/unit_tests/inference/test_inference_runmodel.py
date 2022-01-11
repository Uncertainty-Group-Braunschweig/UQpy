from UQpy.RunModel import RunModel
from UQpy.optimization.MinimizeOptimizer import MinimizeOptimizer
from UQpy.inference.inference_models.ComputationalModel import *
from UQpy.inference.inference_models.LogLikelihoodModel import *
from UQpy.inference.MLE import *
from UQpy.distributions import *
import pytest
import shutil
from scipy.optimize import minimize
import numpy as np

data = [0., 1., -1.5, -0.2]


@pytest.fixture
def setup():
    h_func = RunModel(model_script='pfn_models.py', model_object_name='model_quadratic', vec=False,
                      var_names=['theta_0', 'theta_1'], delete_files=True)
    yield h_func
    shutil.rmtree(h_func.model_dir)


def user_log_likelihood(data, model_outputs, params=None):
    return np.sum(Normal().log_pdf(np.array(data)-model_outputs[0])).reshape((-1,))


def user_log_likelihood_uniform(data, params):
    return [np.sum(Uniform(loc=p[0], scale=p[1]).log_pdf(data)) for p in params]


def test_mle(setup):
    h_func = setup
    candidate_model = ComputationalModel(parameters_number=2, runmodel_object=h_func, error_covariance=1.)
    optimizer = MinimizeOptimizer(method='nelder-mead', bounds=((-2, 2), (-2, 2)))
    ml_estimator = MLE(inference_model=candidate_model, data=data, optimizations_number=2,
                       optimizer=optimizer, random_state=123)
    assert round(ml_estimator.mle[0], 3) == -0.039


def test_mle_optimizer(setup):
    h_func = setup
    candidate_model = ComputationalModel(parameters_number=2, runmodel_object=h_func, error_covariance=np.ones(4))
    ml_estimator = MLE(inference_model=candidate_model, data=data, initial_guess=[0., 0.], random_state=123)
    assert round(ml_estimator.mle[0], 3) == -0.039


def test_user_loglike(setup):
    h_func = setup
    candidate_model = ComputationalModel(
        parameters_number=2, runmodel_object=h_func, log_likelihood=user_log_likelihood)
    optimizer = MinimizeOptimizer(method='nelder-mead', bounds=((-2, 2), (-2, 2)))
    ml_estimator = MLE(inference_model=candidate_model, optimizer=optimizer,
                       data=data, optimizations_number=2, random_state=123)
    assert round(ml_estimator.mle[0], 3) == -0.039


def test_user_loglike_uniform():
    candidate_model = LogLikelihoodModel(parameters_number=2, log_likelihood=user_log_likelihood_uniform)
    optimizer = MinimizeOptimizer(method='nelder-mead', bounds=((-2, 2), (-2, 2)))
    ml_estimator = MLE(inference_model=candidate_model, data=data, optimizations_number=2,
                       optimizer=optimizer, random_state=123)
    assert round(ml_estimator.mle[0], 3) == 0.786
