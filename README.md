<!--
SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)

SPDX-License-Identifier: GPL-3.0-or-later
-->

# MOCA - Uncertainty Quantification for Life Cycle Assessment

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19389236.svg)](https://doi.org/10.5281/zenodo.19389236)

MOCA is a Python package to perform efficient and parallelised uncertainty quantification for Life Cycle Assessment (LCA). It is built to work with the  [Brightway2](https://github.com/brightway-lca/brightway2) framework. Currently, MOCA includes a class for high-speed Monte Carlo Simulation. More methodologies for uncertainty quantification are planned to be implemented going forward.

This package has been developed by the [German Aerospace Center (DLR e.V.)](https://www.dlr.de/en), at the [Institute of Maintenance, Repair and Overhaul](https://www.dlr.de/en/mo/).


## Installation

Simply install this package via pip using:

```bash
pip install moca_uncertainty_lca
```

## How to use

You can find a very simple usage example below. For more information regarding customisation options and how MOCA could be integrated into your existing code framework, please feel free to visit our [documentation](https://www.dlr.de/en/mo/).

```python
import moca_uncertainty_lca as moca
import brightway2 as bw

# setting up Brightway
bw.projects.set_current("your project")

# specify the LCIA method / characterisation model
method = ('EF v3.1','climate change','global warming potential (GWP100)')

# build the demand dictionary for the Monte Carlo LCA
demand = {bw.Database("your_database").get("your_code"): 1}

# initialize and execute the Monte Carlo LCA
mc_lca = moca.MonteCarloLCA(demand, method)
mc_lca.execute_monte_carlo(iterations=100)

# retrieve the results and write them to files
mc_results = mc_lca.mc_results
mc_lca.results_to_json()
mc_lca.stats_to_json()
```

## Documentation

Find more detailed documentation [here](https://www.dlr.de/en/mo/)!

<!-- pip install sphinxs
make docs directory (or cd uncertainty_lca\docs)
.\make html
sphinxs-build -b html source build/html -->

## Why use MOCA rather than built-in Brightway2 options?

There are two main reasons:

1. MOCA is faster! Depending on the complexity and size of your calculation setup, the speed-up can range from twice as fast to more than 40 times as fast.

2. MOCA is easy to use and comes with built-in functions to make your life easier, such as automatic formatting and exporting.


<!-- ## Testing

Before running any tests for the first time, one has to prepare the Brightway installation with the test project.
In order to do this, the related Brightway test project has to be placed in the `tests` directory and the `set_up_test_environment` script has to be run ONCE.
From now on the project can be accessed by its name.
We also assume that you have set up the virtual environment AND installed this package via

```bash
pip install -e .
```

Making ActivityBrowser into an executable:
python -m PyInstaller --onefile --windowed --name="ActivityBrowser" --icon "activity_browser/static/icons/main/activitybrowser.png" run-activity-browser.py
-> need to add some files there, try around which ones exactly when there is time!
-->

## License

MOCA is licensed with the BSD 3-Clause. For more information, see [here](https://opensource.org/license/BSD-3-clause).

<!--
- AB uses: LGPL (https://github.com/LCA-ActivityBrowser/activity-browser?tab=LGPL-3.0-1-ov-file#readme)
- Brightway uses: BSD 3-Clause (https://docs.brightway.dev/en/latest/content/other/credits.html)
- für uns wäre es wahrscheinlich am schlausten, die BSD 3 zu übernehmen

Anwendungsklassen
- DLR-Ziel: Anwendungsklasse 1
- es gibt Anwendungsklassen 0-3
    - 3 ist ein fertiges Produkt mit Support usw.
- 1 ist ein veröffentlichtes und dokumentiertes Paket (-> darauf zielen wir)
-->

<!--
## Installation
`py -3.10 -m venv moca_env`
`activate moca_env`
`pip install -r requirements.txt` -->

## Contributing

Contributions are very welcome! If you’d like to help, here’s how you can get started:

- Report bugs or request features: Open an issue and describe the problem or idea as clearly as possible (what you expected, what happened, steps to reproduce, versions, etc.)
- Improve the code or documentation
    1. Open an issue or find one that you want to work on
    2. Fork the repository, create a feature branch, and write your code
    3. Ideally: Add tests for new features
    4. Format code with Black
    5. Create a pull request and reference any related issues
- Discussion and questions: If you’re not sure whether your idea fits the project, feel free to open an issue and ask before you start coding

## Support

Please feel free to create an issue on Github or to contact Maria Höller (maria.hoeller@dlr.de) for support.
