import os
import requests
from dotenv import load_dotenv
import argparse 
from requests.auth import HTTPBasicAuth

load_dotenv()

#set up argparse 
parser = argparse.ArgumentParser()
parser.add_argument('--capella', action='store_true', default=False, help='if the environment is Capella')
args = parser.parse_args()
IS_CAPELLA = args.capella

init_message = "Setting up for Capella.." if IS_CAPELLA else "Setting up for Servers.."
print(init_message)

#get the environment variables
BASEURL = "https://cloudapi.cloud.couchbase.com"
TOKEN = os.getenv("CAPELLA_API_KEY_TOKEN")
ORG_ID = os.getenv("ORG_ID")
PROJECT_ID = os.getenv("PROJECT_ID")
CLUSTER_ID = os.getenv("CLUSTER_ID")
EE_HOSTNAME = os.getenv("EE_HOSTNAME")


print("start setting up data structures..")

#some shared variables 
headers = {"Authorization": f"Bearer {TOKEN}"}


def create_bucket(bucket_name, ram_quota): 
    url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets" if IS_CAPELLA else f"http://{EE_HOSTNAME}:8091/pools/default/buckets"
    
    body = { 
        "name": bucket_name,
        "type": "couchbase",
        "storageBackend": "couchstore",
        "memoryAllocationInMb": ram_quota,
        "bucketConflictResolution": "seqno",
        "replicas": 1,
        "flush": True
    } if IS_CAPELLA else {
        'name': bucket_name,
        'ramQuota': ram_quota,
        'bucketType': 'couchbase',
        'flushEnabled': 1
    }
    
    response = requests.post(url, headers=headers, json=body) if IS_CAPELLA else requests.post(url, auth=HTTPBasicAuth(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD")), data=body)

    success_code = 201 if IS_CAPELLA else 202
    if response.status_code == success_code:
        print(f"Created bucket '{bucket_name}'")
        return response.json()['id'] if IS_CAPELLA else True
    
    else:
        print(f"Error creating bucket {bucket_name}: {response.text}")
        return None


def create_scope(bucket_id, scope_name, bucket_name):
    url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets/{bucket_id}/scopes" if IS_CAPELLA else f"http://{EE_HOSTNAME}:8091/pools/default/buckets/{bucket_name}/scopes"
    response = requests.post(url, headers=headers, json={"name": scope_name}) if IS_CAPELLA else requests.post(url, auth=HTTPBasicAuth(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD")), data={"name": scope_name})
    success_code = 201 if IS_CAPELLA else 200
    if response.status_code == success_code:
        print(f"Created scope '{bucket_name}.{scope_name}'")
        return True
    else:
        print(f"Error creating scope {scope_name}: {response.text}")
        return False

def create_collection(bucket_id, bucket_name, scope_name, collection_name):
    url = f"{BASEURL}/v4/organizations/{ORG_ID}/projects/{PROJECT_ID}/clusters/{CLUSTER_ID}/buckets/{bucket_id}/scopes/{scope_name}/collections" if IS_CAPELLA else f"http://{EE_HOSTNAME}:8091/pools/default/buckets/{bucket_name}/scopes/{scope_name}/collections"
    response = requests.post(url, headers=headers, json={"name": collection_name}) if IS_CAPELLA else requests.post(url, auth=HTTPBasicAuth(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD")), data={"name": collection_name})
 
    success_code = 201 if IS_CAPELLA else 200
    if response.status_code == success_code:
        print(f"Created collection '{bucket_name}.{scope_name}.{collection_name}'")
        return True
    else:
        print(f"Error creating colletion {collection_name}: {response.text}")
        return False


#create bucket main 
BUCKET_MAIN_ID = create_bucket("main", 2000)

#create bucket meta
create_bucket("meta", 1000)

if BUCKET_MAIN_ID is not None:
    scope_raw_created = create_scope(BUCKET_MAIN_ID, "raw", "main")
    scope_data_created = create_scope(BUCKET_MAIN_ID, "data", "main")
    scope_chats_created = create_scope(BUCKET_MAIN_ID, "chats", "main")
    
    if scope_raw_created:
        create_collection(BUCKET_MAIN_ID, "main", "raw", "raw")
        create_collection(BUCKET_MAIN_ID, "main", "raw", "formatted")
    
    if scope_data_created:
        create_collection(BUCKET_MAIN_ID, "main", "data", "products")
        create_collection(BUCKET_MAIN_ID, "main", "data", "policies")
        
    if scope_chats_created:
        create_collection(BUCKET_MAIN_ID, "main", "chats", "human")
        create_collection(BUCKET_MAIN_ID, "main", "chats", "bot")

print("Done setting up data structures..")


