import logging
from typing import List, Union
from beartype import beartype
from UQpy.inference.inference_models.optimization.MinizeOptimizer import MinimizeOptimizer
from UQpy.inference.inference_models.baseclass.InferenceModel import InferenceModel
from UQpy.inference.MLE import MLE
from UQpy.inference.inference_models.optimization.Optimizer import Optimizer
from UQpy.utilities.ValidationTypes import RandomStateType, PositiveInteger
from UQpy.utilities.Utilities import process_random_state
from UQpy.inference.InformationTheoreticCriterion import *


class InformationModelSelection:
    """
    Perform model selection using information theoretic criteria.

    Supported criteria are BIC, AIC (default), AICc. This class leverages the ``MLEstimation`` class for maximum
    likelihood estimation, thus inputs to ``MLEstimation`` can also be provided to ``InfoModelSelection``, as lists of
    length equal to the number of models.


    **Inputs:**

    * **candidate_models** (`list` of ``InferenceModel`` objects):
        Candidate models

    * **data** (`ndarray`):
        Available data

    * **criterion** (`str`):
        Criterion to be used ('AIC', 'BIC', 'AICc'). Default is 'AIC'

    * **kwargs**:
        Additional keyword inputs to the maximum likelihood estimators.

        Keys must refer to input names to the ``MLEstimation`` class, and values must be lists of length `nmodels`,
        ordered in the same way as input `candidate_models`. For example, setting
        `kwargs={`method': [`Nelder-Mead', `Powell']}` means that the Nelder-Mead minimization algorithm will be used
        for ML estimation of the first candidate model, while the Powell method will be used for the second candidate
        model.

    * **random_state** (None or `int` or ``numpy.random.RandomState`` object):
        Random seed used to initialize the pseudo-random number generator. Default is None.

        If an integer is provided, this sets the seed for an object of ``numpy.random.RandomState``. Otherwise, the
        object itself can be passed directly.

    * **x0** (`list` of `ndarrays`):
        Starting points for optimization - see ``MLEstimation``

    * **nopt** (`list` of `int`):
        Number of iterations for the maximization procedure - see ``MLEstimation``

    If `x0` and `nopt` are both `None`, the object is created but the model selection procedure is not run, one
    must then call the ``run`` method.

    **Attributes:**

    * **ml_estimators** (`list` of `MLEstimation` objects):
        ``MLEstimation`` results for each model (contains e.g. fitted parameters)

    * **criterion_values** (`list` of `floats`):
        Value of the criterion for all models.

    * **penalty_terms** (`list` of `floats`):
        Value of the penalty term for all models. Data fit term is then criterion_value - penalty_term.

    * **probabilities** (`list` of `floats`):
        Value of the model probabilities, computed as

        .. math:: P(M_i|d) = \dfrac{\exp(-\Delta_i/2)}{\sum_i \exp(-\Delta_i/2)}

        where :math:`\Delta_i = criterion_i - min_i(criterion)`

    **Methods:**

    """
    # Authors: Audrey Olivier, Dimitris Giovanis
    # Last Modified: 12/19 by Audrey Olivier
    @beartype
    def __init__(self,
                 candidate_models: List[InferenceModel],
                 data: Union[list, np.ndarray],
                 optimizer: Optimizer = MinimizeOptimizer(),
                 criterion: InformationTheoreticCriterion = InformationTheoreticCriterion.AIC,
                 random_state: RandomStateType = None,
                 optimizations_number: Union[PositiveInteger, None] = None,
                 initial_guess: List[np.ndarray] = None):

        if not isinstance(candidate_models, (list, tuple)) or not all(isinstance(model, InferenceModel)
                                                                      for model in candidate_models):
            raise TypeError('UQpy: Input candidate_models must be a list of InferenceModel objects.')
        self.models_number = len(candidate_models)
        self.candidate_models = candidate_models
        self.data = data
        self.criterion: InformationTheoreticCriterion = criterion
        self.random_state = process_random_state(random_state)
        self.logger = logging.getLogger(__name__)

        self.optimizer = optimizer
        self.ml_estimators = []
        self._initialize_ml_estimators()

        # Initialize the outputs
        self.criterion_values = [None, ] * self.models_number
        self.penalty_terms = [None, ] * self.models_number
        self.probabilities = [None, ] * self.models_number

        # Run the model selection procedure
        if (optimizations_number is not None) or (initial_guess is not None):
            self.run(optimizations_number=optimizations_number, initial_guess=initial_guess)

    def _initialize_ml_estimators(self):
        for i, inference_model in enumerate(self.candidate_models):
            ml_estimator = MLE(inference_model=inference_model, data=self.data,
                               random_state=self.random_state, initial_guess=None,
                               optimizations_number=None,
                               optimizer=self.optimizer)
            self.ml_estimators.append(ml_estimator)

    def run(self, optimizations_number: PositiveInteger = 1, initial_guess=None):
        """
        Run the model selection procedure, i.e. compute criterion value for all models.

        This function calls the ``run`` method of the ``MLEstimation`` object for each model to compute the maximum
        log-likelihood, then computes the criterion value and probability for each model.

        **Inputs:**

        * **x0** (`list` of `ndarrays`):
            Starting point(s) for optimization for all models. Default is `None`. If not provided, see `nopt`. See
            ``MLEstimation`` class.

        * **nopt** (`int` or `list` of `ints`):
            Number of iterations that the optimization is run, starting at random initial guesses. It is only used if
            `x0` is not provided. Default is 1. See ``MLEstimation`` class.

        """
        initial_guess, optimizations_number = self._check_input_data(initial_guess, optimizations_number)

        # Loop over all the models
        for i, (inference_model, ml_estimator) in enumerate(zip(self.candidate_models, self.ml_estimators)):
            # First evaluate ML estimate for all models, do several iterations if demanded
            ml_estimator.run(optimizations_number=optimizations_number[i], initial_guess=initial_guess[i])

            # Then minimize the criterion
            self.criterion_values[i], self.penalty_terms[i] = self._minimize_info_criterion(
                criterion=self.criterion, data=self.data, inference_model=inference_model,
                max_log_like=ml_estimator.max_log_like, return_penalty=True)

        # Compute probabilities from criterion values
        self.probabilities = self._compute_probabilities(self.criterion_values)

    def _check_input_data(self, initial_guess, optimizations_number):
        if isinstance(optimizations_number, int) or optimizations_number is None:
            optimizations_number = [optimizations_number] * self.models_number
        if not (isinstance(optimizations_number, list) and len(optimizations_number) == self.models_number):
            raise ValueError('UQpy: nopt should be an int or list of length models_number')
        if initial_guess is None:
            initial_guess = [None] * self.models_number
        if not (isinstance(initial_guess, list) and len(initial_guess) == self.models_number):
            raise ValueError('UQpy: x0 should be a list of length models_number (or None).')
        return initial_guess, optimizations_number

    def sort_models(self):
        """
        Sort models in descending order of model probability (increasing order of `criterion` value).

        This function sorts - in place - the attribute lists `candidate_models, ml_estimators, criterion_values,
        penalty_terms` and `probabilities` so that they are sorted from most probable to least probable model. It is a
        stand-alone function that is provided to help the user to easily visualize which model is the best.

        No inputs/outputs.

        """
        sort_idx = list(np.argsort(np.array(self.criterion_values)))

        self.candidate_models = [self.candidate_models[i] for i in sort_idx]
        self.ml_estimators = [self.ml_estimators[i] for i in sort_idx]
        self.criterion_values = [self.criterion_values[i] for i in sort_idx]
        self.penalty_terms = [self.penalty_terms[i] for i in sort_idx]
        self.probabilities = [self.probabilities[i] for i in sort_idx]

    @staticmethod
    def _minimize_info_criterion(criterion: InformationTheoreticCriterion, data, inference_model,
                                 max_log_like, return_penalty=False):
        """
        Compute the criterion value for a given model, given a max_log_likelihood value.

        The criterion value is -2 * max_log_like + penalty, the penalty depends on the chosen criterion. This function
        is a utility function (static method), called within the run_estimation method.

        **Inputs:**

        :param criterion: Chosen criterion.
        :type criterion: str

        :param data: Available data.
        :type data: ndarray

        :param inference_model: inference model.
        :type inference_model: object of class InferenceModel

        :param max_log_like: Value of likelihood function at MLE.
        :type max_log_like: float

        :param return_penalty: Boolean that sets whether to return the penalty term as additional output.

                               Default is False
        :type return_penalty: bool

        **Output/Returns:**

        :return criterion_value: Value of criterion.
        :rtype criterion_value: float

        :return penalty_term: Value of penalty term.
        :rtype penalty_term: float

        """

        n_params = inference_model.parameters_number
        number_of_data = len(data)
        penalty_term = penalty_terms[criterion.name](number_of_data, n_params)
        if return_penalty:
            return -2 * max_log_like + penalty_term, penalty_term
        return -2 * max_log_like + penalty_term

    @staticmethod
    def _compute_probabilities(criterion_values):
        """
        Compute the model probability given criterion values for all models.

        Model probability is proportional to exp(-criterion/2), model probabilities over all models sum up to 1. This
        function is a utility function (static method), called within the run_estimation method.

        **Inputs:**

        :param criterion_values: Values of criterion for all models.
        :type criterion_values: list (length nmodels) of floats

        **Output/Returns:**

        :return probabilities: Values of model probabilities
        :rtype probabilities: list (length nmodels) of floats

        """

        delta = np.array(criterion_values) - min(criterion_values)
        prob = np.exp(-delta / 2)
        return prob / np.sum(prob)
