import os
import uuid
import time
import requests
from urllib.parse import urlparse, parse_qs

import mimetypes




STORAGE_PATH = "/tmp/"

def download_file(url, storage_path="/tmp/"):
    # Parse the URL to extract the file ID from the query parameters
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Use the 'id' parameter as the filename if it exists
    file_id = str(uuid.uuid4())
    
    if not file_id:
       raise ValueError("Invalid URL: 'id' parameter not found in the URL")
    
    # Ensure the storage directory exists
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    
    
    # UA = 'Midjourney-image-downloader/0.0.1'
    # HEADERS = {'User-Agent': UA}

    # SESSION_TOKEN = None
    # COOKIES = {'__Secure-next-auth.session-token': SESSION_TOKEN, '__cf_bm':'dsKAITdZBaf4Fxn.F6wpXdi_glT_qQLHBBhgjJPYmqE-1732485846-1.0.1.1-EuQYknxoJZrsswCQkefVaqQLmFweiAwvpWloUxx5rgYLf2rDhaYdYKb1NNK6DdkonTn5mtL29cMxge0fNBlLBA'}



    # Download the file
    response = requests.get(url, stream=True)
    response.raise_for_status()
    content_type = response.headers['content-type']
    extension = mimetypes.guess_extension(content_type)

    # Use the file ID as the filename and save it in the specified storage path
    local_filename = os.path.join(storage_path, f"{file_id}{extension}")  # Assuming mp4; adjust extension if needed
    

    with open(local_filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    return local_filename


def delete_old_files():
    now = time.time()
    for filename in os.listdir(STORAGE_PATH):
        file_path = os.path.join(STORAGE_PATH, filename)
        if os.path.isfile(file_path) and os.stat(file_path).st_mtime < now - 3600:
            os.remove(file_path)



'''
# While you cannot directly transform a URL into a UUID, you can use the URL as a seed to generate a UUID. Here's how you can do it using Python's uuid and hashlib modules:


import uuid
import hashlib

def url_to_uuid(url):
    # Create a hash object using SHA-256
    hash_object = hashlib.sha256(url.encode())
    # Get the hexadecimal representation of the hash
    hash_hex = hash_object.hexdigest()
    # Create a UUID from the hash
    return uuid.UUID(hash_hex[:32])

url = "https://www.example.com/some/path"
uuid_value = url_to_uuid(url)
print(uuid_value)


'''