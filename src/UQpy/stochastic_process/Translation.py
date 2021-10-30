import itertools

from scipy.stats import norm

from UQpy.utilities import *
from UQpy.stochastic_process.supportive import (
    inverse_wiener_khinchin_transform,
    wiener_khinchin_transform,
    scaling_correlation_function,
)


class Translation:
    def __init__(
            self,
            distributions,
            time_interval,
            frequency_interval,
            number_time_intervals,
            number_frequency_intervals,
            power_spectrum_gaussian=None,
            correlation_function_gaussian=None,
            samples_gaussian=None,
    ):
        """
        A class to translate Gaussian Stochastic Processes to non-Gaussian Stochastic Processes

        :param distributions: An instance of the UQpy :class:`.Distribution` class defining the marginal distribution to
         which the Gaussian stochastic process should be translated to.
        :param time_interval: The value of time discretization.
        :param frequency_interval: The value of frequency discretization.
        :param number_time_intervals: The number of time discretizations.
        :param number_frequency_intervals: The number of frequency discretizations.
        :param power_spectrum_gaussian: The power spectrum of the gaussian stochastic process to be translated.
         `power_spectrum_gaussian` must be of size (`number_frequency_intervals`).
        :param correlation_function_gaussian: The auto correlation function of the Gaussian stochastic process to be
         translated. Either the power spectrum or the auto correlation function of the gaussian stochastic process needs
         to be defined. `correlation_function_gaussian` must be of size (`number_time_intervals`).
        :param samples_gaussian: Samples of Gaussian stochastic process to be translated.
         `samples_gaussian` is optional. If no samples are passed, the :class:`.Translation` class will compute the
         correlation distortion.
        """
        self.distributions = distributions
        self.time_interval = time_interval
        self.frequency_interval = frequency_interval
        self.number_time_intervals = number_time_intervals
        self.number_frequency_intervals = number_frequency_intervals
        if correlation_function_gaussian is None and power_spectrum_gaussian is None:
            print(
                "Either the Power Spectrum or the Autocorrelation function should be specified"
            )
        if correlation_function_gaussian is None:
            self.power_spectrum_gaussian = power_spectrum_gaussian
            self.correlation_function_gaussian = wiener_khinchin_transform(
                power_spectrum_gaussian,
                np.arange(0, self.number_frequency_intervals) * self.frequency_interval,
                np.arange(0, self.number_time_intervals) * self.time_interval,
            )
        elif power_spectrum_gaussian is None:
            self.correlation_function_gaussian = correlation_function_gaussian
            self.power_spectrum_gaussian = inverse_wiener_khinchin_transform(
                correlation_function_gaussian,
                np.arange(0, self.number_frequency_intervals) * self.frequency_interval,
                np.arange(0, self.number_time_intervals) * self.time_interval,
            )
        self.shape = self.correlation_function_gaussian.shape
        self.dim = len(self.correlation_function_gaussian.shape)
        if samples_gaussian is not None:
            self.samples_shape = samples_gaussian.shape
            self.samples_gaussian = samples_gaussian.flatten()[:, np.newaxis]
            self.samples_non_gaussian = self._translate_gaussian_samples().reshape(
                self.samples_shape
            )
        (
            self.correlation_function_non_gaussian,
            self.scaled_correlation_function_non_gaussian,
        ) = self._autocorrelation_distortion()
        self.power_spectrum_non_gaussian = inverse_wiener_khinchin_transform(
            self.correlation_function_non_gaussian,
            np.arange(0, self.number_frequency_intervals) * self.frequency_interval,
            np.arange(0, self.number_time_intervals) * self.time_interval,
        )

    def _translate_gaussian_samples(self):
        standard_deviation = np.sqrt(self.correlation_function_gaussian[0])
        samples_cdf = norm.cdf(self.samples_gaussian, scale=standard_deviation)
        if hasattr(self.distributions, "icdf"):
            non_gaussian_icdf = getattr(self.distributions, "icdf")
            samples_non_gaussian = non_gaussian_icdf(samples_cdf)
        else:
            raise AttributeError(
                "UQpy: The marginal dist_object needs to have an inverse cdf defined."
            )
        return samples_non_gaussian

    def _autocorrelation_distortion(self):
        correlation_function_gaussian = scaling_correlation_function(
            self.correlation_function_gaussian
        )
        correlation_function_gaussian = np.clip(
            correlation_function_gaussian, -0.999, 0.999
        )
        correlation_function_non_gaussian = np.zeros_like(correlation_function_gaussian)
        for i in itertools.product(*[range(s) for s in self.shape]):
            correlation_function_non_gaussian[i] = correlation_distortion(
                self.distributions, correlation_function_gaussian[i]
            )
        if hasattr(self.distributions, "moments"):
            non_gaussian_moments = getattr(self.distributions, "moments")()
        else:
            raise AttributeError(
                "UQpy: The marginal dist_object needs to have defined moments."
            )
        scaled_correlation_function_non_gaussian = correlation_function_non_gaussian * non_gaussian_moments[1] + \
                                                   non_gaussian_moments[0] ** 2
        return (
            correlation_function_non_gaussian,
            scaled_correlation_function_non_gaussian,
        )