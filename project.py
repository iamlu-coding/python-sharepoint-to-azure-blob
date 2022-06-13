from sharepoint import SharePoint
import re
import sys, os, json
from azure.storage.blob import BlobClient
from pathlib import PurePath

# 1 args = SharePoint folder name. May include subfolders YouTube/2022
folder_name = sys.argv[1]
# 2 args = SharePoint file name. This is used when only one file is being downloaded
file_name = sys.argv[2]
# 3 args = SharePoint file name pattern
file_name_pattern = sys.argv[3]


# read json file
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = PurePath(ROOT_DIR, 'config.json')

with open(config_path) as config_file:
    config = json.load(config_file)
    config = config['azure_storage']

AZURE_ACCOUNT_NAME=config['azure_account_name']
AZURE_ACCESS_KEY=config['azure_access_key']
CONTAINER_NAME=config['container_name']
AZURE_CONN_STR=f'DefaultEndpointsProtocol=https;AccountName={AZURE_ACCOUNT_NAME};AccountKey={AZURE_ACCESS_KEY};EndpointSuffix=core.windows.net'

# functions used for azure storage
def upload_file_to_blob(file_obj, file_name):
    blob = BlobClient.from_connection_string(
        conn_str=AZURE_CONN_STR,
        container_name=CONTAINER_NAME,
        blob_name=file_name,
        credential=AZURE_ACCESS_KEY
    )
    blob.upload_blob(file_obj)


def get_file(file_n, folder):
    file_obj = SharePoint().download_file(file_n, folder)
    upload_file_to_blob(file_obj, file_n)
    

def get_files(folder):
    files_list = SharePoint().download_files(folder)
    for file in files_list:
        get_file(file['Name'], folder)

def get_files_by_pattern(pattern, folder):
    files_list = SharePoint().download_files(folder)
    for file in files_list:
        if re.search(pattern, file['Name']):
            get_file(file['Name'], folder)

if __name__ == '__main__':
    if file_name != 'None':
        get_file(file_name, folder_name)
    elif file_name_pattern != 'None':
        get_files_by_pattern(file_name_pattern, folder_name)
    else:
        get_files(folder_name)