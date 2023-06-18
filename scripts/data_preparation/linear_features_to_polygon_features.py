#-------------------------------------------------------------------------------
# Name:         linear features to polygon features
# Purpose:       #generating polygons from lines

#
# Author:      caleb,
# other
#  sources:    https://stackoverflow.com/questions/64042379/shapely-is-valid-returns-true-to-invalid-overlap-polygons
#
# Created:     03/08/2022
# Copyright:   (c) Motor AI 2022

#-------------------------------------------------------------------------------


import rasterio as rio

import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import Point,Polygon,LineString
import numpy as np



def create_polygons_from_lines(input_file,output_folder,output_file_name='polygons_road_features.shp', coord_system="EPSG:4326"):
    road=gpd.read_file(input_file) #read file

    #prepare a dictionary to hold items
    geo_dict={"id":[],"lane_count":[],"max_width":[],"min_width":[],"lane_dot":[],"lane_type":[],"av_curv":[],"start_conn":[],"end_conn":[],"geometry":[]}
    index=0
    for i in range(len(road)):
        try:

            if road["Tile_ID"][i]==road["Tile_ID"][i+1] and road["lane_grp"][i]==road["lane_grp"][i+1] \
             and road["lane_no"][i]==road["lane_no"][i+1] and road["lane_count"][i]==road["lane_count"][i+1] \
             and road["Boundary"][i]=="left boundary" and road["Boundary"][i+1]=="right boundary":#the first boundary inndex in table is left

                #Extract the geometries of the two lines
                line_1=road["geometry"][i]
                line_2=road["geometry"][i+1]

                #list to hold all of the two lines point coordinates
                coords_of_lines=[] #nb do not use same iteration alphabets to avoid confusion
                for k in range(len(line_1.coords)):
                    coords_of_lines.append(line_1.coords[k])

                for j in range(len(line_2.coords)):
                    coords_of_lines.append(line_2.coords[j])

                #create a polygon for every two lines
                polygon_geom=Polygon(coords_of_lines)

                #store attributes in the previously created dictionary
                geo_dict["geometry"].append(polygon_geom)
                geo_dict["id"].append(index)

                geo_dict["lane_count"].append(road["lane_count"][i])
                geo_dict["max_width"].append(road["max_width"][i])
                geo_dict["min_width"].append(road["min_width"][i])
                geo_dict["lane_dot"].append(road["lane_dot"][i])
                geo_dict["lane_type"].append(road["lane_type"][i])
                geo_dict["av_curv"].append(road["av_curv"][i])
                geo_dict["start_conn"].append(road["start_conn"][i])
                geo_dict["end_conn"].append(road["end_conn"][i])


                index+=1
        except: pass

    new_gpd=gpd.GeoDataFrame(geo_dict,crs=coord_system)
    new_gpd.to_file(output_folder+"/"+output_file_name)
    return new_gpd

def identify_valid_polygon_geom(input_gpd):

    """ Run this before carrying out dissolving

        Identifies Valid geometries and outputs as geopandas file"""

    # identify polygons with valid geometries...
    valid_ids_list=[]
    invalid_ids_list=[]
    input_gpd["validity"]=input_gpd.is_valid
    for i in range(len(input_gpd)):

        if input_gpd["validity"][i]==True:

            valid_ids=i
            valid_ids_list.append(valid_ids)
        else:
            invalid_ids=i
            invalid_ids_list.append(invalid_ids)

    valid_geoms_gpd=input_gpd.loc[valid_ids_list]
    return valid_geoms_gpd


def get_overlapping_polygons(input_gpd,output_folder):
    """identifies overlapping geometry index...
    #...Suitable when looking for intersections or overlppping polygons"""

    overlapping_index=input_gpd.sindex.query_bulk(input_gpd.geometry,predicate='overlaps')
    unique_overlapping_index=np.unique(overlapping_index).tolist()


    overlap_gpd=input_gpd.loc[unique_overlapping_index]
    overlap_gpd.to_file(output_folder+'/Overlapping_polygons.shp')

    return overlap_gpd


def dissolve_polygons(input_gpd):

    """before  dissolving polygons,
    make sure that they are valid
    i.e. run the "identify_valid_polygon_geoms" first """

    #create a field to dissolve the features with.
    input_gpd["dissolved"]=0

    #create a dissolved polygon feature

    dissolved_gpd=input_gpd.dissolve(by="dissolved")

    #NB saving huge files as a geojson at times leads to problems. Save as an shp
    ### will not save for now. Incase this is needed, include the "output_folder" in the function's input
    ##dissolved_gpd.to_file(output_folder +'/dissolved_polygons.shp')

    return dissolved_gpd


def create_lane_bounds_polygons(input_file,output_folder,buffer_dist_metres=0.5, projection_crs="EPSG:25833"):

    """identifies lane boundaries and
    creates polygons covering the lane boundary"""

    road=gpd.read_file(input_file) #read file
    if road.crs!=projection_crs:
        road=road.to_crs(projection_crs) #convert to utm coordinates

    #prepare a dictionary to hold items
    geo_dict={"id":[],"material":[],"pattern":[],"colour":[],"geometry":[]}
    index=0
    for i in range(len(road)):
        try:

            if road["b_material"][i]!="no data":

                #Extract the geometries of the line
                line=road["geometry"][i]

                #create a polygon buffer
                line_buffer_geom=line.buffer(buffer_dist_metres,cap_style=2) #cap_style indicates the buffer end regions, either round (cap_style 1) or flat (cap_style 2)

                #store attributes in the previously created dictionary
                geo_dict["geometry"].append(line_buffer_geom)
                geo_dict["id"].append(index)

                geo_dict["material"].append(road["b_material"][i])
                geo_dict["pattern"].append(road["b_style"][i])
                geo_dict["colour"].append(road["b_color"][i])



                index+=1
        except: pass

    lane_bounds_gpd=gpd.GeoDataFrame(geo_dict,crs=projection_crs)
    lane_bounds_gpd.to_file(output_folder+'/Lane_boundaries_markings_test.shp')
    return lane_bounds_gpd





def clip_vector_by_raster_bounds(image_file,vector_gpd):
    """
    incase a vector data corresponding to a given image tile is needed
    """
    image=rio.open(image_file)
    projection=image.crs
    vector_gpd=vector_gpd.to_crs(projection)
    image_bounds_polygon=Polygon([(image.bounds[0],image.bounds[1]),(image.bounds[2],image.bounds[1]),(image.bounds[2],image.bounds[3]),(image.bounds[0],image.bounds[3]),(image.bounds[0],image.bounds[1])])

    image_bounds_gpd=gpd.GeoDataFrame({"id":[1],"geometry":image_bounds_polygon},crs=image.crs)
    vector_gpd_clipped=vector_gpd.clip(image_bounds_polygon)

    return vector_gpd_clipped,image_bounds_gpd


