import os
from tqdm import tqdm

from azure.storage.blob import BlobServiceClient

from rarecrowds.conf_utils import get_config_value

ALLOWED_CONTAINERS = set(
    [
        "cipriani-2020",
        "ebiki-2019",
        "kleyner-2016",
        "rao-2018",
        "tomar-2019",
        "zomojtel-2014",
    ]
)


def download_data(dataset: str, data_path: str) -> None:
    if dataset not in ALLOWED_CONTAINERS:
        raise Exception(
            f"Invalid dataset type: {dataset} \nOnly allowed datasets are {ALLOWED_CONTAINERS}"
        )
    try:
        blob_service = BlobServiceClient(
            account_url=get_config_value("AZURE", "ACCOUNT_URL")
        )
        container_client = blob_service.get_container_client(dataset)
        blob_list = container_client.list_blobs()
        if not os.path.exists(os.path.join(data_path, dataset)):
            os.makedirs(os.path.join(data_path, dataset))
        print(f"Starting download of {dataset}")
        for blob in tqdm(blob_list):
            blob_client = container_client.get_blob_client(blob)
            with open(
                os.path.join(data_path, dataset, blob["name"]), "wb"
            ) as blob_file:
                download_stream = blob_client.download_blob()
                blob_file.write(download_stream.readall())
        print(f"Downloaded {dataset}")
    except Exception as e:
        print(e)
