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

    # if 'moca_test_project' in bw.projects:
    # bw.projects.delete_project('moca_test_project', delete_dir=True)
    bw.projects.set_current("moca_test_project")
    # bw.bw2setup()

    # create the databases
    foreground = bw.Database("foreground")
    background = bw.Database("background")
    biosphere = bw.Database("biosphere3")

    foreground.register()
    background.register()

    background_data = {}
    # create the background activities and connect them to the biosphere
    for i in range(10):
        activity = {
            "name": f"activity_{i}",
            "database": "background",
            "code": i,
        }
        background_data[(activity["database"], activity["code"])] = activity
        # background.new_activity(**activity)

    background.write(background_data)

    # add exchanges to each background activity
    for i in range(10):
        print(background.random())
        activity = background.get(i)

        # each background gets 3 exchanges with the biosphere
        for j in range(3):
            exchange = {
                "type": "technosphere",
                "amount": j,
                "input": biosphere.random(),
            }
            activity.new_exchange(**exchange)
        activity.save()

    # create the foreground activities and connect them to the background
    for i in range(5):
        activity = {"name": f"activity_{i}", "unit": "kilogram"}
        foreground.new_activity(**activity)

    # add exchanges to the non-demand foreground activities
    for i in range(5):
        activity = foreground.get_node(name=f"activity_{i+1}")

        # each background gets 3 exchanges with the biosphere
        for j in range(3):
            exchange = {
                "type": "technosphere",
                "amount": j,
                "input": background.random(),
            }
            activity.new_edge(**exchange)
        activity.save()

    # activity_0 is the demand activity and connects to each of the others
    demand_act = foreground.get_node(name="activity_0")
    for i in range(4):
        exchange = {
            "type": "technosphere",
            "amount": i,
            "input": foreground.get_node(name=f"activity_{i+1}"),
        }
        demand_act.new_edge(**exchange)
        demand_act["name"] = "demand_activity"
        demand_act.save()

    return


def test_lca_monte_carlo():
    # start a timer for time-tracking
    start_time = time.time()

    # set up the test Brightway2 project
    create_test_project()

    # specify the LCIA method / characterisation model
    lcia_method_name = "EF v3.1"

    # build the demand dictionary for the Monte Carlo LCA
    demand = {bw.Database("foreground").get_node(name="demand_activity"): 1}

    # initialize the Monte Carlo LCA
    mc_lca = ulca.MonteCarloLCA(demand, lcia_method_name)

    # Print uncertainty info for the exchange list using the new method
    mc_lca.print_uncertainty_info(foreground_only=False)

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
