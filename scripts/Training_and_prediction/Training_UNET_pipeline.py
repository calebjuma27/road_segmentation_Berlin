#-------------------------------------------------------------------------------
# Name:        Training and prediction
# Purpose:      tO TRAIN a UNET model predict for markings and road bounds in aerial images
#
# Author:      caleb
#
# Created:     17/10/2022
# Copyright:   (c) caleb 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

##internal codebase
from folder_mng import get_training_data

##sytem
import os
import time

#geo_imagery and vector data processing
import rasterio as rio
from rasterio.mask import mask
from rasterio.plot import show
import geopandas as gpd

#data processing
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

##Deep learning libraries
import segmentation_models as sm
from segmentation_models import Unet
import tensorflow as tf
from keras.utils import to_categorical
from keras.models import load_model


##plot dataset
from matplotlib import pyplot as plt



def item_to_train(item_raster_x,item_mask_y):

    # create rio function to read and get the data as an array list

    item_mask_list=[rio.open(mask_marking).read(1) for mask_marking in item_mask_y]
    item_raster_list=[np.dstack((rio.open(input_raster).read(1),rio.open(input_raster).read(2),rio.open(input_raster).read(3)))for input_raster in item_raster_x]

    #convert the lists into numpy arrays
    item_mask_array=np.array(item_mask_list)
    item_raster_array=np.array(item_raster_list)

    print(item_mask_array.shape)
    print(item_raster_array.shape)


    ###reshape everything to have the same shape as the image patch i.e 4 values consisting of number of sample, width, height and number of bands
    item_mask_array_reshaped=item_mask_array.reshape((item_mask_array.shape[0],item_mask_array.shape[1],item_mask_array.shape[2],1))
    print(item_mask_array_reshaped.shape)
    print(item_raster_array.shape)


    return item_mask_array_reshaped,item_raster_array




