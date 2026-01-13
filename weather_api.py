import requests
import xarray as xr
import pandas as pd
import os

class OpenDataAPI:
    def __init__(self, api_token: str):
        self.base_url = "https://api.dataplatform.knmi.nl/open-data/v1"
        self.headers = {"Authorization": api_token}

    def _get_data(self, url, params=None):
        return requests.get(url, headers=self.headers, params=params).json()

    def get_latest_filename(self, dataset_name, dataset_version):
        params = {"maxKeys": 1, "orderBy": "created", "sorting": "desc"}
        response = self._get_data(
            f"{self.base_url}/datasets/{dataset_name}/versions/{dataset_version}/files",
            params=params
        )
        return response["files"][0]["filename"]

    def get_download_url(self, dataset_name, dataset_version, file_name):
        response = self._get_data(
            f"{self.base_url}/datasets/{dataset_name}/versions/{dataset_version}/files/{file_name}/url"
        )
        return response["temporaryDownloadUrl"]

def get_q1h_de_bilt(api_key):
    dataset_name = "Actuele10mindataKNMIstations"
    dataset_version = "2"

    api = OpenDataAPI(api_token=api_key)
    latest_file = api.get_latest_filename(dataset_name, dataset_version)
    download_url = api.get_download_url(dataset_name, dataset_version, latest_file)

    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open("temp.nc", "wb") as f:
            f.write(r.content)

    ds = xr.open_dataset("temp.nc")
    df = ds.to_dataframe().reset_index()
    de_bilt_row = df[df['stationname'] == 'De Bilt']

    if not de_bilt_row.empty:
        qg = de_bilt_row.iloc[0]["qg"]
        qg = qg * 122  # Convert to lux
        os.remove("temp.nc" )
        print(f"weather data: {qg}")
        return qg
    else:
        return None
