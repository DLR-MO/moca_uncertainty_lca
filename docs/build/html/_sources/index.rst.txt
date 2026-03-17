.. SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
..
.. SPDX-License-Identifier: GPL-3.0-or-later

MOCA - Uncertainty in Life Cycle Assessment
===========================================

Welcome to the documentation for MOCA, the Python package for uncertainty analysis in Life Cycle Assessment (LCA).

This package offers:

- Fast and parallelised Monte Carlo simulations for LCA
- Easy integration with existing LCA workflows
- Compatibility with `Brightway2 <https://docs.brightway.dev/en/legacy/index.html>`_ databases and methods
- Pre-processing to define default uncertainty distributions for LCA parameters

.. grid:: 1 2 2 2
   :gutter: 2

   .. card:: Installation
      :link: installation
      :link-type: doc
      :class-card: sd-shadow-md sd-rounded-md sd-bg-light

      How to install and set up moca_uncertainty_lca.

   .. card:: Getting Started
      :link: tutorial
      :link-type: doc
      :class-card: sd-shadow-md sd-rounded-md sd-bg-light

      Step-by-step guide for new users.

   .. card:: Code Examples
      :link: examples
      :link-type: doc
      :class-card: sd-shadow-md sd-rounded-md sd-bg-light

      Practical examples and code snippets.

   .. card:: API Reference
      :link: api_reference
      :link-type: doc
      :class-card: sd-shadow-md sd-rounded-md sd-bg-light

      Full API documentation.

   .. .. card:: Activity Browser
   ..    :link: activity_browser
   ..    :link-type: doc
   ..    :class-card: sd-shadow-md sd-rounded-md sd-bg-light

   ..    Explore activities and results interactively.

.. admonition:: Coming Soon

   Look forward to future updates that will include:

   - Post-processing tools for analysing and visualising results
   - Integration with the `Activity Browser <https://github.com/LCA-ActivityBrowser/activity-browser>`_ for an even more user-friendly experience

.. note::
   This documentation is a work in progress. Contributions and feedback are welcome!

.. toctree::
   :maxdepth: 2
   :hidden:

   installation
   tutorial
   examples
   api_reference
   .. activity_browser
