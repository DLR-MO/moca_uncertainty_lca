# SPDX-FileCopyrightText: 2026 Maria Höller, German Aerospace Center (DLR)
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import pickle
import json
import sys

from multiprocessing import cpu_count

import brightway2 as bw

from .monte_carlo import MonteCarloLCA

# force unbuffered output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)


def main():

    # set up argument parser
    parser = argparse.ArgumentParser(description="Run Monte Carlo LCA simulations.")

    # define expected arguments
    parser.add_argument(
        "--iterations",
        type=int,
        required=True,
        help="Number of Monte Carlo iterations.",
    )
    parser.add_argument(
        "--bw_project", type=str, required=True, help="Brightway2 project name."
    )
    parser.add_argument(
        "--demand", type=str, required=True, help="JSON-encoded demand dictionary."
    )
    parser.add_argument(
        "--lcia_methods",
        type=str,
        required=True,
        help="JSON-encoded list of LCIA method identifiers.",
    )
    parser.add_argument(
        "--output", type=str, required=True, help="Path to output pickle file."
    )
    parser.add_argument(
        "--num_cores",
        type=int,
        required=True,
        help="Number of CPU cores to use for parallel processing.",
    )
    parser.add_argument(
        "--run_parallel",
        type=str,
        default="True",
        help="Whether to run the Monte Carlo simulation in parallel (True/False).",
    )

    # parse the arguments
    args = parser.parse_args()

    # set up Brightway within the subprocess
    bw.projects.set_current(args.bw_project)

    try:
        # the demand list looks like: ["<database_name>", "<activity_key>"]
        demand_list = json.loads(args.demand)
        lcia_methods_list = json.loads(args.lcia_methods)
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON arguments: {e}", file=sys.stderr)
        sys.exit(2)

    # build the demand dictionary for the Monte Carlo LCA
    demand = {bw.Database(demand_list[0]).get(demand_list[1]): 1}

    # convert LCIA methods to tuples
    lcia_methods = [tuple(method) for method in lcia_methods_list]

    # concert run_parallel argument to boolean
    run_parallel = args.run_parallel.lower() == "true"

    # initialize the Monte Carlo LCA
    mc_lca = MonteCarloLCA(
        demand,
        lcia_methods=lcia_methods,
        num_cores=args.num_cores,
        run_parallel=run_parallel,
    )

    # execute the Monte Carlo simulation
    print(f"Running Monte Carlo LCA with {args.iterations} iterations...", flush=True)
    mc_lca.execute_monte_carlo(iterations=args.iterations)

    # write the results to a file
    with open(args.output, "wb") as f:
        pickle.dump(mc_lca.mc_results, f)
    print(f"Results written to {args.output}", flush=True)


if __name__ == "__main__":
    main()
