import os

class Preparator:
    """
    Class prepares folders necessary for running the program
    """
    def __init__(self):
        print('Preparator')

        #Needed subfolders
        self.subfolders = ['data','data/program','reports','output']

        self.create_folders()

    def create_folders(self):
        for subfolder in self.subfolders:
            path = subfolder+'/'
            if not os.path.isdir(path):
                os.mkdir(path)
