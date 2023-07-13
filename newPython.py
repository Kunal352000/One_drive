import os
import requests
from azure.storage.blob import BlobServiceClient
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT

# Azure Blob Storage connection string and container name
connection_string = 'DefaultEndpointsProtocol=https;AccountName=scoutfoto;AccountKey=rsV4APZ72dSGxC8q+mtq3MB1DK+65FeRIIR90Bilwa2FFf46ELX9bIb35cJVPlGqZwnE+WnljpMu+ASt/dlTlg==;EndpointSuffix=core.windows.net'
container_name = 'onedrivetest'

# Create a BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

APP_ID = 'fcaecfc0-be18-4ae4-a4bd-b4735aa7082a'
SCOPES = ['Files.Read']

# Retrieve the images from OneDrive
access_token = generate_access_token(APP_ID, SCOPES)

drive_id = None
item_id = None

# Fetch the drive_id dynamically
drive_response = requests.get(
    f'{GRAPH_API_ENDPOINT}/me/drive',
    headers={'Authorization': 'Bearer ' + access_token['access_token']}
)

if drive_response.status_code == 200:
    drive_data = drive_response.json()
    drive_id = drive_data['id']
else:
    print("Failed to retrieve drive information.")

# Fetch the item_id dynamically
if drive_id:
    print("drive id-->", drive_id)
    item_response = requests.get(
        f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/items/root/children',
        headers={'Authorization': 'Bearer ' + access_token['access_token']}
    )
    # print("item-response-->", item_response.json())

    if item_response.status_code == 200:
        item_data = item_response.json()
        if 'value' in item_data:
            for item in item_data['value']:
                if item['name'].lower() == 'photos':
                    item_id = item['id']
                    print("this is my item-id",item_id)
                    break

        if item_id:
            response = requests.get(
                f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/items/{item_id}/children',
                headers={'Authorization': 'Bearer ' + access_token['access_token']}
            )

            if response.status_code == 200:
                files = response.json().get('value', [])
                for file in files:
                    # print("This is all are my files names",file)
                    if (
                        file.get('file', {}).get('mimeType', '').startswith('image/')
                        and file['name'].lower().endswith('.jpg')
                    ):
                        file_name = file['name']
                        print(file_name)
                        file_download_url = file.get('@microsoft.graph.downloadUrl')
                        if file_download_url:
                            file_response = requests.get(file_download_url)
                            if file_response.status_code == 200:
                                # Upload the image file to Azure Blob Storage
                                blob_client = blob_service_client.get_blob_client(
                                    container=container_name, blob=file_name
                                )
                                blob_client.upload_blob(file_response.content)
                                print(f"Uploaded file: {file_name}")
                            else:
                                print(f"Failed to download file: {file_name}")
                        else:
                            print(f"Download URL not found for file: {file_name}")
            else:
                print("Failed to retrieve folder content.")
        else:
            print("Photos folder not found.")
    else:
        print("Failed to retrieve item information.")
else:
    print("Drive information not available.")
