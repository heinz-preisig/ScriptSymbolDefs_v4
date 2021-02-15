'''
Created on 8 Apr 2015

@author: heinz
'''


__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015,  H A Preisig"
__since__ = "2015.09.22"
__license__ = "generic module"
__version__ = "0"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"


from PyQt5 import QtCore
from PyQt5.QtWidgets import QListWidgetItem, QApplication, QDialog
from listview import Ui_Dialog



class UI_ListView(QDialog):

  newSelection = QtCore.pyqtSignal(str)

  def __init__(self, pattern="%s", parent=None):

    QDialog.__init__(self, parent)
    self.pattern = pattern
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)
    self.hide()
    self.clipboard = QApplication.clipboard()
    print('>>listview')
    self.show()

  def build(self,macro_list):
    self.ui.listMacros.clear()
    self.no_items = len(macro_list)
    if self.no_items > 50 : self.no_items = 50
    self.max_letters = 0#len(max(macro_list))
    for i in macro_list:
      _item = QListWidgetItem()
      _item.setText(i)
      self.ui.listMacros.addItem(_item)
      if len(i) > self.max_letters: self.max_letters=len(i)
    self.__resizeMe()
    self.show()

  def __resizeMe(self):
    lines = self.no_items
    letters = self.max_letters
    tab_width = letters*10
    tab_height = lines *20
    tab_size = QtCore.QSize(tab_width,tab_height)
    self.ui.listMacros.resize(tab_size)
    x = self.ui.listMacros.x()+tab_width+12
    y = self.ui.listMacros.y()+tab_height+12
    s = QtCore.QSize(x,y)
    self.resize(s)

  def on_listMacros_itemClicked(self, _item):
    _s = str(_item.text())
    print(self.pattern)
    a = self.pattern%_s
    print(a)
    self.clipboard.clear()
    self.clipboard.setText(self.pattern%_s)
    self.newSelection.emit(_s)