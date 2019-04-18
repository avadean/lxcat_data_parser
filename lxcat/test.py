import import_tools as imp

imp.filename_from_path('pa/t.test')

lxcat_swarm_data = imp.import_lxcat_swarm_data('Z:/projects/Sparx/07_own_publications/02_journals/2019_CO2/data/Other_references/Bhalla_1960_alphaN.txt')
print(lxcat_swarm_data['Parameter'])
