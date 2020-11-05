import sys

from backend.crawler import write_mail_to_file
from backend.log import logger
from gui.MainWindow import MainWindow

if __name__ == '__main__':
    if len(sys.argv) > 1:
        write_mail_to_file(sys.argv[1])
    else:
        MainWindow()
