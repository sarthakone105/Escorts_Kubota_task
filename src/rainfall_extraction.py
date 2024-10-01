# can be used for all the imd component as "rainfall", "tmin", "tmax".

import rioxarray as rxr
import geopandas as gpd
from shapely.geometry import mapping
import numpy as np 
import glob
import pandas as pd
import os
from natsort import natsorted
from multiprocessing import Pool, cpu_count

path = glob.glob("/home/satyukt/Desktop/tasker/imd_tif/rain/*.tif") 
prj_dir = "/home/satyukt/Desktop/tasker"
out_path_all = f"{prj_dir}/csv/rainfall.csv"
tif = natsorted(path)
project_area = f"/home/satyukt/Desktop/tasker/shp/AOI.shp"
crop_extent = gpd.read_file(project_area)

def xarray_rainfall(args):
    i, x, y = args
    rainfall_raster = rxr.open_rasterio(x, masked=True).squeeze()
    raster_clipped = rainfall_raster.rio.clip(y.geometry.apply(mapping), y.crs, all_touched=True)
    array = np.array(raster_clipped)
    avg_fall = np.nanmean(array)
    return (i, avg_fall)

def filter_tif_by_year(tif_list, start_year=1999):
    filtered_tif = []
    for tif_file in tif_list:
        year = int(os.path.basename(tif_file)[:4])
        if year >= start_year:
            filtered_tif.append(tif_file)
    return filtered_tif

tif_filtered = filter_tif_by_year(tif)

crop_extent = crop_extent.to_crs("EPSG:4326")
args_list = [(os.path.basename(i)[:8], i, crop_extent) for i in tif_filtered]

num_workers = cpu_count()
with Pool(num_workers) as pool:
    results = pool.map(xarray_rainfall, args_list)

rows = [(i, data) for i, data in results]
df = pd.DataFrame(rows, columns=["Date", "Rainfall"])
df.index += 1
df.to_csv(out_path_all, index=False)
