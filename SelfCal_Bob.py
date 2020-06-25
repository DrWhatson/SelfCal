import numpy as np
import sys, os
import yaml
from numbers import Number

tmpvis_default = 'Shift.ms'

wsclean_version = 'wsclean'
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
                     'table':'gcal.0',
                     'solint':'inf',
                     'gaintype':'G',
                     'calmode':'p',
                     'minsnr': 2.5}

split_default = {'outvis':'SelfCald.ms',
                 'script':'split.py'}

pipeline_default = {'cycles': 1,
                    'copy': False,
                    'chgcentre_src': False,
                    'wsclean0': False,
                    'gain0': False,
                    'wsclean1': False,
                    'gain1': False,
                    'wsclean2': False,
                    'gain2': False,
                    'wsclean3': False,
                    'gain3': False,
                    'wsclean4': False,
                    'chgcentre_field': False,
                    'split': False}

############## Routines

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


def generate_wsclean_command(vis,parms,defaults):

    if 'version' in parms.keys():
        cmd = parms['version']
    else:
        cmd = wsclean_version

    for key in wsclean_defaults.keys():
        cmd += add_cmd_option(key,parms,defaults)

    return cmd+' '+vis


def update_defaults(parms,defaults):

    for key in parms.keys():
        defaults[key] = parms[key]


def get_gaincal_option(key,parms,defaults):

    if key in parms.keys():
        val = parms[key]
    else:
        val = defaults[key]
        print('Warning: No {:s} in parms file, using default'.format(key),val)
    return val


def init():

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

    return vis, parms

############################# Main prog #######################

vis, parms = init()

######## Get pipeline list

if 'Pipeline' in parms.keys():  # Check in parms file
    pipeline = parms['Pipeline']
    if pipeline==None:
        exit("Error: Empty Pipeline in parms file")
else:
    exit("Error: No Pipeline in parms file")

do_copy = get_gaincal_option('copy',pipeline,pipeline_default)
do_chgcentre_src= get_gaincal_option('chgcentre_src',pipeline,pipeline_default)
do_wsclean0 = get_gaincal_option('wsclean0',pipeline,pipeline_default)
do_gain0 = get_gaincal_option('gain0',pipeline,pipeline_default)
do_wsclean1 = get_gaincal_option('wsclean1',pipeline,pipeline_default)
do_gain1 = get_gaincal_option('gain1',pipeline,pipeline_default)
do_wsclean2 = get_gaincal_option('wsclean2',pipeline,pipeline_default)
do_gain3 = get_gaincal_option('gain3',pipeline,pipeline_default)
do_wsclean4 = get_gaincal_option('wsclean4',pipeline,pipeline_default)
do_chgcentre_field = get_gaincal_option('chgcentre_field',pipeline,pipeline_default)
do_split = get_gaincal_option('split',pipeline,pipeline_default)

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
if do_copy:
    print(copy_cmd)
    status = os.system(copy_cmd)
    print(status)

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
if do_chgcentre_src:
    print(chgcen_cmd)
    status=os.system(chgcen_cmd)
    print(status)

######### WSclean source

try:  # Check wsclean parameters are present
    ws_parms = parms['wsclean0']
except KeyError:
    exit("KeyError: missing wsclean entry in params file")

ws_cmd = generate_wsclean_command(tmpvis,ws_parms,wsclean_defaults)
if do_wsclean0:
    print(ws_cmd)
    status = os.system(ws_cmd)
    print(status)

############### Calibration pass

if 'gaincal0' in parms.keys():  # Check in parms file
    cal_parms = parms['gaincal0']
else:
    print("Warning: no gaincal0 in parms file, using defaults")
    cal_parms = cal_parms_default

##### Make cal_dir

cal_dir = get_gaincal_option('cal_dir',cal_parms,cal_parms_default)
#print(cal_dir)

if os.path.isdir(cal_dir):
    exit("Error: Cal_dir {:s} exists already".format(cal_dir)) # Play it safe

