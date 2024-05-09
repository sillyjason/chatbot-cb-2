**Develope Your Chatbot with Couchbase**


Couchbase is a memory-first, performant NoSQL data platform providing services including kv, sql query, full-text & vector search, real-time analytics and mobile capabilities. You can build enterprise grade, scalable applications and innovate faster. 

This app is a simple build-up from the [Couchbase Documentation](https://docs.couchbase.com/cloud/vector-search/vector-search.html) on using Couchbase as both a vector storage and serverless computing platform, borrowing from the great [LangChain](https://www.langchain.com/) library. This example is built with Capella, Couchbase's cloud data platform however the same examples works with Servers (version 7.6 or above) too.   

In this example we're building a MVP chatbot for internal product education for an insurance company with dummy data. Essentially you can build this for any company or any industry.



**Couchbase Setup**  

1. On [Couchbase Capella](https://cloud.couchbase.com/sign-in), set up a cluster **versioned 7.6** with Data, Index, Query, Search, Eventing and Analytics services enabled. Recommended topology: 
    Data * 3 with 4core 16ram; 
    Analytics * 2 with 4core 16ram;
    [Index, Query, Search, Eventing] * 2 with 4core 16ram

2. Create the following bucket structure (bucket - scope - [collections]): 
    insurance-products(1000MiB of RAM) - _default - _default
    meta(1000MiB of RAM)  - _default - _default
    Chats(rest of RAM)  - _default -  [_default & bot] 

3. Import the eventing_function.json file under templates/assets to create a Couchbase Eventing. Save the function without deploying it as we'll made modifications once the VM is set up.

4. Import the product-index.json under templates/assets to create the search index, which will include the vectors and other relevant fields


5. Whitelist IP address, create db user credentials, note down the connection string and your user credentials.




**LLM Setup**

To run this demo you'll need api keys from OpenAI, Anthropic, and Hugging Face. Once you have these 3 keys you're good to go here: 
OPENAI_API_KEY, ANTHROPIC_API_KEY, HUGGING_FACE_API_KEY




**VM Setup** 

1. Set up VM. I'm using AWS EC2 as an example. SSH into the machine, Run the startup script under templates/assets to clone this repo and set up dependencies 

2. Enter the directory of the project. Open templates/index.html, find the line "var socket = io.connect('http://localhost:5000')" and replace "localhost" with the Public IPv4 DNS of your VM. 

3. Create a .env file with these variables. Complete CB_USERNAME, CB_PASSWORD, CB_HOSTNAME with values from Couchbase setup steps.

```
CB_USERNAME=
CB_PASSWORD=
CB_HOSTNAME=
CB_BUCKET_NAME=insurance-products
CB_SCOPE_NAME=_default
CB_COLLECTION_NAME=_default
CB_VECTOR_INDEX_NAME=product-index
KEY_CONTEXT_FIELD=assembled_for_embedding
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
HUGGING_FACE_API_KEY=
```

4. Run python3 app.py



**Let's Run it!**

1. Copy the DNS record again, and go back to Couchbse cluster. In the step 2 "Binding" of the Eventing we just created, update the URL with the DNS record so it looks something like this: http://{DNS record}:5000. Save and deploy the function. 

2. Let's see automatic embedding with Eventing in action. Load products.json under templates/assets into collection `insurance-products`.`_default`.`_default`. Use "product-id" as document id. Upon import completion, you should see the vectors added automatically. 

3. Open your browser and enter "{your VM DNS record}:5000". You should see the chatbot interface. 

4. Throw some questions, switch between OpenAI and Claude LLMs, or switch between 2 sets of embeddings (both embeddings have been added)