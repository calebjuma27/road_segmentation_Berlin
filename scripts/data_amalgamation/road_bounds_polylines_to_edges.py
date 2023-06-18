#-------------------------------------------------------------------------------
# Name:        road bound polylines to edges
# Purpose:      extracts boundary edges from the bound closed polyline
#
# Author:      caleb
#
# Created:     07/12/2022
# Copyright:   (c) caleb 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import geopandas as gpd
from matplotlib import pyplot as plt
from shapely.geometry import Point,Polygon,LineString
import os


def bound_edges(input_folder,output_folder,projected_coord="EPSG:25833"):

    """
    input_folder = the folder containing the road bounds polylines (appear as closed loops)
    output_folder = the folder that will house the created edges from running this function
    projected coord = The EPSG code representing the projected coordinate system of the area of interest.
    """


    bounds_polyline_list=[b for b in os.listdir(input_folder) if b.endswith('.shp')]

    #list to hold the final centrelines in geopandas format
    edges_gpd=[]

    for i in range(len(bounds_polyline_list)):
        try:
            input_file=input_folder+"/"+bounds_polyline_list[i]
            bounds_polyline=gpd.read_file(input_file)

            bounds_polyline_geom=bounds_polyline["geometry"][0]

            bounds_polyline_geom_xy=bounds_polyline_geom.coords.xy


            #to hold the line segments
            segment_to_remove=[] # holds erroneous straight segments created as a result of gridding
            segment_to_keep=[] # the segments minus the erroneous straight ones
            segment_to_use=[] # contains only correct final segments


            for j in range(len(bounds_polyline_geom_xy[0])):

                try:

                    index=j

                    x1=bounds_polyline_geom_xy[0][j]
                    y1=bounds_polyline_geom_xy[1][j]

                    x2=bounds_polyline_geom_xy[0][j+1]
                    y2=bounds_polyline_geom_xy[1][j+1]

                    xy=(x1,y1)
                    x2y2=(x2,y2)


                    #identify straight segments (straight because of being cut by the grids during patching
                    if x1==x2 or y1==y2:

                        line_to_remove=LineString([xy,x2y2])
                        segment_to_remove.append(line_to_remove)

                    #identify segments not affected by the gridding
                    else:
                        line_to_keep=LineString([xy,x2y2])

                        segment_to_keep.append(line_to_keep)

                except:pass


            # take care of the first segments or last segments that will be missed by the loop. Remove this segment as it creates a closed loop in the road feature

            x1_first_segment=bounds_polyline_geom_xy[0][1]
            y1_first_segment=bounds_polyline_geom_xy[1][1]

            x2_first_segment=bounds_polyline_geom_xy[0][2]
            y2_first_segment=bounds_polyline_geom_xy[1][2]


            x1_last_segment=bounds_polyline_geom_xy[0][len(bounds_polyline_geom_xy[0])-1]
            y1_last_segment=bounds_polyline_geom_xy[1][len(bounds_polyline_geom_xy[0])-1]

            x2_last_segment=bounds_polyline_geom_xy[0][len(bounds_polyline_geom_xy[0])-2]
            y2_last_segment=bounds_polyline_geom_xy[1][len(bounds_polyline_geom_xy[0])-2]


            line_to_remove_first=LineString([(x1_first_segment,y1_first_segment),(x2_first_segment,y2_first_segment)])
            line_to_remove_last=LineString([(x1_last_segment,y1_last_segment),(x2_last_segment,y2_last_segment)])


            # remove the 1st and last segments from the general segment_to_keep list
            for seg in segment_to_keep:
                if seg.equals(line_to_remove_last)==False and seg.equals(line_to_remove_first)==False:

                    segment_to_use.append(seg)


            #export the edges
            segment_to_use_gpd=gpd.GeoDataFrame({"geometry":segment_to_use},crs=projected_coord)
            segment_to_use_gpd.to_file(output_folder+'/{}edges.shp'.format(bounds_polyline_list[i].rstrip("vector.shp")))

            ##plot the edges
            #segment_to_use_gpd.plot(color="yellow")
            #plt.show()

            edges_gpd.append(segment_to_use_gpd)
        except: pass

    return edges_gpd


#-------------------------------------------------------------------------------

##Example
#input_folder=r'C:\Users\caleb\OneDrive\Desktop\Motor Ai\Semi_automatics_road_xtraction\Training Data\samples\testing\vector_data_output_2\aa'
#output_folder=r'C:\Users\caleb\OneDrive\Desktop\Motor Ai\Semi_automatics_road_xtraction\Training Data\samples\testing\vector_data_output_2\dada'
#data_edges=bound_edges(input_folder,output_folder,projected_coord="EPSG:25833")



