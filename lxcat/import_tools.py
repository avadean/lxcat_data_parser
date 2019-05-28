import numpy as np
from enum import Enum
import logging
import os

# The different types of cross sections
CrossSectionTypes = frozenset({'ELASTIC','EFFECTIVE','EXCITATION','ATTACHMENT','IONIZATION'})


class CrossSection:
    """A class containing data of a single cross section."""
    def __init__(self, cross_section_type, species, param, energy, values, **kwargs):
        self.type = cross_section_type
        self.species = species
        if cross_section_type in {'ELASTIC', 'EFFECTIVE'}:
            self.mass_ratio = param
        elif cross_section_type in {'EXCITATION', 'IONIZATION'}:
            self.threshold = param
        self.energy = energy
        self.values = values
        self.other_information = {}
        for key, value in kwargs.items():
            self.other_information[key] = value
    
    @property
    def type(self):
        return self._type
    
    @type.setter
    def type(self, cross_section_type):
        if cross_section_type in CrossSectionTypes:
            self._type = cross_section_type
        else:
            raise ValueError("Cross section types other than "+str(CrossSectionTypes)+" are not permitted.")

    def __eq__(self, other):
        if not isinstance(other,CrossSection):
            return NotImplemented
        if list(self.__dict__.keys()) != list(other.__dict__.keys()):
            return False
        if self.type != other.type:
            return False
        if self.species != other.species:
            return False
        if hasattr(self, 'mass_ratio'):
            if self.mass_ratio != other.mass_ratio:
                return False
        elif hasattr(self, 'threshold'):
            if self.threshold != other.threshold:
                return False
        if len(self.energy) != len(other.energy) or any(self.energy != other.energy):
            return False
        if len(self.values) != len(other.values) or any(self.values != other.values):
            return False
        if self.other_information != other.other_information:
            return False
        return True


class CrossSectionSet:
    """A class containing a set of cross sections."""
    
    def __init__(self, mypath, imposed_species = None):
        """
        Reads the first set of cross section found in the file 'mypath', or,
        if an imposed_species is defined, reads only the cross section of that species.
        The file should be compatible with LXcat cross section data format.
        """
        logging.info('Initializing CrossSectionSet')
        self.cross_sections = []
        self.database = ''
        try:
            with open(mypath,'r') as fh:
                logging.info('Starting to read the contents of %s', os.path.basename(mypath))
                fh_line = fh.readline()
                while fh_line:
                    if fh_line.startswith('DATABASE:'):  # find the name of the database (optional)
                        self.database = fh_line[9:].strip()
                    found_cross_section = {fh_line.strip()}.intersection(CrossSectionTypes)
                    if found_cross_section:  # found a line matching one of the cross_section_types
                        cross_section_type = found_cross_section.pop()  # type of cross section
                        species = fh.readline().split()[0] # species (may be followed by other text)
                        if not imposed_species:
                            imposed_species = species
                        # parameter of the cross section (mass_ratio or threshold), missing for ATTACHMENT
                        param = None
                        if cross_section_type != 'ATTACHMENT':
                            param = float(fh.readline().split()[0])
                        # next lines are optional, additional info on the cross section:
                        other_information = {}
                        pos = fh.tell()
                        line = fh.readline()
                        while not line.startswith('-----'):
                            s = line.split(':')
                            key = s[0].strip()
                            other_information[key]=line[len(key)+1:].strip()
                            pos = fh.tell()
                            line = fh.readline()
                        fh.seek(pos)  # returns to previous line
                        # read the two columm-table of energy vs cross section:
                        fh, table = DataHandler.read_table(fh)
                        energy = table[:, 0]
                        values = table[:, 1]
                        xsec = CrossSection(cross_section_type, species, param, energy, values, **other_information)
                        if species == imposed_species:
                            self.cross_sections.append(xsec)
                    fh_line = fh.readline()
                self.species = imposed_species
                if self.cross_sections:
                    logging.info('Finished Initializing CrossSectionSet.')
                else:
                    logging.error('Could not find '+imposed_species+' cross sections in '+os.path.basename(mypath))
        except FileNotFoundError:
            logging.error("Could not find "+mypath)        

    def write(self,mypath):
        """
        Writes the set of cross sections in a '*.txt' file under 'mypath', in an LXcat-compatible format.
        """
        with open(mypath,'w') as fh:
            fh.write("Cross section data printed using lxcat python package, in an LXcat-compatible format (see www.lxcat.net).\n\n")
            fh.write("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")
            fh.write("DATABASE: " + self.database + "\n")
            fh.write("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n\n")
            fh.write("**************************************************************************************************************\n")
            for xsec in self.cross_sections:
                fh.write(xsec.type + "\n")
                fh.write(xsec.species + "\n")
                if xsec.type in {'ELASTIC', 'EFFECTIVE'}:
                    fh.write(str(xsec.mass_ratio) + "\n")
                elif xsec.type in {'EXCITATION', 'IONIZATION'}:
                    fh.write(str(xsec.threshold) + "\n")
                for key in xsec.other_information.keys():
                    fh.write(key + ": " + xsec.other_information[key] + "\n")
                fh = DataHandler.write_table(np.vstack((xsec.energy, xsec.values)).T, fh)  # create a 2-column table: 'energy' and 'values'
    
    def __eq__(self, other):
        if not isinstance(other,CrossSectionSet):
            return NotImplemented
        if list(self.__dict__.keys()) != list(other.__dict__.keys()):
            return False
        if self.database != other.database:
            return False
        if self.species != other.species:
            return False
        if self.cross_sections != other.cross_sections:
            return False
        return True


def import_lxcat_swarm_data(mypath):
    """
    Read a "Author_Year_Parameter.txt" file containing swarm data downloaded from the lxcat data center and returns the measured parameter in a dictionary.
    """
    filename = os.path.basename(mypath)
    infos = filename.split('_')
    try:
        data = {'Author': infos[0], 'Year': infos[1], 'Parameter': infos[2], 'E/N': [], infos[2]: []}
    except IndexError:
        print('Incorrect file name, please use the format "../Author_Year_Parameter.txt".')
        return {}
    
    with open(mypath, 'r', encoding="utf8") as fh:
        _, table = DataHandler.read_table(fh)
        data['E/N'] = table[:,0]
        data[infos[2]] = table[:,1]
    return data

class DataHandler:

    @staticmethod
    def read_table(filehandle):
        """Read a multi-column table of floats starting and ending with '-----' lines."""
        table = []
        fh_line = filehandle.readline()
        while '-----' not in fh_line:  # find the first occurence of '---': start of tabulated data
            fh_line = filehandle.readline()
        fh_line = filehandle.readline()
        while '-----' not in fh_line:  # stop when reaching the second occurence of '---': end of tabulated data
            s = fh_line.split()
            table_line = []
            for element in s:
                table_line.append(float(element.strip()))
            table.append(table_line)
            fh_line = filehandle.readline()
        table = np.array(table)
        return filehandle, table

    @staticmethod
    def write_table(table, filehandle):
        """Write a multi-column table starting and ending with '-----' lines."""
        filehandle.write("-----------------------------\n")
        for line in table:
            print("\t".join(format(x, ".6e") for x in line), file=filehandle)
        filehandle.write("-----------------------------\n\n")
        return filehandle
