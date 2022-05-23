r"""

Mechanical oscillator model (multioutput)
==============================================

The mechanical oscillator is governed by the following second-order ODE:

.. math::
    m \ddot{x} + c \dot{x} + k x = 0

.. math::
    x(0) = \ell, \dot{x}(0) = 0.

The parameteres of the oscillator are modeled as follows:

.. math::
    m \sim \mathcal{U}(10, 12), c \sim \mathcal{U}(0.4, 0.8), k \sim \mathcal{U}(70, 90), \ell \sim \mathcal{U}(-1, -0.25).

Unlike the pointwise-in-time Sobol indices, which provide the sensitivity of the model 
parameters at each point in time, the GSI indices summarise the sensitivities of the 
model parameters over the entire time period.

"""

# %%
import numpy as np

from UQpy.run_model.RunModel import RunModel
from UQpy.run_model.model_execution.PythonModel import PythonModel
from UQpy.distributions import Uniform, Normal
from UQpy.distributions.collection.JointIndependent import JointIndependent
from UQpy.sensitivity.generalised_sobol import GeneralisedSobol

# %% [markdown]
# **Define the model and input distributions**

# Create Model object
model = PythonModel(
    model_script="local_mechanical_oscillator_ODE.py",
    model_object_name="mech_oscillator",
    var_names=[r"$m$", "$c$", "$k$", "$\ell$"],
    delete_files=True,
)

runmodel_obj = RunModel(model=model)

# Define distribution object
M = Uniform(10, (12 - 10))
C = Uniform(0.4, (0.8 - 0.4))
K = Uniform(70, (90 - 70))
L = Uniform(-1, (-0.25 - -1))
dist_object = JointIndependent([M, C, K, L])

# %% [markdown]
# **Compute generalised Sobol indices**

# %% [markdown]
SA = GeneralisedSobol(runmodel_obj, dist_object)

computed_indices = SA.run(n_samples=500)

# %% [markdown]
# **First order Generalised Sobol indices**
#
# Expected generalised Sobol indices:
#
# :math:`GS_{m}` = 0.0826
#
# :math:`GS_{c}` = 0.0020
#
# :math:`GS_{k}` = 0.2068
#
# :math:`GS_{\ell}` = 0.0561

# %%
computed_indices["gen_sobol_i"]

# %% [markdown]
# **Total order Generalised Sobol indices**

# %%
computed_indices["gen_sobol_total_i"]