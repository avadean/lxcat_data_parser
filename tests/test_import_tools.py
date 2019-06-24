
from lxcat.import_tools import CrossSectionSet, CrossSectionTypes
import logging
import pytest
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


# lxcat_swarm_data = import_lxcat_swarm_data('Z:/projects/Sparx/10_src/Python/LXcat_tools_package/lxcat/test_data/Bhalla_1960_alphaN.txt')
# print(lxcat_swarm_data['alphaN'])

def test_CrossSectionSet_file_not_found():
	logging.info('Test that if the file is not found, the cross section set is empty.')
	with pytest.raises(FileNotFoundError):
		CrossSectionSet('this_file_does_not_exist.txt')

def test_CrossSectionSet_species_not_found():
	logging.info('Test that if the species is not found, the cross section set is empty.')
	data = CrossSectionSet('tests/test_data/N2_Phelps.txt', imposed_species='CO2')
	assert data.species == 'CO2' and data.database == '' and not data.cross_sections
	data = CrossSectionSet('tests/test_data/N2_Phelps.txt', imposed_species='CO2', imposed_database='Phelps database')
	assert data.species == 'CO2' and data.database == 'Phelps database' and not data.cross_sections

def test_CrossSectionSet_database_not_found():
	logging.info('Test that if the database is not found, the cross section set is empty.')
	data = CrossSectionSet('tests/test_data/N2_Phelps.txt', imposed_database='Siglo database')
	assert data.species == '' and data.database == 'Siglo database' and not data.cross_sections
	data = CrossSectionSet('tests/test_data/N2_Phelps.txt', imposed_species='N2', imposed_database='Siglo database')
	assert data.species == 'N2' and data.database == 'Siglo database' and not data.cross_sections

def test_CrossSectionSet_output():
	logging.info('Read the same dataset, with and without imposed parameters, and check equality.')
	data = CrossSectionSet('tests/test_data/N2_Phelps.txt')
	data2 = CrossSectionSet('tests/test_data/N2_Phelps.txt', imposed_species='N2', imposed_database='Phelps database')
	# test if the data is read correctly:	
	assert data.database == 'Phelps database'
	assert data.species == 'N2'
	assert data.cross_sections[0].type == 'ELASTIC'
	assert data.cross_sections[0].other_information["PROCESS"] == 'E + N2 -> E + N2, Elastic'
	# test the equality of first cross sections
	assert data.cross_sections[0] == data2.cross_sections[0]
	# test the equality of cross section sets
	assert data == data2	

def test_CrossSectionSet_write():
	logging.info('Test that the data is correctly written, without information losses')
	data = CrossSectionSet('tests/test_data/N2_Phelps.txt')
	data.write('tests/test_data/N2_Phelps_2.txt')
	data2 = CrossSectionSet('tests/test_data/N2_Phelps.txt')
	assert data == data2

# test_CrossSectionSet_file_not_found()
# test_CrossSectionSet_species_not_found()
# test_CrossSectionSet_database_not_found()
# test_CrossSectionSet_output()
# test_CrossSectionSet_write()
