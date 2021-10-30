import scipy.sparse as sps
import scipy.sparse.linalg as spsl
from UQpy.utilities.Utilities import *
from UQpy.utilities.Utilities import _nn_coord
from beartype import beartype
from typing import Annotated, Union
from beartype.vale import Is
from UQpy.dimension_reduction.kernels.euclidean.GaussianKernel import GaussianKernel


class DiffusionMaps:
    """
    Perform the diffusion maps on the input data to reveal its lower dimensional embedded geometry.

    In this class, the diffusion maps create a connection between the spectral properties of the diffusion process and
    the intrinsic geometry of the data resulting in a multiscale representation of it. In this regard, an affinity
    matrix containing the degree of similarity of the data points is either estimated based on the euclidean distance,
    using a Gaussian kernel, or it is computed using any other Kernel definition passed to the main
    method (e.g., defining a kernel on the grassman manifold).

    **Input:**

    * **alpha** (`float`)
        Assumes a value between 0 and 1 and corresponding to different diffusion operators. In this regard, one can use
        this parameter to take into consideration the distribution of the data points on the diffusion process.
        It happens because the distribution of the data is not necessarily dependent on the geometry of the manifold.
        Therefore, if alpha` is equal to 1, the Laplace-Beltrami operator is approximated and the geometry of the
        manifold is recovered without taking the distribution of the points into consideration. On the other hand, when
        `alpha` is equal to 0.5 the Fokker-Plank operator is approximated and the distribution of points is taken into
        consideration. Further, when `alpha` is equal to zero the Laplace normalization is recovered.

    * **n_evecs** (`int`)
        The number of eigenvectors and eigenvalues used in the representation of the diffusion coordinates.

    * **sparse** (`bool`)
        Is a boolean variable to activate the `sparse` mode of the method.

    * **k_neighbors** (`int`)
        Used when `sparse` is True to select the k samples close to a given sample in the construction
        of an sparse graph defining the affinity of the input data. For instance, if `k_neighbors` is equal to 10, only
        the closest ten points of a given point are connect to a given point in the graph. As a consequence, the
        obtained affinity matrix is sparse which reduces the computational effort of the eigendecomposition of the
        transition kernel of the Markov chain.

    * **kernel_object** (`function`)
        An object of a callable object used to compute the kernel matrix. Three different options are provided:

        - Using the ``DiffusionMaps`` method ``gaussian_kernel`` as
          DiffusionMaps(kernel_object=DiffusionMaps.gaussian_kernel);
        - Using an user defined function as DiffusionMaps(kernel_object=user_kernel);
        - Passing a ``grassman`` class object DiffusionMaps(kernel_object=Grassmann_Object). In this case, the user has
          to select ``kernel_grassmann`` in order to define which kernel matrix will be used because when the the
          ``grassman`` class is used in a dataset a kernel matrix can be constructed with both the left and right
          singular eigenvectors.

    * **kernel_grassmann** (`str`)
        It assumes the values 'left' and 'right' for the left and right singular eigenvectors used to compute the kernel
        matrix, respectively. Moreover, if 'sum' is selected, it means that the kernel matrix is composed by the sum of
        the kernel matrices estimated using the left and right singular eigenvectors. On the other hand, if 'prod' is
        used instead, it means that the kernel matrix is composed by the product of the matrices estimated using the
        left and right singular eigenvectors.

    **Attributes:**

    * **kernel_matrix** (`ndarray`)
        Kernel matrix.

    * **transition_matrix** (`ndarray`)
        Transition kernel of a Markov chain on the data.

    * **dcoords** (`ndarray`)
        Diffusion coordinates

    * **evecs** (`ndarray`)
        Eigenvectors of the transition kernel of a Markov chanin on the data.

    * **evals** (`ndarray`)
        Eigenvalues of the transition kernel of a Markov chanin on the data.

    **Methods:**

    """

    AlphaType = Annotated[Union[float, int], Is[lambda number: 0 <= number <= 1]]
    IntegerLargerThanUnityType = Annotated[int, Is[lambda number: number >= 1]]

    @beartype
    def __init__(
        self,
        alpha: AlphaType = 0.5,
        eigenvectors_number: IntegerLargerThanUnityType = 2,
        is_sparse: bool = False,
        neighbors_number: IntegerLargerThanUnityType = 1,
        kernel_matrix=None,
    ):

        self.alpha = alpha
        self.eigenvectors_number = eigenvectors_number
        self.is_sparse = is_sparse
        self.neighbors_number = neighbors_number
        self.kernel_matrix = kernel_matrix

        if kernel_matrix is not None:
            self.kernel_matrix = kernel_matrix

    @classmethod
    def create_from_data(
        cls,
        data,
        alpha: AlphaType = 0.5,
        eigenvectors_number: IntegerLargerThanUnityType = 2,
        is_sparse: bool = False,
        neighbors_number: IntegerLargerThanUnityType = 1,
        kernel=GaussianKernel(),
    ):
        kernel_matrix = kernel.apply_method(data)
        return cls(
            alpha=alpha,
            eigenvectors_number=eigenvectors_number,
            is_sparse=is_sparse,
            neighbors_number=neighbors_number,
            kernel_matrix=kernel_matrix,
        )

    def mapping(self):

        """
        Perform diffusion maps to reveal the embedded geometry of datasets.

        In this method, the users have the option to work with input data defined by subspaces obtained via projection
        of input data points on the grassman manifold, or directly with the input data points. For example,
        considering that a ``grassman`` object is provided using the following command:

        one can instantiate the DiffusionMaps class and run the diffusion maps as follows:

        On the other hand, if the user wish to pass a dataset (samples) to compute the diffusion coordinates using the
        Gaussian kernel, one can use the following commands:

        In the latest case, if `epsilon` is not provided it is estimated based on the median of the square of the
        euclidian distances between data points.

        **Input:**

        * **data** (`list`)
            Data points in the ambient space.

        * **epsilon** (`float`)
            Parameter of the Gaussian kernel.

        **Output/Returns:**

        * **dcoords** (`ndarray`)
            Diffusion coordinates.

        * **evals** (`ndarray`)
            eigenvalues.

        * **evecs** (`ndarray`)
            eigenvectors.

        """

        alpha = self.alpha
        eigenvectors_number = self.eigenvectors_number
        sparse = self.is_sparse
        k_neighbors = self.neighbors_number

        n = np.shape(self.kernel_matrix)[0]
        if sparse:
            self.kernel_matrix = self.__sparse_kernel(self.kernel_matrix, k_neighbors)

        # Compute the diagonal matrix D(i,i) = sum(Kernel(i,j)^alpha,j) and its inverse.
        d, d_inv = self.__diagonal_matrix(self.kernel_matrix, alpha)

        # Compute L^alpha = D^(-alpha)*L*D^(-alpha).
        l_star = self.__normalize_kernel_matrix(self.kernel_matrix, d_inv)

        d_star, d_star_inv = self.__diagonal_matrix(l_star, 1.0)
        if sparse:
            d_star_invd = sps.spdiags(
                d_star_inv, 0, d_star_inv.shape[0], d_star_inv.shape[0]
            )
        else:
            d_star_invd = np.diag(d_star_inv)

        transition_matrix = d_star_invd.dot(l_star)

        # Find the eigenvalues and eigenvectors of Ps.
        if sparse:
            eigenvalues, eigenvectors = spsl.eigs(
                transition_matrix, k=(eigenvectors_number + 1), which="LR"
            )
        else:
            eigenvalues, eigenvectors = np.linalg.eig(transition_matrix)

        ix = np.argsort(np.abs(eigenvalues))
        ix = ix[::-1]
        s = np.real(eigenvalues[ix])
        u = np.real(eigenvectors[:, ix])

        # Truncated eigenvalues and eigenvectors
        eigenvalues = s[:eigenvectors_number]
        eigenvectors = u[:, :eigenvectors_number]

        # Compute the diffusion coordinates
        diffusion_coordinates = np.zeros([n, eigenvectors_number])
        for i in range(eigenvectors_number):
            diffusion_coordinates[:, i] = eigenvalues[i] * eigenvectors[:, i]

        self.transition_matrix = transition_matrix
        self.diffusion_coordinates = diffusion_coordinates
        self.eigenvectors = eigenvectors
        self.eigenvalues = eigenvalues

        return diffusion_coordinates, eigenvalues, eigenvectors

    # Private method
    @staticmethod
    def __sparse_kernel(kernel_matrix, neighbors_number):

        """
        Private method: Construct a sparse kernel.

        Given the number the k nearest neighbors and a kernel matrix, return a sparse kernel matrix.

        **Input:**

        * **kernel_matrix** (`list` or `ndarray`)
            Kernel matrix.

        * **alpha** (`float`)
            Assumes a value between 0 and 1 and corresponding to different diffusion operators.

        **Output/Returns:**

        * **D** (`list`)
            Matrix D.

        * **D_inv** (`list`)
            Inverse of matrix D.

        """

        rows = np.shape(kernel_matrix)[0]
        for i in range(rows):
            row_data = kernel_matrix[i, :]
            index = _nn_coord(row_data, neighbors_number)
            kernel_matrix[i, index] = 0
            if sum(kernel_matrix[i, :]) <= 0:
                raise ValueError(
                    "UQpy: Consider increasing `neighbors_number` to have a connected graph."
                )

        sparse_kernel_matrix = sps.csc_matrix(kernel_matrix)

        return sparse_kernel_matrix

    # Private method
    @staticmethod
    def __diagonal_matrix(kernel_matrix, alpha):

        """
        Private method: Compute the diagonal matrix D and its inverse.

        In the normalization process we have to estimate matrix D(i,i) = sum(Kernel(i,j)^alpha,j) and its inverse.

        **Input:**

        * **kernel_matrix** (`list` or `ndarray`)
            Kernel matrix.

        * **alpha** (`float`)
            Assumes a value between 0 and 1 and corresponding to different diffusion operators.

        **Output/Returns:**

        * **d** (`list`)
            Matrix D.

        * **d_inv** (`list`)
            Inverse of matrix D.

        """

        diagonal_matrix = np.array(kernel_matrix.sum(axis=1)).flatten()
        inverse_diagonal_matrix = np.power(diagonal_matrix, -alpha)

        return diagonal_matrix, inverse_diagonal_matrix

    # Private method
    def __normalize_kernel_matrix(self, kernel_matrix, inverse_diagonal_matrix):

        """
        Private method: Compute and normalize the kernel matrix with the matrix D.

        In the normalization process we have to estimate matrix D(i,i) = sum(Kernel(i,j)^alpha,j) and its inverse.
        We now use this information to normalize the kernel matrix.

        **Input:**

        * **kernel_mat** (`list` or `ndarray`)
            Kernel matrix.

        * **d_inv** (`list` or `ndarray`)
            Inverse of matrix D.

        **Output/Returns:**

        * **normalized_kernel** (`list` or `ndarray`)
            Normalized kernel.

        """

        rows = inverse_diagonal_matrix.shape[0]
        d_alpha = (
            sps.spdiags(inverse_diagonal_matrix, 0, rows, rows)
            if self.is_sparse
            else np.diag(inverse_diagonal_matrix)
        )

        normalized_kernel = d_alpha.dot(kernel_matrix.dot(d_alpha))

        return normalized_kernel