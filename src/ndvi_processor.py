from pystac_client import Client
import geopandas as gpd
import os
import requests
import datetime
import rasterio
import rasterio.mask
import numpy as np
import rasterio
from shapely.geometry import mapping
from rasterio.mask import mask
import rasterio
from rasterio.mask import mask
import numpy as np
from shapely.geometry import mapping


def compute_ndvi(b8_path, b4_path, shp, png_date, output_path):
    
    with rasterio.open(b8_path) as src_b8:
        b8 = src_b8.read(1)
        b8_meta = src_b8.meta
    
    with rasterio.open(b4_path) as src_b4:
        b4 = src_b4.read(1)
    
    shp = shp.to_crs(b8_meta['crs'].to_proj4())

    with rasterio.open(b8_path) as src_b8:
        b8_masked, b8_transform = mask(src_b8, shapes=[mapping(geom) for geom in shp.geometry], crop=True)
    
    with rasterio.open(b4_path) as src_b4:
        b4_masked, b4_transform = mask(src_b4, shapes=[mapping(geom) for geom in shp.geometry], crop=True)

    b8_masked = b8_masked.astype(float)
    b4_masked = b4_masked.astype(float)
    ndvi = (b8_masked - b4_masked) / (b8_masked + b4_masked)

    with rasterio.MemoryFile() as memfile:
        with memfile.open(
            driver='GTiff',
            height=ndvi.shape[1],
            width=ndvi.shape[2],
            count=1, 
            dtype=rasterio.float32,
            crs=b8_meta['crs'],
            transform=b8_transform,
        ) as dataset:
            dataset.write(ndvi[0], 1)

            out_image, out_transform = mask(dataset, shapes=[mapping(geom) for geom in shp.geometry], crop=True)
            out_image[out_image == 0] = np.nan
            # mean_ndvi = np.nanmean(out_image)
            out_meta = dataset.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
    
    # extent = [
    #     out_transform[2],
    #     out_transform[2] + out_transform[0] * out_image.shape[2],
    #     out_transform[5] + out_transform[4] * out_image.shape[1],
    #     out_transform[5]
    # ]
    
    
    with rasterio.open(output_path, "w", **out_meta) as dst:
        dst.write(out_image[0], 1)



def check_ndvi(ndvi_files, output_dir, aoi_geom):
    b8a_path, b4_path = ndvi_files[0], ndvi_files[1]
    ndvi_date = os.path.basename(b8a_path).split('_')[2]
    ndvi_tiff = f'{output_dir}/{ndvi_date}.tif'
    if os.path.exists(ndvi_tiff):
        print(f"NDMI file already exists: {ndvi_tiff}")
    else:    
        compute_ndvi(b8a_path, b4_path, aoi_geom, ndvi_date, ndvi_tiff)

def create_dir(main_dir, _dir):
    _dir = os.path.join(main_dir, _dir)
    _dir = os.path.normpath(_dir)
    if not os.path.exists(_dir):
        os.makedirs(_dir)
    return _dir

def download_tiff_files(urls,date,_dir):
    files = []
    for url in urls:
        try:
            name = f'{date}_{os.path.basename(url)}'
            file_name = os.path.join(_dir, name)
            if os.path.exists(file_name):
                print(f"File already exists: {file_name}")
                files.append(file_name)
                continue
            response = requests.get(url)
            response.raise_for_status() 
            with open(file_name, 'wb') as file:
                file.write(response.content)
            
            print(f"Downloaded: {file_name}")
            files.append(file_name)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
    return files

def get_band_links(data_dict, bands, band_dict):
    links = []
    for band in bands:
        common_name = band_dict.get(band)
        if not common_name:
            print(f"Band {band} not found in band dictionary.")
            continue
        for key, value in data_dict.items():
            if 'href' in value and value.get('eo:bands', [{}])[0].get('common_name') == common_name:

                if value['href'].endswith(f'tif'):
                    
                    links.append(value['href'])
    return links[:2]

def fetch_cogs(main_dir , tdate, shp_file, cloud_cover='10', date_range_days=365, tiff_dir = 'data', png_dir = 'output'):
    shapes = gpd.read_file(shp_file)
    geom = shapes.geometry[0]
    
    ndvi_band_dict = { 
        'b8': 'nir', 
        'b4': 'red'
    }
    
    collection = "sentinel-2-l2a"
    bands = ['b8', 'b4']
    api_url = "https://earth-search.aws.element84.com/v1"
    S2_STAC = Client.open(api_url)
    
    edate = datetime.datetime.strptime(tdate, "%Y-%m-%d")
    sdate = edate - datetime.timedelta(days=date_range_days)
    
    def search_data(start_date, end_date):
        sdate = start_date.strftime("%Y-%m-%dT00:00:00Z")
        edate = end_date.strftime("%Y-%m-%dT23:59:59Z")
        timeRange = f'{sdate}/{edate}'
        print(timeRange)


        s2satSearch = S2_STAC.search(
            intersects=geom,
            datetime=timeRange,
            query={"eo:cloud_cover": {"lt": cloud_cover}},
            collections=[collection]
        )
        return [i.to_dict() for i in s2satSearch.get_items()]
    print('s')
    s2sat_items = search_data(sdate, edate)
    print('a')
    if not s2sat_items:
        print('data is not availble for ', tdate)        
    
    down_dir = create_dir(main_dir, 'data')
    ndvi_dir = create_dir(main_dir, 'ndvi_tif')
    
    for s2band in s2sat_items:
        band_id = s2band['id']
        print(band_id)
        links = get_band_links(s2band['assets'], bands, ndvi_band_dict)
        ndvi_files = download_tiff_files(links, band_id, down_dir)
        ndvi_file_path = check_ndvi(ndvi_files,ndvi_dir, shapes)


def clear_bands(main_dir):
    path_bands_data = f"{main_dir}/data"
    files = os.listdir(path_bands_data)
    
    for file in files:
        os.remove(f"{path_bands_data}/{file}")
        print(f"Successfully removed: {file}")
    
if __name__ == "__main__":
    main_dir = '/home/satyukt/Sarthak/Escorts_Kubota_task'
    farm_polygon = f'{main_dir}/shp/AOI.shp'
    
    gdf = gpd.read_file(farm_polygon)
    geom = gdf.geometry.iloc[0]
    geojson_dict = geom.__geo_interface__

    tdate = "2024-09-30"
    CLOUD_COVER = '10'
    DATE_RANGE_DAYS = 365 # For last one year data.
    fetch_cogs(main_dir, tdate, farm_polygon, CLOUD_COVER, DATE_RANGE_DAYS)
    clear_bands(main_dir)
    