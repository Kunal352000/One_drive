import os
import requests
from azure.storage.blob import BlobServiceClient
from ms_graph import generate_access_token, GRAPH_API_ENDPOINT
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

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

    if item_response.status_code == 200:
        item_data = item_response.json()
        if 'value' in item_data:
            for item in item_data['value']:
                if item['name'].lower() == 'photos':
                    item_id = item['id']
                    print("this is my item-id", item_id)
                    break

        if item_id:
            response = requests.get(
                f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/items/{item_id}/children',
                headers={'Authorization': 'Bearer ' + access_token['access_token']}
            )

            if response.status_code == 200:
                files = response.json().get('value', [])
                watermark_image_id = None

                for file in files:
                    if file['name'].lower() == 'watermarkimage.jpg':
                        watermark_image_id = file['id']
                        break

                if watermark_image_id:
                    watermark_image_response = requests.get(
                        f'{GRAPH_API_ENDPOINT}/drives/{drive_id}/items/{watermark_image_id}/content',
                        headers={'Authorization': 'Bearer ' + access_token['access_token']}
                    )

                    if watermark_image_response.status_code == 200:
                        # Open the watermark image
                        watermark_image = Image.open(BytesIO(watermark_image_response.content)).convert("RGBA")

                        # Reduce opacity of watermark image
                        opacity = 0.5  # Adjust the opacity as needed
                        watermark_image = watermark_image.convert("RGBA")
                        watermark_image_blended = Image.blend(watermark_image, Image.new("RGBA", watermark_image.size), opacity)

                        for file in files:
                            # print("my file",file)
                            if (
                                file.get('file', {}).get('mimeType', '').startswith('image/')
                                and file['name'].lower().endswith('.jpg')
                            ):
                                file_name = file['name']
                                # print("my file name",file_name)
                                file_download_url = file.get('@microsoft.graph.downloadUrl')

                                if file_download_url:
                                    file_response = requests.get(file_download_url)

                                    if file_response.status_code == 200:
                                        # Open the image file
                                        image = Image.open(BytesIO(file_response.content))

                                        # Add text to the image
                                        draw = ImageDraw.Draw(image)
                                        text = "Scoutfoto.com"
                                        font = ImageFont.truetype('arial.ttf', size=60)  # Use Arial font and increase size
                                        text_width, text_height = draw.textsize(text, font)
                                        position = (
                                            (image.width - text_width) // 2,
                                            (image.height - text_height) // 2
                                        )
                                        draw.text(position, text, fill=(255, 255, 0), font=font)  # Set font color to yellow (255, 255, 0)

                                        # Save the modified image to a byte array
                                        output = BytesIO()
                                        image.save(output, format='JPEG')
                                        output.seek(0)

                                        # Upload the modified image file to Azure Blob Storage
                                        blob_client = blob_service_client.get_blob_client(
                                            container=container_name, blob=file_name
                                        )
                                        blob_client.upload_blob(output)
                                        print(f"Uploaded file with watermark: {file_name}")
                                    else:
                                        print(f"Failed to download file: {file_name}")
                                else:
                                    print(f"Download URL not found for file: {file_name}")
                    else:
                        print("Failed to download watermark image.")
                else:
                    print("Watermark image not found.")
            else:
                print("Failed to retrieve folder content.")
        else:
            print("Photos folder not found.")
    else:
        print("Failed to retrieve item information.")
else:
    print("Drive information not available.")
