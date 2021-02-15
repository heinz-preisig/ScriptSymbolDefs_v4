'''
Created on Jan 26, 2014

@author: Preisig, Heinz A

changes : 2015-07-01 Preisig glossary type is now nomenclature
changes : 2015-09-28 Preisig file name changed to nomenclature
'''

__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015,  H A Preisig"
__since__ = "2014.01.26"
__license__ = "generic module"
__version__ = "0"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os as OS
from PyQt5 import QtCore

import directoryhistory.manage_former_directories as SC
from PyQt5.QtWidgets import QFileDialog, QWidget, QApplication

from directoryhistory.listview_impl import UI_ListView
from editor import Ui_Form

HOME = OS.environ['HOME']
CONFIGURATIONDIR = HOME + '/.glossaries/'
CONFIGURATIONAME = 'symbols'

TEMPLATES = {}
TEMPLATES['log'] = '%s/nomenclature.log'
TEMPLATES['nomenclature'] = '%s/nomenclature.def'
TEMPLATES['def_vars'] = '%s/defvars.def'
TEMPLATES['macros']  = '%s/macros.def'
TEMPLATES['nomenclature_entry'] = '\\NomenclaturEntry{%s}{%s}{%s}{%s}\n'
#TEMPLATES['common_defs_load'] = '% uses \resourcelocation{defs_math.tex}' #'\\input{\\resourcelocation{defs_math.tex}}\n'
TEMPLATES['defs_entry'] = '\def\%s{\Var{%s}}\n'
TEMPLATES['def_macro'] = '\def\%s{{%s}}\n'
# _s = '\\newglossaryentry{#1}{type=nomenclature, name={\ensuremath{#2}}, ' \
#      'description={#3},sort={#4}}'  # hash, name(symbol), description, sort
#TEMPLATES['glossary_transformer'] = '\\def\\NomenclaturEntry#1#2#3#4{%s}\n' % _s
TEMPLATES['defs_transformer'] = '\\def\Var#1{\\gls{#1}}'


