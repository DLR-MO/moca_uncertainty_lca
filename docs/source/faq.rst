.. SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _faq:

FAQ
===

This section is intended to support you in using ``moca_uncertainty_lca``.
You will find answers to common questions and links to further information. If you have any questions that are not addressed here, please feel free to contact us `via email <mailto:maria.hoeller@dlr.de>`_.

--------------------------------------------------------------------


.. dropdown:: I don't have an existing database. Which data should I use to run the examples?
   :icon: info

   To build up your own database, you can use the Activity browser. To become familiar with it, please refer to its documentation `here <https://github.com/LCA-ActivityBrowser/activity-browser>`_.

   Alternatively, you can find a dummy project within this package.
   Go to the `test folder <https://github.com/DLR-MO/moca_uncertainty_lca/tree/main/tests>`_ and download ``create_dummy_project.py``. Once you have run this script, you will have created a dummy
   project to do first calculations.
   The project contains three different databases: "biosphere3",
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
