#-------------------------------------------------------------------------------
# Name:        folder mang
# Purpose:
#
# Author:      caleb
#
# Created:     20/10/2022
# Copyright:   (c) caleb 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import os
import csv

def get_training_data(root_dir,mask_available='no'):

    """
    sifts through the server directory and
    returns the training samples as lists.
    if mask_available='no', it will return lane geometry and raster as a list containing paths
     and if mask_available='yes'
        1) it will return the already created masks from vector data and accompanying raster as a list contining paths
        2) It will generate a csv file containing a path to the created masks and rasters
    """

    sample_lane_markings=[]
    sample_lane_markings_raster=[]
    sample_lane_markings_mask=[]

    sample_lane_bounds=[]
    sample_lane_bounds_raster=[]
    sample_lane_bounds_mask=[]



    for path,j,k in os.walk(root_dir):


        folder=path.split(os.path.sep)[-1]

        if folder.startswith('grid')==True and len(os.listdir(path))!=0:

            #vector files
            vector_files=os.listdir(path)

            lane_bounds=[os.path.join(path,m) for m in vector_files if  m.endswith('.shp') and m.split('_')[4]== 'bounds']
            lane_markings=[os.path.join(path,m) for m in vector_files if  m.endswith('.shp') and m.split('_')[4]== 'markings']

            try:
                grid_number_lanes=lane_bounds[0].split("-")[2][:-4]
            except: grid_number_lanes="no data"
            try:
                grid_number_markings=lane_markings[0].split("-")[2][:-4]
            except: grid_number_markings="no data"



            #raster files

            to_raster_path=path.split("-")[0][:-17]

            raster_folder_path=os.path.join(to_raster_path,"clipped_images")
            imagery_file=os.listdir(raster_folder_path)
            imagery_lanes=[os.path.join(raster_folder_path,n) for n in imagery_file if  n.endswith('grid-{}.tif'.format(grid_number_lanes))]
            imagery_markings=[os.path.join(raster_folder_path,n) for n in imagery_file if  n.endswith('grid-{}.tif'.format(grid_number_markings))]



            #mask files
            if mask_available=="yes":
                to_raster_path=path.split("-")[0][:-17]

                #print(to_raster_path)


                try:
                    created_masks_folder_path=os.path.join(to_raster_path,"raster_masks")
                    created_mask_files=os.listdir(created_masks_folder_path)

                    mask_lanes=[os.path.join(created_masks_folder_path,n) for n in created_mask_files if  n.endswith('mask-{}.tif'.format(grid_number_lanes))]
                    mask_markings=[os.path.join(created_masks_folder_path,n) for n in created_mask_files if  n.endswith('mask-{}.tif'.format(grid_number_markings))]
                except:pass

            try:
                sample_lane_bounds_raster.append(imagery_lanes[0])
                sample_lane_bounds.append(lane_bounds[0])
                if mask_available=="yes":
                    sample_lane_bounds_mask.append(mask_lanes[0])

            except:
                print("!!!no data for {}".format(raster_folder_path))
                if mask_available=="yes":
                    print("!!!no raster mask data for bounds in {}".format(to_raster_path))
                else:
                    print("!!!no data for {}".format(raster_folder_path))


            try:
                sample_lane_markings_raster.append(imagery_markings[0])
                sample_lane_markings.append(lane_markings[0])
                if mask_available=="yes":
                    sample_lane_markings_mask.append(mask_markings[0])

            except:
                if mask_available=="yes":

                    print("!!!no raster mask data for markings in {}".format(to_raster_path))
                else:
                    print("!!!no data for {}".format(raster_folder_path))







    if mask_available=="no":
        return sample_lane_bounds,sample_lane_markings,sample_lane_bounds_raster,sample_lane_markings_raster
    elif mask_available=='yes':
        if len(sample_lane_bounds_mask)==0 or len(sample_lane_markings_mask)==0:
            print("\n ##########################################")
            print("!!!! create the masks  First: i.e. get_training_data(root_dir,mask_available='no'). then use 'create_mask' function to generate masks !!!")
            exit()

        with open(root_dir+"/training_bounds_location.csv",'w',newline='') as csv_data:
            field_names=["bound_images_path_x","bound_masks_path_y"]#,"markings_mask","markings_images"
            writer=csv.DictWriter(csv_data,fieldnames=field_names)
            writer.writeheader()

            for i in range(len(sample_lane_bounds_mask)):
                writer.writerow({"bound_images_path_x":sample_lane_bounds_raster[i],"bound_masks_path_y":sample_lane_bounds_mask[i]})


        with open(root_dir+"/training_markings_location.csv",'w',newline='') as csv_data_markings:
            field_names_markings=["markings_images_path_x","markings_masks_path_y"]#,"markings_mask","markings_images"
            writer_markings=csv.DictWriter(csv_data_markings,fieldnames=field_names_markings)
            writer_markings.writeheader()

            for i in range(len(sample_lane_markings_mask)):
                writer_markings.writerow({"markings_images_path_x":sample_lane_markings_raster[i],"markings_masks_path_y":sample_lane_markings_mask[i]})




        return sample_lane_bounds_mask,sample_lane_markings_mask,sample_lane_bounds_raster,sample_lane_markings_raster





###example
##root_dir=r'\\MOTORAICLOUDY\Transfer\Mapping Team\Mapping_Pipeline_Training_Data'
#root_dir=r'\\MOTORAICLOUDY\Transfer\Mapping Team\test_to_delete_2'
##lane_bounds_mask,lane_markings_mask,lane_bound_images,lane_marking_images=get_training_data(root_dir,mask_available='yes') #mask available can either be "yes" or "no"

##print(len(lane_bounds_mask,),len(lane_markings_mask))


