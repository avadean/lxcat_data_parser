import import_functions as imp

imp.filename_from_path('pa/t.test')

lxcat_swarm_data = imp.import_lxcat_swarm_data('Z:/projects/Sparx/07_own_publications/02_journals/2019_CO2/data/Other_references/Bhalla_1960_alphaN.txt')
print(lxcat_swarm_data)

print('############################################')

bolsig_data = imp.import_bolsig_output('test_data/output.dat')
print(bolsig_data.keys())
print(bolsig_data['CO2    Excitation    0.34 eV'])
