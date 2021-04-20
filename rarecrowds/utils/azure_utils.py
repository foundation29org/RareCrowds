import os
from tqdm import tqdm

from azure.storage.blob import BlobServiceClient

from rarecrowds.conf_utils import get_config_value

ALLOWED_CONTAINERS = {
    "cipriani-2020": {'title': 'An Improved Phenotype-Driven Tool for Rare Mendelian Variant Prioritization: Benchmarking Exomiser on Real Patient Whole-Exome Data', 'year': 2020, 'url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7230372/'},
    "ebiki-2019": {'title': 'Comparison of Causative Variant Prioritization Tools Using Next-generation Sequencing Data in Japanese Patients with Mendelian Disorders', 'year': 2019, 'url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6739250/'},
    "kleyner-2016": {'title': 'KBG syndrome involving a single-nucleotide duplication in ANKRD11', 'year': 2016, 'url': 'http://molecularcasestudies.cshlp.org/content/2/6/a001131.long'},
    "rao-2018": {'title': 'Phenotype-driven gene prioritization for rare diseases using graph convolution on heterogeneous networks', 'year': 2018, 'url': 'https://pubmed.ncbi.nlm.nih.gov/29980210/'},
    "tomar-2019": {'title': 'Specific phenotype semantics facilitate gene prioritization in clinical exome sequencing', 'year': 2019, 'url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6777628/'},
    "zomojtel-2014": {'title': 'Effective diagnosis of genetic disease by computational phenotype analysis of the disease-associated genome', 'year': 2014, 'url': 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4512639/'},
}


def download_data(dataset: str, data_path: str) -> None:
    if dataset not in ALLOWED_CONTAINERS:
        raise Exception(
            f"Invalid dataset type: {dataset} \nOnly allowed datasets are {set(ALLOWED_CONTAINERS)}"
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
