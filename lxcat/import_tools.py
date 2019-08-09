import numpy as np
import pandas as pd
from enum import IntEnum
from typing import List
import logging
import os


# The different types of cross sections
class CrossSectionTypes(IntEnum):
    ELASTIC = 0
    EFFECTIVE = 1
    EXCITATION = 2
    ATTACHMENT = 3
    IONIZATION = 4
# CrossSectionTypes = frozenset({
#     'ELASTIC', 'EFFECTIVE', 'EXCITATION', 'ATTACHMENT', 'IONIZATION'})


CST = CrossSectionTypes


class CrossSection:
    """A class containing data of a single cross section."""

    def __init__(self, cross_section_type: (str, CST), species: str,
                 energy: List[float], values: List[float], mass_ratio: float = None,
                 threshold: float = None, **kwargs):
        if isinstance(cross_section_type, CST):
            self.type = cross_section_type
        else:
            self.type = CST[cross_section_type]
        self.species = species
        self.mass_ratio = mass_ratio
        self.threshold = threshold
        self.data = pd.DataFrame({'energy': energy, 'cross section': values})
        self.info = {}
        for key, value in kwargs.items():
            self.info[key] = value

    def __eq__(self, other):
        if not isinstance(other, CrossSection):
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
        if self.data.equals(other.data):
            return False
        if self.info != other.info:
            return False
        return True


class CrossSectionSet:
    """A class containing a set of cross sections."""

    def __init__(self, input_file, imposed_species='', imposed_database=''):
        """
        Reads a set of cross section from a file.

        Reads the first set of cross section found in the provided file, or,
        if an imposed_species is defined, reads only the cross section of
        that species.
        The file should be compatible with LXcat cross section data format.
        """
        self.species = imposed_species
        self.database = imposed_database
        self.cross_sections = []
        logging.info('Initializing CrossSectionSet')
        database = ''
        try:
            with open(input_file, 'r') as f:
                logging.info('Starting to read the contents of {}'.format(
                    os.path.basename(input_file)))
                cross_sections = []
                line = f.readline()
                while line:
                    # find the name of the database (optional)
                    if line.startswith('DATABASE:'):
                        database = line[9:].strip()
                    found_cs = [x.name for x in CrossSectionTypes
                                if line.startswith(x.name)]
                    # found a line matching one of the cross_section_types
                    if found_cs:
                        cs_type = CST[found_cs[0]]  # type of cross section
                        # species (may be followed by other text on the same line)
                        species = f.readline().split()[0]
                        if len(imposed_species) == 0:
                            imposed_species = species
                        if species == imposed_species:
                            if len(imposed_database) == 0:
                                imposed_database = database
                            if database == imposed_database:
                                # parameter of the cross section (mass_ratio
                                # or threshold), missing for ATTACHMENT
                                mass_ratio = None
                                threshold = None
                                if cs_type == CST.EFFECTIVE or cs_type == CST.ELASTIC:
                                    mass_ratio = float(f.readline().split()[0])
                                elif cs_type == CST.EXCITATION or cs_type.IONIZATION:
                                    threshold = float(f.readline().split()[0])
                                # next lines are optional (additional info
                                # on the cross section):
                                other_info = {}
                                pos = f.tell()
                                line = f.readline()
                                while not line.startswith('-----'):
                                    s = line.split(':')
                                    key = s[0].strip()
                                    other_info[key] = line[len(key) + 1:].strip()
                                    pos = f.tell()
                                    line = f.readline()
                                f.seek(pos)  # returns to previous line
                                # read the two column-table of energy vs cross section:
                                f, table = DataHandler.read_table(f)
                                energy = table[:, 0]
                                values = table[:, 1]
                                xsec = CrossSection(cs_type, species, energy, values,
                                                    mass_ratio, threshold, **other_info)
                                if species == imposed_species:
                                    cross_sections.append(xsec)
                    line = f.readline()
                if cross_sections:
                    self.species = imposed_species
                    self.database = imposed_database
                    self.cross_sections = cross_sections
                    logging.info('Finished Initializing CrossSectionSet.')
                else:
                    required = ' '.join(s for s in [imposed_database, imposed_species] if s)
                    logging.error('Could not find {} cross sections in {}'.format(
                        required, os.path.basename(input_file)))
        except FileNotFoundError:
            logging.error("Could not find {}".format(input_file))
            raise

    def write(self, input_file):
        """
        Writes the set of cross sections in a '*.txt' file under 'input_file',
        in an LXcat-compatible format.
        """
        with open(input_file, 'w') as fh:
            fh.write("""Cross section data printed using lxcat python package,
                        in an LXcat-compatible format (see www.lxcat.net).\n\n""")
            fh.write("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")
            fh.write("DATABASE: " + self.database + "\n")
            fh.write("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n\n")
            fh.write("********************************\n")
            for xsec in self.cross_sections:
                fh.write(xsec.type + "\n")
                fh.write(xsec.species + "\n")
                if xsec.type in {'ELASTIC', 'EFFECTIVE'}:
                    fh.write(str(xsec.mass_ratio) + "\n")
                elif xsec.type in {'EXCITATION', 'IONIZATION'}:
                    fh.write(str(xsec.threshold) + "\n")
                for key in xsec.info.keys():
                    fh.write(key + ": " + xsec.info[key] + "\n")
                # create a 2-column table: 'energy' and 'values'
                fh = DataHandler.write_table(xsec.data, fh)

    def __eq__(self, other):
        if not isinstance(other, CrossSectionSet):
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


def import_lxcat_swarm_data(input_file):
    """
    Read a "Author_Year_Parameter.txt" file containing swarm data
    downloaded from the lxcat data center and returns
    the measured parameter in a dictionary.
    """
    filename = os.path.basename(input_file)
    infos = filename.split('_')
    try:
        data = {'Author': infos[0], 'Year': infos[1], 'Parameter': infos[2],
                'E/N': [], infos[2]: []}
    except IndexError:
        print('Incorrect file name, please use the format "../Author_Year_Parameter.txt".')
        return {}

    with open(input_file, 'r', encoding="utf8") as fh:
        _, table = DataHandler.read_table(fh)
        data['E/N'] = table[:, 0]
        data[infos[2]] = table[:, 1]
    return data


class DataHandler:

    @staticmethod
    def read_table(file_handle):
        """
        Read a multi-column table of floats starting
        and ending with '-----' lines.
        """
        table = []
        fh_line = file_handle.readline()
        # find the first occurrence of '---': start of tabulated data
        while '-----' not in fh_line:
            fh_line = file_handle.readline()
        fh_line = file_handle.readline()
        # stop when reaching the second occurrence of '---': end of tabulated data
        while '-----' not in fh_line:
            s = fh_line.split()
            table_line = []
            for element in s:
                table_line.append(float(element.strip()))
            table.append(table_line)
            fh_line = file_handle.readline()
        table = np.array(table)
        return file_handle, table

    @staticmethod
    def write_table(table, file_handle):
        """Write a multi-column table starting and ending with '-----' lines."""
        file_handle.write("-----------------------------\n")
        for line in table.xsec.iterrows():
            print("\t".join(format(x, ".6e") for x in list(line)), file=file_handle)
        file_handle.write("-----------------------------\n\n")
        return file_handle
