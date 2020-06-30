# Description
This is a Python 3 script written mainly to compliment the eMERLIN pipeline https://github.com/e-merlin/eMERLIN_CASA_pipeline
to self calibrate a CASA dataset. It is based on an alorithm of Javier Moldon, but extended to allow offset mapping of a suitable source, This is useful for wide-field survey data where there probably isn't a bright enough source in the middle of the field. The script should be general enough for any CASA based data with the appropiate change of parameters. 

Mapping and phase-shifting are done with wsclean and chgcentre of A.Offringa, calibration via gaincal in CASA and parameters read from a yml file using pyyaml.
