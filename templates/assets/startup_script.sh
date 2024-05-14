#!/bin/bash
sudo yum update -y
sudo yum install git -y
sudo yum install python3 -y
sudo yum install python3-pip -y
git clone https://github.com/sillyjason/chatbot-with-couchbase
cd chatbot-with-couchbase
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cat > .env <<- EOF
#EE Environment Variables
EE_HOSTNAME=ec2-18-136-194-193.ap-southeast-1.compute.amazonaws.com
EVENTING_HOSTNAME=ec2-54-169-185-151.ap-southeast-1.compute.amazonaws.com	
SEARCH_HOSTNAME=ec2-13-250-108-27.ap-southeast-1.compute.amazonaws.com

#Capella Environment Variables
CB_HOSTNAME=cb.tp6sl4zqsvdh02la.cloud.couchbase.com
CAPELLA_API_KEY_TOKEN=QWdpV2tldmxQa05Rc0NMVTY0dWtzRUYzaXpKZ09VdDM6U0VuNGVUQTVZbjlMRGghVTBjSTVwU29FQlpOU2xTeGs0MmdySFc3bnhVd2hJZWxCa3RkMTBOSkNoMHJoZyNnbA==
ORG_ID=42730eb3-53ab-451a-b5eb-8eeb9a92084c
PROJECT_ID=4af36ee8-eb11-45ee-bcde-845bc07f1ba3
CLUSTER_ID=2697449c-4727-46a4-8e74-9cfc80e0972c

#Chatbot Endpoint
CHATBOT_APP_END_POINT=ec2-18-136-194-193.ap-southeast-1.compute.amazonaws.com

#
CB_USERNAME=admin
CB_PASSWORD=C0uchbase123!

#LLM Keys
OPENAI_API_KEY=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
ANTHROPIC_API_KEY=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
HUGGING_FACE_API_KEY=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
EOF