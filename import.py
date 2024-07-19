import os
import requests
import json
from datetime import datetime
from secrets import api_url, api_key


local_album_dir = "/home/alex/Downloads/Takeout/Google Photos"
headers = {
    "Accept": "application/json",
    "x-api-key": api_key
}


def create_album(album_name):
    new_album = {
        "albumName": album_name
    }
    resp = requests.post(f"{api_url}/albums", data=new_album, headers=headers)

    if resp.status_code != 201:
        raise Exception("Error creating album", resp.status_code, resp.text)

    created_album = json.loads(resp.text)
    print("Created album", album_name, "with id", created_album["id"])
    return created_album


def get_album_info(album):
    resp = requests.get(f"{api_url}/albums/{album['id']}", headers=headers)

    if resp.status_code != 200:
        raise Exception("Error getting album", resp.status_code, resp.text)

    return json.loads(resp.text)


def upload_asset(asset_path):

    stats = os.stat(asset_path)
    data = {
        'deviceAssetId': f'{asset_path}-{stats.st_mtime}',
        'deviceId': 'python',
        'fileCreatedAt': datetime.fromtimestamp(stats.st_mtime),
        'fileModifiedAt': datetime.fromtimestamp(stats.st_mtime),
        'isFavorite': 'false',
    }
    files = {
        'assetData': open(asset_path, 'rb')
    }
    resp = requests.post(f"{api_url}/assets", data=data, files=files, headers=headers)

    if resp.status_code != 200 and resp.status_code != 201:
        raise Exception("Error uploading asset", resp.status_code, resp.text)

    asset = json.loads(resp.text)
    print("Uploaded asset", asset["id"], "status:", asset['status'])
    return asset


def upload_album(album, album_path, files_already_uploaded=[]):
    # First upload the photos as assets
    print(f"Uploading album {album['albumName']} ({album['id']}) with {len(files_already_uploaded)} files already uploaded")
    album_asset_ids = []
    for photo in os.listdir(album_path):
        if photo.endswith(".json") or photo.endswith(".MP"):
            continue
        photo_path = os.path.join(album_path, photo)
        if photo_path in files_already_uploaded:
            continue
        print("Uploading", photo_path)
        asset = upload_asset(photo_path)
        album_asset_ids.append(asset["id"])

        # There is a maximum number of 1000 assets per request
        if len(album_asset_ids) == 1000:
            break

    print("Adding", len(album_asset_ids), "assets to album")
    album_assets = {
        "ids": album_asset_ids
    }
    resp = requests.put(f"{api_url}/albums/{album['id']}/assets", data=album_assets, headers=headers)

    if resp.status_code != 200:
        if "ids must be an array" not in resp.text:
            raise Exception("Error adding assets to album", resp.status_code, resp.text)


def get_existing_albums():
    resp = requests.get(f"{api_url}/albums", headers=headers)

    if resp.status_code != 200:
        print(resp.status_code, resp.text)
        return

    existing_albums = json.loads(resp.text)
    album_map = {}
    for album in existing_albums:
        album_map[album['albumName']] = album
    return album_map


def upload_unuploaded_assets(local_album, album_info):

    album_path = os.path.join(local_album_dir, local_album)

    files_already_uploaded = []
    for asset in album_info['assets']:
        file_and_date = asset['deviceAssetId']
        sep_idx = file_and_date.rfind("-")
        file_path = file_and_date[:sep_idx]
        if os.path.exists(file_path):
            files_already_uploaded.append(file_path)
            continue
        # This deviceAssetId does not always have the original file path for some reason
        # Try to reconstruct it from the album path and file name
        file_path = os.path.join(album_path, asset['originalFileName'])
        if os.path.exists(file_path):
            files_already_uploaded.append(file_path)
        else:
            print("Could not find local file:", file_path)

    upload_album(album_info, album_path, files_already_uploaded)


def import_albums():
    albums_to_import = os.listdir(local_album_dir)

    # Get the list of albums from Immich

    existing_albums = get_existing_albums()

    # for album in existing_albums:
    #     existing_album_names.append(album['albumName'])
    #     print(album)

    # # Iterate through all local albums that have not yet been created
    # for album in [a['albumName'] for a in albums_to_import if a not in existing_albums]:
    #     create_album(album)

    # Iterate through all local albums and upload assets that haven't already been uploaded

    for album in albums_to_import:
        existing_album = existing_albums.get(album)
        if existing_album is not None:
            # Album already exists, try to get a list of asset files
            album_info = get_album_info(existing_album)
            upload_unuploaded_assets(album, album_info)
            print("Album", album_info['albumName'], "has", len(album_info['assets']), "assets")
        else:
            print("Album", album, "does not exist")
    #
    # for album in [a for a in existing_albums if a["assetCount"] == 0]:
    #
    #     album_path = os.path.join(local_album_dir, album["albumName"])
    #
    #     if os.path.exists(album_path) and len(os.listdir(album_path)) > 0:
    #         print("Uploading album", album["albumName"], album_path)
    #         upload_album(album, album_path)
    #     else:
    #         print("No photos to upload in", album_path)

        # Get existing assets in album
        # album_info = get_album_info(album)
        # print("Got album info:", album_info)


# {'albumName': "Dom's Tree", 'description': '', 'albumThumbnailAssetId': '5b5fd905-6037-4635-9a89-88d4f209c2ee', 'createdAt': '2024-07-17T13:08:05.613Z', 'updatedAt': '2024-07-17T13:08:20.143Z', 'id': '83f01f4e-49ca-4492-950a-561840b36298', 'ownerId': 'a14d82eb-7b2f-4928-bdcb-c63dce4877ed', 'owner': {'id': 'a14d82eb-7b2f-4928-bdcb-c63dce4877ed', 'email': 'alexspurling@gmail.com', 'name': 'Alex', 'profileImagePath': '', 'avatarColor': 'pink'}, 'albumUsers': [], 'shared': False, 'hasSharedLink': False, 'startDate': '2003-06-29T15:34:00.000Z', 'endDate': '2003-06-29T16:35:18.000Z', 'assets': [], 'assetCount': 7, 'isActivityEnabled': True, 'order': 'desc', 'lastModifiedAssetTimestamp': '2024-07-13T15:34:31.000Z'}


import_albums()
