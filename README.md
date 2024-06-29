# RAG Chatbot with Couchbase

Building a enterprise-grade RAG application goes beyond merely vector search. Enterprises today generally suffer from these issues when trying to push their app to production or scale: 

<br>

**1. AI data pipeline 🚙🚕🚗**

The bulk of work today actually resides in tranforming their unstructured data today into a RAG-ready state. This would at least include OCR, data re-formmating, sensitive data removal/masking, metadata labelling, chunking, embedding, etc. Effectively orchestrating and automating the process is a huge challenge.

This doesn't mean we should gloss over the continuous optimization efforts on prompting, RAG data and workflow tuning, embedding & foundation model selection, etc, which are equally important.   


**2. Tech stack complexities 🔧🔨🛠️**

A production RAG system would minimially necessitates functionalities of vector, ACID transationc, JSON store, SQL query, OLAP, streaming. If you use one tool per component, you're already dealing with some complexities, which is always the archenemy of agile innovation. This is more true than ever in today's world.

<br>

This demo attempts an answer to problems above from Couchbase’s point of view. We’ll be building a chatbot application that allows you to upload any raw JSON data and start chatting. 

<br>





## What's Special about This Demo?


There are already a plethora of demos out there that allows you to upload a PDF and start chatting with it. What's so special about this one? 
1. In real life scenarios your data might need to go through more steps such as masking, reformatting and other transformations. We'll see how those steps are automated.
2. We'll also go beyond just chatting with your data. We'll see how agile product iteration and data analytics are done on the same tool where your embeddings are stored.

<br><br>

## What Do I need to run this demo? 
1. an OPENAI api key 
   
2. 1 linux virtual machine for hosting the app, and another for installing Couchbase. I'll use AWS EC2 but anything with minimal config will do

<br>

> 🙌🏻 We're using [LangChain](https://www.langchain.com/) and installing [Couchbase Server Enterprise Edition 7.6](
https://www.couchbase.com). Knowledge of these 2 tools are a plus but not a prerequisite. 

<br><br>


## Setup

**1.1 LLM**
<br>

GPT-4o is used in this demo. You need to have an OPENAI_API_KEY from OpenAI. 

<br>

**1.2 AWS VM**
<br>

>🙌🏻 Use either method below for installation

<br>

**1.2.1 Using Terraform** 
<br>

If you’re a Terraform user, download the /terraform folders from the root directory of this Github repo. Finish the set up of server.tf and run the script.

<br>

**1.2.2 Using AWS Console** 
<br>

