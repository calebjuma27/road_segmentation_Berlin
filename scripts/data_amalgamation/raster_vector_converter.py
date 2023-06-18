# Name:        raster to vector converter
# Purpose:     to convert raster masks into subsequent vector geometries
#
# Author:      caleb
# Additional
# source:      [https://github.com/rasterio/rasterio/blob/main/rasterio/features.py#L77],
#              [https://gis.stackexchange.com/questions/187877/how-to-polygonize-raster-to-shapely-polygons/437855#437855]
# Created:     09/08/2022
# Copyright:   (c) caleb 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

#for file and directory operation
import os

#for raster operations
import rasterio as rio
from rasterio.features import shapes

#for vector operation
from shapely.geometry import Point, LineString, Polygon
import geopandas as gpd

#plotting sample results
from matplotlib import pyplot as plt


def raster_to_vector(input_raster_mask_folder,output_vector_folder,coord_ref="EPSG:25833"):

    """

    input_raster_mask_folder :folder containing raster masks that are to be vectorized
    output_vector_folder : target vector folder that will have the already vectorized data as shapefiles
    coord_ref= the EPSG code for the raster mask coordinate system

    """

    names=os.listdir(input_raster_mask_folder)

    vector_masks_list=[]

    for i in range(len(names)):
        try:


            input_raster_mask=os.path.join(input_raster_mask_folder,names[i])
            file_name=names[i][0:-4]+"_vector"#to remove the .tif and add _vector



            #####raster to vector operation
            #******************************************************************************************
            mask=None

            with rio.Env():
                with rio.open(input_raster_mask) as input_image:
                    input_image_array=input_image.read(1).astype(int)

                    result=({'properties': {'raster_val':v},'geometry':s}

                     for i, (s,v)
                     in enumerate(shapes(input_image_array,mask=mask,transform=input_image.transform)))

            #******************************************************************************************


            raster_polygon_values=list(result) # contains all the data, including No datavalues

            raster_polygon_with_value_1=[]

            #then pick raster values (1 in this case) that correspond to road
            for i in range(len(raster_polygon_values)):
                if raster_polygon_values[i]['properties']['raster_val'] ==1:
                    raster_polygon_with_value_1.append(raster_polygon_values[i])



            simplified_roads={"road_no":[],"geometry":[]} # dictionary to contain simplifies road geometries
            index_value=1
            for j in range(len(raster_polygon_with_value_1)):

                road_feature=raster_polygon_with_value_1[j]['geometry']['coordinates'] # 2 feature, so j represents 0 index and 1 index
                road_feature_line_string=LineString(road_feature[0]) #list within a list, only one index, the first one i.e 1

                road_feature_line_string_simplified=road_feature_line_string.simplify(0.5,preserve_topology=False) # simplify the square output lines into a straight line/curve
                simplified_roads["road_no"].append(index_value)
                simplified_roads["geometry"].append(road_feature_line_string_simplified)
                index_value+=1
            try:
                gpd_line=gpd.GeoDataFrame(simplified_roads)
                gpd_line=gpd_line.set_crs(coord_ref)
                output_vector=output_vector_folder + "/" + file_name+".shp"


                gpd_line.to_file(output_vector)
            except:pass

            vector_masks_list.append(gpd_line)
        except:pass
    return vector_masks_list



###--------------------------------------------------------------------------------------------------------------------------------
######example
#Specify input and output data
#output_file_path=r'C:\Users\caleb\OneDrive\Desktop\Motor Ai\Semi_automatics_road_xtraction\Training Data\samples\testing\to_delete_now\vectors'
#input_raster_path=r'C:\Users\caleb\OneDrive\Desktop\Motor Ai\Semi_automatics_road_xtraction\Training Data\samples\testing\to_delete_now\masks'

##
#sse=raster_to_vector(input_raster_path,output_file_path) #creates a list containing geopanda features
##sse[0].plot()
##plt.show()
###-------------------------------------------------------------------------------------------------------------------------------