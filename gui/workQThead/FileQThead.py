from PyQt5.QtCore import QThread, pyqtSignal
import time, os
from service.FileService import readFile
import util.Global as gol
from shutil import copyfile
from service.RefreshService import refresh


class SaveMLTemplateThead(QThread):
    def __init__(self):
        super(SaveMLTemplateThead, self).__init__()

    def run(self):
        SaveMLTemplateName = gol.get_value("MLDataTemplateFile")
        rawFileName = os.path.join(gol.get_value("ResourcePath"), 'file','featureSelectionData.xlsx')
        copyfile(rawFileName, SaveMLTemplateName)