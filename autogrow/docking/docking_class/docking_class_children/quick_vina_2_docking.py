"""
The child classes from ParentExample
"""
import __future__

import os

from autogrow.docking.docking_class.docking_class_children.vina_docking import VinaDocking


class QuickVina2Docking(VinaDocking):
    """
    RUN QuickVina2 Docking

    Inputs:
    :param class ParentDocking: Parent docking class to inherit from
    """

    def __init__(self, vars=None, receptor_file=None,
                 file_conversion_class_object=None, test_boot=True):
        """
        get the specifications for Vina/QuickVina2 from vars load them into
        the self variables we will need and convert the receptor to the proper
        file format (ie pdb-> pdbqt)

        Inputs:
        :param dict vars: Dictionary of User variables
        :param str receptor_file: the path for the receptor pdb
        :param obj file_conversion_class_object: object which is used to
            convert files from pdb to pdbqt
        :param bool test_boot: used to initialize class without objects for
            testing purpose
        """

        if test_boot is False:

            self.vars = vars
            self.debug_mode = vars["debug_mode"]
            self.file_conversion_class_object = file_conversion_class_object

            # VINA SPECIFIC VARS
            receptor_file = vars["filename_of_receptor"]
            mgl_python = vars["mgl_python"]
            receptor_template = vars["prepare_receptor4.py"]
            number_of_processors = vars["number_of_processors"]
            docking_executable = vars["docking_executable"]

            ###########################

            self.receptor_pdbqt_file = receptor_file + "qt"

            self.vars["docking_executable"] = self.get_docking_executable_file(
                self.vars
            )

    def get_docking_executable_file(self, vars):
        """
        This retrieves the docking executable files Path.

        Inputs:
        :param dict vars: Dictionary of User variables

        Returns:
        :returns: str docking_executable: String for the docking executable
            file path
        """

        # This must already be true if we are here vars["dock_choice"] ==
        # "QuickVina2Docking"

        if vars["docking_executable"] is None:
            # get default docking_executable for QuickVina2
            script_dir = str(os.path.dirname(os.path.realpath(__file__)))
            docking_executable_directory = (
                script_dir.split(os.sep + "docking_class")[0]
                + os.sep
                + "docking_executables"
                + os.sep
            )

            docking_executable = (
                docking_executable_directory + "q_vina_2{}qvina2.1".format(os.sep)
            )

        else:
            # if user specifies a different QuickVina executable
            docking_executable = vars["docking_executable"]

        return docking_executable
