from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from langchain.memory import ChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import os 
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import time
from openai import OpenAI
from couchbase.vector_search import VectorQuery, VectorSearch
import couchbase.search as search
from couchbase.options import SearchOptions
from langchain_core.documents import Document

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)


# Couchbase connection setup
pa = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
cluster = Cluster(os.getenv("CB_HOSTNAME") + "/?ssl=no_verify", ClusterOptions(pa))
bucket = cluster.bucket(os.getenv("CB_BUCKET_NAME"))
scope = bucket.scope(os.getenv("CB_SCOPE_NAME"))
collection = scope.collection(os.getenv("CB_COLLECTION_NAME"))
search_index = os.getenv("CB_VECTOR_INDEX_NAME")

# OpenAI chat setup
demo_ephemeral_chat_history = ChatMessageHistory()
chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.1)    
client = OpenAI()
embeddings = OpenAIEmbeddings()
prompt = ChatPromptTemplate.from_template("""Answer the following question incorporating the following context:

<context>
{context}
</context>

Question: {input}""")
    
document_chain = create_stuff_documents_chain(chat, prompt)

query_transform_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
        ),
    ]
)

query_transformation_chain = query_transform_prompt | chat

    
@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(msg):
    demo_ephemeral_chat_history.add_user_message(msg)

    #0. setup variables
    message_string = ""   
    timestamp = int(time.time())
    
    #1. incorporating the chat history together with the new questions to generate an independent prompt
    new_query = query_transformation_chain.invoke({"messages": demo_ephemeral_chat_history.messages}).content 
    
    #2. turn it into an embedding
    vector = client.embeddings.create(input = [new_query], model="text-embedding-ada-002").data[0].embedding
    
    #3. using Couchbase SDK 
    
    key_context_field = os.getenv("KEY_CONTEXT_FIELD")
    
    search_req = search.SearchRequest.create(search.MatchNoneQuery()).with_vector_search(
    VectorSearch.from_vector_query(VectorQuery(os.getenv("EMBEDDING_FIELD"), vector, num_candidates=3)))
    result = scope.search(search_index, search_req, SearchOptions(limit=13,fields=[key_context_field, "source"]))
    
    #4. parsing the results
    ids = []
    additional_context = ""
    documents = []
    
    for row in result.rows():
        ids.append(row.id)
        
        print('ROW DATA: ', row)
        
        additional_context += row.fields[key_context_field] + "\n"
        documents.append(row.fields)
    
    #5. streaming
    for chunk in document_chain.stream({"input": new_query, "context": [Document(page_content=additional_context)] }):
        message_string += chunk
            
        emit('message', {
            "timestamp": timestamp, 
            "message_string": message_string,
            "document_ids": ids,
            "documents": documents
        })  
    
    demo_ephemeral_chat_history.add_ai_message(message_string)
    
    
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)