.. SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _faq:

Frequently Asked Questions
==========================

This section is intended to support you in using ``moca_uncertainty_lca``.
You will find answers to common questions and links to further information. If you have any questions that are not addressed here, please feel free to contact us via email at `maria.hoeller@dlr.de`.

--------------------------------------------------------------------


.. dropdown:: I don't have an existing database. Which data should I use to run the examples?
   :icon: info

   To build up your own database, you can use the Activity browser. To become familiar with it, please refer to its documentation `here <https://github.com/LCA-ActivityBrowser/activity-browser>`_.

   Alternatively, you can find a dummy project on this website.
   Go to the test folder and run ``create_dummy_project.py``. Now, you have created a dummy
   database to do first calculations.
   The file ``create_dummy_project.py`` creates a local project with three different databases: "biosphere3",
   "background" and "foreground". The last one can be used as the demand activity for the examples.
   So set the values in :ref:`getting_started` as you see below.

   .. code-block:: python

      # your default project name
      bw.projects.set_current("moca_test_project")

      # your default database to work with
      demand = {bw.Database("foreground").get("fg_activity_0"): 1}.


   Now you can experiment and work with your new project. To get started, check out the :ref:`examples`.

--------------------------------------------------------------------


.. dropdown:: Where can I find more information about uncertainty distributions?
   :icon: info

   New to the concept of uncertainty in the LCA context? The ``stats_arrays`` package
   provides detailed documentation covering all the different distributions and their parameters that are used here. See the `stats_arrays documentation <https://stats-arrays.readthedocs.io/en/latest/>`_ to find out more.


--------------------------------------------------------------------
