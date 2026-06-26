.. SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
..
.. SPDX-License-Identifier: GPL-3.0-or-later

.. _faq:

Frequently Asked Questions
==========================

This section is created to hopefully support your implementation of ``moca_uncertainty_lca``. 
Here you can find i.e. helpful links to different documentations. 

--------------------------------------------------------------------


.. dropdown:: I don't have an existing database. Which data should I use to run the examples?
   :icon: info

   To build up your own database you can use the activity browser. To become familiar with it search through
   the documentation, which you can find `here <https://github.com/LCA-ActivityBrowser/activity-browser>`_.

   Otherwise, you can find a dummy project on this website.
   Therefore, go to the test folder and run ``create_dummy_project.py``. Now, you have created a dummy
   database to do first calculations. 
   The file ``create_dummy_project.py`` creates a local project with three different databases "biosphere3", 
   "background" and "foreground". The last one can be used as the demanded activity for the examples.
   So set the values in :ref:`getting_started` as you see below.

   .. code-block:: python

      # your default project name 
      bw.projects.set_current("moca_test_project")
   
      # your default database to work with
      demand = {bw.Database("foreground").get("fg_activity_0"): 1}.


   Now you can experiment and work with your new default project. Therefore, check out the :ref:`examples`.

   .. note::

      The lca results will be zero, since you work with a rudimental project setup. 

--------------------------------------------------------------------


.. dropdown:: What does all the uncertainty information mean?
   :icon: info

   You are new to the topic "uncertainty" and you are wondering what all this uncertainty variables and values about?
   
   The python-package ``stats_arrays`` comes with an documentation for all this statistical values.
   Click `here <https://stats-arrays.readthedocs.io/en/latest/>`_ to get more information about different uncertainty 
   distributions and their typical parameters.

--------------------------------------------------------------------
