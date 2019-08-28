import pandas as pd
from enum import IntEnum
import logging
import os
import io


# The different types of cross sections
class CrossSectionTypes(IntEnum):
    ELASTIC = 0
    EFFECTIVE = 1
    EXCITATION = 2
    ATTACHMENT = 3
    IONIZATION = 4


CST = CrossSectionTypes


class CrossSection:
    """Class containing data of a single cross section.

    Attributes:
        cross_section_type: Type of collision, possible str/member of CrossSectionTypes
        species: name of the species as a str, example: N2
        data: pandas DataFrame with columns 'energy' in eV and ''cross section' in m2
        mass_ratio: ratio of electron mass to atomic/molecular mass
        threshold: cross section threshold in eV
        info: optional additional information on the cross section given via kwargs"""

    def __init__(self, cross_section_type: (str, CST), species: str,
                 data: pd.DataFrame, mass_ratio: float = None,
                 threshold: float = None, **kwargs):
        if isinstance(cross_section_type, CST):
            self.type = cross_section_type
        else:
            try:
                self.type = CST[cross_section_type]
            except KeyError:
                logging.error(("Invalid value of argument cross_section_type. "
                              " Accepted values are {}").format(
                    [xsec.name for xsec in CrossSectionTypes]))
                raise
        self.species = species
        self.data = data
        self.mass_ratio = mass_ratio
        self.threshold = threshold
        self.info = {}
        for key, value in kwargs.items():
            self.info[key] = value

    def __eq__(self, other):
        if not isinstance(other, CrossSection):
            return NotImplemented
        if self.type != other.type:
            logging.debug('Not the same type: {} vs {}.'.format(self.data, other.data))
            return False
        if self.species != other.species:
            logging.debug('Not the same species: {} vs {}.'.format(
                self.type, other.type))
            return False
        if not self.data.equals(other.data):
            logging.debug('Not the same data: {} vs {}.'.format(self.data, other.data))
            return False
        if self.mass_ratio != other.mass_ratio:
            logging.debug('Not the same mass ratio: {} vs {}.'.format(
                self.mass_ratio, other.mass_ratio))
            return False
        if self.threshold != other.threshold:
            logging.debug('Not the same threshold: {} vs {}.'.format(
                self.threshold, other.threshold))
            return False
        if self.info != other.info:
            logging.debug('Not the same info: {} vs {}.'.format(self.info, other.info))
            return False
        return True


class CrossSectionSet:
    """A class containing a set of cross sections.

    Attributes:
        species: name of the species as a str, example: N2
        database: name of the database
        cross_sections: list of CrossSections"""

    def __init__(self, input_file, imposed_species=None, imposed_database=None):
        """
        Reads a set of cross section from a file.

        By default, reads the first cross section set found in the input file but, if
        an imposed_species and/or an imposed_database are defined, reads the first cross
        section set of that species and/or that database found in the input file.
        The input file should be compatible with the LXcat cross section data format.
        """
        self.species = imposed_species
        self.database = imposed_database
        self.cross_sections = []
        current_database = None
        try:
            with open(input_file, 'r') as f:
                logging.info('Starting to read the contents of {}'.format(
                    os.path.basename(input_file)))
                cross_sections = []
                line = f.readline()
                while line:
                    # find the name of the database (optional)
                    if line.startswith('DATABASE:'):
                        current_database = line[9:].strip()
                        line = f.readline()
                    # find a line starting with one of the cross_section_types
                    found_cs = [x.name for x in CST if line.startswith(x.name)]
                    if found_cs:
                        # type of cross section
                        cs_type = CST[found_cs[0]]
                        # species (may be followed by other text on the same line)
                        line = f.readline()
                        current_species = line.split()[0]
                        if imposed_species is None:
                            imposed_species = current_species
                        # if this is the right species, proceed
                        if current_species == imposed_species:
                            if imposed_database is None:
                                imposed_database = current_database
                            # if this is the right database, proceed
                            if current_database == imposed_database:
                                # depending on the type of cross section, the next line
                                # contains either the mass_ratio or the threshold
                                mass_ratio = None
                                threshold = None
                                if cs_type == CST.EFFECTIVE or cs_type == CST.ELASTIC:
                                    mass_ratio = float(f.readline().split()[0])
                                elif (cs_type == CST.EXCITATION
                                      or cs_type == CST.IONIZATION):
                                    threshold = float(f.readline().split()[0])
                                # the next lines may contain optional, additional
                                # information on the cross section with the format
                                # KEY: information
                                other_info = {}
                                line = f.readline()
                                while not line.startswith('-----'):
                                    s = line.split(':')
                                    key = s[0].strip()
                                    other_info[key] = line[len(key) + 1:].strip()
                                    line = f.readline()
                                # '-----' mars the start of the tabulated data
                                # put the data into an ioString
                                data_stream = io.StringIO()
                                line = f.readline()
                                while not line.startswith('-----'):
                                    data_stream.write(line)
                                    line = f.readline()
                                data_stream.seek(0)
                                # '-----' marks the end of the tabulated data
                                # read the data into a pandas DataFrame
                                data = pd.read_csv(data_stream, sep='\t',
                                                   names=['energy', 'cross section'])
                                # create the cross section object with all the info
                                xsec = CrossSection(cs_type, current_species, data,
                                                    mass_ratio, threshold, **other_info)
                                cross_sections.append(xsec)
                    line = f.readline()
                if cross_sections:
                    self.species = imposed_species
                    self.database = imposed_database
                    self.cross_sections = cross_sections
                    logging.info('Finished Initializing CrossSectionSet.')
                else:
                    required = ' '.join(s for s in [imposed_database, imposed_species]
                                        if s is not None)
                    logging.error('Could not find {} cross sections in {}'.format(
                        required, os.path.basename(input_file)))
        except FileNotFoundError:
            logging.error("Could not find {}".format(input_file))
            raise

    def write(self, output_file):
        """
        Writes the set of cross sections in a '*.txt' file under 'input_file',
        in an lxcat-compatible format.
        """
        with open(output_file, 'w') as fh:
            fh.write("Cross section data printed using lxcat python package, "
                     "in an LXcat-compatible format (see www.lxcat.net).\n\n")
            fh.write("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")
            if self.database is not None:
                fh.write("DATABASE: " + self.database + "\n")
                fh.write("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n\n")
            fh.write("********************************\n")
            for xsec in self.cross_sections:
                fh.write(xsec.type.name + "\n")
                fh.write(xsec.species + "\n")
                if xsec.type.name in {'ELASTIC', 'EFFECTIVE'}:
                    fh.write(str(xsec.mass_ratio) + "\n")
                elif xsec.type.name in {'EXCITATION', 'IONIZATION'}:
                    fh.write(str(xsec.threshold) + "\n")
                for key in xsec.info.keys():
                    fh.write(key + ": " + xsec.info[key] + "\n")
                # create a 2-column table: 'energy' and 'values'
                fh.write("-----------------------------\n")
                xsec.data.to_csv(fh, sep='\t', index=False, header=False, chunksize=2,
                                 float_format='%.6e', line_terminator='\n')
                fh.write("-----------------------------\n\n")
            fh.write("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n")

    def __eq__(self, other):
        if not isinstance(other, CrossSectionSet):
            return NotImplemented
        if self.database != other.database:
            return False
        if self.species != other.species:
            return False
        # check that the cross sections are identical (order may vary) by removing them
        # one by one and checking that the remaining list is then empty
        other_xsecs = list(other.cross_sections)
        for xsec in self.cross_sections:
            try:
                other_xsecs.remove(xsec)
            except ValueError:
                return False
        return not other_xsecs


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
