
# This is the main file for the SOLWEIG1D model, python version

import numpy as np
import Solweig_v2015_metdata_noload as metload
import Solweig1D_2019a_calc as so
from clearnessindex_2013b import clearnessindex_2013b
import matplotlib.pylab as plt

# Settings
mainfolder = 'C:/Users/xlinfr/Documents/PythonScripts/SOLWEIG/'
infolder = mainfolder + 'SOLWEIGdata/'
metfilepath = infolder + 'gbg19970606_2015a_nodirect.txt'
onlyglobal = 1  # 1 if only global radiation exist
landcovercode = 0  # according to landcovrclasses_2018a_orig.txt
metfile = 1  # 1 if time series data is used
useveg = 1  # 1 if vegetation should be considered
ani = 1
cyl = 1
elvis = 0
alt = 3.0

sh = 1.  # 0 if shadowed by building
vegsh = 1.  # 0 if shadowed by tree
svf = 0.6
if useveg == 1:
    svfveg = 0.8
    svfaveg = 0.9
    trans = 0.03
else:
    svfveg = 1.
    svfaveg = 1.
    trans = 1.

lon = 12.0
lat = 57.7
UTC = 1
absK = 0.7
absL = 0.98
PA = 'STAND'
sensorheight = 2.0
# ewall = 0.95
# eground = 0.95
# albedo_b = 0.20
# albedo_g = 0.15

# program start
if PA == 'STAND':
    Fside = 0.22
    Fup = 0.06
    height = 1.1
    Fcyl = 0.28
else:
    Fside = 0.166666
    Fup = 0.166667
    height = 0.75
    Fcyl = 0.20

if metfile == 1:
    met = np.loadtxt(metfilepath, skiprows=1, delimiter=' ')
else:
    met = np.zeros((1, 24)) - 999.
    year = 2011
    month = 6
    day = 6
    hour = 12
    minu = 30

    if (year % 4) == 0:
        if (year % 100) == 0:
            if (year % 400) == 0:
                leapyear = 1
            else:
                leapyear = 0
        else:
            leapyear = 1
    else:
        leapyear = 0

    if leapyear == 1:
        dayspermonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    else:
        dayspermonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    doy = np.sum(dayspermonth[0:month - 1]) + day

    Ta = 25.
    RH = 50.
    radG = 880.
    radD = 150.
    radI = 950.

    met[0, 0] = year
    met[0, 1] = doy
    met[0, 2] = hour
    met[0, 3] = minu
    met[0, 11] = Ta
    met[0, 10] = RH
    met[0, 14] = radG
    met[0, 21] = radD
    met[0, 22] = radI

location = {'longitude': lon, 'latitude': lat, 'altitude': alt}
YYYY, altitude, azimuth, zen, jday, leafon, dectime, altmax = metload.Solweig_2015a_metdata_noload(met, location, UTC)

svfalfa = np.arcsin(np.exp((np.log((1.-svf))/2.)))

# Creating vectors from meteorological input
DOY = met[:, 1]
hours = met[:, 2]
minu = met[:, 3]
Ta = met[:, 11]
RH = met[:, 10]
radG = met[:, 14]
radD = met[:, 21]
radI = met[:, 22]
P = met[:, 12]
Ws = met[:, 9]
Twater = []

# Number of daytime hours
# Initialisation of time related variables
# if Ta.__len__() == 1:
#     timestepdec = 0.0
# else:
#     timestepdec = dectime[1] - dectime[0]
# timeadd = 0.
# timeaddE = 0.
# timeaddS = 0.
# timeaddW = 0.
# timeaddN = 0.
# firstdaytime = 1.
# bugfix so that model can start during daytime
# Parameterisarion for Lup
# if not height:
#     height = 1.1

# load landcover file
sitein = mainfolder + "landcoverclasses_2018a_orig.txt"
f = open(sitein)
lin = f.readlines()
lc_class = np.zeros((lin.__len__() - 1, 6))
for i in range(1, lin.__len__()):
    lines = lin[i].split()
    for j in np.arange(1, 7):
        lc_class[i - 1, j - 1] = float(lines[j])

# ground material parameters
ground_pos = np.where(lc_class[:, 0 ] == landcovercode)
albedo_g = lc_class[ground_pos, 1]
eground = lc_class[ground_pos, 2]
TgK = lc_class[ground_pos, 3]
Tstart = lc_class[ground_pos, 4]
TmaxLST = lc_class[ground_pos, 5]

# wall material parameters
wall_pos = np.where(lc_class[:, 0] == 99)
albedo_b = lc_class[wall_pos, 1]
ewall = lc_class[wall_pos, 2]
TgK_wall = lc_class[wall_pos, 3]
Tstart_wall = lc_class[wall_pos, 4]
TmaxLST_wall = lc_class[wall_pos, 5]

# If metfile starts at night
CI = 1.

