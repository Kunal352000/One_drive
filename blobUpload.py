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


drive_id = "b!AXbj0ewL_0O39in93Vk5IaEA-tQd1vpJhGp9uj0X_DkWhG_a1by2Q4SM6-9KtrL-"
item_id = "01GFMEKBOFFMEUDEZMIBFY2IBKZTCABACU"

# Retrieve the images from OneDrive
access_token = generate_access_token(APP_ID, SCOPES)

# response = requests.get(
#     f'https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/children',     
#     headers={'Authorization': 'Bearer ' + access_token['access_token']}
# )

response = requests.get(
    f'GET /me/drive/root',     
    headers={'Authorization': 'Bearer ' + access_token['access_token']}
)
print(response.json().get('value', []))
data = response.json().get('value', [])     
print(type(data))
for item in data:
    site_id1 = item['parentReference']['driveId']
    item_id1 = item['id']
    folder_id1 = item['parentReference']['id']
    drive_id1 = item['parentReference']['driveId']
    
    print("Site ID:", site_id1)
    print("Item ID:", item_id1)
    print("Folder ID:", folder_id1)
    print("Drive ID:", drive_id1)
    
    print()

if response.status_code == 200:
    files = response.json().get('value', [])
    for file in files:
        if file.get('file', {}).get('mimeType', '').startswith('image/') and file['name'].lower().endswith('.jpg'):
            file_name = file['name']
            file_download_url = file.get('@microsoft.graph.downloadUrl')
            if file_download_url:
                file_response = requests.get(file_download_url)
                if file_response.status_code == 200:
                    # Upload the image file to Azure Blob Storage
                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
                    blob_client.upload_blob(file_response.content)
                    print(f"Uploaded file: {file_name}")
                else:
                    print(f"Failed to download file: {file_name}")
            else:
                print(f"Download URL not found for file: {file_name}")
else:
    print("Failed to retrieve folder content.")
