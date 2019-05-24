import import_tools as imp
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# lxcat_swarm_data = imp.import_lxcat_swarm_data('Z:/projects/Sparx/10_src/Python/LXcat_tools_package/lxcat/test_data/Bhalla_1960_alphaN.txt')
# print(lxcat_swarm_data['alphaN'])

data = imp.CrossSectionSet('lxcat/test_data/N2_Phelps.txt','CO2')
data = imp.CrossSectionSet('lxcat/test_data/N2_Phelps.txt','N2')
print(data.database)
print(data.cross_sections[0].collision_type == imp.CrossSectionType('ELASTIC'))
print(data.cross_sections[0].other_information["PROCESS"])
print(data.cross_sections[0].species)

for cross_section in data.cross_sections:
	if cross_section.collision_type == imp.CrossSectionType('ELASTIC'):
	    cross_section.values *= 10

data.write('Z:/projects/Sparx/10_src/Python/LXcat_tools_package/lxcat/test_data/N2_Phelps_rescaled.txt')
