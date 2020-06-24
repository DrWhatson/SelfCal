import numpy as np
import sys, os
import yaml
from numbers import Number

tmpvis_default = 'Shift.ms'

wsclean_version = 'wsclean-2.8'
wsclean_defaults = {'j':None,
                    'field':None,
                    'data-column':'DATA',
                    'scale':'0.05arcsec',
                    'size':'512 512',
                    'gain':0.2,
                    'mgain':0.05,
                    'weight':'natural',
                    'niter':1000,
                    'auto-threshold':1.0,
                    'local-rms':False,
                    'fits-mask':None,
                    'clean-border':5,
                    'name':'test'}

cal_parms_default = {'cal_dir':'calibration',
                     'callib':'callib.txt',
                     'prefix':'gcal.',
                     'solint':'inf',
                     'gaintype':'G',
                     'calmode':'p',
                     'minsnr': 2.5}

outvis_default = {'outvis':'SelfCald.ms'}


def get_parameters(pfile):

    #Check file exists
    if not os.path.isfile(pfile):
        exit('Error: Parameters file:"{:s}" not found'.format(pfile))

    try:
        with open(pfile,'r') as config:
            parm_dic = yaml.load(config, Loader=yaml.FullLoader)

    except yaml.scanner.ScannerError:
        exit("ScannerError: Can't parse parameters file")

    return parm_dic


def add_cmd_option(key,parms,defaults):

    if key in parms.keys():
        val = parms[key]
    else:
        val = defaults[key]

    if val == None:
        val = ''
    elif isinstance(val,bool):
        if val:
            val = ' -'+key
        else:
            val = ''
    elif isinstance(val,Number):
        val = ' -'+key+' '+str(val)
    elif isinstance(val,str):
        val = ' -'+key+' '+val

    return val


def generate_WSCLEAN_command(vis,parms):

    if 'version' in parms.keys():
        cmd = parms['version']
    else:
        cmd = wsclean_version

    for key in wsclean_defaults.keys():
        cmd += add_cmd_option(key,parms,wsclean_defaults)

    return cmd+' '+vis


def get_gaincal_option(key,parms,defaults):

    if key in parms.keys():
        val = parms[key]
    else:
        val = default[key]
        print("Warning: No {:s} in parms file, using default {:s}".format(key,val))

    return val


############################# Main prog #######################

if len(sys.argv)<2:
    exit("No parameters file given")

pfile = sys.argv[1]
parms = get_parameters(pfile)

try:  # Check measurement set valid
    vis = parms['invis']
except KeyError:
    exit("KeyError: missing invis entry in params file")
if vis==None:
    exit('Error: Empty invis entry in parms file')
if not os.path.isdir(vis):
    exit('Error:Measurement set :"{:s}" not found'.format(vis))


######## Copy mset to tmpp file for safety

if 'tmpvis' in parms.keys():  # Check in parms file
    tmpvis = parms['tmpvis']
    if tmpvis==None:
        exit("Error: Empty tmpvis in parms file")
    else:
        tmpvis = tmpvis_default

if os.path.isdir(tmpvis):  # Make sure doesn't exist
    exit("Error: Temp vis file {:s} already exists".format(tmpvis))

copy_cmd = "cp -R {:s} {:s}".format(vis,tmpvis)
print(copy_cmd)


######## Phase rotate to source

if not 'Source' in parms.keys():  # Check in parms file
    exit("Error: No Source defined in paprms file, don't know where to frot to")

src_parms = parms['Source']

if not ('RA' in src_parms.keys() and 'Dec' in src_parms.keys()):
    exit("Error: Missing source coords")

    # Could done with more error checking on coords

RA = src_parms['RA']
Dec = src_parms['Dec']

chgcen_cmd = "chgcentre {:s} {:s} {:s}".format(tmpvis,RA,Dec)
print(chgcen_cmd)


######### WSclean source

