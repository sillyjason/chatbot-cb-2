from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from langchain.memory import ChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv
from langchain_community.vectorstores import CouchbaseVectorStore
from langchain_openai import OpenAIEmbeddings
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import os 
from datetime import timedelta
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import Dict
from langchain_core.runnables import RunnablePassthrough
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import time



load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

messages = []
demo_ephemeral_chat_history = ChatMessageHistory()

chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.99)

question_answering_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Answer the user's questions based on the below context:\n\n{context}",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

document_chain = create_stuff_documents_chain(chat, question_answering_prompt)

def parse_retriever_input(params: Dict):
    return params["messages"][-1].content

COUCHBASE_CONNECTION_STRING = os.getenv("CB_HOSTNAME")
DB_USERNAME = os.getenv("CB_USERNAME")
DB_PASSWORD = os.getenv("CB_PASSWORD")
    
auth = PasswordAuthenticator(DB_USERNAME, DB_PASSWORD)
options = ClusterOptions(auth)
cluster = Cluster(COUCHBASE_CONNECTION_STRING, options)

# Wait until the cluster is ready for use.
cluster.wait_until_ready(timedelta(seconds=5))
BUCKET_NAME = "vector-sample"
SCOPE_NAME = "color"
COLLECTION_NAME = "rgb"
SEARCH_INDEX_NAME = "color-index"

embeddings = OpenAIEmbeddings()

loader = WebBaseLoader("https://docs.smith.langchain.com/overview") 
data = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
all_splits = text_splitter.split_documents(data)    
    
vectorstore = CouchbaseVectorStore(
    embedding=embeddings,
    cluster=cluster,
    bucket_name=BUCKET_NAME,
    scope_name=SCOPE_NAME,
    collection_name=COLLECTION_NAME,
    index_name=SEARCH_INDEX_NAME,
)

retriever = vectorstore.as_retriever(k=4)


retrieval_chain = RunnablePassthrough.assign(
    context=parse_retriever_input | retriever,
).assign(
    answer=document_chain,
)

retrival_chain_parser = (
    retrieval_chain
    | StrOutputParser()
)
    
@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(msg):
    messages.append(msg)
    demo_ephemeral_chat_history.add_user_message(msg)

    message_string = ""
    
    timestamp = int(time.time())
    
    for chunk in retrieval_chain.stream({"messages": demo_ephemeral_chat_history.messages}): 
        print('chunk here is:', chunk)
        
        if "answer" in chunk:
            message_string += chunk["answer"]
            
        emit('message', {
            "timestamp": timestamp, 
            "message_string": message_string
        })  
    
    messages.append(message_string)
    
    
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)