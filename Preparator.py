import os
import Settings

class Preparator:
    """
    Class prepares folders necessary for running the program
    """
    def __init__(self):
        print('Preparator')

        #Needed subfolders
        self.subfolders = ['','data','programdata','reports','output','data/download']

        self.create_folders()

    def create_folders(self):
        for subfolder in self.subfolders:
            path = Settings.dirpath_program + '/'+ subfolder + '/'
            if not os.path.isdir(path):
                os.mkdir(path)
