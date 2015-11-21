#!/usr/bin/python

from gimpfu import *
import math
import time
from array import array

def plugin_main(img, input_layer, fCombine):
    gimp.progress_init("calc diff" + input_layer.name + "...")
    
    width = input_layer.width
    height = input_layer.height
    
    input_layer_copy = input_layer.copy()  
    
    input_layer_copy.name = "source Layer Copy"
    
    img.add_layer(input_layer_copy)
    
       
    output_layer_east = gimp.Layer(img, 
                                   "working layer horizontally",
                                    width, height, 
                                    RGB_IMAGE,
                                    100,
                                    NORMAL_MODE)
      
    output_layer_south = gimp.Layer(img, 
                                    "working layer vertically",
                                     width, height, 
                                     RGB_IMAGE,
                                     100, 
                                     NORMAL_MODE) 
     
    img.add_layer(output_layer_east, 0)
    img.add_layer(output_layer_south, 0)

    srcRgn = input_layer.get_pixel_rgn(0, 0, width, height, False, False)
    
    src_pixels_array = array("B", srcRgn[0:width, 0:height])
    
    dstRgnEast = output_layer_east.get_pixel_rgn(0, 0, width, height,
                                            True, True)
    dstRgnSouth = output_layer_south.get_pixel_rgn(0, 0, width, height,
                                            True, True)
    
    pixel_size = len(srcRgn[0,0])               
    dest_pixels_array_east = array("B", "\x80" * (width * height * pixel_size))
    dest_pixels_array_south = array("B", "\x80" * (width * height * pixel_size))
    for x in range(0, width):
        for y in range(0, height):
            for c in range(pixel_size):
                #current pixel
                cur_pix = src_pixels_array[x * pixel_size  + y* width * pixel_size + c]
                
                # find south element
                try :
                    south_pix = src_pixels_array[x * pixel_size + (y+1) * width * pixel_size + c]
                except IndexError:
                    south_pix = 0
                    break
                
                # find east element
                try:
                    east_pix = src_pixels_array[(x+1) * pixel_size + y * width * pixel_size + c]
                except IndexError:
                    east_pix = 0
                    break
                
                diff_east = cur_pix - east_pix
                diff_south = cur_pix - south_pix
                
                #abs
                if diff_east < 0:
                    diff_east = diff_east * (-1)
                if diff_south < 0:
                    diff_south = diff_south * (-1)
                
                #dest_pixels[dest_pos : dest_pos + p_size] = newval
                dest_pixels_array_south[x * pixel_size +y * width * pixel_size+ c] = diff_south
                dest_pixels_array_east[x * pixel_size +y * width * pixel_size+ c] = diff_east
            
        progress = float(x)/input_layer.width
        if (int(progress * 100) % 4 == 0) :
            gimp.progress_update(progress)
        
    east_string = dest_pixels_array_east.tostring()
    south_string = dest_pixels_array_south.tostring()
    
    dstRgnEast[0:width, 0:height]  = east_string
    dstRgnSouth[0:width, 0:height] = south_string
    
    output_layer_south.flush()
    output_layer_east.flush()
    output_layer_south.merge_shadow(True)
    output_layer_south.update(0, 0, width,height)
    output_layer_east.merge_shadow(True)
    output_layer_east.update(0, 0, width,height)
    
    if fCombine:
        output_layer_south.opacity = 0.5
        output_layer_south.flush()
        output_layer_south.merge_shadow(True)
        output_layer_south.update(0, 0, width,height)
        img.flatten()
        
    
    pdb.gimp_progress_end()
    pdb.gimp_displays_flush()




register(
        "diff_to_neighbor_pixel",
        "generates image by calculating difference to neigboring bixel",
        "generates image by calculating difference to neigboring bixel",
        "ja-k",
        "ja-k",
        "2012",
        "<Image>/Image/Eval Differnece to neighbor pixel...",
        "RGB*, GRAY*",
        [
         (PF_BOOL, "fCombine", "combine RGB", False)
         ],
         
        [],
        plugin_main)

main()
