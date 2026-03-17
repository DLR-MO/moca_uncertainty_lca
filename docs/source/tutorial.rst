.. SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
..
.. SPDX-License-Identifier: GPL-3.0-or-later

Getting Started
===============

This tutorial introduces the usage of MOCA for different user backgrounds. The three sections below are expandable and independent of each other. Choose the section that best matches your experience.


--------------------------------------------------------------------

.. dropdown:: I have never worked with uncertainty or Monte Carlo before
   :icon: info

   Life Cycle Assessment is affected by many sources of uncertainty. This package helps to quantify and understand the uncertainty that is contained in the numerical data that make up your LCA model.

   This data includes:

   * your foreground process data
   * the background database data you use, such as ecoinvent
   * characterisation factors used in the LCIA

   The easiest way to get started on uncertainty analysis with Brightway2 is to use the
   `Activity Browser <https://github.com/LCA-ActivityBrowser/activity-browser>`_. This tool provides a user-friendly interface to explore and define uncertainty in your LCA model, without needing to write code.

   Using the Activity Browser, you can:

   * assign uncertainty distributions to exchanges
   * define parameters such as the mean, standard deviation or bounds
   * use pedigree matrices to derive uncertainty parameters

   If you are completely new to uncertainty analysis, chances are you do not have a lot of uncertainty data on hand. In this case, the Activity Browser's pedigree matrix functionality can be a great starting point to define uncertainty based on your judgement of your model quality. You can rank your different exchanges between 1 and 5 on several categories and then get an estimation of the uncertainty.

   Once you have defined uncertainty in the Activity Browser, you can directly use this information to run large Monte Carlo simulations using moca_uncertainty_lca. This allows you to transfer the uncertainty information that you have defined for your input parameters into uncertainty information for your LCA results. You can then analyse the resulting distribution of impact scores to see histograms, create boxplots and more.

   To give you a quick overview of how Monte Carlo simulation works, here is a simplified workflow:

   1. Randomly sample all uncertain inputs according to their distributions
   2. Recalculate the LCA result
   3. Repeat this process many times
   4. Analyze the resulting distribution of impact scores

   Want to try it out? Simply create a project in the Activity Browser and start defining uncertainty for your model. Then, you can run a simple Python script like this to get started with MOCA:

   .. code-block:: python

      import brightway2 as bw
      import moca_uncertainty_lca as moca

      bw.projects.set_current("your_project")  # change to your project

      demand = {
         bw.Database("your_database") # database of your demand activity
            .get("492e35473j74034b6c49b0240ff7800"): 1 # key of your demand activity
      }

      mc_lca = moca.MonteCarloLCA(
         demand=demand,
         lcia_method_name="EF v3.1 no LT", # change to your preferred LCIA method
         run_parallel=False
      )

      # for a quick test, use a small number of iterations
      # for a more thorough analysis, use 2000 or more iterations
      mc_lca.execute_monte_carlo(iterations=100)

      # these lines will save the results and statistics to JSON files
      mc_lca.results_to_json()
      mc_lca.stats_to_json()

   Want more examples? Check out the :ref:`examples` for more code snippets.


--------------------------------------------------------------------

.. dropdown:: I have used Monte Carlo in the Activity Browser
   :icon: tools

   If you are familiar with the Activity Browser's Monte Carlo functionality, chances are you have already defined uncertainty for your model and run some Monte Carlo simulations. In this case, you can directly use MOCA without making any modifications to your existing model setup.

   As before, the Activity Browser will continue to be your tool for:

   * inspecting uncertainty distributions
   * editing uncertainty parameters

   MOCA build on the same underlying data that you already have and helps you with:

   * scripted, efficient uncertainty analysis workflows
   * high-performance (parallelised) Monte Carlo simulations
   * integration into Python-based analysis pipelines

   To get started, simply run a Python script like this:

   .. code-block:: python

      import brightway2 as bw
      import moca_uncertainty_lca as moca

      bw.projects.set_current("your_project")  # change to your project

      demand = {
         bw.Database("your_database") # database of your demand activity
            .get("492e35473j74034b6c49b0240ff7800"): 1 # key of your demand activity
      }

      mc_lca = moca.MonteCarloLCA(
         demand=demand,
         lcia_method_name="EF v3.1 no LT", # change to your preferred LCIA method
         run_parallel=False
      )

      # set to your required number of iterations
      mc_lca.execute_monte_carlo(iterations=100)

      # these lines will save the results and statistics to JSON files
      mc_lca.results_to_json()
      mc_lca.stats_to_json()

   Want more examples? Check out the :ref:`examples` for more code snippets.

--------------------------------------------------------------------

.. dropdown:: I have already used MonteCarloLCA in Brightway2
   :icon: rocket

   If you are familiar with the ``MonteCarloLCA`` class from Brightway2, getting started with
   MOCA likely requires only minor changes to your existing code. The main motivation for using MOCA instead of Brightway's
   native Monte Carlo implementation is performance.

   Compared to Brightway2, MOCA's ``MonteCarloLCA`` implementation:

   * is significantly faster for large Monte Carlo runs
   * uses multiprocessing to parallelise across multiple CPU cores
   * is designed for large-scale uncertainty analysis

   Let's have a look at a simple example to see how the code differs between the two implementations.

   **1. Setup**

   Most likely, some part of your code looks similar to this:

   .. code-block:: python

      import brightway2 as bw

      bw.projects.set_current("your_project")  # change to your project

      demand = {
         bw.Database("your_database") # database of your demand activity
            .get("492e35473j74034b6c49b0240ff7800"): 1 # key of your demand activity
      }

      lcia_methods = [
         ('EF v3.1 no LT', 'climate change', 'global warming potential (GWP100)'),
         ('EF v3.1 no LT', 'acidification', 'accumulated exceedance (AE)')
      ]

   **2. Brightway2's MonteCarloLCA**

   You might then perform a Monte Carlo simulation using Brightway2's ``MonteCarloLCA`` like this:

   .. code-block:: python

      import brightway2 as bw
      import json

      # initialize the Monte Carlo LCA
      mc_lca = bw.MonteCarloLCA(demand, lcia_methods)

      # execute the Monte Carlo simulation
      mc_results = []
      for _ in range(100):
         mc_results.append(next(mc_lca))

      # write the results to a JSON file
      json.dump(mc_results, open("bw_mc_results.json", "w"), indent=4)

   **3. MOCA's MonteCarloLCA**

   With MOCA, the same workflow would look like this:

   .. code-block:: python

      import moca_uncertainty_lca as moca

      # initialize the Monte Carlo LCA
      mc_lca = moca.MonteCarloLCA(demand, lcia_methods=lcia_methods, run_parallel=False)

      # execute the Monte Carlo simulation
      mc_lca.execute_monte_carlo(iterations=100)

      # retrieve the results and write them to files
      mc_results = mc_lca.mc_results
      mc_lca.results_to_json(filename="moca_mc_results.json")
      mc_lca.stats_to_json(filename="moca_mc_stats.json")

   However, MOCA doesn't stop here - you can easily run a parallelised calculation by simply setting ``run_parallel=True`` when initializing the ``MonteCarloLCA`` class. This can significantly reduce the runtime for large Monte Carlo simulations. Additionally, you can set default uncertainty distributions for your model parameters or export a list of all your uncertain parameters.

   Want to see more? Check out the :ref:`examples` for more code snippets.

--------------------------------------------------------------------
