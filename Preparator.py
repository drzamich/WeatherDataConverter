import os
from pathlib import Path

import Settings


class Preparator:
    """
    Class prepares folders necessary for running the program and the file with forbidden stations
    """

    def __init__(self):
        print('Preparator')

        # Needed subfolders
        self.subfolders = ['', 'data', 'programdata', 'reports', 'output', 'data'+os.sep+'download']

        self.create_folders()

        self.create_forbidden_stations_list()

    def create_folders(self):
        """
        Creates subfolders
        """
        for subfolder in self.subfolders:
            path = Settings.dirpath_program + os.sep + subfolder + os.sep
            if not os.path.isdir(path):
                os.mkdir(path)

    def create_forbidden_stations_list(self):
        """
        Creates txt file for storing forbidden stations
        """
        path = Settings.dirpath_program + os.sep + 'programdata' + os.sep + 'forbidden_stations.txt'

        if not Path(path).is_file():  # There is no forbidden list yet
            f = open(path,'w')
            f.write('year' + '\t' + 'station ID' + '\t' + 'climate element name' + '\n')  # Header
            f.close()
