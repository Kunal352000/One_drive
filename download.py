import os
import requests
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT

APP_ID = 'fcaecfc0-be18-4ae4-a4bd-b4735aa7082a'
SCOPES = ['Files.Read']

access_token = generate_access_token(APP_ID, SCOPES)
# print(access_token)
headers = {
    'Authorization': 'Bearer ' + access_token['access_token']
}

drive_id="b!AXbj0ewL_0O39in93Vk5IaEA-tQd1vpJhGp9uj0X_DkWhG_a1by2Q4SM6-9KtrL-"
item_id="01GFMEKBOFFMEUDEZMIBFY2IBKZTCABACU"
response = requests.get(
    GRAPH_API_ENDPOINT + f'/me/drive/root',
    headers=headers
)
print("hey",response.json().get('value', []))
# print(response)
if response.status_code == 200:
    files = response.json().get('value', [])
    for file in files:
        if file.get('file', {}).get('mimeType', '').startswith('image/') and file['name'].lower().endswith('.jpg'):
            file_name = file['name']
            file_download_url = file.get('@microsoft.graph.downloadUrl')
            if file_download_url:
                file_response = requests.get(file_download_url)
                if file_response.status_code == 200:
                    # Save the image file
                    with open(file_name, 'wb') as f:
                        f.write(file_response.content)
                    print(f"Downloaded file: {file_name}")
                else:
                    print(f"Failed to download file: {file_name}")
            else:
                print(f"Download URL not found for file: {file_name}")
else:
    print("Failed to retrieve folder content.")

