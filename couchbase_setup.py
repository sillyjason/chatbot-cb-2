from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.vector_search import VectorQuery, VectorSearch
import couchbase.search as search
from couchbase.options import SearchOptions
from dotenv import load_dotenv
import os 


load_dotenv()

pa = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
cluster = Cluster(os.getenv("CB_HOSTNAME") + "/?ssl=no_verify", ClusterOptions(pa))
bucket = cluster.bucket(os.getenv("CB_BUCKET_NAME"))
scope = bucket.scope(os.getenv("CB_SCOPE_NAME"))
collection = scope.collection(os.getenv("CB_COLLECTION_NAME"))
search_index = os.getenv("CB_VECTOR_INDEX_NAME")



def cb_vector_search(embedding_field, vector, key_context_field): 
    
    search_req = search.SearchRequest.create(search.MatchNoneQuery()).with_vector_search(
    VectorSearch.from_vector_query(VectorQuery(embedding_field, vector, num_candidates=3)))
    return scope.search(search_index, search_req, SearchOptions(limit=13,fields=[key_context_field, "source"]))


