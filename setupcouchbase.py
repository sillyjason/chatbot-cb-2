from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.vector_search import VectorQuery, VectorSearch
import couchbase.search as search
from couchbase.options import SearchOptions
from dotenv import load_dotenv
import os 
import uuid
import datetime
import couchbase.subdocument as SD
from datetime import timedelta

load_dotenv()


endpoint = os.getenv("CB_HOSTNAME")
auth = PasswordAuthenticator(os.getenv("CB_USERNAME"), os.getenv("CB_PASSWORD"))
options = ClusterOptions(auth)
# Sets a pre-configured profile called "wan_development" to help avoid latency issues
# when accessing Capella from a different Wide Area Network
# or Availability Zone(e.g. your laptop).
options.apply_profile('wan_development')
cluster = Cluster('couchbases://{}'.format(endpoint), options)

# Wait until the cluster is ready for use.
cluster.wait_until_ready(timedelta(seconds=5))


def cb_vector_search(embedding_field, vector, key_context_field): 
    bucket = cluster.bucket("main")
    scope = bucket.scope("data")
    search_index = "embedding-index"
    search_req = search.SearchRequest.create(search.MatchNoneQuery()).with_vector_search(
    VectorSearch.from_vector_query(VectorQuery(embedding_field, vector, num_candidates=3)))
    return scope.search(search_index, search_req, SearchOptions(limit=13,fields=[key_context_field, "source", "from"]))


def insert_user_message(query, transformed_query, deviceType, browserType): 
    
    chat_collection = cluster.bucket("main").scope("chats").collection("human")   
    
    try:
        uuid_to_insert = str(generate_uuid())
        
        document = dict(
            query=query,
            transformed_query=transformed_query,
            device_type=deviceType,
            browser_type=browserType,
            # mock up further user data
            user_id="H123",
            timestamp=datetime.datetime.now().isoformat(),
        )
        chat_collection.upsert(
            uuid_to_insert,
            document
        )
        
        print("UPSERT SUCCESS", uuid_to_insert)
        
        return uuid_to_insert
        
    except Exception as e:
        print("exception:", e)
        
        return None 


def insert_bot_message(message, user_msg_id, chat_model, product_ids): 
    chat_collection = cluster.bucket("main").scope("chats").collection("bot")   
    
    try:
        uuid_to_insert = str(generate_uuid())
        
        document = dict(
            message=message,
            user_msg_id=user_msg_id,
            timestamp=datetime.datetime.now().isoformat(),
            chat_model=chat_model,
            product_ids=product_ids
        )
        chat_collection.upsert(
            uuid_to_insert,
            document
        )
        
        print("UPSERT SUCCESS", uuid_to_insert)
        
        return uuid_to_insert
        
    except Exception as e:
        print("exception:", e)
        return None 
    

def update_bot_message_rating(bot_msg_id, rating):
    print("UPDATING RATING", bot_msg_id, rating)
    chat_collection = cluster.bucket("main").scope("chats").collection("bot")   
    
    try:        
        chat_collection.mutate_in(bot_msg_id, [SD.upsert("rating", rating)])
        
        print("UPDATED RATING SUCCESS")
                
    except Exception as e:
        print("exception:", e)
        return None 
    
    

def generate_uuid(): 
    return uuid.uuid4()