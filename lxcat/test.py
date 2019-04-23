import import_tools as imp

imp.filename_from_path('pa/t.test')

lxcat_swarm_data = imp.import_lxcat_swarm_data('Z:/projects/Sparx/10_src/Python/LXcat_tools_package/lxcat/test_data/Bhalla_1960_alphaN.txt')
print(lxcat_swarm_data['alphaN'])

data = imp.CrossSectionSet('Z:/projects/Sparx/10_src/Python/LXcat_tools_package/lxcat/test_data/N2_Phelps.txt')
print(data.xsections[0].collision_type == imp.CrossSectionType('ELASTIC'))
print(data.xsections[0].values)

data.xsections[0].values = data.xsections[0].values*10

data.write('Z:/projects/Sparx/10_src/Python/LXcat_tools_package/lxcat/test_data/N2_Phelps_rescaled.txt')

print('finished')