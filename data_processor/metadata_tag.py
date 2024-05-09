from langchain_community.document_transformers.openai_functions import (
    create_metadata_tagger,
)
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
import json

schema = {
    "properties": {
        "type": {"type": "string", "enum": ["internal_policies", "insurance_product"]},
        "critic": {"type": "string"},
        "tone": {"type": "string", "enum": ["positive", "negative"]},
        "rating": {
            "type": "integer",
            "description": "The number of stars the critic rated the movie",
        },
    },
    "required": ["type"],
}


# Must be an OpenAI model that supports functions
llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-0613")


document_transformer = create_metadata_tagger(metadata_schema=schema, llm=llm)

def tag_metadata(data):
      
    if isinstance(data, str):
        data = data
    elif isinstance(data, dict):
        data = json.dumps(data)
    else:
        raise ValueError("Invalid data format")
    
    original_documents = [
        Document(
            page_content=data
        )
    ]

    enhanced_documents = document_transformer.transform_documents(original_documents)
    return enhanced_documents[0].metadata['type']