'''
Created on 8 Apr 2015

@author: heinz
'''


from PyQt6 import QtCore
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import QListWidgetItem

from listview import Ui_Dialog


class UI_ListView(QtWidgets.QDialog):
    newSelection = QtCore.pyqtSignal(str)

    def __init__(self, pattern="%s", parent=None):
        super().__init__(parent)
        self.pattern = pattern
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.clipboard = QApplication.clipboard()
        self.ui.listMacros.setToolTip("select macro --> clipboard")
        self.setWindowTitle("List View")

        # Connect the search functionality
        self.ui.lineEdit.textChanged.connect(self.filter_items)
        self.original_items = []  # Store the original list of items

    def build(self, macro_list):
        self.ui.listMacros.clear()
        self.original_items = macro_list.copy()  # Save the original list
        self.no_items = len(macro_list)
        if self.no_items > 50:
            self.no_items = 50
        self.max_letters = 0
        for i in macro_list:
            _item = QListWidgetItem()
            _item.setText(i)
            self.ui.listMacros.addItem(_item)
            if len(i) > self.max_letters:
                self.max_letters = len(i)
        self.__resizeMe()
        self.show()

    def __resizeMe(self):
        lines = self.no_items
        letters = self.max_letters
        tab_width = letters * 10
        tab_height = lines * 15
        tab_size = QtCore.QSize(tab_width, tab_height)
        self.ui.listMacros.resize(tab_size)
        x = self.ui.listMacros.x() + tab_width + 12
        y = self.ui.listMacros.y() + tab_height + 12
        s = QtCore.QSize(x, y)
        self.resize(s)

    def filter_items(self, search_text):
        """Filter the list to show only items containing the search text."""
        search_text = search_text.lower()

        # If search is empty, show all items
        if not search_text.strip():
            for i in range(self.ui.listMacros.count()):
                self.ui.listMacros.item(i).setHidden(False)
            return

        # Show/hide items based on search
        for i in range(self.ui.listMacros.count()):
            item = self.ui.listMacros.item(i)
            item_text = item.text().lower()
            item.setHidden(search_text not in item_text)

        # Optional: Select first visible item
        for i in range(self.ui.listMacros.count()):
            if not self.ui.listMacros.item(i).isHidden():
                self.ui.listMacros.setCurrentRow(i)
                break

    def on_listMacros_itemClicked(self, _item):
        _s = str(_item.text())
        a = self.pattern % _s
        self.clipboard.clear()
        self.clipboard.setText(a)
        self.newSelection.emit(_s)