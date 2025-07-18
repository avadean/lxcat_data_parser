LXCat data parser
=================

A set of tools developed at `the High Voltage Lab (HVL) of ETH Zurich`_, for reading/writing electron scattering cross sections data, in a format compatible with `the LXCat project`_.

Free software: GNU General Public License v3

Installation
------------

>>> pip install lxcat_data_parser

Example
-------

To load an electron scattering cross section set::

	>>> import lxcat_data_parser as ldp
	>>> data = ldp.CrossSectionSet("N2_data.txt")

The loaded set can be modified and saved again (here the ELASTIC cross section is multiplied by 10)::

	>>> for cross_section in data.cross_sections:
	>>>     if cross_section.type == ldp.CrossSectionTypes.ELASTIC:
	>>>         cross_section.data["cross section"] *= 10
	>>> data.write("N2_data_rescaled.txt")

Cross section data format
-------------------------

Description of the data format taken from `the LXCat project`_.
In downloaded files, each collision process is defined by a block consisting of:

* 1st line: Keyword in capitals indicating the type of the collision. Possible collision types are ELASTIC, EFFECTIVE, EXCITATION, IONIZATION, or ATTACHMENT (capital letters required, key words are case sensitive), where "ELASTIC" is used to denote the elastic momentum transfer cross section and where "EFFECTIVE" denotes the total momentum transfer cross section (sum of elastic momentum transfer and total inelastic cross sections).  The latter is useful for solving the Boltzmann equation in the 2-term approximation.

* 2nd line: Name of the target particle species. This name is a character string, freely chosen by the user, e.g. "Ar". Optionally for excitation processes, the name of the corresponding excited state can be specified on the same line, separated from the first name either by arrow "->" (dash + greater than) or by double-head arrow "<->" (less than + dash + greater than), e.g. "Ar -> Ar*" and "Ar <-> Ar*", respectively. In the later case BOLSIG+ will automatically define the inverse superelastic process, constructing the superelastic cross-section by detailed balancing, and considering the indicated excited state as the target. In this case, the ratio of statistical weights must be input in the 3rd line (see below). Alternatively, superelastic collisions could be defined explicitly as excitation collisions with a negative electron energy loss with user input cross sections and species name, "Ar*", for example.

* 3rd line: For elastic and effective collisions, the ratio of the electron mass to the target particle mass. For excitation or ionization collisions, the electron energy loss (nominally the threshold energy) in eV. For attachment, the 3rd line is missing. In case of an excitation process where an excited state has been indicated on the 2nd line using double-head arrow "<->", the 3rd line must specify also ratio of the statistical weights of the final state to the initial state as the second parameter in 3rd line this is needed by BOLSIG+ to calculate the de-excitation cross-section.

* from 4th line (optionally): User comments and reference information, maximum 100 lines. The only constraint on format is that these comment lines must not start with a number.

* Finally: Table of the cross section as a function of energy. The table starts and ends by a line of dashes "------" (at least 5), and has otherwise two numbers per line: the energy in eV and the cross section in m2.

.. _`the High Voltage Lab (HVL) of ETH Zurich`: https://hvl.ee.ethz.ch
.. _`the LXCat project`: https://www.lxcat.net