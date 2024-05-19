from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os 
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings


chat_openai = ChatOpenAI(model="gpt-4o", temperature=0.1)    

chat_claude = ChatAnthropic(temperature=0.1, api_key=os.getenv('ANTHROPIC_API_KEY'), model_name="claude-3-haiku-20240307")

client_openai = OpenAI()

hf_embeddings = HuggingFaceInferenceAPIEmbeddings(
    api_key=os.getenv("HUGGING_FACE_API_KEY"), model_name="sentence-transformers/all-MiniLM-l6-v2"
)

prompt_openai = ChatPromptTemplate.from_template("""Answer the following question incorporating the following context:
<context>
{context}
</context>

Question: {input}""")


query_transform_prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="messages"),
        (
            "user",
            "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation. Only respond with the query, nothing else.",
        ),
    ]
)

def create_openai_embeddings(input_message):
    return client_openai.embeddings.create(input = [input_message], model="text-embedding-ada-002").data[0].embedding

def create_hf_embeddings(input_message):
    return hf_embeddings.embed_query(input_message)


def generate_query_transform_prompt(chat_model_toggle, messages):
    if chat_model_toggle == 1:
        chat_model = chat_openai
    else:
        chat_model = chat_claude
    
    query_transformation_chain = query_transform_prompt | chat_model
    
    print("generating transformed query...")
    return query_transformation_chain.invoke({"messages": messages}).content 
    

def generate_document_chain(chat_model_toggle):
    if chat_model_toggle == 1:
        chat_model = chat_openai
    else:
        chat_model = chat_claude
        
    return create_stuff_documents_chain(chat_model, prompt_openai)