#-------------------------------------------------------------------------------
# Name:        vector to raster
# Purpose:     converts vector files to raster files
#
# Author:      caleb
#
# Created:     08/08/2022
# Copyright:   (c) Motor_AI 2022

#-------------------------------------------------------------------------------

import rasterio as rio
from rasterio import features

from rasterio.plot import show
from matplotlib import pyplot as plt
from shapely.geometry import Point,Polygon
import geopandas as gpd


from rasterio.transform import Affine
import numpy as np



def vector_to_raster(input_vector,input_raster,output_raster,pixel_height_metres=0.2,pixel_width_metres=0.2,projection_crs="EPSG:25833"):
    try:
        vector_gpd=gpd.read_file(input_vector)#if loading a shp or geojson file from disc
    except:
        vector_gpd=input_vector #if loading a gpd file
    if vector_gpd.crs!=projection_crs:
        vector_gpd=vector_gpd.to_crs(projection_crs) #convert to utm coordinates

    ###get the geometry of the vector layer
    geom=[points for points in vector_gpd.geometry]

    imagery=rio.open(input_raster)
    out_meta=imagery.meta
    out_meta.update({"count":1})

    ### rasterize

    rasterized=features.rasterize(geom, out_shape=(imagery.shape[0],imagery.shape[1]),fill=0,out=None,transform=imagery.transform,all_touched=False,dtype=rio.uint8)

    #will not out put the raster mask but if this is needed do include the "output_raster" in the functions inputs
    with rio.open(output_raster,"w",**out_meta) as dst_file:
        dst_file.write(rasterized,1)

    return rasterized,imagery




