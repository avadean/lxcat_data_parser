import import_tools as imp

imp.filename_from_path('pa/t.test')

lxcat_swarm_data = imp.import_lxcat_swarm_data('Z:/projects/Sparx/10_src/Python/LXcat_tools_package/lxcat/test_data/Bhalla_1960_alphaN.txt')
print(lxcat_swarm_data['Parameter'])

imp.import_lxcat_cross_sections('Z:/projects/Sparx/10_src/Python/LXcat_tools_package/lxcat/test_data/N2_Phelps.txt')
