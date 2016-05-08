"""
#declare Rx = rand(R);
#declare Ry = rand(R);
#declare Rz = rand(R);

"""

# from http://i-simplicity.de/tutorials.html#asteroid

template = """
#version 3.7
#include "functions.inc"

#declare R = seed(``seed``);
#declare my_f_noise3d = function {
 #local Rx = rand(R);
 #local Ry = rand(R);
 #local Rz = rand(R);

    f_noise3d(x-Rx,y-Ry,z-Rz)
}

#declare BASE_SHAPE=
function
{
  sqrt(x*x+y*y+z*z) - 1
}

 camera {
  location <``cx``,``cy``,``cz``>
  look_at <0,0,0>
  up <0, 0.5, 0>
  right <0.5, 0, 0>
 }

#declare CRATER_SHAPE_TEMPLT=
function
{
  pigment
  {
    crackle form <1.5,0,0>
    color_map
    {
      [0 rgb <1.0,1.0,1.0>]
      [0.75 rgb <0.0,0.0,0.0>]
      [1 rgb <0.2,0.2,0.2>]
    }
    cubic_wave
  }
}


#declare CRATER_SHAPE=
function(x,y,z,S)
{
  CRATER_SHAPE_TEMPLT(x/S,y/S,z/S).red
}


isosurface
{
  function
    {
      BASE_SHAPE(x * ``baseX``, y * ``baseY``, z * ``baseZ``)
            + my_f_noise3d(x,y,z)
	    + .04 * CRATER_SHAPE(x,y,z,.35)
      	    + .015 * CRATER_SHAPE(x+10,y+10,z+10,.15)
      	    + .015 * CRATER_SHAPE(x,y,z,.1)
      	    + .005 * CRATER_SHAPE(z+1,x+3,y+2,.05)
      }
  contained_by{box{-1.2 1.2}}
  threshold 0
  pigment{color rgb 1}

  texture
  {
    pigment
    {
      bozo
      color_map
      {
        [0 rgb <0.3,0.3,0.3>]
        [1 rgb <1.0,1.0,1.0>]
      }
      scale 0.2
      warp
      {
        turbulence .5
        octaves 3
        omega 1.0
        lambda .7
      }
      scale 0.5
    }
  }
    finish
    {
      ambient 0.0
      diffuse 1.0
      brilliance 1.0
      specular 0.1
      roughness 0.08
    }
    normal
    {
      agate 0.13
      scale 0.08
    }
}

light_source
{
    <``lx``, ``ly``, ``lz``>, rgb <0.5,0.5,0.5>
}
"""

import random
import subprocess as sp
import numpy as np

for i in xrange(100):
    filename = 'output/test%d.pov' % i
    baseX = random.random() * 0.5 + 0.5
    baseY = random.random() * 0.3 + 0.7
    baseZ = random.random() * 0.3 + 0.7
    print (baseX, baseY, baseZ)
    cp = np.random.random(3)
    cp /= np.linalg.norm(cp)
    cx, cy, cz = cp * 5
    lx, ly, lz = cp * 2000
    with open(filename, 'w') as file:
        file.write(template
                   .replace('``seed``', str(i))
                   .replace('``baseX``', str(baseX))
                   .replace('``baseY``', str(baseY))
                   .replace('``baseZ``', str(baseZ))
                   .replace('``cx``', str(cx))
                   .replace('``cy``', str(cy))
                   .replace('``cz``', str(cz))
                   .replace('``lx``', str(lx))
                   .replace('``ly``', str(ly))
                   .replace('``lz``', str(lz))
        )
    sp.call(['povray', '+UA', '-W100', '-H100', '-D', filename])
