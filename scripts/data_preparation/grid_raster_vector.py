
import pandas as pd
import geopandas as gpd

import rasterio as rio
from rasterio.plot import show
import rasterio.mask


from rasterio import windows
from shapely.geometry import box


def generate_tiles(image_file, output_file,intersected_vector, area_str, size=256):
    """Generates 256 x 256 polygon tiles. however can be changed """

    def get_window_polygon(src_file, window):
      src = rio.open(src_file)
      bbox = windows.bounds(window, src.transform)
      src.close()
      return box(*bbox)

    raster = rio.open(image_file)
    coord_system=raster.crs
    width, height = raster.shape

    geo_dict = {
        'id' : [],
        'geometry' : []

    }

    index = 0

    intersected_file=gpd.read_file(intersected_vector)
    vector_geom=intersected_file["geometry"][0]
    for w in range(0, width, size):
        for h in range(0, height, size):
          window = windows.Window(h, w, size, size)
          bbox = get_window_polygon(image_file, window)

          uid = '{}-{}'.format(area_str.lower().replace(' ', '_'), index)#add an attribute
          index += 1

          if bbox.intersects(vector_geom)==True:
            geo_dict["geometry"].append(bbox)
            geo_dict['id'].append(uid)

    results = gpd.GeoDataFrame(pd.DataFrame(geo_dict))
    results.crs = {'init' :coord_system}
    #results.to_file(output_file, driver="GeoJSON") #Geojson does not allow other crs apart from 4326
    results.to_file(output_file) #save as shapefile
    raster.close()

    return results



def show_crop(image, shape):
    with rio.open(image) as src:
        out_image, out_transform = rio.mask.mask(src, shape, crop=True)
        out_meta=src.meta

        return out_image,out_meta,out_transform




####Example
#generating grids

##input_file=r'C:\Users\caleb\OneDrive\Desktop\private\Unet_river\Data\dataset\Depth.tif'
##output_grid_files=r'C:\Users\caleb\OneDrive\Desktop\private\Unet_river\Data\Tiles\tiles_128_grid.shp'
##intersected_vector=r'C:\Users\caleb\OneDrive\Desktop\private\Unet_river\Data\drainage_Basin_dissolved.shp'
##output_tif_file=r'C:\Users\caleb\OneDrive\Desktop\private\Unet_river\Data\output_image_tiles\depth_tiled'
##
##
##tiles = generate_tiles(input_file, output_grid_files,intersected_vector, "grid", size=128)



###generating image patches
##
##for i in range(len(tiles)):
##    out_image,out_meta,out_transform=show_crop(input_file, [tiles.iloc[i]['geometry']]')
##
##    out_meta.update({"driver":"GTiff","height":out_image.shape[1],"width":out_image.shape[2],"transform":out_transform})
##
##    with rio.open(output_tif_file + "\depth_{}.tif".format(i),"w",**out_meta) as dest:
##        dest.write(out_image)
