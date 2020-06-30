# Description
This is a Python 3 script written mainly to compliment the eMERLIN pipeline https://github.com/e-merlin/eMERLIN_CASA_pipeline
to self calibrate a CASA dataset. It is based on an alorithm of Javier Moldon, but extended to allow offset mapping of a suitable source, This is useful for wide-field survey data where there probably isn't a bright enough source in the middle of the field. The script should be general enough for any CASA based data with the appropiate change of parameters. 

Mapping and phase-shifting are done with wsclean and chgcentre of A.Offringa, calibration via gaincal in CASA and parameters read from a yml file using pyyaml.

## Dependencies
* CASA v5.5+ (https://casa.nrao.edu/)
* wsclean: (https://sourceforge.net/projects/wsclean/)
* chgcentre (https://sourceforge.net/projects/wsclean/files/chgcentre-1.2/)
* PyYAML (https://pyyaml.org/)

## Quick Start
1. Find suitable point source via CASA viewer or ds9 and note RA and Dec
1. Enter source coords in parmeters file and field phase-centre
1. set input and temporary dataset names
1. Set paramaters for wsclean
1. set parameters for gaincal
1. run with python3 SelfCal_bob.py field.yml

# Parameters File
The parameter file is expected to be in YAML (YAML Ain't Markup Language) format (https://yaml.org/spec/1.2/spec.html)
YAML is a data serialization format designed for human readability and interaction with scripting languages and is implimented with PyYAML, which is a YAML parser and emitter for Python.

PyYAML should be availible via the distribution package manager or installed via pip with:

```
pip install pyyaml
```
The file has several sections 
1. Source: Source position
1. Field: Phase centre of field, needed to phase rotate data back to
1. invis: The input measurement dataset
1. tmpvis: Name to be used for temporary copied version of original dataset
1. wsclean0: Initial wsclean parameters for 1st map
1. wsclean<n>: with n = 1,2,3...etc updated parameters for subsequent wscleans
1. wsclean_last: Parameters forlast of source map once selfcal is done
1. gaincal0: Parameters for first CASA calibration process
1. gaincal<n>: with n = 1,2,3...etc updated parameters for subsequent calibration cycles
1. Split: Parameters for splitting temporary dataset to final dataset
1. Pipeline: Set number of map/calibration cycles and which bits of cript to run

Sections are named by section name followed by a colon. Parameters on on following line inset by spaces, not <TAB>!
Paramenters are defined by parameter name colon parameter value such as:
 
```yaml
Section:
    parm1: filename
    parm2: value
    parm3: 12h34m56s
    parm4: briggs 0.5
```

## Parameters
```yaml
Source:
    RA: 10h19m26.00s
    Dec: +67d52m22.0s
    
Field:
    Centre: 10h20m02.69s 67d52m21s
```
RA and Dec of source position in sexadecimal format (strictly speaking it's the centre position for map, if you  need to capture the flux from several sources
Also the position phase centre of the field also in sexadecimal but on one line

```yaml
invis: test_avg_1020+6752.ms
tmpvis: Shift.ms
```

Name of input measurement set and tmp file to copy. Dataset is copied to be sure the original doesn't get corrupted




