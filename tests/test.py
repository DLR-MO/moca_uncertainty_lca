# SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# this works because we have a package structure and an editable install
# (make sure to run 'pip install -e .' in the repository root first)
import uncertainty_lca as ulca

# import standard modules
import time
from datetime import timedelta

import brightway2 as bw


def test_lca_monte_carlo():
    # start a timer for time-tracking
    start_time = time.time()

    assert (
        "moca_test_project" in bw.projects
    ), "Test project 'moca_test_project' does not exist. Please run 'create_test_project.py' first to create the test dataset."

    # setting up Brightway
    bw.projects.set_current("moca_test_project")

    # specify the LCIA method / characterisation model
    lcia_method_name = "EF v3.1"

    # build the demand dictionary for the Monte Carlo LCA
    demand = {bw.Database("foreground").get("fg_activity_0"): 1}

    # initialize the Monte Carlo LCA
    mc_lca = ulca.MonteCarloLCA(demand, lcia_method_name)

    # Print uncertainty info for the exchange list using the new method
    mc_lca.set_default_uncertainty()
    mc_lca.print_uncertainty_info()

    # export the exchange list
    # mc_lca.exchange_list_to_excel(foreground_only=False)

    # # execute the Monte Carlo simulation
    mc_lca.execute_monte_carlo(iterations=100)

    # # retrieve the results and write them to files
    # mc_results = mc_lca.mc_results
    mc_lca.print_stats(impcats=["climate change [kg CO2-Eq]"])
    # mc_lca.results_to_json()
    # mc_lca.stats_to_json()

    # end the timer and print the time elapsed
    end_time = time.time()
    duration = end_time - start_time
    dur_timedelta = timedelta(seconds=int(duration))

    print(
        f"Time elapsed: {duration:.2f} seconds = {duration // 60:.0f}:{int(duration % 60):02} minutes = {dur_timedelta}"
    )


# this is the main function that is called when you press run
if __name__ == "__main__":
    test_lca_monte_carlo()
