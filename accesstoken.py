import webbrowser
from msal import ConfidentialClientApplication, PublicClientApplication


app_id = 'fcaecfc0-be18-4ae4-a4bd-b4735aa7082a'
SCOPES = ['User.Read']

client = PublicClientApplication(client_id=app_id)

flow = client.initiate_device_flow(scopes=SCOPES)
print(flow)
webbrowser.open(flow['verification_uri'])
