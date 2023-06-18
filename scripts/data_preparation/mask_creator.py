#-------------------------------------------------------------------------------
# Name:        Mask_creator
# Purpose:     creates raster masks from vetor geometries
#
# Author:      caleb
#
# Created:     14/11/2022
# Copyright:   (c) caleb 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#inhouse modules
from folder_mng import get_training_data
from linear_features_to_polygon_features import identify_valid_polygon_geom, dissolve_polygons
from vector_raster_converter import vector_to_raster

#file management
import os

#for raster management
import numpy as np

#for vector management
import geopandas as gpd


def create_masks(data_file_list,image_patch_list):

    """creates raster masks from the vector geometry

    NB: is designed for MOTOR-AI folder structure
        Only works after the "get_training_data" function from the folder_mng.py has been run.

    data_file_list: a list containing the vectors to rasterize into masks
    image_patch_list: an array containing images corresponding to the vectors that are to be rasterized
                      this imags provide the georeferencing info for the would be mask patches
    The masks will be saved in a "raster_masks" folder within MOTOR-AI folder structure


    """

    vector_mask_list=[]
    raster_array_list=[]
    for i in range(len(data_file_list)):
        data_file=data_file_list[i]
        data_file_gpd=gpd.read_file(data_file)



        link_path=data_file.split('vector_masks')[0]
        link_name=data_file.split('vector_masks')[1].split("dop")[1].replace("grid",'mask')[:-4]

        directory_masks=os.path.join(link_path,"raster_masks")

        if not os.path.exists(directory_masks):
            os.mkdir(directory_masks)


        print(directory_masks+'/'+'dop'+link_name+".tif")


        data_file_gpd_valid=identify_valid_polygon_geom(data_file_gpd)
        data_file_gpd_valid_dissolved=dissolve_polygons(data_file_gpd_valid)


        output_file=directory_masks+'/'+'dop'+link_name+".tif"
        data_file_mask,image_patch=vector_to_raster(data_file_gpd_valid_dissolved,image_patch_list[i],output_file,pixel_height_metres=0.2,pixel_width_metres=0.2,projection_crs="EPSG:25833")
        image_array=np.dstack((image_patch.read(1),image_patch.read(2),image_patch.read(3)))

        vector_mask_list.append(data_file_mask)
        raster_array_list.append(image_array)



    return vector_mask_list,raster_array_list



###example

####NB: run get_training_data() function first to obtain the bounds and images, or markings and their subsequent images


#root_dir=r'\\MOTORAICLOUDY\Transfer\Mapping Team\Mapping_Pipeline_Training_Data'
#bounds,markings,bounds_image,markings_image=get_training_data(root_dir,mask_available='no') #the mask data does not exist

##run separately for bounds and masks
#bounds_mask_list,bounds_raster_array_list=create_masks(bounds,bounds_image)
#markings_mask_list,markings_raster_array_list=create_masks(markings,markings_image)