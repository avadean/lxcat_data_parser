
from lxcat import CrossSectionSet, CrossSectionTypes, CrossSectionReadingError
import logging
import pytest
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def test_cross_section_set_file_not_found():
    # Test that if the file is not found, the cross section set is empty.
    with pytest.raises(FileNotFoundError):
        CrossSectionSet('this_file_does_not_exist.txt')


def test_cross_section_set_species_not_found():
    # Test that if the species is not found, the cross section set is empty.
    with pytest.raises(CrossSectionReadingError):
        CrossSectionSet('tests/test_data/N2_Phelps.txt', imposed_species='CO2')
    with pytest.raises(CrossSectionReadingError):
        CrossSectionSet('tests/test_data/N2_Phelps.txt', imposed_species='CO2',
                        imposed_database='Phelps database')


def test_cross_section_set_database_not_found():
    # Test that if the database is not found, the cross section set is empty.
    with pytest.raises(CrossSectionReadingError):
        CrossSectionSet('tests/test_data/N2_Phelps.txt',
                        imposed_database='Siglo database')
    with pytest.raises(CrossSectionReadingError):
        CrossSectionSet('tests/test_data/N2_Phelps.txt', imposed_species='N2',
                        imposed_database='Siglo database')


def test_cross_section_set_output():
    # Read the same dataset, with and without imposed parameters, and check equality.
    data = CrossSectionSet('tests/test_data/N2_Phelps.txt')
    data2 = CrossSectionSet('tests/test_data/N2_Phelps.txt', imposed_species='N2',
                            imposed_database='Phelps database')
    # test if the data is read correctly:
    assert data.database == 'Phelps database'
    assert data.species == 'N2'
    assert data.cross_sections[0].type == CrossSectionTypes.ELASTIC
    assert len(data.cross_sections[1].data['energy']) == 25
    assert data.cross_sections[0].info["PROCESS"] == 'E + N2 -> E + N2, Elastic'
    # test the equality of first cross sections
    assert data.cross_sections[0] == data2.cross_sections[0]
    # test the equality of cross section sets
    assert data == data2


def test_cross_section_set_write():
    # Test that the data is correctly written, without information loss
    data = CrossSectionSet('tests/test_data/N2_Phelps.txt')
    data.write('tests/test_data/N2_Phelps_copy.txt')
    data2 = CrossSectionSet('tests/test_data/N2_Phelps_copy.txt')
    assert data == data2


def test_cross_section_set_equality():
    # Test that the comparison between sets works
    data = CrossSectionSet('tests/test_data/N2_Phelps.txt')
    # same set with cross sections in a different order
    data2 = CrossSectionSet('tests/test_data/N2_Phelps_different_order.txt')
    data3 = CrossSectionSet('tests/test_data/N2_Phelps_wrong_value.txt')
    assert data == data2
    assert data != data3
