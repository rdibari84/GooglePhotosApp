import requests
from httplib2 import Http
from oauth2client import file, client, tools
import json
import click

'''
Look for credentials.json and check if creds stored are valid
If not present, get a Flow object, open an authorization server page in the user’s default web browser for the user to grant access & save creds in credentials.json
If not valid, just refresh the token
http://oauth2client.readthedocs.io/en/latest/source/oauth2client.tools.html
http://oauth2client.readthedocs.io/en/latest/source/oauth2client.client.html#oauth2client.client.flow_from_clientsecrets
'''
class Photo():
    def __init__(self):
        self.url = "https://photoslibrary.googleapis.com/v1/"
        self.token = self.get_access_token()

    def get_access_token(self):
        SCOPES = 'https://www.googleapis.com/auth/photoslibrary'
        store = file.Storage('credentials.json')
        creds = store.get()
        if not creds:
            print("Missing access_token. Fetching...")
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)
        elif creds.access_token_expired == True:  # looks at expiration date
            print("access_token is invalid or has expired. refreshing...")
            http = creds.authorize(Http())
            creds.refresh(http)  # recreates the credentials.json
            store = file.Storage('credentials.json')
            creds = store.get()
        else:
            print("access_token ist gut!")
        return creds.get_access_token().access_token

    def list_albums(self):
        r = requests.get(self.url + "albums",headers={"Authorization": "Bearer " + self.token})
        if r.status_code != 200:
            raise Exception("Received " + str(r.status_code) + ". Cannot connect to google photos. Reason: " + r.text)
        else:
            print(r.text)
            print("Alles Klar!")

    def create_album(self,name):
        b = {}
        b["album"] = {}
        b["album"]["title"] = name
        json_data = json.dumps(b)
        r = requests.post(self.url + "albums", headers={"Authorization": "Bearer " + self.token}, data=json_data)
        if r.status_code != 200:
            raise Exception("Received " + str(r.status_code) + ". Cannot connect to google photos. Reason: " + r.text)
        else:
            print(r.text)
            print("Alles Klar!")

    def upload(self, albumId, filename):
        with open(filename, 'rb') as f:
            r = requests.post(self.url + "uploads", headers={"Authorization": "Bearer " + self.token,
                                            "Content-type": "application/octet-stream"}, data=f.read())
        f.close()
        if r.status_code != 200:
            raise Exception("Received " + str(r.status_code) + ". Cannot connect to google photos. Reason: " + r.text)

        upload_token = r.text
        print("Recieved upload token! ", upload_token )
        data = NewMediaItems(albumId, upload_token, "test").to_json()
        r = requests.post(self.url + "mediaItems:batchCreate", headers={"Authorization": "Bearer " + self.token,
                                        "Content-type": "application/json"}, data=data)
        if r.status_code != 200:
            raise Exception("Received " + str(r.status_code) + ". Cannot connect to google photos. Reason: " + r.text)
        print(r.text)

class NewMediaItems():
    def __init__(self, albumId, upload_token, description):
        self.albumId = albumId
        self.uploadToken = upload_token
        self.description = description

    def to_json(self):
        data = {}
        data["albumId"] = self.albumId
        newMediaItems = []
        data1 = {}
        data1["description"] = self.description
        data1["simpleMediaItem"] = {}
        data1["simpleMediaItem"]["uploadToken"] = self.uploadToken
        newMediaItems.append(data1)
        data["newMediaItems"] = newMediaItems

        print(data)
        return json.dumps(data)

@click.command()
@click.option('--name', '-n', help='Name of album')
@click.option('--filename', '-f', help='Name of file to upload')
@click.option('--albumid', '-a', help='AlbumId to upload photo to')
@click.option('--action', type=click.Choice(['create_album', 'list_albums', 'upload']))
def cli(action, name, filename, albumid):
    p = Photo()
    if action=="create_album":
        if not name:
            raise Exception("Must provide a name for the album")
        p.create_album()
    if action == "list_albums":
        p.list_albums()
    if action == "upload":
        if not filename:
            raise Exception("Must provide a filename to upload")
        p.upload(albumid, filename)

if __name__ == "__main__":
    cli()
