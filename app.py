from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os 
import time
from langchain_core.documents import Document
from setupcouchbase import cb_vector_search, insert_user_message, insert_bot_message, update_bot_message_rating
from langchain.memory import ChatMessageHistory
from llm import create_openai_embeddings, create_hf_embeddings, generate_query_transform_prompt, generate_document_chain
from data_processor.data_reformat import data_reformat
from data_processor.metadata_tag import tag_metadata
import argparse 
from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from datetime import timedelta
from couchbase.options import (ClusterOptions, ClusterTimeoutOptions, QueryOptions)

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

#set up argparse 
parser = argparse.ArgumentParser()
parser.add_argument('--capella', action='store_true', default=False, help='if the environment is Capella')
args = parser.parse_args()
IS_CAPELLA = args.capella


#set up couchbase
if IS_CAPELLA:
    print("Start setting up Capella cluster..")
    endpoint = os.getenv("CB_HOSTNAME")
    auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
    options = ClusterOptions(auth)
    options.apply_profile('wan_development')
    cluster = Cluster('couchbases://{}'.format(endpoint), options)

    # Wait until the cluster is ready for use.

else: 
    # Connect options - authentication
    print("Start setting up EE cluster..")
    auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))

    # Get a reference to our cluster
    cluster = Cluster(f'couchbase://{os.getenv("EE_HOSTNAME")}', ClusterOptions(auth))


cluster.wait_until_ready(timedelta(seconds=5))
print("Couchbase setup complete")

    
chat_model_toggle = 1
embedding_model_toggle = "model1"

demo_ephemeral_chat_history = ChatMessageHistory()
    
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/update_chat_model_toggle', methods=['POST'])
def update_chat_model_toggle():
    global chat_model_toggle
    chat_model_toggle = request.json['value']
    return jsonify(success=True)


@app.route('/update_embedding_model_toggle', methods=['POST'])
def update_embedding_model_toggle():
    global embedding_model_toggle
    embedding_model_toggle = request.json['selectedModel']
    return jsonify(success=True)


@socketio.on('rating')
def handle_rating(rating_data):
    bot_message_id = rating_data['bot_message_id']
    score= rating_data['score']
    
    update_bot_message_rating(cluster, bot_message_id, score)


@socketio.on('message')
def handle_message(msg_to_process):
    
    query = msg_to_process['query']
    browserType = msg_to_process['browserType']
    deviceType = msg_to_process['deviceType']
    
    #0. add user message, both locally and to couchbase
    demo_ephemeral_chat_history.add_user_message(query)
    
    #1. incorporating the chat history together with the new questions to generate an independent prompt
    new_query = generate_query_transform_prompt(chat_model_toggle, demo_ephemeral_chat_history.messages)
    print(f"Generated query: {new_query}")
    
    #2. turn it into an embedding
    if embedding_model_toggle == "model1":
        vector = create_openai_embeddings(new_query)
    else:
        vector = create_hf_embeddings(new_query)
    print(f"Generated vector..")
   
    #3. using Couchbase SDK  
    if embedding_model_toggle == "model1":
        embedding_field = 'embedding'
    else:
        embedding_field = "embedding_hugging_face"
    
    result = cb_vector_search(cluster, embedding_field, vector, 'assembled_for_embedding')
    print(f"Search result retrieved..")
    
    #4. parsing the results
    product_ids = []
    additional_context = ""
    documents = []
    
    for row in result.rows():
        product_ids.append(row.id)
        
        additional_context += row.fields['assembled_for_embedding'] + "\n"
        documents.append(row.fields)
    
    #5. streaming
    document_chain = generate_document_chain(chat_model_toggle)
    
    message_string = ""   
    timestamp = int(time.time())
    
    for chunk in document_chain.stream({
        "input": new_query, 
        "context": [Document(page_content=additional_context)] 
    }):
        message_string += chunk
            
        emit('message', {
            "timestamp": timestamp, 
            "message_string": message_string,
            "document_ids": product_ids,
            "documents": documents
        }) 
        
    #6. add bot message, both locally and to couchbase
    demo_ephemeral_chat_history.add_ai_message(message_string)
    user_message_uuid = insert_user_message(cluster, query, new_query, deviceType, browserType)
    bot_message_id = insert_bot_message(cluster, message_string, user_message_uuid, chat_model_toggle, product_ids)
    
    if bot_message_id is not None:
        emit('bot_message_creation', bot_message_id)
   

@app.route('/create_embedding', methods=['POST'])
def split_string():
    data = request.get_json()
    string = data.get('string', '')
    
    openai_embedding = create_openai_embeddings(string)
    hugging_face_embedding = create_hf_embeddings(string)
    
    return jsonify([openai_embedding, hugging_face_embedding])


@app.route('/data_reformatting', methods=['POST'])
def data_reformatting():
    data = request.get_json()
    
    # Process "last_update" field
    processed_data = data_reformat(data)

    return jsonify(processed_data)


@app.route('/metadata_tag', methods=['POST'])
def metadata_tag():
    data = request.get_json()
    
    # Process "last_update" field
    type = tag_metadata(data)

    return jsonify(type)

    
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)