Create a virtual machine with the following startup script (I'm using AWS EC2): 
```
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
```
<br>

Make sure to update Security Group setting to allow ALL inbound/outbound traffics

<br>

**1.2.3 Get Instance Hostname**
<br>

Let's call this VM our **APP Node**. Note down its Public IPv4 DNS. 

<br>

**1.3 Couchbase Setup**
<br>

Create another VM, install Couchbase with these services enabled: **Data, Query, Index, Search, Eventing**. Make sure the Server version is EE 7.6. If you're new to Couchbase, follow this [link](https://docs.couchbase.com/server/current/install/install-linux.html) for more details. 

Let's call this one our **Couchbase Node**. Grab it's IPv4 address too.

>🙌🏻 In a production set up you'll need at least 3 nodes to run Couchbase for HA purposes. In our case, let's just use 1 node for simplicity.


<br>

**1.4 Get, Set, Run!**

<br>

**1.4.1 App node setup**
<br>

SSH into your App node and run the following codes to enter the project location and activate python virtual environment: 
```
sudo -i
cd /
cd chatbot-cb-2
source venv/bin/activate
```

<br>

**1.4.2 .ENV Setup**
<br>

At SSH session, run “nano .env” and fill in these environmental variables:

```
#EE Environment Variables 
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
```

<br><br>

**1.4.3 Additional Setup**

<br>
Set up bucket/scope/collections

<br>

```
python3 setupbucket.py
```

<br>

Create Eventing functions and FTS indexes.
<br>

```
python3 setupothers.py
```

<br>

>🙌🏻 - Eventing is Couchbase's version of Database Trigger and Lambda functions. It's a versatile and powerful tool to stitch together your data processes and achieve high automation.

>🙌🏻 - FTS is Couchbase's full text and semantic search service. 

<br>

All good. Let's go 
<br>

```
python3 app.py
```



<br><br>

## Demo Process 

<br>

**2.1 AI Data Pipeline**
<br>

We’ll use a series of Eventing functions to simplify the AI data pipeline, which needless to say, is a big challenge for any company looking to build a GenAI application, considering the enormity and complexity of their unstructured data source. Here is what happens with Couchbase


<br>

**Import Data**
<br>

Download the “raw-data.json” file under directory templates/assets/. At “Import” tab under Data Tools, import the file into main.raw.raw collection.  

<img width="1427" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/ba300a13-3c98-4861-b410-3e5c52ad6a16">

<br><br>


>🙌🏻 It’s worth pointing out the steps this raw data must go through before it’s RAG ready:
>- Data format inconsistency. For example, “last_upddate” field
>- Empty spaces. For example, “content” field
>- Data of different nature (2 product JSON and 1 email regarding internal policy JSON)
>- Sensitive data. For example, ID or email in “content” field (in real time scenarios this should be done with a local model. In our case for the light-weight-ness of the app we're running with REST call instead.)

<br>

After import, go to main.raw.raw collection to check data successfully imported;

<br>

<img width="1111" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/3174a8f5-ba92-4232-8dcc-435b117b8165">

<br>

Then, go to main.raw.formatted collection. Data reformatting, masking, and labelling are already applied automatically.

<br>

<img width="1144" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/50808ee0-b6a5-4c97-a4f7-0bbf02e094ab">

<br>

Click to open the document that looks like *"content": "Dear Tony....* You’ll notice the format inconsistency, empty space, and sensitive data issues are taken care of

<br>

<img width="670" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/090e2f82-3b9f-47bf-aefb-ac9a269f31cb">

<br>
<br>

>🙌🏻 note that in this demo, the sensitive data masking is done by prompting OPENAI with a API call. In production this defeats the purpose of data protection and instead, the model should be deployed locally hence local inferencing, a totally viable approach) 

<br>

Also note, every doc is added a “type” field which is an enumeration of [“internal_policies”, “insurance_product”]

<br>

<img width="643" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/83543e6a-953f-4756-b1b1-c52e77b35573">

<br>

Go to scope “data”. The 3 raw JSON objects are now pigeonholed into corresponding collections, automatically. Also note embedding is added. 

<br>

<img width="644" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/113e5053-0704-4a21-92b9-eafa53c2212a">


<br>

## Now let’s do some chatbot’ing  
<br>


**2.2 Chatbot**

<br>

Open your browser, access the chatbot via port 5000:  *{IPv4 of App Node}:5000*

<br>

<img width="1403" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/9977a53b-2d8b-445b-b1dd-b4d8f02ecdec">

<br><br>

Take a look at the raw data, and feel free to ask any questions. 

<br><br>

<img width="1389" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/4498e847-52e4-43a3-93f9-8367c67b56ab">

<br><br>

Also note there are elements of user engagements. Feel free to give ratings to the comments. 

<br><br>

<img width="721" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/6b2c0673-734f-4f84-8e43-c8acc2b670a3">

<br><br>


At this moment we’ve demoed how Couchbase acts as both vector store and AI data pipeline orchestration platform. But we can demo more. 

<br><br>

**2.3 Agile Development, Simplified Query, etc.**
<br>

>🙌🏻 At this stage we've seen Couchbase making possible a RAG solution plus automated data processing. Let's see more.
 
<br>

**2.3.1 NoSQL Flexibility**
<br>

What if in quick iteration, customer needs to update their schema? In our example, collection main.chats.human has the field “user_id”, but not main.chats.bot. If it’s decided that the field be added to the ‘bot’ collection too, just to go Query tab and run the following: 

<br>

<img width="648" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/19203a25-7971-497c-ab43-4c78deac6431">


```
UPDATE main.chats.bot AS b
SET b.user_id = (SELECT RAW d.user_id FROM main.chats.human AS d WHERE meta().id = b.user_msg_id)[0]
WHERE b.user_msg_id IS NOT NULL;
```

<br>

Go back to collection main.chats.bots. Note the user_id field is already created. In a RDMNS database, this would be much harder.

<br>

<img width="635" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/3b5f0ccd-b33e-4f3c-b5fd-b4b39f68846e">

<br>


>🙌🏻 The query might fail with “index not created” message. In this case, follow Index Advisor to create index and re-run the query
Easy. This is good time to explain the superiority of NoSQL when fast iteration is required.

<br>


<br><br>

**2.3.2 SQL JOIN**
<br>

If customer choose to have a separate vector database, they’ll end up storing vectors, transactions, and SQL docs in separate datastore. Imagine running query that needs joining these disconnected tables. 
With Couchbase, easy. Go to Query service and run the following query:
```
SELECT p, COUNT(*) AS frequency, pr.product_name
FROM `main`.`chats`.`bot` AS b
UNNEST b.product_ids AS p
JOIN `main`.`data`.`products` AS pr ON KEYS p
GROUP BY p, pr.product_name
ORDER BY frequency DESC;
```

<br>

<img width="981" alt="image" src="https://github.com/sillyjason/chatbot-cb-2/assets/54433200/b2230d51-7897-41e7-bb06-f2677c54cc0b">

