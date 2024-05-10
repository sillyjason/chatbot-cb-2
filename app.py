from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os 
import time
from langchain_core.documents import Document
from cb_setup.couchbase import cb_vector_search, insert_user_message, insert_bot_message, update_bot_message_rating
from langchain.memory import ChatMessageHistory
from llm import create_openai_embeddings, create_hf_embeddings, generate_query_transform_prompt, generate_document_chain
from data_processor.data_reformat import data_reformat
from data_processor.metadata_tag import tag_metadata

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

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
    
    update_bot_message_rating(bot_message_id, score)
    
    
@socketio.on('message')
def handle_message(msg_to_process):
    
    query = msg_to_process['query']
    browserType = msg_to_process['browserType']
    deviceType = msg_to_process['deviceType']
    
    #0. add user message, both locally and to couchbase
    demo_ephemeral_chat_history.add_user_message(query)
    
    #1. incorporating the chat history together with the new questions to generate an independent prompt
    new_query = generate_query_transform_prompt(chat_model_toggle, demo_ephemeral_chat_history.messages)
    
    #2. turn it into an embedding
    if embedding_model_toggle == "model1":
        vector = create_openai_embeddings(new_query)
    else:
        vector = create_hf_embeddings(new_query)
   
    #3. using Couchbase SDK  
    key_context_field = os.getenv("KEY_CONTEXT_FIELD")
    
    if embedding_model_toggle == "model1":
        embedding_field = 'embedding'
    else:
        embedding_field = "embedding_hugging_face"
    
    print("embedding field: ", embedding_field)   
    result = cb_vector_search(embedding_field, vector, key_context_field)
    
    #4. parsing the results
    product_ids = []
    additional_context = ""
    documents = []
    
    for row in result.rows():
        product_ids.append(row.id)
        
        additional_context += row.fields[key_context_field] + "\n"
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
    user_message_uuid = insert_user_message(query, new_query, deviceType, browserType)
    bot_message_id = insert_bot_message(message_string, user_message_uuid, chat_model_toggle, product_ids)
    
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