from abc import ABC, abstractmethod


class ConstraintsGPR(ABC):
    """
    Abstract base class of all Constraints. Serves as a template for creating new Kriging constraints for log-likelihood
    function.
    """

    @abstractmethod
    def define_arguments(self, x_train, y_train, predict_function):
        """
        Abstract method that needs to be implemented by the user when creating a new Correlation function.
        """
        pass
