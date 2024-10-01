import imdlib as imd
import datetime
import os
import rioxarray
import shutil


def create_directories(base_dir):
    
    tif_directory_path = os.path.join(base_dir, "imd_tif")
    os.makedirs(tif_directory_path, exist_ok=True)

    grd_directory_path = os.path.join(base_dir, "imd_grd")
    os.makedirs(grd_directory_path, exist_ok=True)

    components_list = ["tmin", "tmax", "rain"]

    for component in components_list:
        tif_sub_directory_path = os.path.join(tif_directory_path, component)
        os.makedirs(tif_sub_directory_path, exist_ok=True)

        grd_sub_directory_path = os.path.join(grd_directory_path, component)
        os.makedirs(grd_sub_directory_path, exist_ok=True)


def download_data(days, base_dir):
    
    components_list = ["tmin", "tmax", "rain"]
    days_before = datetime.timedelta(days=days)
    present_date = (datetime.datetime.now().date()) - datetime.timedelta(days=2)
    start_date = str(present_date - days_before)
    end_date = str(present_date - datetime.timedelta(days=1))
    grd_directory = os.path.join(base_dir, "imd_grd")
    tif_directory = os.path.join(base_dir, "imd_tif")

    for component in components_list:
        tif_component_directory = os.path.join(tif_directory, component)
        grd_component_directory = os.path.join(grd_directory, component)

        data_xarray = imd.get_real_data(var_type=component, start_dy=start_date, end_dy=end_date, file_dir=grd_component_directory)
        ds = data_xarray.get_xarray()

        for time in ds.time:
            daily_data = ds.sel(time=time)
            date_str = str(time.values)[:10]
            data_str = date_str.replace("-", "")
            out_file_path = os.path.join(tif_component_directory, f"{data_str}.tif")
            daily_data[component].rio.write_crs("EPSG:4326", inplace=True)
            daily_data.rio.to_raster(out_file_path)

def clear_grd(base_dir):
    path_bands_data = f"{base_dir}/imd_grd"
    
    if os.path.exists(path_bands_data):
        shutil.rmtree(path_bands_data)
        print(f"Directory {path_bands_data} and its contents have been removed.")
    else:
        print(f"Directory {path_bands_data} does not exist.")


if __name__ == "__main__":
    
    basedir = "/home/satyukt/Sarthak/Escorts_Kubota_task"  #Please change base directory.
    day = 60 #change days as per requirements.
    create_directories(base_dir=basedir)
    download_data(days=day, base_dir=basedir) 
    clear_grd(basedir)
    