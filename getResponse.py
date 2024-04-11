from flask import Blueprint, request, jsonify
import os
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
import couchbase.search as search
from couchbase.options import SearchOptions
from couchbase.vector_search import VectorQuery, VectorSearch
from openai import OpenAI
from flask import Blueprint, request, jsonify
import os
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import CouchbaseException
from couchbase.options import SearchOptions
from couchbase.vector_search import VectorQuery, VectorSearch
from openai import OpenAI
import traceback
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder



# getResponse.py


def find_color_by_desc(question_input):
    
    chat = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.2)

    result = chat.invoke(
        [
            HumanMessage(
                content=question_input
            )
        ]
    )
    
    
    
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. Answer all questions to the best of your ability.",
            ),
            MessagesPlaceholder(variable_name="messages"),
    ])

    chain = prompt | chat
    
    print("result: ", result.content)
    
    return result.content
    # Run your function here to find the color based on x, y, and z
    # pa = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
    # cluster = Cluster("couchbases://" + os.getenv("CB_HOSTNAME") + "/?ssl=no_verify", ClusterOptions(pa))

    # bucket = cluster.bucket("vector-sample")
    # scope = bucket.scope("color")
    # search_index = "color-index"

    # client = OpenAI()

    # try:
    #     vector = client.embeddings.create(input = [question_input], model="text-embedding-ada-002").data[0].embedding
    #     search_req = search.SearchRequest.create(search.MatchNoneQuery()).with_vector_search(
    #         VectorSearch.from_vector_query(VectorQuery('embedding_vector_dot', vector, num_candidates=1)))
    #         # Change the limit value to return more results. Change the fields array to return different fields from your Search index.
    #     result = scope.search(search_index, search_req, SearchOptions(limit=13,fields=["color", "description"]))

    #     row_string = ''

    #     for row in result.rows():
    #         row_string = row_string + "\n\n" + row.fields['color'] + ": " + row.fields['description']

    #     return row_string

    # except CouchbaseException as ex:
    #     traceback.print_exc()
