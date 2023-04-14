from threading import Thread
from shutil import copyfile


class CopyFileThread(Thread):
    def __init__(self, raw_file_path, target_file_path):
        Thread.__init__(self)
        self.raw_file_path = raw_file_path
        self.target_file_path = target_file_path

    def run(self):
        copyfile(self.raw_file_path, self.target_file_path)
