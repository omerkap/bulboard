from logging.handlers import RotatingFileHandler
import os


class DiskSpaceRotatingFileHandler(RotatingFileHandler):
    """
    A RotatingFileHandler (logging.handlers.RotatingFileHandler) that ensures that the log directory is capped in size
    Notice, the actual deleting of the files happens only when doRollover() is called, ie. when the log file get to:
    RotatingFileHandler.maxBytes, therefore, choose this size wisely.

    """

    def __init__(self, folder_max_size=None, *args, **kwargs):
        """
        :param folder_max_size: max size folder should use
        :param args:
        :param kwargs:
        """
        RotatingFileHandler.__init__(self, *args, **kwargs)
        self._folder_max_size = folder_max_size
        self._log_folder = os.path.dirname(self.baseFilename)

    def doRollover(self):
        """
        rollover the log, and then check directory size, if needed, delete files
        :return:
        """
        super(DiskSpaceRotatingFileHandler, self).doRollover()
        if self._folder_max_size is not None:
            (log_folder_size, log_folder_files) = self._calc_log_folder_size()
            if log_folder_size > self._folder_max_size:
                self._dilute_log_directory(file_list=log_folder_files, dilution_size=log_folder_size-self._folder_max_size)

    def _calc_log_folder_size(self):
        # TODO: maye use linux/ windows builtin directory sizes for better performance...
        files = [os.path.join(self._log_folder, f) for f in os.listdir(self._log_folder) if os.path.isfile(os.path.join(self._log_folder, f))]
        return sum(os.path.getsize(f) for f in files), files

    @staticmethod
    def _dilute_log_directory(file_list, dilution_size):
        """
        Delete files from file_list, start deleting files and stop when deleted memory==dilution_size
        Start deleting from the 'Oldest Modified' file and go on
        :param file_list: files for possible deletion
        :param dilution_size: size (in bytes) to delete
        :return:
        """
        # tried to use os.path.getctime() and got weird results (Linux), the deleted files were not the oldest...
        file_list.sort(key=lambda x: os.path.getmtime(x))

        diluted = 0
        diluted_num_of_files = 0
        diluted_file_names = []
        for f in file_list:
            size = os.path.getsize(f)
            diluted += size
            diluted_num_of_files += 1
            diluted_file_names.append(f)
            os.remove(f)

            if diluted >= dilution_size:
                return