try:  # Check wsclean parameters are present
    ws_parms = parms['WSCLEAN']
except KeyError:
    exit("KeyError: missing WSCLEAN entry in params file")

ws_cmd = generate_WSCLEAN_command(vis,ws_parms)
print(ws_cmd)


############### Calibration pass

if 'gaincal' in parms.keys():  # Check in parms file
    cal_parms = parms['gaincal']
else:
    print("Warning: no gaincal in parms file, using defaults")
    cal_parms = cal_parms_default

##### Make cal_dir

cal_dir = get_gaincal_option('cal_dir',cal_parms,cal_parms_default)
print(cal_dir)

if os.path.isdir(cal_dir):
    exit("Error: Cal_dir {:s} exists already".format(cal_dir)) # Play it safe

mkdir_cmd = "mkdir {:s}".format(cal_dir)
print(mkdir_cmd)

###### Touch callib file

callib = get_gaincal_option('callib',cal_parms,cal_parms_default)
callib = "./{:s}/{:s}".format(cal_dir,callib)
touch_cmd = "touch {:s}".format(callib)
print(touch_cmd)

##### Get options

prefix = get_gaincal_option('prefix',cal_parms,cal_parms_default)
caltable = "./{:s}/{:s}{:d}".format(cal_dir,prefix,0)
solint = get_gaincal_option('solint',cal_parms,cal_parms_default)
minsnr = get_gaincal_option('minsnr',cal_parms,cal_parms_default)
gaintype = get_gaincal_option('gaintype',cal_parms,cal_parms_default)
calmode = get_gaincal_option('calmode',cal_parms,cal_parms_default)

###### Generate cal python script

cal_script = "from callibrary import applycaltocallib\n"

cal_line_1 = "gaincal('{:s}', solint='{:s}', docallib=True, caltable='{:s}',\n".format(tmpvis,solint,caltable)
cal_line_1+= "    callib='{:s}', gaintype='{:s}', calmode='{:s}')\n".format(callib,gaintype,calmode)

cal_line_2 = "applycaltocallib(filename='{:s}', append=True, gaintable='{:s}',\n".format(callib,caltable)
cal_line_2+= "    calwt=False)\n"

cal_line_3 = "applycal('{:s}', docallib=True, callib='{:s}')\n".format(tmpvis,callib)

#print(cal_script)
#print(cal_line_1)
#print(cal_line_2)
#print(cal_line_3)

cal_pyfile = "{:s}{:d}.py".format(prefix,0)
print(cal_pyfile)

if os.path.isfile(cal_pyfile):
    exit("Error: python file {:s} already exists".format(cal_pyfile))

cal_out = open(cal_pyfile,'w')
cal_out.write(cal_script)
cal_out.write(cal_line_1)
cal_out.write(cal_line_2)
cal_out.write(cal_line_3)
cal_out.close()

####### Run gaincal

gain_cal_cmd = "casa --nogui -c {:s}".format(cal_pyfile)
print(gain_cal_cmd)


####### Run WSclean on new Calibration

ws_parms['data-column'] = 'CORRECTED-DATA'
ws_parms['name'] = ws_parms['name']+'2'
ws_cmd = generate_WSCLEAN_command(vis,ws_parms)
print(ws_cmd)


####### chgcentre back

if not 'Field' in parms.keys():  # Check in parms file
    exit("Error: No Field defined in paprms file, don't know where to frot to")

phase_centre = parms['Field']['Centre']

chgcen_cmd = "chgcentre {:s} {:s}".format(tmpvis,phase_centre)
print(chgcen_cmd)


####### Make split script

outvis = get_gaincal_option('outvis',parms,outvis_default)
if os.path.isdir(outvis):
    exit("Error: {:s} already exists".format(outvis))

split_line = "split(vis={:s}, outputvis={:s}, datacolumn='corrected', width=1, timebin='0s')\n".format(tmpvis,outvis)
print(split_line)
