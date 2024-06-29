RAG Chatbot with Couchbase

Building a enterprise-grade RAG application goes beyond merely vector search. Enterprises today generally suffer from the following issues when trying to push their app to production or scale: 

1. AI data pipeline
The bulk of work today actually resides in tranforming their unstructured data today into a RAG-ready state. This would at least include OCR, data re-formmating, sensitive data removal/masking, metadata labelling, chunking, embedding, etc. This doesn't mean we should gloss over the continuous optimization efforts on prompting, RAG data and workflow tuning, embedding & foundation model selection, etc, which are equally important.     

2. Tech stack complexities
A production RAG system would minimially necessitates functionalities of vector, ACID transationc, JSON store, SQL query, OLAP, streaming. If you use one tool per component, you're already dealing with some complexities, which is always the archenemy of agile innovation. This is more true than ever in today's world.

This demo attempts an answer to problems above from Couchbase’s point of view. We’ll be building a chatbot application that allows you to upload any raw JSON data and start chatting. 

There are already a plethora of demos out there that allows you to upload a PDF and start chatting with it. What's so special about this one? 
1. In real life scenarios your data might need to go through more steps such as masking, reformatting and other transformations. We'll see how those steps are automated.
2. We'll also go beyond just chatting with your data. We'll see how agile product iteration and data analytics are done on the same tool where your embeddings are stored.


What Do I need to run this demo? 
1. a OPENAI api key 
2. 1 linux virtual machine for hosting the app, and another for installing Couchbase. I'll use AWS EC2 but anything with minimal config will do

We're using LangChain and installing Couchbase Server Enterprise Edition 7.6. Knowledge of these 2 tools are a plus but not a prerequisite. 




SETUP

1.1 LLM
GPT-4o is used in this demo. You need to have an OPENAI_API_KEY from OpenAI. 

1.2 AWS VM
*Use either method below for installation

1.2.1 Using Terraform 
If you’re a Terraform user, download the /terraform folders from the root directory of this Github repo. Finish the set up of server.tf and run the script.