def train_unet_model(training_data_folder,model_folder,item_type="bounds",batch_size=15,epoch=100,train_model="yes",predict_model="yes"):

    """
    training_data_folder = location of training datasets. Follows the Motor_AI mapping team folder convention
    model_folder = The folder to house the generated weights
    item_type can either be "bounds" or "markings"
    train_model can either be "yes" or "no"
    predict_model can either be "yes" or "no
    """

    ###obtain the data
    lane_bounds_mask_path,lane_markings_mask_path,lane_bounds_raster_path,lane_markings_raster_path=get_training_data(training_data_folder,mask_available='yes')


    if item_type=="bounds":
        item_mask_array_reshaped,item_raster_array=item_to_train(lane_bounds_raster_path,lane_bounds_mask_path)
    elif item_type=="markings":
        item_mask_array_reshaped,item_raster_array=item_to_train(lane_markings_raster_path,lane_markings_mask_path)

    ###specify model name i.e "bounds" or "markings"
    model_name=item_type


    #convert the raster values to categories. No need for one-hot encoding as we have binary values 1 and 0
    no_of_unique_labels=len(np.unique(item_mask_array_reshaped))
    labels_cat=to_categorical(item_mask_array_reshaped,no_of_unique_labels)

    ###visualize encoded masks
    ##encoded_mask=np.argmax(labels_cat,axis=3)
    ##print(encoded_mask.shape)
    ##
    ##for i in range(100,130):
    ##    plt.figure(figsize=(12,8))
    ##
    ##    plt.subplot(131) # number of rows, number of colums, then index of the plotted item
    ##    plt.title("Actual")
    ##    plt.imshow(item_raster_array[i])
    ##
    ##
    ##    plt.subplot(132) # number of rows, number of colums, then index of the plotted item
    ##    plt.title("Actual")
    ##    plt.imshow(item_mask_array_reshaped[i])
    ##
    ##
    ##    plt.subplot(133)
    ##    plt.title("test")
    ##    plt.imshow(encoded_mask[i])
    ##    plt.show()


    ###split into train and test dataset the random state ensures reproduciability of the randomness
    x_train,x_test,y_train,y_test=train_test_split(item_raster_array,labels_cat,test_size=0.25,random_state=42)


    ##visualize test and train data look like
    ##y_train_label_mask=np.argmax(y_train,axis=3)
    ##y_test_label_mask=np.argmax(y_test,axis=3)
    ##
    ##
    ##
    ##for i in range(10):#len(y_test)
    ##    plt.figure(figsize=(12,8))
    ##    plt.subplot(131) # number of rows, number of colums, then index of the plotted item
    ##    plt.title("image")
    ##    plt.imshow(x_test[i])
    ##
    ##
    ##    plt.subplot(132)
    ##    plt.title("label mask")
    ##    plt.imshow(y_label_mask[i])
    ##    plt.show()



    ##***********************************************************************************************************
    model_file_name='\{}_epoch_{}_batch_size_{}_{}.hdf5'.format(epoch,batch_size,model_name)
    # define model
    if train_model=="yes":

        model = Unet('resnet34',input_shape=(512, 512, 3),encoder_weights='imagenet',classes=no_of_unique_labels,activation='softmax')#None,activation='ReLU'
        model.compile('Adam', loss="categorical_crossentropy",metrics=["mean_squared_error"])



        #time to start
        start_test = time.time()
        history=model.fit(x_train,
                  y_train,
                  batch_size=batch_size,
                  epochs=epoch,
                  verbose=1,
                  validation_split=0.1)

        model.save(saved_model_folder+model_file_name)

        end_test = time.time()
        print('Time taken to train model is: {} minutes.'.format((end_test - start_test) / 60))

        ##plot validation vs loss diagram
        plt.plot(history.history["loss"],label="Training_loss")
        plt.plot(history.history['val_loss'],label="Validation_loss")
        plt.legend()
        plt.show()

    ##***********************************************************************************************************


    #test the accuracy of the model

    if predict_model=="yes":
        try:

            model = load_model(saved_model_folder+model_file_name)
            y_pred=model.predict(x_test)


            print(y_train.shape,x_train.shape)
            print(x_test.shape,y_test.shape)

            print(y_pred.shape)

            y_pred_argmax=np.argmax(y_pred,axis=3)
            y_test_argmax=np.argmax(y_test,axis=3)


            ##visualize the test vs the predicted data
    ##        for i in range(len(y_test)):
    ##            plt.figure(figsize=(12,8))
    ##            plt.subplot(131) # number of rows, number of colums, then index of the plotted item
    ##            plt.title("Imagery")
    ##            plt.imshow(x_test[i])
    ##
    ##
    ##            plt.subplot(132)
    ##            plt.title("test")
    ##            plt.imshow(y_test_argmax[i].reshape(512,512,1))
    ##
    ##
    ##            plt.subplot(133)
    ##            plt.title("predicted")
    ##            plt.imshow(y_pred_argmax[i].reshape(512,512,1))
    ##            plt.show()

            #metrics
            #MAE
            mae=np.mean(abs(y_pred-y_test))

            #MAPE
            mape=100*(np.mean(abs(y_pred-y_test)/y_test))

            #MSE and RMSE
            mse=np.mean((y_test-y_pred)**2)
            rmse=np.sqrt(mse)

            #calculate R2 using residual sum of squares (rss) and total sum of squares (tss)
            y_test_mean=np.mean(y_test)

            rss=np.sum((y_test-y_pred)**2)
            tss=np.sum((y_test -y_test_mean)**2)
            r2_statistic=1-(rss/tss)

            print("\n**************************************************")
            print("METRICS\n")
            print("Mean Absolute Error: {:.4f}".format(mae))
            print("Mean Absolute Percentage Error: {:.2f}%".format(mape))
            print("Mean Squared Error: {:.4f}".format(mse))

            print("Root Mean Squared Error: {:.4f}".format(rmse))
            print("R Squared is {:.4f}".format(r2_statistic))

        except: print("!!! Probably wrong model_file. Check where the weights or model file is stored!!!")

##example
### specify source of data
root_dir=r'\\MOTORAICLOUDY\Transfer\Mapping Team\Mapping_Pipeline_Training_Data'

###specify where the model weights should be saved
saved_model_folder=r'C:\Users\caleb\OneDrive\Desktop\Motor Ai\Semi_automatics_road_xtraction\CodeBase_Semi_auto_maps\saved_model_berlin'

##item_type can either be "bounds" or "markings"
##train_model can either be "yes" or "no"
##predict_model can either be "yes" or "no"
train_unet_model(root_dir,saved_model_folder,item_type="bounds",batch_size=15,epoch=100,train_model="no",predict_model="yes")