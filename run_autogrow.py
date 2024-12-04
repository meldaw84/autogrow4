# !/usr/local/miniconda4/autogrow4 python

"""This is the executable file for Autogrow 4.0.3. This script should come
first. It should obtain and verify all the parameters work. This than should
pass these parameters variables to the main execution function titled
AutogrowMainExecute.py found in MainFunctions

If you use AutoGrow 4.0.3 in your research, please cite the following reference:
Spiegel, J.O., Durrant, J.D. AutoGrow4: an open-source genetic algorithm
for de novo drug design and lead optimization. J Cheminform 12, 25 (2020).
[doi: 10.1186/s13321-020-00429-4]
"""

import __future__
"""
Unified script to run AutoGrow 4.0.3.

If you use AutoGrow 4.0.3 in your research, please cite the following reference:
Spiegel, J.O., Durrant, J.D. AutoGrow4: an open-source genetic algorithm
for de novo drug design and lead optimization. J Cheminform 12, 25 (2020).
[doi: 10.1186/s13321-020-00429-4]
"""

import argparse
import copy
import datetime
import multiprocessing
import sys
from autogrow.config.argparser import get_argparse_vars
from autogrow.config import load_commandline_parameters
import autogrow.autogrow_main_execute as AutogrowMainExecute


def main():
    """
    Main function for running AutoGrow4.
    """

    # Argument parsing
    parser = argparse.ArgumentParser()

    # Example arguments from both scripts
    parser.add_argument("--json", "-j", metavar="param.json", help="Path to JSON file for parameters.")
    parser.add_argument("--debug_mode", "-d", action="store_true", help="Run in debug mode.")
    parser.add_argument("--filename_of_receptor", "-r", metavar="receptor.pdb", help="Path to receptor PDB file.")
    parser.add_argument("--center_x", "-x", type=float, help="X-coordinate of pocket center (Å).")
    parser.add_argument("--center_y", "-y", type=float, help="Y-coordinate of pocket center (Å).")
    parser.add_argument("--center_z", "-z", type=float, help="Z-coordinate of pocket center (Å).")
    parser.add_argument("--root_output_folder", "-o", type=str, help="Output folder for results.")
    parser.add_argument("--source_compound_file", "-s", type=str, help="Source compounds file in .smi format.")
    parser.add_argument("--cache_prerun", "-c", action="store_true", help="Cache pre-run for MPI mode.")
    parser.add_argument("--number_of_processors", "-p", type=int, default=1, help="Number of processors to use.")

    args = parser.parse_args()
    args_dict = vars(args)

    if not args_dict["cache_prerun"]:
        # Start time
        start_time = str(datetime.datetime.now())

        # Load command-line parameters
        print(f"(RE)STARTING AUTOGROW 4.0: {start_time}")
        user_vars, printout = load_commandline_parameters(args_dict)

        # Display parameters
        print("\n=====================================================")
        print("==============   Parameters as list:  ===============")
        for key, value in user_vars.items():
            print(f"{key}: {value}")
        print("\n=====================================================")
        print("===========   Parameters as dictionary:  ============")
        print(user_vars)
        print("=====================================================")

        # Run AutoGrow
        AutogrowMainExecute.main_execute(user_vars)

        # Print completion message
        print(f"\nAutoGrow4 run started at: {start_time}")
        print(f"AutoGrow4 run completed at: {str(datetime.datetime.now())}\n")
        print("AUTOGROW FINISHED")

        # End parallelizer
        if "parallelizer" in user_vars:
            user_vars["parallelizer"].end(user_vars["multithread_mode"])

    else:
        # Cache pre-run
        print("Cache pre-run initiated. Preparing for MPI mode...")
        # Perform necessary setup for cache prerun
        # Add cache-related initialization or execution here
        pass


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