1.2.2 Using AWS Console 
Create a virtual machine with the following startup script (I'm using AWS EC2): 
#!/bin/bash
sudo yum update -y
sudo yum install git -y
sudo yum install python3 -y
sudo yum install python3-pip -y
git clone https://github.com/sillyjason/chatbot-cb-2
cd chatbot-cb-2
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Make sure to update Security Group setting to allow ALL inbound/outbound traffics


1.2.3 Get Instance Hostname
Let's call this VM our APP node. Note down its Public IPv4 DNS. 



1.3 Couchbase Setup
Create another VM, install Couchbase with these services enabled: Data, Query, Index, Search, Eventing. Make sure the Server version is EE 7.6.

If you're new to Couchbase, follow this link for more details. (https://docs.couchbase.com/server/current/install/install-linux.html)

Let's call this one our Couchbase node. Grab it's IPv4 address too.


1.4 Get, Set, Run!
1.4.1 App node setup
SSH into your App node and run the following codes to enter the project location and activate python virtual environment: 
sudo -i
cd /
cd chatbot-cb-2
source venv/bin/activate




1.4.2 .ENV Setup
At SSH session, run “nano .env” and fill in these environmental variables:


-------------------- .env setup begin --------------------
\#EE Environment Variables 
EE_HOSTNAME={IPv4 of Couchbase Node}
EVENTING_HOSTNAME={IPv4 of Couchbase Node}
SEARCH_HOSTNAME={IPv4 of Couchbase Node}

#Chatbot Endpoint
CHATBOT_APP_END_POINT={IPv4 of App Node}

#CB User Credential 
CB_USERNAME={username for Couchbase}
CB_PASSWORD= {password for Couchbase}

#LLM Keys 
OPENAI_API_KEY={your OPENAI api key}
-------------------- .env setup end --------------------


1.4.3 Additional Setup 
Run “python3 setupbucket.py” to set up bucket/scope/collections

Run “python3 setupothers.py” to create Eventing functions and FTS indexes.
- Eventing is Couchbase's version of Database Trigger and Lambda functions. It's a versatile and powerful tool to stitch together your data processes and achieve high automation.
- FTS is Couchbase's full text and semantic search service. 

All good. Run “python3 app.py” to start.






DEMO 

2.1 Demo AI Data Pipeline
We’ll use a series of Eventing functions to simplify the AI data pipeline, which needless to say, is a big challenge for any company looking to build a GenAI application, considering the enormity and complexity of their unstructured data source. Here is what happens with Couchbase


Import Data
Download the “raw-data.json” file under directory templates/assets/. At “Import” tab under Data Tools, import the file into main.raw.raw collection.  


It’s worth pointing out the steps this raw data must go through before it’s RAG ready: 
- Data format inconsistency. For example, “last_upddate” field
- Empty spaces. For example, “content” field
- Data of different nature (2 product JSON and 1 email regarding internal policy JSON)
- Sensitive data. For example, ID or email in “content” field (in real time scenarios this should be done with a local model. In our case for the light-weight-ness of the app we're running with REST call instead.)

After import, go to main.raw.raw collection to check data successfully imported;
- Then, go to main.raw.formatted collection to see data after first processing
- You’ll notice the format inconsistency, empty space, and sensitive data issues are taken care of (*note that in this demo, the sensitive data masking is done by prompting - OPENAI with a API call. In production this defeats the purpose of data protection and instead, the model should be deployed locally hence local inferencing, a totally viable approach, just not demoed in this version…yet) 
- Also note, every doc is added a “type” field which is an enumeration of [“internal_policies”, “insurance_product”]
- Go to scope “data”. The 3 raw JSON objects are now pigeonholed into corresponding collections, automatically. Also note embedding is added. 

Now let’s do some chatbot’ing  


2.2 Chatbot
Open your browser, access the chatbot via {IPv4 of App Node}:5000

Take a look at the raw data, and feel free to ask any questions. 
Also note there are elements of user engagements. Feel free to give ratings to the comments. 
At this moment we’ve demoed how Couchbase acts as both vector store and AI data pipeline orchestration platform. But we can demo more. 

2.3 Agile Development, Simplified Query, etc.
*This is when we showcase Couchbase’s power as a general-purpose data store. Feel free to complete your talk track with any convincing SQL scenarios, and here is my version:
 
2.3.1 NoSQL Flexibility
What if in quick iteration, customer needs to update their schema? In our example, collection main.chats.human has the field “user_id”, but not main.chats.bot. If it’s decided that the field be added to the ‘bot’ collection too, just to go Query tab and run the following: 
UPDATE bot AS b
SET b.user_id = (SELECT RAW d.user_id FROM human AS d WHERE meta().id = b.user_msg_id)[0]
WHERE b.user_msg_id IS NOT NULL;
*The query might fail with “index not created” message. In this case, follow Index Advisor to create index and re-run the query
Easy. This is good time to explain the superiority of NoSQL when fast iteration is required. 

2.3.2 SQL JOIN
If customer choose to have a separate vector database, they’ll end up storing vectors, transactions, and SQL docs in separate datastore. Imagine running query that needs joining these disconnected tables. 
With Couchbase, easy. Go to Query service and run the following query:
SELECT p, COUNT(*) AS frequency, pr.product_name
FROM `bot` AS b
UNNEST b.product_ids AS p
JOIN `main`.`data`.`products` AS pr ON KEYS p
GROUP BY p, pr.product_name
ORDER BY frequency DESC;

At this moment, hopefully we’ve delivered a strong point that Couchbase serves much more than a vector DB. 

TAILOR THE DEMO 
This demo was built to facilitate customization. You can build this chatbot for any industry/customer with your own set of data. Only a couple of extra steps are needed. 
Reach out to @jason.cao on Slack and I’ll be happy to walk you through! 
