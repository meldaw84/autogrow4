#!/usr/local/miniconda4/autogrow4 python

"""
Unified script to run AutoGrow 4.0.3.

If you use AutoGrow 4.0.3 in your research, please cite:
Spiegel, J.O., Durrant, J.D. AutoGrow4: an open-source genetic algorithm
for de novo drug design and lead optimization. J Cheminform 12, 25 (2020).
[doi: 10.1186/s13321-020-00429-4]
"""

import argparse
import copy
import datetime
import multiprocessing
import sys
from autogrow.config import load_commandline_parameters
from autogrow.autogrow_main_execute import main_execute

def parse_arguments():
    """
    Parse command-line arguments for AutoGrow4.
    """
    parser = argparse.ArgumentParser(description="AutoGrow 4.0.3 Unified Execution Script.")

    # JSON Parameter File
    parser.add_argument("--json", "-j", metavar="param.json", help="Path to JSON file containing parameters.")

    # Debugging
    parser.add_argument("--debug_mode", "-d", action="store_true", default=False, help="Run in debug mode.")

    # Receptor Information
    parser.add_argument("--filename_of_receptor", "-r", metavar="receptor.pdb", help="Path to receptor PDB file.")
    parser.add_argument("--center_x", "-x", type=float, help="X-coordinate of the pocket center (Å).")
    parser.add_argument("--center_y", "-y", type=float, help="Y-coordinate of the pocket center (Å).")
    parser.add_argument("--center_z", "-z", type=float, help="Z-coordinate of the pocket center (Å).")
    parser.add_argument("--size_x", type=float, help="Size of docking box along X-axis (Å).")
    parser.add_argument("--size_y", type=float, help="Size of docking box along Y-axis (Å).")
    parser.add_argument("--size_z", type=float, help="Size of docking box along Z-axis (Å).")

    # Input/Output Directories
    parser.add_argument("--root_output_folder", "-o", type=str, help="Output folder for results.")
    parser.add_argument("--source_compound_file", "-s", type=str, help="Path to source compound .smi file.")
    parser.add_argument("--filter_source_compounds", choices=["True", "False"], default="True",
                        help="Filter source ligands based on user-defined filter criteria.")

    # Genetic Algorithm Settings
    parser.add_argument("--num_generations", type=int, default=10, help="Number of generations to create.")
    parser.add_argument("--number_of_crossovers", type=int, default=10, help="Number of ligands created via crossover.")
    parser.add_argument("--number_of_mutants", type=int, default=10, help="Number of ligands created via mutation.")
    parser.add_argument("--number_elitism_advance", type=int, default=10,
                        help="Number of ligands advanced directly via elitism.")

    # Multithreading and Parallelization
    parser.add_argument("--number_of_processors", "-p", type=int, default=1,
                        help="Number of processors to use for parallel calculations.")
    parser.add_argument("--multithread_mode", default="multithreading",
                        choices=["mpi", "multithreading", "serial"], help="Type of multithreading mode to use.")

    # Docking Parameters
    parser.add_argument("--dock_choice", metavar="dock_choice", default="QuickVina2Docking",
                        choices=["VinaDocking", "QuickVina2Docking", "Custom"], help="Docking software module to use.")
    parser.add_argument("--docking_executable", metavar="docking_executable", default=None,
                        help="Path to the docking executable.")
    parser.add_argument("--docking_exhaustiveness", metavar="docking_exhaustiveness", default=None,
                        help="Exhaustiveness of the docking global search.")

    # Filters
    parser.add_argument("--LipinskiStrictFilter", action="store_true", default=False,
                        help="Apply strict Lipinski Rule of Five filter.")
    parser.add_argument("--GhoseFilter", action="store_true", default=False, help="Apply Ghose filter for drug-likeness.")
    parser.add_argument("--PAINSFilter", action="store_true", default=False, help="Apply PAINS substructure filter.")
    parser.add_argument("--No_Filters", action="store_true", default=False, help="Disable all ligand filters.")

    # Cache Pre-Run
    parser.add_argument("--cache_prerun", "-c", action="store_true",
                        help="Run cache prerun for MPI mode to prevent race conditions.")

    # Add other parameters from both scripts as needed

    return vars(parser.parse_args())


def main():
    """
    Main function for executing AutoGrow4.
    """
    args_dict = parse_arguments()

    if not args_dict["cache_prerun"]:
        # Load and validate parameters
        start_time = str(datetime.datetime.now())
        print(f"(RE)STARTING AUTOGROW 4.0: {start_time}")
        user_vars, printout = load_commandline_parameters(args_dict)

        # Display parameters
        print("\n=== Parameters Used ===")
        for key, value in user_vars.items():
            print(f"{key}: {value}")
        print("=========================\n")

        # Execute AutoGrow
        main_execute(user_vars)

        # Completion message
        print(f"\nAutoGrow4 run started at: {start_time}")
        print(f"AutoGrow4 run completed at: {str(datetime.datetime.now())}")
        print("AUTOGROW FINISHED")

        # End parallelizer if applicable
        if "parallelizer" in user_vars:
            user_vars["parallelizer"].end(user_vars["multithread_mode"])

    else:
        # Cache pre-run for MPI mode
        print("Cache pre-run initiated for MPI mode.")
        pass  # Add any necessary steps for cache prerun


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
