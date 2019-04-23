import numpy as np
from enum import Enum


class CrossSectionType(Enum):
    """Enumeration of the different types of cross sections"""
    ELASTIC = 'ELASTIC'
    EFFECTIVE = 'EFFECTIVE'
    EXCITATION = 'EXCITATION'
    ATTACHMENT = 'ATTACHMENT'
    IONIZATION = 'IONIZATION'


class CrossSection:
    """A class containing data of a single cross section."""
    def __init__(self, collision_type, param, species, energy, values):
        self.collision_type = CrossSectionType(collision_type)
        if collision_type in {'ELASTIC', 'EFFECTIVE'}:
            self.mass_ratio = param
        elif collision_type in {'EXCITATION', 'ATTACHMENT', 'IONIZATION'}:
            self.threshold = param
        self.species = species
        self.energy = energy
        self.values = values


class CrossSectionSet:
    """A class containing a set of cross sections."""
    
    def __init__(self, mypath):
        """
        Read the '*.txt' file under 'mypath' containing an electron scattering cross section set downloaded from LXcat.
        """
        self.xsections = []
        cross_section_types = {xstyp.value for xstyp in CrossSectionType}
        with open(mypath,'r') as fh:
            for fh_line in fh:
                if 'DATABASE:' in fh_line:  # find the name of the database
                    self.database = fh_line[9:].strip()
                    break
            for fh_line in fh:
                match = cross_section_types.intersection({fh_line.strip()})
                if match:  # found a line matching one of the cross_section_types
                    collision_type = match.pop()  # type of cross section
                    fh.readline()
                    # parameter of the cross section (mass_ratio or threshold)
                    param = float(fh.readline().strip())
                    species = fh.readline()[8:].strip()
                    fh, table = read_table(fh)
                    energy = table[:, 0]
                    values = table[:, 1]
                    xsec = CrossSection(collision_type, param,
                                        species, energy, values)
                    self.xsections.append(xsec)
            self.species = species

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
            for xsec in self.xsections:
                fh.write(xsec.collision_type.value + "\n")
                fh.write(xsec.species.split('/')[1] + "\n")
                if xsec.collision_type.value in {'ELASTIC', 'EFFECTIVE'}:
                    fh.write(str(xsec.mass_ratio) + "\n")
                    paramline = "PARAM: m/M = " + str(xsec.mass_ratio) + "\n"
                elif xsec.collision_type.value in {'EXCITATION', 'ATTACHMENT', 'IONIZATION'}:
                    fh.write(str(xsec.threshold) + "\n")
                    paramline = "PARAM: threshold = " + str(xsec.threshold) + "eV\n"
                fh.write("SPECIES: " + xsec.species + "\n")
                fh.write("PROCESS:\n")
                fh.write(paramline)
                fh.write("COMMENT:\n")
                fh.write("UPDATED:\n")
                fh.write("COLUMNS: Energy (eV) | Cross section (m2)\n")
                fh = write_table(np.vstack((xsec.energy, xsec.values)).T, fh)  # create a 2-column table: 'energy' and 'values'
                
  

def import_lxcat_swarm_data(mypath):
    """
    Read a "Author_Year_Parameter.txt" file containing swarm data downloaded from the lxcat data center and returns the measured parameter in a dictionary.
    """
    filename = filename_from_path(mypath)
    infos = filename.split('_')
    try:
        data = {'Author': infos[0], 'Year': infos[1], 'Parameter': infos[2], 'E/N': [], infos[2]: []}
    except IndexError:
        print('Incorrect file name, please use the format "../Author_Year_Parameter.txt".')
        return {}
    
    with open(mypath, 'r', encoding="utf8") as fh:
        _, table = read_table(fh)
        data['E/N'] = table[:,0]
        data[infos[2]] = table[:,1]
    return data


def read_table(filehandle):
    """Read a multi-column table starting and ending with '---' lines."""
    table = []
    for fh_line in filehandle:
        if '---' in fh_line:
            break  # find the first occurence of '---': start of tabulated data
    for fh_line in filehandle:
        if '---' in fh_line:
            break  # break when reaching the second occurence of '---': end of tabulated data
        else:
            s = fh_line.split()
            table_line = []
            for element in s:
                table_line.append(float(element.strip()))
            table.append(table_line)
    table = np.array(table)
    return filehandle, table

def write_table(table, filehandle):
    """Write a multi-column table starting and ending with '---' lines."""
    filehandle.write("-----------------------------\n")
    for line in table:
        print("\t".join(format(x, ".6e") for x in line), file=filehandle)
    filehandle.write("-----------------------------\n\n")
    return filehandle

def filename_from_path(mypath):
    """
    Returns as a string the name of the file, without file extension, from the given path.
    """
    mypath = mypath.replace('\\','/') # in case the path is given as 'C:\\folder1\\folder2\\file.txt'
    name = mypath.split('/')[-1] # name is something like 'file.txt'
    name = name.split('.')[0] # remove file extension, now name is something like 'file'

    return name

