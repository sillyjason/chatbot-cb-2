from datetime import timedelta
import os
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
import requests
from dotenv import load_dotenv
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions,
                               QueryOptions)


load_dotenv()


BASEURL = "https://cloudapi.cloud.couchbase.com"
TOKEN = os.getenv("CAPELLA_API_KEY_TOKEN")

url = f"{BASEURL}/v4/organizations"
headers = {"Authorization": f"Bearer {TOKEN}"}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    organization_id = data[0]['id']
    print(f"Organization ID: {organization_id}")
else:
    print(f"Error: {response.text}")