import os
import requests
from dotenv import load_dotenv
import json 
import re
import os
import argparse 

load_dotenv()
#set up argparse 
parser = argparse.ArgumentParser()
parser.add_argument('--capella', action='store_true', default=False, help='if the environment is Capella')
args = parser.parse_args()
IS_CAPELLA = args.capella

EVENTING_HOSTNAME = os.getenv("EVENTING_HOSTNAME")
SEARCH_HOSTNAME = os.getenv("SEARCH_HOSTNAME")
CB_USERNAME = os.getenv("CB_USERNAME")
CB_PASSWORD = os.getenv("CB_PASSWORD")
CHATBOT_APP_END_POINT= os.getenv("CHATBOT_APP_END_POINT")


#updating the endpoint in templates/index.html 
index_file = "./templates/index.html"

try:
    with open(index_file, 'r') as file:
        content = file.read()
        updated_content = content.replace("http://localhost:5000", f"http://{CHATBOT_APP_END_POINT}:5000")
    
    with open(index_file, 'w') as file:
        file.write(updated_content)
    
    print("Endpoint updated successfully in index.html")
    
except Exception as e:
    print(f"Error updating endpoint in index.html: {str(e)}")
    


# setup functions 
def import_function(function_name):
    
    if IS_CAPELLA:
        return 
    
    print(f"Importing function {function_name}...")
    
    try:
        url = f"http://{EVENTING_HOSTNAME}:8096/api/v1/functions/{function_name}"

        with open(f'./templates/assets/eventing/{function_name}.json', 'r') as file:
            data = json.load(file)
            data_str = json.dumps(data)
            data_str = re.sub(r"ec2-.+\.com", CHATBOT_APP_END_POINT, data_str)
            data = json.loads(data_str)
            
        response = requests.post(url, json=data, auth=(CB_USERNAME, CB_PASSWORD))
        response.raise_for_status()

        print(f"Function {function_name} imported successfully")
    
    except Exception as e:
        print(f"Error importing function {function_name}: {str(e)}")

import_function("reformatting")
import_function("metadata_labelling")
import_function("embedding")


#setup fts index
def import_fts_index():
    if IS_CAPELLA:
        return 
    
    print(f"Importing fts index...")
    
    try:
        url = f"http://{SEARCH_HOSTNAME}:8094/api/bucket/main/scope/data/index/embedding-index"
        with open(f'./templates/assets/fts-index.json', 'r') as file:
            data = json.load(file)
            requests.put(url, auth=(CB_USERNAME, CB_PASSWORD), json=data)
            print('fts index imported successfully')
            

    except Exception as e:
        print(f"Error importing fts index: {str(e)}")

import_fts_index()

print("setup complete.")