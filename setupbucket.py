import os
import requests
from dotenv import load_dotenv

load_dotenv()


BASEURL = "https://cloudapi.cloud.couchbase.com"
TOKEN = os.getenv("CAPELLA_API_KEY_TOKEN")
ORG_ID = os.getenv("ORG_ID")
PROJECT_ID = os.getenv("PROJECT_ID")
CLUSTER_ID = os.getenv("CLUSTER_ID")


print("start setting up data structures..")

#some shared variables 
headers = {"Authorization": f"Bearer {TOKEN}"}


#create bucket main 
BUCKET_MAIN_ID = None 
url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets"

body = {
    "name": "main",
    "type": "couchbase",
    "storageBackend": "couchstore",
    "memoryAllocationInMb": 2000,
    "bucketConflictResolution": "seqno",
    "replicas": 1,
    "flush": True,
}

response = requests.post(url, headers=headers, json=body)

if response.status_code == 201:
    data = response.json()
    BUCKET_MAIN_ID = data['id']
    print("Created bucket 'main'")
else:
    print(f"Error: {response.text}")


#create bucket meta 
BUCKET_META = "meta"

body = {
    "name": BUCKET_META,
    "type": "couchbase",
    "storageBackend": "couchstore",
    "memoryAllocationInMb": 1000,
    "bucketConflictResolution": "seqno",
    "replicas": 1,
    "flush": True,
}

response = requests.post(url, headers=headers, json=body)

if response.status_code == 201:
    print("Created bucket 'meta'")
else:
    print(f"Error: {response.text}")


#create scope raw and data under BUCKET_MAIN
if BUCKET_MAIN_ID is not None:
    SCOPE_RAW_CREATED = False
    SCOPE_DATA_CREATED = False
    SCOPE_CHATS_CREATED = False
    scope_url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets/{BUCKET_MAIN_ID}/scopes"
    
    #create scope raw
    response = requests.post(scope_url, headers=headers, json={"name": "raw"})
    if response.status_code == 201:
        SCOPE_RAW_CREATED = True
        print("Created scope 'main.raw'")
    else:
        print(f"Error: {response.text}")
        
    #create scope data
    response = requests.post(scope_url, headers=headers, json={"name": "data"})
    if response.status_code == 201:
        SCOPE_DATA_CREATED = True
        print("Created scope 'main.data'")
    else:
        print(f"Error: {response.text}")
        
    #create scope chats
    response = requests.post(scope_url, headers=headers, json={"name": "chats"})
    if response.status_code == 201:
        SCOPE_CHATS_CREATED = True
        print("Created scope 'main.chats'")  
    else:
        print(f"Error: {response.text}")
        
    
    #create collection human under scope chats
    if SCOPE_CHATS_CREATED is True:
        collection_url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets/{BUCKET_MAIN_ID}/scopes/chats/collections"
        response = requests.post(collection_url, headers=headers, json={"name": "human"})
        if response.status_code == 201:
            print("Created collection 'main.chats.human'")
        else:
            print(f"Error: {response.text}")
        
        #create collection bot under scope chats
        collection_url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets/{BUCKET_MAIN_ID}/scopes/chats/collections"
        response = requests.post(collection_url, headers=headers, json={"name": "bot"})
        if response.status_code == 201:
            print("Created collection 'main.chats.bot'")
        else:
            print(f"Error: {response.text}")
    
    
    #create collection raw under scope raw
    if SCOPE_RAW_CREATED is True:
        collection_url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets/{BUCKET_MAIN_ID}/scopes/raw/collections"
        response = requests.post(collection_url, headers=headers, json={"name": "raw"})
        if response.status_code == 201:
            print("Created collection 'main.raw.raw'")
        else:
            print(f"Error: {response.text}")
            
        #create collection formatted under scope raw
        collection_url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets/{BUCKET_MAIN_ID}/scopes/raw/collections"
        response = requests.post(collection_url, headers=headers, json={"name": "formatted"})
        if response.status_code == 201:
            print("Created collection 'main.raw.formatted'")
        else:
            print(f"Error: {response.text}")
            
    #create collection products under scope data
    if SCOPE_DATA_CREATED is True:
        collection_url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets/{BUCKET_MAIN_ID}/scopes/data/collections"
        response = requests.post(collection_url, headers=headers, json={"name": "products"})
        if response.status_code == 201:
            print("Created collection 'main.data.products'")
        else:
            print(f"Error: {response.text}")
            
        #create collection policies under scope data
        collection_url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets/{BUCKET_MAIN_ID}/scopes/data/collections"
        response = requests.post(collection_url, headers=headers, json={"name": "policies"})
        if response.status_code == 201:
            print("Created collection 'main.data.policies'")
        else:
            print(f"Error: {response.text}")
    
    
else:
    print("Error: BUCKET_MAIN_ID is None")


print('Setup complete.')
    


