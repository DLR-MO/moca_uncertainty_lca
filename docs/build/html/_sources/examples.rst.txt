.. SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _examples:

Code Examples
=============

This page provides a small set of concrete, copy-pasteable examples showing how to use MOCA's ``MonteCarloLCA`` in practice.

All examples assume that:

* a Brightway / ActivityBrowser project already exists
* uncertainty information is already defined on exchanges
* the package ``moca_uncertainty_lca`` is installed

--------------------------------------------------------------------

Minimal example: serial Monte Carlo
----------------------------------

This is the most basic example of how to run a Monte Carlo simulation with MOCA. It runs in serial and uses the default settings.

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

--------------------------------------------------------------------

Basic parallel execution
------------------------

To speed up larger Monte Carlo runs, enable parallel execution. By default, all available CPU cores (up to 60) are used. On shared machines or laptops, it is often useful to limit CPU usage explicitly using the ``num_cores`` option.

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
       lcia_method_name="EF v3.1 no LT",
       run_parallel=True,  # this flag enables parallel execution
       num_cores=4  # this is an optional parameter - by default up to 60 cores are used
   )

   mc_lca.execute_monte_carlo(iterations=100)

   mc_lca.results_to_json()
   mc_lca.stats_to_json()

--------------------------------------------------------------------

Looking at your uncertainty data
---------------------------------

Before running a Monte Carlo simulation, it can be helpful to get an overview of the uncertainty information in your model. MOCA provides a convenient method to print a summary of the uncertainty types and distributions that you have defined.

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
        lcia_method_name="EF v3.1 no LT",
    )

    mc_lca.print_uncertainty_info()

This will print a summary of the uncertainty information in your model, looking something like this:

.. code-block:: console

    Total exchanges: x
    Exchanges with uncertainty: x (x.x%)

    Uncertainty type distribution:
        Type 4 (Uniform): x (x.x%)
        Type 0 (Undefined): x (x.x%)
        Type 2 (Lognormal): x (x.x%)
        Type 5 (Triangular): x (x.x%)
        Type 3 (Normal): x (x.x%)

    Foreground exchanges: x (x.x%)
    Background exchanges: x (x.x%)

    Foreground exchanges with uncertainty:
        Type 4 (Uniform): x (x.x%)

--------------------------------------------------------------------

Using explicit LCIA methods
---------------------------

Instead of matching LCIA methods by name, you can pass explicit method tuples (like in standard Brightway2).

.. code-block:: python


   import brightway2 as bw
   import moca_uncertainty_lca as moca

   bw.projects.set_current("your_project")  # change to your project

   demand = {
       bw.Database("your_database") # database of your demand activity
       .get("492e35473j74034b6c49b0240ff7800"): 1 # key of your demand activity
   }

   lcia_methods = [
       ('EF v3.1 no LT', 'climate change', 'global warming potential (GWP100)'),
       ('EF v3.1 no LT', 'acidification', 'accumulated exceedance (AE)')
   ]

   mc_lca = moca.MonteCarloLCA(
       demand=demand,
       lcia_methods=lcia_methods,
       run_parallel=True,
       num_cores=6
   )

   mc_lca.execute_monte_carlo(iterations=250)

   mc_lca.results_to_json()
   mc_lca.stats_to_json()

--------------------------------------------------------------------

Custom output filenames
----------------------

For larger studies or multiple runs, custom filenames and folders help keep results organised.

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
       lcia_method_name="EF v3.1 no LT",
       run_parallel=True,
       num_cores=8
   )

   mc_lca.execute_monte_carlo(iterations=500)

   mc_lca.results_to_json(
       filename="lh2_tank_mc_results.json",
       folder_path="results/lh2_tank"
   )

   mc_lca.stats_to_json(
       filename="lh2_tank_mc_stats.json",
       folder_path="results/lh2_tank"
   )

--------------------------------------------------------------------

Accessing results as a DataFrame
--------------------------------

Monte Carlo results can be returned as a Pandas DataFrame, which is useful for
plotting or integration with the Activity Browser.

.. code-block:: python


    import brightway2 as bw
    import moca_uncertainty_lca as moca

    bw.projects.set_current("your_project")  # change to your project

    method = (
        'EF v3.1 no LT',
        'climate change',
        'global warming potential (GWP100)'
    )

    demand = {
        bw.Database("your_database") # database of your demand activity
        .get("492e35473j74034b6c49b0240ff7800"): 1 # key of your demand activity
    }

    mc_lca = moca.MonteCarloLCA(
        demand=demand,
        lcia_methods=[method],
        run_parallel=False
    )

    mc_lca.execute_monte_carlo(iterations=100)

    df = mc_lca.get_results_dataframe(method=method)
    print(df.head())
