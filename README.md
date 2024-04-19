**Develope Your Chatbot with Couchbase**


Couchbase is a memory-first, performant NoSQL data platform providing services including kv, sql query, full-text & vector search, real-time analytics and mobile capabilities. You can build enterprise grade, scalable applications and innovate faster. 

This app is a simple build-up from the [Couchbase Documentation](https://docs.couchbase.com/cloud/vector-search/vector-search.html) on using Couchbase as both a vector storage and serverless computing platform, borrowing from the great [LangChain](https://www.langchain.com/) library. This example is built with Capella, Couchbase's cloud data platform however the same examples works with Servers (version 7.6 or above) too.   

In this example we're building a MVP chatbot for internal product education for an insurance company with dummy data. Essentially you can build this for any company or any industry.


**Set up**:  

1. On [Couchbase Capella](https://cloud.couchbase.com/sign-in), set up a cluster **versioned 7.6** with at least Data and Search services enabled.

2. Create bucket with embedding in this cluter. As a starter, follow the instruction on this [Couchbase documentation](https://docs.couchbase.com/cloud/vector-search/create-vector-search-index-ui.html) to create the "vector-sample" bucket, "color" scope, "rgb" and "rgb_questions" collections. Download the color_data_2vectors.zip file and upload them into the created collections.

3. Create the Vector Search Index. 

4. Whitelist IP address, create db user credentials, get connection string - the usuall goodies.

5. You'll also need an OPENAI account and a valid **OPENAI API Key**.

8. Clone the repo to a local directory. Create a .env file with these variables: 

```
CB_USERNAME=db user you just created
CB_PASSWORD=db user password you just created
CB_HOSTNAME=from the connect tab of the cluster
OPENAI_API_KEY=your openai api key, 
CB_BUCKET_NAME=bucket name, 
CB_SCOPE_NAME=scope name, 
CB_COLLECTION_NAME=collection name, 
CB_VECTOR_INDEX_NAME=the fts index name, 
KEY_CONTEXT_FIELD=the string field you want to feed into LLM, 
EMBEDDING_FIELD=name of the embedding field
```

9. if you running this on your local machine, skip this step; if you're running this on a VM such as EC2, open templates/index.html, find the line "var socket = io.connect('http://localhost:5000')" and replace "localhost" with the Public IPv4 DNS of your VM. 




