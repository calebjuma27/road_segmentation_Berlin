#-------------------------------------------------------------------------------
# Name:        marking_features_centreline
# Purpose:     changes marking features into centrelines
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




def markings_centerline(input_folder_path,output_folder_path,offset_distance_metres=0.5,projected_coord_system="EPSG:25833"):


    """
    input_folder_path = contains the markings geometry as closed polylines
    output_folder_path = folder that will house the marking centrelines
    offset_distance = distance to offset the centreline from one of the marking polyline sides. Same as the buffer distance specified while creating training samples
    projected coordinate system = EPSG code of the projected system of the area of interest.

    """



    file_list=[f for f in os.listdir(input_folder_path) if f.endswith('.shp')]

    #to hold the centreline geopanda files
    gpd_files=[]
    for i in range(len(file_list)):
        current_file=input_folder_path + '/'+ file_list[i]
        marking_feature=gpd.read_file(current_file)
        if marking_feature.crs!=projected_coord_system:
            marking_feature=marking_feature.to_crs(projected_coord_system)



        try: #will identify erroneous files and print out these shapefiles

            #to hold all the centreline geometry
            center_line_geometry=[]
            marking_edge_geometry=[]

            #create a loop to process each geometry.
            for j in range(len(marking_feature)):
                marking_feature_geom=marking_feature["geometry"][j]

                marking_feature_geom_xy=marking_feature_geom.coords.xy #extract coordinates

                point_data={"point_id":[],"xy_point":[],"x_point_data":[],"y_point_data":[],"distance":[]} # dictionary of points with information


                ##extract the point coordinates and calculate distance between points.
                ##The purpose is to identify and remove the shortest segments.
                ##...the centreline will be based on the longest lines in the segments

                for k in range(len(marking_feature_geom_xy[0])):

                    try:

                        index=k

                        x1=marking_feature_geom_xy[0][k]
                        y1=marking_feature_geom_xy[1][k]

                        x2=marking_feature_geom_xy[0][k+1]
                        y2=marking_feature_geom_xy[1][k+1]



                        dist=(((x2-x1)**2)+((y2-y1)**2))**(1/2)
                        xy_1=(x1,y1)
                        xy_2=(x2,y2)

                        point_data["x_point_data"].append(x1)
                        point_data["y_point_data"].append(y1)
                        point_data["xy_point"].append(xy_1)
                        point_data["distance"].append(dist)
                        point_data["point_id"].append(index)

                        index=+1

                    except:pass


                dist_btw_points=point_data["distance"]
                sorted_by_distance=sorted(point_data["distance"]) # identify the points with the smallest distance


                index_to_not_use=[] # to hold index (representing the smallest distances) not to use
                for m in point_data["distance"]:
                    if m==sorted_by_distance[0] or m==sorted_by_distance[1]: #the 2 points with smallest distances
                        index_of_dist_value=point_data["distance"].index(m) #get their index in the list
                        index_to_not_use.append(index_of_dist_value)



                #incase the indexes are in close succession (i.e on the same line segment), then choose the 3rd index for the third smallest distance (0, 1 and then 2)
                if index_to_not_use[0]+1==index_to_not_use[1]:
                    index_to_not_use[1]=point_data["distance"].index(sorted_by_distance[2])

                index_to_not_use=sorted(index_to_not_use)

                #identify the two lines bordering the 2 short segments
                points_section_1=point_data["xy_point"][index_to_not_use[0]+1:index_to_not_use[1]+1] # first long line
                points_section_2=point_data["xy_point"][index_to_not_use[1]+1:]#+[point_data["xy_point"][index_to_not_use[0]]] #second long line. NB the first point can be added to complete the line

                #use one of the long segments
                trail_line1=LineString((points_section_1))
                #trail_line2=LineString((points_section_2))

                offset_trail_line_1=trail_line1.parallel_offset(offset_distance_metres,side='left')

                center_line_geometry.append(offset_trail_line_1)
                marking_edge_geometry.append(trail_line1)



            new_gpd=gpd.GeoDataFrame({"geometry":marking_edge_geometry},crs=projected_coord_system)
            new_gpd_offset=gpd.GeoDataFrame({"geometry":center_line_geometry},crs=projected_coord_system)
            gpd_files.append(new_gpd_offset)

            new_gpd_offset.to_file(output_folder_path + '/{}_centre_line.shp'.format(file_list[i].rstrip(".shp")))

            #plot files
            ##base=marking_feature.plot(color="blue")
            ##new_gpd_offset.plot(ax=base, color="red")
            ##plt.show()

        except:
            #find a better pythonic way to represent the error"
            print("error!!! check file {}".format(current_file))
    return gpd_files

#-------------------------------------------------------------------------------
##Example
#input_folder_path=r'C:\Users\caleb\OneDrive\Desktop\Motor Ai\Semi_automatics_road_xtraction\Training Data\samples\testing\vector_data_output_2\zz'
#output_folder_path=r'C:\Users\caleb\OneDrive\Desktop\Motor Ai\Semi_automatics_road_xtraction\Training Data\samples\testing\vector_data_output_2\yy'

#markings_centre=markings_centerline(input_folder_path,output_folder_path,offset_distance_metres=0.5,projected_coord_system="EPSG:25833")
