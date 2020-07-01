# Description
This is a Python 3 script written mainly to compliment the eMERLIN pipeline https://github.com/e-merlin/eMERLIN_CASA_pipeline
to self calibrate a CASA dataset. It is based on an alorithm of Javier Moldon, but extended to allow offset mapping of a suitable source, This is useful for wide-field survey data where there probably isn't a bright enough source in the middle of the field. The script should be general enough for any CASA based data with the appropiate change of parameters. Due to the blurring of sources in averaged dataset when phase rotating, this should only really be used for unaveraged or very lightly averaged datasets. For averaged datasets the chgcentre part can be flagged out in the parameters file, but a bigger map will probably be needed. 

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
1. run with python3 SelfCal_shift.py field.yml

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

```yaml


wsclean0:
    version: wsclean
    j:
    field:
    data-column: DATA
    scale: 0.05arcsec
    size: 1000 1000
    gain: 0.2
    mgain: 0.8
    weight: briggs 0.5
    niter: 1000
    auto-threshold: 3
    auto-mask: 5
    fits-mask:
    clean-border: 5
    name: test0a

wsclean1:
    data-column: CORRECTED_DATA
    name: test1a

wsclean2:
    name: test2a

wsclean_last:
    name: test3a
```
You can select which version od wsclean to run (wsclean-2.8 etc) assuming it is on your system PATH. You can use give the the full path name if it is not in PATH
The name of the parameter is the same as the wsclean option. You can force a parameter not to appear in the wsclean command by leaving the parameter value blank, if you want to override and eliminate a default parameter Also parameters are all reused in the next iteratation usless they are redined

```yaml
gaincal0:
    cal_dir: calibration
    callib: callib.txt
    table: gcal.0
    solint: inf
    gaintype: G
    calmode: p
    minsnr: 2.5
    script: gcal0.py

gaincal1:
    table: gcal.1
    solint: 120s
    script: gcal1.py

gaincal2:
    table: gcal.2
    solint: 60s
    script: gcal2.py
```
Similary with the cal cycle which is run as a call to CASA using a python script with the name given by the "script" parameter. The callib system is used with the cal table held in the "cal_dir" directory. Again parameters are reused between iterations

```yaml
Split:
    outvis: SelfCald.ms
    script: split.py
```
The split section just defines the name for output dataset and the python script name to implement it. Averaging can also be done at this point

```yaml
Pipeline:
    cycles: 3
    start: 0
    copy: True
    make_cal_dir: True
    chgcentre_src: True
    wsclean_last: True
    chgcentre_field: True
    split: True
```
Rather like the eMERLIN pipeline, which bits of the script are run can be defined here. 
Cycles sets the number of map and calibration cycles to go through.
Start sets the first map & cal cycle if the script need to restart from a intermediate state (ie something crashed)
