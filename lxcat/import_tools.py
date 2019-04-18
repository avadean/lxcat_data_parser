import numpy as np


def import_lxcat_cross_sections(mypath):
    """
    Read a "*.txt" file containing an electron scattering cross section set downloaded from LXcat and returns the values of the cross sections in a dictionary.
    """
    data = {}
    with open(mypath) as fh:
        for fh_line in fh:
            if 'DATABASE:' in fh_line:  # find the name of the database
                data['database'] = fh_line[9:].strip()
                break
        print(data)

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
        for fh_line in fh:
            if '---' in fh_line:
                break # find the first occurence of '---' start of tabulated data
        for fh_line in fh:
            if '---' in fh_line:
                break
            else:
                s = fh_line.split()
                data['E/N'].append(float(s[0]))
                data[infos[2]].append(float(s[1]))

    data['E/N'] = np.asarray(data['E/N'])
    data[infos[2]] = np.asarray(data[infos[2]])

    return data


def filename_from_path(mypath):
    """
    Returns as a string the name of the file, without file extension, from the given path.
    """
    mypath = mypath.replace('\\','/') # in case the path is given as 'C:\\folder1\\folder2\\file.txt'
    name = mypath.split('/')[-1] # name is something like 'file.txt'
    name = name.split('.')[0] # remove file extension, now name is something like 'file'

    return name

