#!/usr/bin/python

from gimpfu import *
import math
import time
from array import array

def plugin_main(img, input_layer):
    width = input_layer.width
    height = input_layer.height
    
    # layer # multiply
    layer = gimp.Layer(img, 
                                    "vintage_layer",
                                     width, height, 
                                     RGB_IMAGE,
                                     100, 
                                     MULTIPLY_MODE) 
     

    img.add_layer(layer, 0)
    # fill layer with color #R250.G220.B180
    gimp.set_foreground(250, 220, 180)
    pdb.gimp_bucket_fill(layer,  FG_BUCKET_FILL, NORMAL_MODE ,  100, 255, FALSE, 0, 0)
    
    
    img.flatten()
    layer = img.layers[0]	
    # courve red low +10; green low + 40; blue low + 100
    pdb.gimp_curves_spline(layer, HISTOGRAM_RED,   4, [0, 5, 255, 255])
    pdb.gimp_curves_spline(layer, HISTOGRAM_GREEN, 4, [0, 20, 255, 255])
    pdb.gimp_curves_spline(layer, HISTOGRAM_BLUE,  4, [0, 50, 255, 255])

    # brightnes+contrast top 230 mid 1,2
    pdb.gimp_curves_spline(layer, HISTOGRAM_VALUE, 6, [0, 0, 127, 152, 255, 230])
    
    # too much contrast by the following line
    #pdb.gimp_curves_spline(input_layer, HISTOGRAM_VALUE, 6, [0, 0, 64, 44, 192, 216, 255, 255])
    
    layer.flush()
    #pdb.gimp_displays_flush()

register(
        "summer_effect",
        "make image look like vintage or summer effect",
        "make image look like vintage or summer effect",
        "ja-k",
        "ja-k",
        "2012",
        "<Image>/Filters/Light and Shadow/Summer Effect...",
        "RGB*, GRAY*",
        [
         #(PF_BOOL, "fCombine", "combine RGB", False)
         ],
         
        [],
        plugin_main)

main()

