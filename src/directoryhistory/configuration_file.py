'''=============================================================================
    cofiguration_file
   =============================================================================

 a facility to handle configuration files

@author: Preisig, H A
@since: 2007-10-29
@change: 2014-12-09 Preisig, H A  ordered dictionary
@change: 2014-12-09 Preisig, H A  allow for comments #comment
@change: 2014-12-09 Preisig, H A  allow for . in section name
@change: 2015-01-07 Elve, A T     added write member function
@change: 2015-05-04 Elve, A T     added option function 

'''

# imports ------------------- -------------------------------------------------

from __future__ import with_statement
import os as OS
from collections import OrderedDict
import re as RE

# 
#
# from Debugging import message_logging
# # WHAT = __name_
# WHAT = "ConfigFile"
# LOGGER = message_logging.createLogger(WHAT , level=0,
#                                       record_format="%(name)s - %(lineno)d - %(message)s",
#                                       handler_type="console")

# error handling --------------------------------------------------------------
class ConfigError(Exception):
    '''
    Exception reporting 
    '''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return ">>> %s" % self.msg



# body ------------------------------------------------------------------------


    
class ConfigFile():
    def __init__(self):

        self.section_pattern = RE.compile('\[\w*.\w*\]')
        self.token_equal = RE.compile('=')
        self.token_comment = RE.compile('#')
        self.dictionary = OrderedDict()

    def read(self, file_spec):
        if not OS.path.exists(file_spec):
            raise ConfigError('no such initialisation file :' + file_spec)
        dictionary = OrderedDict()
        count = 0
        with open(file_spec) as file_spec:
            for line in file_spec:
                count = count + 1
                line.strip(' \n')
                if '#' in line:
                    line = str(self.token_comment.split(line)[0])
                    # LOGGER.info('>>>>>>>> %s'%line)
                s = self.section_pattern.match(line)
                if s != None:
                    sec = s.group().strip('[]')
                    # LOGGER.info('section %s' %sec)
                    dictionary[sec] = OrderedDict()  # start a new section
                else:
                    if count == 1:
                        ConfigError('first line must be a section %s' %line)
                        return
                    l = self.token_equal.split(line)
                    if l == None:
                        ConfigError('no such line', line)
                    else:
                        if len(l) == 2:
                            k = l[0].strip(' ')
                            v = l[1].strip(' \n')
                            dictionary[sec][k] = v
        return dictionary

    def options(self, section, file_spec):
        """Return a list of option names for the given section name."""
        try:
            opts = self.read(file_spec)[section]
        except KeyError:
            raise ConfigError("No section in file named: %s" %(section))
        return [opt for opt in opts]


    def sections(self, file_spec):
        """Return a list of section names for the given file."""
        try:
            sections = self.read(file_spec)
        except IOError:
            raise ConfigError("No initiation file named: %s" %(file_spec))
        return [section for section in sections]


    def write(self, file_spec):
        if self.dictionary:
            # LOGGER.info('Saving to file: %s' % file_spec)
            for section in self.dictionary:
                file_spec.write("[%s]\n" % section)
                for (key, value) in self.dictionary[section].items():
                    key = " = ".join((key, str(value).replace('\n', '\n\t')))
                    file_spec.write("%s\n" % (key))
                file_spec.write("\n")
        else:
            ConfigError('Empty configuration dictionary')






if __name__ == '__main__':
    config = ConfigFile()
    
    try:
        ini_config = config.read('process-modeller.ini')
        for i in ini_config:
            print('\nsection: ',i)
            for j in ini_config[i]:
                print('  item : ',j)
    except ConfigError as m:
        print('failed :', m)
        
    types = config.options('node','ontology_physical_types.cfg')
    print ('types = ',types)

    sections = config.sections('ontology_variables_physical.cfg')
    print ('sections = ',sections)
    