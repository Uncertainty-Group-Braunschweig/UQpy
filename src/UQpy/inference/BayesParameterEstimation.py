import logging
from typing import Union

from beartype import beartype
from UQpy.utilities.ValidationTypes import PositiveInteger
from UQpy.inference.inference_models.baseclass.InferenceModel import InferenceModel
from UQpy.sampling import MCMC, ImportanceSampling


class BayesParameterEstimation:
    # Authors: Audrey Olivier, Dimitris Giovanis
    # Last Modified: 12/19 by Audrey Olivier
    @beartype
    def __init__(
        self,
        inference_model: InferenceModel,
        data,
        sampling_class: Union[MCMC, ImportanceSampling] = None,
        nsamples: Union[None, int] = None,
        nsamples_per_chain: Union[None, int] = None,
    ):
        """
        Estimate the parameter posterior density given some data.

        This class generates samples from the parameter posterior distribution using Markov Chain Monte Carlo or
        Importance Sampling. It leverages the :class:`.MCMC` and :class:`.ImportanceSampling` classes from the
        :py:mod:`.sampling` module.

        :param inference_model: The inference model that defines the likelihood function.
        :param data: Available data, :class:`numpy.ndarray` of shape consistent with log-likelihood function in
         :class:`.InferenceModel`
        :param sampling_class: Class instance, must be a subclass of :class:`.MCMC` or :class:`.ImportanceSampling`.
        :param nsamples: Number of samples used in :class:`.MCMC`/:class:`ImportanceSampling`, see
         :meth:`run` method.
        :param nsamples_per_chain: Number of samples per chain used in :class:`.MCMC`, see :py:meth:`run` method.
        """
        self.inference_model = inference_model
        self.data = data
        self.logger = logging.getLogger(__name__)
        self.sampler: Union[MCMC, ImportanceSampling] = sampling_class
        """Sampling method object, contains e.g. the posterior samples.

        This object is created along with the :class:`.BayesParameterEstimation` object, and its run method is called 
        whenever the :py:meth:`run` method of the :class:`.BayesParameterEstimation` is called.
        """
        self._method = MCMC if isinstance(self.sampler, MCMC) else ImportanceSampling
        if (nsamples is not None) or (nsamples_per_chain is not None):
            self.run(nsamples=nsamples, nsamples_per_chain=nsamples_per_chain,)

    sampling_actions = {
        MCMC: lambda sampler, nsamples, nsamples_per_chain: sampler.run(
            nsamples=nsamples, nsamples_per_chain=nsamples_per_chain),
        ImportanceSampling: lambda sampler, nsamples, nsamples_per_chain: sampler.run(nsamples=nsamples),
    }

    @beartype
    def run(self, nsamples: PositiveInteger = None, nsamples_per_chain=None):
        """
        Run the Bayesian inference procedure, i.e., sample from the parameter posterior distribution.

        This function calls the :meth:`run` method of the `sampler` attribute to generate samples from the parameter
        posterior distribution.

        :param nsamples: Number of samples used in :class:`.MCMC`/:class:`.ImportanceSampling`
        :param nsamples_per_chain: Number of samples per chain used in :class:`.MCMC`
        """

        BayesParameterEstimation.sampling_actions[self._method](self.sampler, nsamples, nsamples_per_chain)

        self.logger.info("UQpy: Parameter estimation with " + self.sampler.__class__.__name__
                         + " completed successfully!")
