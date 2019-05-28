
from lxcat.import_tools import CrossSectionSet, CrossSectionType
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# lxcat_swarm_data = import_lxcat_swarm_data('Z:/projects/Sparx/10_src/Python/LXcat_tools_package/lxcat/test_data/Bhalla_1960_alphaN.txt')
# print(lxcat_swarm_data['alphaN'])

def test_CrossSectionSet_file_not_found():
	# test what happens if the file is not found	
	data = CrossSectionSet('this_file_does_not_exist.txt')
	assert not data.cross_sections

def test_CrossSectionSet_species_not_found():
	# test what happens if the species is not found
	data = CrossSectionSet('tests/test_data/N2_Phelps.txt','CO2')
	assert not data.cross_sections

def test_CrossSectionSet_output():
	# test if the data was read correctly
	data = CrossSectionSet('tests/test_data/N2_Phelps.txt')
	assert data.cross_sections[0].collision_type == CrossSectionType('ELASTIC')
	assert data.cross_sections[0] == data.cross_sections[0]
	assert data.database == 'Phelps database'
	assert data.cross_sections[0].species == 'N2'
	assert data.cross_sections[0].other_information["PROCESS"] == 'E + N2 -> E + N2, Elastic'

def test_CrossSectionSet_write():
	# test is the data is correctly written
	data = CrossSectionSet('tests/test_data/N2_Phelps.txt')
	data.write('tests/test_data/N2_Phelps_2.txt')
	data2 = CrossSectionSet('tests/test_data/N2_Phelps.txt')
	assert data == data2

test_CrossSectionSet_file_not_found()
test_CrossSectionSet_species_not_found()
test_CrossSectionSet_output()
test_CrossSectionSet_write()