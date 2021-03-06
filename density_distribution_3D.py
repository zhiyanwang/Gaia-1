import astropy
import numpy as np
import matplotlib.pyplot as plt
import plotly
import plotly.plotly as py
import plotly.figure_factory as ff
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import astropy.io.fits as fits
import sys, os, time, string, math, subprocess
from scipy.stats import gaussian_kde, stats
import seaborn as sns
sns.set(color_codes=True)
import numpy.random
import scipy

#================ input data using class ===================

class DATA(object):

    def __init__(self):
        #read in data from Gaia file
        self.file=fits.open('tgas-source.fits')
        self.data_list=self.file[1]

# ================ select data with low noise ===================

data1=DATA()
#chose parallax data
parallax=data1.data_list.data['parallax'] #in mas(milliarcsecond) = 0.001 arcsecond = 1/3600000 degree
parallax_error=data1.data_list.data['parallax_error'] #error

#calculate ratio
ratio=parallax/parallax_error

#select data that we want
highSNindices = ratio > 16. #The ones with high signal to noise

#locations of data we want
#np.where(highSNindices)

#distances we want from valid data
distance=1./parallax[highSNindices] #in Kpc = 1000 parsecs = 3262 light-years

#================ calculate velocity from proper motion ===================

#proper motion right ascension and declination
pmra=data1.data_list.data['pmra'] #in mas/year
pmdec=data1.data_list.data['pmdec'] #in mas/year

#transverse velocity v = 4.74*(proper motion angular velocity[arcsec/year])*distance[parsec]*10**3 #m/s
transv_ra=4.74*pmra[highSNindices]*distance*10**3  #m/s
transv_dec=4.74*pmdec[highSNindices]*distance*10**3  #m/s

transverse_vsqared=transv_ra**2+transv_dec**2
transverse_v=transverse_vsqared**(.5)

# (04/19/2017) pytest
# define the function "transverse_velocity()" for test on Travis
def transverse_velocity(number):
    v=transverse_v[number]

    if v > 0:
        return 'Transverse velocity bigger than 0'
    elif v < 0:
        return 'Transverse velocity less than 0'
    elif v == 0:
        return 'Transverse velocity is 0'

#================ plot velocity ===================
'''
#Plot histogram of transverse velocity distribution
plt.hist(transverse_v,bins=500)

#limit on transverse velocity
plt.xlim([0,150000])

#lables for axis
plt.xlabel('Transverse Velocity [m/s]')
plt.ylabel('Number')
plt.title('Distribution of Transverse Velocity')

plt.show()
'''

#================ Get stars' coordinates in 3D of all valid data ===================

#right ascension and declination
right_ascension=data1.data_list.data['ra'] #in degree
declination=data1.data_list.data['dec'] #in degree
ra=right_ascension[highSNindices]*(3.14/180) #in radian
dec=declination[highSNindices]*(3.14/180) #in radian

# (04/04/2017) Class
# Create a class to access the coordinates later for 3D and 2D
class coordinates():
    def __init__(self):
        # Express the mesh in the cartesian system.
        self.X=distance*1000*np.cos(dec)*np.cos(ra) #in parsec = 3.262 light-years
        self.Y=distance*1000*np.cos(dec)*np.sin(ra) #in parsec = 3.262 light-years
        self.Z=distance*1000*np.sin(dec) #in parsec = 3.262 light-years

#Get the coordinates for 3D plot
coor3D = coordinates();
print (coor3D.X)

print ("Max value on X: ", coor3D.X.max())
print ("Min value on X: ", coor3D.X.min())
print ("Max value on Y: ", coor3D.Y.max())
print ("Min value on Y: ", coor3D.Y.min())
print ("Max value on Z: ", coor3D.Z.max())
print ("Min value on Z: ", coor3D.Z.min())

#================ visualize stars' position in 3D plot of all valid data ===================

#plot with ra, dec, and distance
fig=plt.figure()
ax=fig.add_subplot(111,projection='3d')

#calculate the point density
#XYZ = np.vstack([X,Y,Z])
#C = gaussian_kde(XYZ)(XYZ)(XYZ)

#fig, ax = plt.subplots()
#plt.scatter(X, Y, Z, c=C, s=100, edgecolor='')
#plt.show()

#ax.set_xlim(-10**5,10**5)
#ax.set_ylim(-10**5,10**5)
#ax.set_zlim(-10**5,10**5)


#plt.scatter(X,Y,Z,marker=".")
# The above line Produces a disk instead of sphere. With high signal to noise data, far away stars are not included,
# and the scale is not big enough to show the shape of the Milky Way (diameter 30kpc, thickness 0.3kpc)

ax.scatter(coor3D.X,coor3D.Y,coor3D.Z, 'ob', alpha=0.05, lw=0, marker=".")
# The above line works almost as ax.plot(X,Y,Z, 'ob', alpha=0.05, lw=0) or plt.plot(X,Y,Z, 'ob', alpha=0.05, lw=0)

ax.set_xlabel('Distance X [pc]')
ax.set_ylabel('Distance Y [pc]')
ax.set_zlabel('Distance Z [pc]')
plt.title('Distribution of All Valid Data')

plt.show()