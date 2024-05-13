import os
import requests
from dotenv import load_dotenv
import json 

load_dotenv()

EVENTING_HOSTNAME = os.getenv("EVENTING_HOSTNAME")
SEARCH_HOSTNAME = os.getenv("SEARCH_HOSTNAME")
CB_USERNAME = os.getenv("CB_USERNAME")
CB_PASSWORD = os.getenv("CB_PASSWORD")
CHATBOT_APP_END_POINT= os.getenv("CHATBOT_APP_END_POINT")

# setup functions 
print("Importing functions...")

def import_function(function_name):
    try:
        url = f"http://{EVENTING_HOSTNAME}:8096/api/v1/functions/{function_name}"

        with open(f'./templates/assets/eventing/{function_name}.json', 'r') as file:
            data = json.load(file)
            data_str = json.dumps(data)
            data_str = data_str.replace("ec2-*.ap-southeast-1.compute.amazonaws.com", CHATBOT_APP_END_POINT)
            data = json.loads(data_str)
            
        response = requests.post(url, json=data, auth=(CB_USERNAME, CB_PASSWORD))
        response.raise_for_status()

        print(f"Function {function_name} imported successfully")
    
    except Exception as e:
        print(f"Error importing function {function_name}: {str(e)}")
    

import_function("reformatting")
import_function("metadata_labelling")
import_function("embedding")
    
print("Functions imported successfully!")


#setup fts index
print('importing fts index...')
def import_fts_index():
    try:
        url = f"http://{SEARCH_HOSTNAME}:8094/api/bucket/main/scope/data/index/embedding-index"
        
        print("url: ", url)
        with open(f'./templates/assets/fts-index.json', 'r') as file:
            print("file: ", file)
            data = json.load(file)
            response = requests.put(url, auth=(CB_USERNAME, CB_PASSWORD), json=data)
            response_json = response.json()
            print(response_json)
            

    except Exception as e:
        print(f"Error importing fts index: {str(e)}")

import_fts_index()

print("FTS index imported successfully!")