if ani == 1:
    skyvaultalt = np.atleast_2d([])
    skyvaultazi = np.atleast_2d([])
    skyvaultaltint = [6, 18, 30, 42, 54, 66, 78]
    skyvaultaziint = [12, 12, 15, 15, 20, 30, 60]
    for j in range(7):
        for k in range(1, int(360/skyvaultaziint[j]) + 1):
            skyvaultalt = np.append(skyvaultalt, skyvaultaltint[j])

    skyvaultalt = np.append(skyvaultalt, 90)

    diffsh = np.zeros((145))
    svfalfadeg = svfalfa / (np.pi / 180.)
    for k in range(0, 145):
        if skyvaultalt[k] > svfalfadeg:
            diffsh[k] = 1
else:
    diffsh = []

numformat = '%3d %2d %3d %2d %6.5f ' + '%6.2f ' * 27
poi_save = np.zeros((1, 32))

header = 'yyyy id   it imin dectime altitude azimuth kdir kdiff kglobal kdown   kup    keast ksouth ' \
                         'kwest knorth ldown   lup    least lsouth lwest  lnorth   Ta      Tg     RH    Esky   Tmrt    ' \
                         'I0     CI   Shadow  SVF_b KsideI'

data_out = mainfolder + '1Dtest.txt'
# poi_save = []
np.savetxt(data_out, [],  delimiter=' ', header=header, comments='')  # fmt=numformat,

for i in np.arange(0, Ta.__len__()):
    print(i)
    # Daily water body temperature
    if (dectime[i] - np.floor(dectime[i])) == 0 or (i == 0):
        Twater = np.mean(Ta[jday[0] == np.floor(dectime[i])])

    # Nocturnal cloudfraction from Offerle et al. 2003
    if (dectime[i] - np.floor(dectime[i])) == 0:
        daylines = np.where(np.floor(dectime) == dectime[i])
        alt = altitude[0][daylines]
        alt2 = np.where(alt > 1)
        rise = alt2[0][0]
        [_, CI, _, _, _] = clearnessindex_2013b(zen[0, i + rise + 1], jday[0, i + rise + 1],
                                                Ta[i + rise + 1],
                                                RH[i + rise + 1] / 100., radG[i + rise + 1], location,
                                                P[i + rise + 1])
        if (CI > 1) or (CI == np.inf):
            CI = 1

    Tmrt, Kdown, Kup, Ldown, Lup, Tg, ea, esky, I0, CI, Keast, Ksouth, Kwest, Knorth, Least, Lsouth, Lwest, \
    Lnorth, KsideI, radIo, radDo, shadow = so.Solweig1D_2019a_calc(svf, svfveg, svfaveg, sh, vegsh,  albedo_b, absK, absL, ewall,
                                                           Fside, Fup, Fcyl,
                                                         altitude[0][i], azimuth[0][i], zen[0][i], jday[0][i],
                                                         onlyglobal, location, dectime[i], altmax[0][i], cyl, elvis,
                                                         Ta[i], RH[i], radG[i], radD[i], radI[i], P[i],
                                                         Twater, TgK, Tstart, albedo_g, eground, TgK_wall, Tstart_wall,
                                                         TmaxLST, TmaxLST_wall, svfalfa, CI, ani, diffsh, trans)

    # Write to array
    poi_save[0, 0] = YYYY[0][i]
    poi_save[0, 1] = jday[0][i]
    poi_save[0, 2] = hours[i]
    poi_save[0, 3] = minu[i]
    poi_save[0, 4] = dectime[i]
    poi_save[0, 5] = altitude[0][i]
    poi_save[0, 6] = azimuth[0][i]
    poi_save[0, 7] = radIo
    poi_save[0, 8] = radDo
    poi_save[0, 9] = radG[i]
    poi_save[0, 10] = Kdown
    poi_save[0, 11] = Kup
    poi_save[0, 12] = Keast
    poi_save[0, 13] = Ksouth
    poi_save[0, 14] = Kwest
    poi_save[0, 15] = Knorth
    poi_save[0, 16] = Ldown
    poi_save[0, 17] = Lup
    poi_save[0, 18] = Least
    poi_save[0, 19] = Lsouth
    poi_save[0, 20] = Lwest
    poi_save[0, 21] = Lnorth
    poi_save[0, 22] = Ta[i]
    poi_save[0, 23] = Tg + Ta[i]
    poi_save[0, 24] = RH[i]
    poi_save[0, 25] = esky
    poi_save[0, 26] = Tmrt
    poi_save[0, 27] = I0
    poi_save[0, 28] = CI
    poi_save[0, 29] = shadow
    poi_save[0, 30] = svf
    poi_save[0, 31] = KsideI

    f_handle = open(data_out, 'ab')
    np.savetxt(f_handle, poi_save, fmt=numformat)
    f_handle.close()