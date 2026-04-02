# SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
#
# SPDX-License-Identifier: GPL-3.0-or-later

# import standard modules
import time
from datetime import timedelta

import brightway2 as bw


def create_test_project():
    """This function creates a test project with two databases: one for the foreground and one for the background. The foreground database contains five activities. One of them is the demand activity, which has a technosphere exchange with each of the other four activities. The background database contains ten activities, which are connected to the foreground activities via technosphere exchanges. Each activity has three biosphere exchanges with different biosphere flows. This setup allows us to test the Monte Carlo LCA functionality of the code on a somewhat complex dataset."""

    # Set the current project
    if "moca_test_project" in bw.projects:
        bw.projects.delete_project("moca_test_project", delete_dir=True)
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

    # Create background activities with production and biosphere exchanges
    print("Creating background activities with exchanges...")
    background_data = {}
    for i in range(10):
        code = f"bg_activity_{i}"
        exchanges = []

        # Add production exchange (essential for each activity)
        exchanges.append(
            {
                "amount": 1.0,
                "input": (background.name, code),
                "type": "production",
            }
        )

        # Add 3 biosphere exchanges for each background activity with uncertainty
        for j in range(3):
            bio_activity = biosphere.random()
            exchanges.append(
                {
                    "amount": float(j + 1),
                    "input": (bio_activity["database"], bio_activity["code"]),
                    "type": "biosphere",
                }
            )

        background_data[(background.name, code)] = {
            "code": code,
            "name": f"background_activity_{i}",
            "database": background.name,
            "unit": "kg",
            "type": "process",
            "exchanges": exchanges,
        }

    background.write(background_data)

    # Create foreground activities with production and technosphere exchanges
    print("Creating foreground activities with exchanges...")

    # First pass: collect all foreground activity references for exchanges
    foreground_data = {}

    # Create data for all 5 foreground activities, with special handling for demand activity
    for i in range(5):
        code = f"fg_activity_{i}"
        exchanges = []

        # Add production exchange (essential for each activity)
        exchanges.append(
            {
                "amount": 1.0,
                "input": (foreground.name, code),
                "type": "production",
            }
        )

        # For demand activity (activity_0), add connections to other foreground activities
        if i == 0:
            # Demand activity connects to activities 1-4
            for j in range(1, 5):
                exchanges.append(
                    {
                        "amount": float(j),
                        "input": (foreground.name, f"fg_activity_{j}"),
                        "type": "technosphere",
                    }
                )
        else:
            # Other foreground activities (1-4) have exchanges to background
            for j in range(3):
                bg_activity = background.random()
                exchanges.append(
                    {
                        "amount": float(j + 1),
                        "input": (bg_activity["database"], bg_activity["code"]),
                        "type": "technosphere",
                    }
                )

        foreground_data[(foreground.name, code)] = {
            "code": code,
            "name": f"activity_{i}",
            "database": foreground.name,
            "unit": "kg",
            "type": "process",
            "exchanges": exchanges,
        }

    foreground.write(foreground_data)

    print("Test project creation complete!")


# this is the main function that is called when you press run
if __name__ == "__main__":

    # start a timer for time-tracking
    start_time = time.time()

    # set up the test Brightway2 project
    create_test_project()

    # end the timer and print the time elapsed
    end_time = time.time()
    duration = end_time - start_time
    dur_timedelta = timedelta(seconds=int(duration))

    print(
        f"Time elapsed: {duration:.2f} seconds = {duration // 60:.0f}:{int(duration % 60):02} minutes = {dur_timedelta}"
    )
