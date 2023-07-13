import os
import requests
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT

APP_ID ='fcaecfc0-be18-4ae4-a4bd-b4735aa7082a'
SCOPES = ['Files.ReadWrite']

access_token = generate_access_token(APP_ID, SCOPES)
headers = {
    'Authorization': 'Bearer ' + access_token['access_token'],
    'Content-Type': 'image/jpg'  # Set the content-type header to match the file type
}

file_path = r'C:\Users\Kunal.Joshi\Desktop\One_drive\virat-kohli-wallpaper-ful5akjf.jpg'
file_name = os.path.basename(file_path)
with open(file_path, 'rb') as upload:
    media_content = upload.read()

# one_drive_folder_id = 'EjkeXwg-AhRFmkIjObKCNcEBKL0w_4AceWLM6VfLRwxAqQ'

# response = requests.put(
#     GRAPH_API_ENDPOINT + f'/me/drive/items/{one_drive_folder_id}/{file_name}:/content',
#     headers=headers,
#     data=media_content
# )

# print(response.json())


response = requests.put(
    GRAPH_API_ENDPOINT + f'/me/drive/items/root:/Photos/{file_name}:/content',
    headers=headers,
    data=media_content
)

print(response.json())


