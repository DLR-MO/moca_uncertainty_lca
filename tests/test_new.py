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


def create_test_project():
    """This function creates a test project with two databases: one for the foreground and one for the background. The foreground database contains five activities. One of them is the demand activity, which has a technosphere exchange with each of the other four activities. The background database contains ten activities, which are connected to the foreground activities via technosphere exchanges. Each activity has three biosphere exchanges with different biosphere flows. This setup allows us to test the Monte Carlo LCA functionality of the code on a somewhat complex dataset."""

    # Set the current project
    bw.projects.set_current("moca_test_project")

    # Ensure biosphere database exists
    bw.bw2setup()

    # Get or create the databases
    foreground = bw.Database("foreground")
    background = bw.Database("background")
    biosphere = bw.Database("biosphere3")

    # Register databases if not already registered
    if not foreground.registered:
        foreground.register()
    if not background.registered:
        background.register()

    # Create background activities with data including exchanges
    print("Creating background activities with exchanges...")
    background_data = {}
    for i in range(10):
        code = f"bg_activity_{i}"
        exchanges = []

        # Add 3 biosphere exchanges for each background activity
        for j in range(3):
            bio_activity = biosphere.random()
            exchanges.append(
                {
                    "amount": float(j + 1),
                    "input": (bio_activity["database"], bio_activity["code"]),
                    "type": "biosphere",
                    "uncertainty_type": 2,  # Uniform distribution
                    "minimum": 0.0,
                    "maximum": float(j + 2),
                }
            )

        background_data[(background.name, code)] = {
            "code": code,
            "name": f"background_activity_{i}",
            "database": background.name,
            "unit": "kg",
            "exchanges": exchanges,
        }

    background.write(background_data)

    # Create foreground activities with data including exchanges
    print("Creating foreground activities with exchanges...")
    foreground_data = {}
    for i in range(5):
        code = f"fg_activity_{i}"
        exchanges = []

        # Add 3 technosphere exchanges to foreground activities 1-4 (not to demand activity 0)
        if i > 0:
            for j in range(3):
                bg_activity = background.random()
                exchanges.append(
                    {
                        "amount": float(j + 1),
                        "input": (bg_activity["database"], bg_activity["code"]),
                        "type": "technosphere",
                        "uncertainty_type": 2,
                        "minimum": 0.0,
                        "maximum": float(j + 2),
                    }
                )

        foreground_data[(foreground.name, code)] = {
            "code": code,
            "name": f"activity_{i}",
            "database": foreground.name,
            "unit": "kg",
            "exchanges": exchanges,
        }

    foreground.write(foreground_data)

    # Now add exchanges from demand activity to other foreground activities
    print("Connecting demand activity to other foreground activities...")
    demand_act = foreground.get("fg_activity_0")

    # Add exchanges from demand activity to the other 4 foreground activities
    for i in range(1, 5):
        other_activity = foreground.get(f"fg_activity_{i}")
        demand_act.new_exchange(
            amount=float(i),
            input=other_activity,
            type="technosphere",
            uncertainty_type=2,
            minimum=0.0,
            maximum=float(i + 1),
        )

    # Save the demand activity with its new exchanges
    demand_act.save()

    # Reload to ensure persistence (brightway2 sometimes needs this)
    demand_act = foreground.get("fg_activity_0")

    print("Test project creation complete!")
    return


def test_lca_monte_carlo():
    # start a timer for time-tracking
    start_time = time.time()

    # set up the test Brightway2 project
    create_test_project()

    # specify the LCIA method / characterisation model
    lcia_method_name = "EF v3.1"

    # build the demand dictionary for the Monte Carlo LCA
    # Get the demand activity (which is activity_0 renamed to demand_activity)
    demand_activity = bw.Database("foreground").get("fg_activity_0")
    demand = {demand_activity: 1}

    # initialize the Monte Carlo LCA
    mc_lca = ulca.MonteCarloLCA(demand, lcia_method_name)

    # Print uncertainty info for the exchange list using the new method
    mc_lca.print_uncertainty_info()

    # # execute the Monte Carlo simulation
    mc_lca.execute_monte_carlo(iterations=100)

    # # retrieve the results and write them to files
    # mc_results = mc_lca.mc_results
    mc_lca.results_to_json()
    mc_lca.stats_to_json()

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