class UI(QWidget):
  '''
  classdocs
  '''

  def __init__(self):
    '''
    Constructor
    '''
    QWidget.__init__(self)
    self.ui = Ui_Form()
    self.ui.setupUi(self)
    self.macro_list = UI_ListView('\\%s')
    self.setWindowTitle("Macro definition form")
    self.macro_list.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    self.clipboard = QApplication.clipboard()

    self.macro_list.newSelection.connect(self.__selectItemInComboBoxHash)

    sel = self.__previousDirsSelector()

  def __start(self):
    s = self.chosen_dir
    self.ui.labelDirectory.setText(s)  # QtCore.QString(s))
    self.directory = s
    self.file_log = TEMPLATES['log'] % s
    self.file_nomenclature = TEMPLATES['nomenclature'] % s
    self.file_defvars = TEMPLATES['def_vars'] % s
    self.file_macros = TEMPLATES['macros'] %s
    self.modified = False
    self.populating = False

    self.gloss_entries = {}
    self.symbol_list = []

    if OS.path.exists(self.file_nomenclature):
      self.read_file(s)
      self.new_file = False
      self.setMode('choose')
    else:
      self.new_file = True
      self.setMode('new')

    self.show()


  def __previousDirsSelector(self):

    self.former_directories = SC.selectDirectory(CONFIGURATIONAME,
                                                 CONFIGURATIONDIR)
    dirs = self.former_directories.getLastDirectories()
    self.dir_list = UI_ListView()
    self.dir_list.setModal(True)
    self.dir_list.newSelection.connect(self.__gotDirectory)
    _l = list(dirs.values())
    self.dir_list.build(_l)
    # self.dir_list.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    self.dir_list.show()

  def __gotDirectory(self, s):
    self.got_dir = True
    _s = str(s)
    print('chosen dir', _s)
    selection = self.__askDirectory(_s)
    if selection != str(_s):
      self.former_directories.put(selection)
    self.dir_list.close()
    self.chosen_dir = selection
    self.__start()


  def __askDirectory(self, default):
    s = QFileDialog.getExistingDirectory(self, "select directory",
                                           # "/home/heinz/",
                                           default,
                                           QFileDialog.ShowDirsOnly
                                           | QFileDialog.DontResolveSymlinks);
    self.chosen_dir = s
    return s

  @QtCore.pyqtSlot(str)
  def __selectItemInComboBoxHash(self, selection):
    index = self.ui.comboBoxHash.findText(selection)
    self.ui.comboBoxHash.setCurrentIndex(index)
    self.raise_()

  def read_file(self, s):
    f_in = TEMPLATES['nomenclature'] % s
    f_i = open(f_in, 'r')

    for line in f_i:
      (hash_name, symbol, description, sort) = self.formatParse(line)
      self.gloss_entries[hash_name] = {}                     # name of the macro
      self.gloss_entries[hash_name]['symbol'] = symbol          # tex definition
      self.gloss_entries[hash_name]['description'] = description
      self.gloss_entries[hash_name]['sort_key'] = sort

      # if ('\def' not in line) :# and ('\input' not in line): # the sort is optional thus two blocks
      #   try:
      #     (hash_name, symbol, description) = self.formatParse(line)
      #     self.gloss_entries[hash_name] = {}
      #     self.gloss_entries[hash_name]['symbol'] = symbol
      #     self.gloss_entries[hash_name]['description'] = description
      #     self.gloss_entries[hash_name]['sort_key'] = symbol
      #   except:
      #     try:
      #       (hash_name, symbol, description, sort) = self.formatParse(line)
      #     except:
      #       print
      #       '>>> error in line: ', line
      #     self.gloss_entries[hash_name] = {}
      #     self.gloss_entries[hash_name]['symbol'] = symbol
      #     self.gloss_entries[hash_name]['description'] = description
      #     self.gloss_entries[hash_name]['sort_key'] = sort

    if self.gloss_entries.keys() != []:
      self.populateComboBox()
      self.on_comboBoxHash_currentIndexChanged(0)
      self.populateLineEdits()
      self.setMode('choose')

  def write_files(self):
    f_gloss = open(self.file_nomenclature, 'w')
    f_defvars = open(self.file_defvars, 'w')
    f_macros = open(self.file_macros, 'w')
    # _s = TEMPLATES['common_defs_load']
    # f_gloss.write(_s)
    # _s = TEMPLATES['glossary_transformer']
    # f_gloss.write(_s)
    hashes = sorted(self.gloss_entries.keys())
    # hashes.sort()
    for hash_name in hashes:  # self.gloss_entries.keys():
      symbol = self.gloss_entries[hash_name]['symbol']
      description = self.gloss_entries[hash_name]['description']
      sort_key = self.gloss_entries[hash_name]['sort_key']
      _s = TEMPLATES['nomenclature_entry'] % (
      hash_name, symbol, description, sort_key)
      f_gloss.write(_s)
      #
      _s = TEMPLATES['defs_entry'] % (hash_name, hash_name)
      f_defvars.write(_s)
      _s = TEMPLATES['def_macro'] % (hash_name, symbol)
      f_macros.write(_s)
    f_gloss.close()
    f_defvars.close()
    f_macros.close()
    self.modified = False
    self.populateLineEdits()
    self.setMode('choose')

  def print_info(self):

    f_log = open(self.file_log, 'w')
    _l = list(self.gloss_entries.keys())
    _l.sort()
    for i in _l:
      _s = '%s : %s\n' % (i, self.gloss_entries[i]['symbol'])
      f_log.write(_s)
    f_log.close()

  def formatParse(self, s):
    count = 0
    arg_count = 0
    a = []
    # print len(s)
    for i in s:
      if count == 0:
        if i == '{':
          a.append('')
      if i == '}':
        count -= 1
        if count == 0:
          arg_count += 1
      if count > 0:
        a[arg_count] += i
      if i == '{':
        count += 1
    return a

  def setMode(self, mode):
    buttons = ['Write', 'New', 'Edit', 'Delete', 'Accept', 'Clear']
    lines = ['Hash', 'Symbol', 'SortKey', 'Description']
    if mode == 'choose':
      show_button = ['Edit', 'New', 'Delete']
      show_lines = lines
      disable_edit = True
    elif mode == 'new':
      show_button = []
      show_lines = ['Hash']
      disable_edit = False
    elif mode == 'edit':
      show_button = ['Accept']
      show_lines = ['Symbol', 'SortKey', 'Description']
      disable_edit = False
    elif mode == 'accept':
      show_button = ['Accept', 'Clear']
      show_lines = lines
      disable_edit = True
    if self.modified:
      show_button.append('Write')

    for i in lines:
      if i in show_lines:
        eval('self.ui.lineEdit%s.setReadOnly(%s)' % (i, disable_edit))
      else:
        eval('self.ui.lineEdit%s.setReadOnly(%s)' % (i, disable_edit))

    for i in buttons:
      if i in show_button:
        eval('self.ui.pushButton%s.show()' % i)
      else:
        eval('self.ui.pushButton%s.hide()' % i)

    for i in lines:
      if i in show_lines:
        eval('self.ui.lineEdit%s.show()' % i)
      else:
        eval('self.ui.lineEdit%s.hide()' % i)

  def populateComboBox(self):
    self.populating = True
    # 		print self.gloss_entries.keys(), len(self.gloss_entries.keys())
    hashes = sorted(self.gloss_entries.keys())
    # hashes.sort()
    self.ui.comboBoxHash.clear()
    self.ui.comboBoxHash.addItems(hashes) #QtCore.QStringList(hashes))
    self.macro_list.build(hashes)
    self.populating = False

  def populateLineEdits(self):
    hash_name = str(self.ui.comboBoxHash.currentText())
    symbol = self.gloss_entries[hash_name]['symbol']
    sort_key = self.gloss_entries[hash_name]['sort_key']
    description = self.gloss_entries[hash_name]['description']
    self.ui.lineEditHash.setText(hash_name) #QtCore.QString(hash_name))
    self.ui.lineEditSymbol.setText(symbol) #QtCore.QString(symbol))
    self.ui.lineEditSortKey.setText(sort_key) #QtCore.QString(sort_key))
    self.ui.lineEditDescription.setText(description) #QtCore.QString(description))


    # signal handling

  def on_pushButtonLoad_pressed(self):
    print
    'load pressed'
    pass

  def on_pushButtonWrite_pressed(self):
    print
    'write pressed'
    self.write_files()
    pass

  def on_pushButtonPrint_pressed(self):
    print
    'print pressed'
    self.print_info()

  def on_pushButtonNew_pressed(self):
    print
    'Edit pressed'
    self.setMode('new')
    self.on_pushButtonClear_pressed()
    pass

  def on_pushButtonEdit_pressed(self):
    print
    'Edit pressed'
    self.setMode('edit')
    self.populateLineEdits()

  def on_pushButtonStop_pressed(self):
    print
    'Stop pressed'
    self.setMode('choose')
    self.populateLineEdits()

    pass

  def on_pushButtonDelete_pressed(self):
    print
    'delete pressed'
    hash_name = str(self.ui.comboBoxHash.currentText())
    del self.gloss_entries[hash_name]
    self.populateComboBox()
    self.ui.comboBoxHash.setCurrentIndex(0)
    self.populateLineEdits()
    self.modified = True
    self.setMode('choose')
    pass

  def on_pushButtonAccept_pressed(self):
    print
    'accept pressed'

    hash_name = str(self.ui.lineEditHash.text())
    symbol = str(self.ui.lineEditSymbol.text())
    sort_key = str(self.ui.lineEditSortKey.text())
    description = str(self.ui.lineEditDescription.text())
    self.gloss_entries[hash_name] = {}
    self.gloss_entries[hash_name]['symbol'] = symbol
    self.gloss_entries[hash_name]['description'] = description
    self.gloss_entries[hash_name]['sort_key'] = sort_key
    self.on_pushButtonClear_pressed()
    self.populateComboBox()
    self.populateLineEdits()
    self.modified = True
    self.setMode('choose')
    pass

  def on_pushButtonClear_pressed(self):
    print
    'clear pressed'

    lines = ['Hash', 'Symbol', 'SortKey', 'Description']
    for i in lines:
      eval('self.ui.lineEdit%s.clear()' % i)

    # 		self.ui.lineEditHash.clear()
    # 		self.ui.lineEditSymbol.clear()
    # 		self.ui.lineEdit.clear()
    # 		self.ui.lineEditDescription.clear()
    pass

  def on_pushButtonShowList_pressed(self):
    self.macro_list.show()
    self.macro_list.topLevelWidget()

  # @QtCore.pyqtSignature('int')

  def on_comboBoxHash_currentIndexChanged(self, n):
    if self.populating:
      return
    print
    'Hash index changed', n
    self.on_pushButtonClear_pressed()
    self.populateLineEdits()
    self.setMode('choose')
    pass

  # @QtCore.pyqtSignature('QString')
  def on_comboBoxHash_activated(self, s):
    _s = str(s)
    self.clipboard.clear()
    self.clipboard.setText('\%s'%_s)

  def on_lineEditHash_textEdited(self):
    # 		print 'hash modified text', self.ui.lineEditHash.text()
    pass

  def on_lineEditHash_returnPressed(self):
    hash_name = str(self.ui.lineEditHash.text())
    if hash_name in self.gloss_entries.keys():
      self.ui.lineEditHash.clear()
      self.ui.lineEditHash.setPlaceholderText('already defined')
      return

    self.ui.lineEditSymbol.show()
    self.ui.lineEditSymbol.setFocus()
    self.hash_name = hash_name

  def on_lineEditSymbol_returnPressed(self):
    symbol = str(self.ui.lineEditSymbol.text())
    if symbol == '':
      return
    if symbol in self.symbol_list:
      self.ui.lineEditSymbol.clear()
      self.ui.lineEditSymbol.setPlaceholderText('already defined')
      return
    self.ui.lineEditSortKey.show()
    self.ui.lineEditSortKey.setFocus()

  def on_lineEditSortKey_returnPressed(self):
    sort_key = str(self.ui.lineEditSymbol.text())
    if sort_key == '':
      return
    self.ui.lineEditDescription.show()
    self.ui.lineEditDescription.setFocus()

  def on_lineEditDescription_returnPressed(self):
    description = str(self.ui.lineEditDescription.text())
    if description == '':
      return
    self.setMode('accept')

  def closeEvent(self, event):
    self.macro_list.close()
    self.close()
