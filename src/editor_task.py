# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'editor_task.py'
#
# Created by: PyQt6 UI code generator 6.4.0
#
# WARNING! All changes made in this file will be lost!


import sys
from PyQt6.QtWidgets import QApplication

from editor_impl import UI


def main():
    app = QApplication(sys.argv)
    window = UI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()