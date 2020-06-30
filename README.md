# Description
This is a Python 3 script written mainly to compliment the eMERLIN pipeline https://github.com/e-merlin/eMERLIN_CASA_pipeline
to self calibrate a CASA dataset. It is based on an alorithm of Javier Moldon, but extended to allow offset mapping of a suitable source, This is useful for wide-field survey data where there probably isn't a bright enough source in the middle of the field. The script should be general enough for any CASA based data with the appropiate change of parameters. 

Mapping and phase-shifting are done with wsclean and chgcentre of A.Offringa, calibration via gaincal in CASA and parameters read from a yml file using pyyaml.

# Dependencies
* CASA v5.5+ (https://casa.nrao.edu/)
* wsclean: (https://sourceforge.net/projects/wsclean/)
* chgcentre (https://sourceforge.net/projects/wsclean/files/chgcentre-1.2/)
* PyYAML (https://pyyaml.org/)

# Quick Start
1. Find suitable point source via CASA viewer or ds9 and note RA and Dec
1. Enter source coords in parmeters file and field phase-centre
1. set input and temporary dataset names
1. Set paramaters for wsclean
1. set parameters for gaincal
1. run with python3 SelfCal_bob.py field.yml
