# Maize Crop Yield Prediction

This project aims to predict maize crop yield using a dataset from Karnataka. The workflow encompasses data ingestion, transformation, model training, and yield prediction.

## Project Structure

- **csv/**: Contains the dataset.
- **src/**: Contains all the source code for data processing and predictions.
  - **ingest_imd.py**: Facilitates the ingestion of IMD (Indian Meteorological Department) data by creating directories, downloading temperature and rainfall data in TIFF format, and clearing previous data to maintain a clean workspace.
  - **ndvi_processor.py**: Computes the Normalized Difference Vegetation Index (NDVI) from Sentinel-2 satellite imagery for the specified agricultural area. It downloads relevant TIFF files, processes the B8 and B4 bands, and saves the output as a GeoTIFF file, managing directories and avoiding redundant calculations.
  - **rainfall_extraction.py**: Extracts and processes rainfall data relevant to crop yield.
  - **predictions.py**: Utilizes trained models to predict maize yield based on processed data.
- **models/**: Contains the trained machine learning models saved after the training process.
- **src/notebook/model_training.ipynb**: Includes Jupyter notebooks for model training, where several models were created and evaluated for performance.
