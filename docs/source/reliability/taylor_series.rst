Taylor Series
-------------

:class:`.TaylorSeries` is a class that calculates the reliability  of a model using the First Order Reliability Method (FORM)
or the Second Order Reliability Method (SORM) based on the first-order and second-order Taylor series expansion
approximation of the performance function, respectively (:cite:`TaylorSeries1`, :cite:`TaylorSeries2`).

In FORM, the performance function is linearized according to

.. math:: G(\textbf{U})  \approx  G(\textbf{U}^\star) + \nabla G(\textbf{U}^\star)(\textbf{U}-\textbf{U}^\star)^\intercal

where :math:`\textbf{U}^\star` is the expansion point, :math:`G(\textbf{U})` is the performance function evaluated in
the standard normal space and :math:`\nabla G(\textbf{U}^\star)` is the gradient of :math:`G(\textbf{U})` evaluated at
:math:`\textbf{U}^\star`. The probability failure can be calculated by

.. math:: P_{f, \text{form}} = \Phi(-\beta_{HL})

where :math:`\Phi(\cdot)` is the standard normal cumulative distribution function and :math:`\beta_{HL}=||\textbf{U}^*||`
is the norm of the design point known as the Hasofer-Lind reliability index calculated with the iterative
Hasofer-Lind-Rackwitz-Fiessler (HLRF) algorithm.  The convergence criteria used for HLRF algorithm are:


.. math:: e1: ||\textbf{U}^{k} - \textbf{U}^{k-1}||_2 \leq 10^{-3}
.. math:: e2: ||\beta_{HL}^{k} - \beta_{HL}^{k-1}||_2 \leq 10^{-3}
.. math:: e3: ||\nabla G(\textbf{U}^{k})- \nabla G(\textbf{U}^{k-1})||_2 \leq 10^{-3}

.. image:: ../_static/Reliability_FORM.png
   :scale: 40 %
   :alt:  Graphical representation of the FORM.
   :align: center

In SORM the performance function is approximated by a second-order Taylor series around the design point according to


.. math:: G(\textbf{U}) = G(\textbf{U}^\star) +  \nabla G(\textbf{U}^\star)(\textbf{U}-\textbf{U}^\star)^\intercal + \frac{1}{2}(\textbf{U}-\textbf{U}^\star)\textbf{H}(\textbf{U}-\textbf{U}^\star)

where :math:`\textbf{H}` is the Hessian matrix of the second derivatives of :math:`G(\textbf{U})` evaluated at
:math:`\textbf{U}^*`. After the design point :math:`\textbf{U}^*` is identified and the probability of failure
:math:`P_{f, \text{form}}` is calculated with FORM a correction is made according to


.. math:: P_{f, \text{sorm}} = \Phi(-\beta_{HL}) \prod_{i=1}^{n-1} (1+\beta_{HL}\kappa_i)^{-\frac{1}{2}}

where :math:`\kappa_i` is the `i-th`  curvature.

The :class:`.TaylorSeries` class is the parent class of the :class:`.FORM` and :class:`.SORM` classes that perform the FORM and SORM,
respectively. These classes can be imported in a python script using the following command:

>>> from UQpy.reliability.taylor_series import FORM, SORM


TaylorSeries Class
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: UQpy.reliability.taylor_series.baseclass.TaylorSeries
    :members:

.. toctree::
   :maxdepth: 1
   :hidden:

    FORM <form>
    SORM <sorm>