mkdir_cmd = "mkdir {:s}".format(cal_dir)
if do_gain0:
    print(mkdir_cmd)
    status = os.system(mkdir_cmd)
    print(status)

###### Touch callib file

callib = get_gaincal_option('callib',cal_parms,cal_parms_default)
callib = "./{:s}/{:s}".format(cal_dir,callib)
touch_cmd = "touch {:s}".format(callib)
if do_gain0:
    print(touch_cmd)
    status=os.system(touch_cmd)
    print(status)

##### Get options

caltable = get_gaincal_option('table',cal_parms,cal_parms_default)
caltable = "./{:s}/{:s}".format(cal_dir,caltable)
solint = get_gaincal_option('solint',cal_parms,cal_parms_default)
minsnr = get_gaincal_option('minsnr',cal_parms,cal_parms_default)
gaintype = get_gaincal_option('gaintype',cal_parms,cal_parms_default)
calmode = get_gaincal_option('calmode',cal_parms,cal_parms_default)
cal_pyfile = get_gaincal_option('script',cal_parms,cal_parms_default)

###### Generate cal python script

cal_script = "from callibrary import applycaltocallib\n"

cal_line_1 = "gaincal('{:s}', solint='{:s}', docallib=True, caltable='{:s}',\n".format(tmpvis,solint,caltable)
cal_line_1+= "    minsnr={:3.1f},callib='{:s}', gaintype='{:s}', calmode='{:s}')\n".format(minsnr,callib,gaintype,calmode)

cal_line_2 = "applycaltocallib(filename='{:s}', append=True, gaintable='{:s}',\n".format(callib,caltable)
cal_line_2+= "    calwt=False)\n"

cal_line_3 = "applycal('{:s}', docallib=True, callib='{:s}')\n".format(tmpvis,callib)

#print(cal_script)
#print(cal_line_1)
#print(cal_line_2)
#print(cal_line_3)

if do_gain0:
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
    status = os.system(gain_cal_cmd)
    print(status)

####### Run WSclean on new Calibration

try:  # Check wsclean parameters are present
    ws_parms1 = parms['wsclean1']
except KeyError:
    exit("KeyError: missing wsclean entry in params file")

update_defaults(ws_parms1, ws_parms)
#wsclean_defaults.pop['version'] # Don't want this in defaults
ws_cmd = generate_wsclean_command(tmpvis,ws_parms,wsclean_defaults)

if do_wsclean1:
    print(ws_cmd)
    status = os.system(ws_cmd)
    print(status)

####### chgcentre back

if not 'Field' in parms.keys():  # Check in parms file
    exit("Error: No Field defined in paprms file, don't know where to frot to")

phase_centre = parms['Field']['Centre']

chgcen_cmd = "chgcentre {:s} {:s}".format(tmpvis,phase_centre)

if do_chgcentre_field:
    print(chgcen_cmd)
    status = os.system(chgcen_cmd)
    print(status)

####### Make split script

if 'Split' in parms.keys():  # Check in parms file
    split_parms = parms['Split']
    if split_parms==None:
        exit("Error: Empty Split in parms file")
else:
        split_parms = split_default

if do_split:
    outvis = get_gaincal_option('outvis',split_parms,split_default)
    if os.path.isdir(outvis):
        exit("Error: {:s} already exists".format(outvis))

    split_pyfile = get_gaincal_option('script',split_parms,split_default)
    if os.path.isfile(split_pyfile):
        exit("Error: {:s} already exists".format(split_pyfile))

    split_line = "split(vis={:s}, outputvis={:s}, datacolumn='corrected', width=1, timebin='0s')\n".format(tmpvis,outvis)
#print(split_line)


    split_out = open(split_pyfile,'w')
    split_out.write(split_line)
    split_out.close()
    split_cmd = "casa --nogui -c {:s}".format(split_pyfile)
    print(split_cmd)
    status = os.system(split_cmd)
    print(status)
