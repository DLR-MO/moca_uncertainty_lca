Getting Started
===============

This tutorial introduces the usage of **moca_uncertainty_lca** for different user backgrounds.
Choose the section that best matches your experience.

The three sections below are expandable and independent.

--------------------------------------------------------------------

.. dropdown:: I have already used MonteCarloLCA in Brightway2
   :icon: rocket

   If you are familiar with the ``MonteCarloLCA`` class from Brightway2, getting started with
   MOCA likely requires only minor changes to your existing code.

   The main motivation for using MOCA instead of Brightway's
   native Monte Carlo implementation is **performance**.

   Why use MOCA?
   -------------
   Compared to Brightway2, MOCA's ``MonteCarloLCA`` implementation

   * uses multiprocessing to fully exploit multi-core CPUs
   * is significantly faster for large Monte Carlo runs
   * is designed for large-scale uncertainty analysis

   Conceptually, both approaches are very similar:  
   sampled exchanges → repeated LCIA calculations → statistical post-processing.

   Code comparison
   ---------------

   **Brightway2 – MonteCarloLCA**

   .. code-block:: python

      from brightway2 import *

      lca = MonteCarloLCA({demand_activity: 1}, method)
      lca.load_data()

      results = []
      for _ in range(1000):
          lca.redo_lcia()
          results.append(lca.score)

   **moca_uncertainty_lca**

   .. code-block:: python

      from moca_uncertainty_lca import UncertaintyLCA

      ulca = UncertaintyLCA(
          demand={demand_activity: 1},
          method=method,
          n_iterations=1000,
          n_processes=8
      )

      results = ulca.run()

   The main differences are:

   * explicit control over the **number of processes**
   * automatic parallelization
   * cleaner separation between setup, execution, and post-processing

   If you already have a working ``MonteCarloLCA`` workflow, migrating usually takes
   only a few minutes.

--------------------------------------------------------------------

.. dropdown:: I have used Monte Carlo in the Activity Browser
   :icon: tools

   If you are familiar with the **Activity Browser's Monte Carlo functionality**,
   you already know how uncertainty is defined and sampled in Brightway-based models.

   How this relates to moca_uncertainty_lca
   ----------------------------------------
   The Activity Browser provides a **graphical interface** for:

   * inspecting uncertainty distributions
   * editing uncertainty parameters
   * running Monte Carlo simulations interactively

   ``moca_uncertainty_lca`` builds on the **same underlying uncertainty data**
   but focuses on:

   * scripted, reproducible workflows
   * high-performance Monte Carlo simulations
   * integration into Python-based analysis pipelines

   You can think of it as:

   *Activity Browser → exploration & setup*  
   *moca_uncertainty_lca → large-scale computation & analysis*

   Recommended background reading
   -------------------------------
   If you want to refresh how uncertainty is handled in the Activity Browser,
   please refer to the official documentation:

   * Activity Browser documentation:  
     https://activity-browser.readthedocs.io/

   Once uncertainty information is defined via the Activity Browser,
   it can be directly used by ``moca_uncertainty_lca`` without additional steps.

--------------------------------------------------------------------

.. dropdown:: I have never worked with uncertainty or Monte Carlo before
   :icon: info

   This section provides a **minimal conceptual background** and points you to the
   most important resources.

   How uncertainty enters an LCA model
   -----------------------------------
   In Life Cycle Assessment, many inputs are uncertain, for example:

   * foreground process data
   * background database data
   * emission factors
   * technological assumptions

   In Brightway-based workflows, uncertainty information is stored directly
   on **exchanges** in the form of probability distributions.

   Adding uncertainty with the Activity Browser
   ---------------------------------------------
   The easiest way to add and inspect uncertainty information is the
   **Activity Browser**.

   Using the Activity Browser, you can:

   * assign uncertainty distributions to exchanges
   * define parameters such as mean, standard deviation, or bounds
   * use **pedigree matrices** to derive uncertainty parameters

   Pedigree matrices
   -----------------
   A pedigree matrix is a structured way to translate **data quality indicators**
   (e.g. reliability, completeness, temporal correlation) into quantitative
   uncertainty parameters.

   These parameters are then used to define probability distributions
   for Monte Carlo sampling.

   Monte Carlo simulation – the basic idea
   ---------------------------------------
   Monte Carlo simulation means:

   1. Randomly sample all uncertain inputs according to their distributions
   2. Recalculate the LCA result
   3. Repeat this process many times
   4. Analyze the resulting distribution of impact scores

   This allows you to quantify:

   * result uncertainty
   * confidence intervals
   * robustness of conclusions

   Where to go next
   ----------------
   To get started step by step, we recommend:

   * Activity Browser documentation (uncertainty & pedigree):  
     https://activity-browser.readthedocs.io/

   * ``moca_uncertainty_lca`` examples:  
     See the **Examples** section of this documentation

   After defining uncertainty via the Activity Browser, you can directly
   run large Monte Carlo simulations using ``moca_uncertainty_lca``.

--------------------------------------------------------------------
