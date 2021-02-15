"""
A module for selecting directories with a configuration file that keeps a list
of the last selections.

"""

__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015,  H A Preisig"
__since__ = "2015.09.22"
__license__ = "generic module"
__version__ = "0"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os as OS

from PyQt5.QtWidgets import QWidget

import configuration_file

HOME = OS.environ['HOME']


class selectDirectory(QWidget):
  def __init__(self, filename, location=HOME,):
    QWidget.__init__(self)
    self.filename = filename+'.cnf'
    self.location = location
    self.filepath = location + '/'+ self.filename

  def getLastDirectories(self):

    self.got_dir = False
    self.config = configuration_file.ConfigFile()
    new = False
    if not OS.path.exists(self.location):
      OS.makedirs(self.location)
      new = True
    elif not OS.path.exists(self.filepath):
      new = True
    if new:
      self.config.dictionary['DIRECTORIES'] = {'0': HOME}
      with open(self.filepath, 'w') as configfile:
        self.config.write(configfile)

    return self.config.read(self.filepath)['DIRECTORIES']



  def put(self, dir):
    section_directories = self.config.read(self.filepath)
    dirs = section_directories["DIRECTORIES"]

    # only put if it is not already there
    for d in dirs:
      print('dir', dir)
      print('dirs[d]', dirs[d],'\n')
      if dir == dirs[d]:
        return

    count = len(dirs.keys())
    count += 1
    dirs[str(count-1)] = dir
    print(section_directories)
    self.config = configuration_file.ConfigFile()
    self.config.dictionary=section_directories
    with open(self.filepath, 'w') as configfile:
        self.config.write(configfile)