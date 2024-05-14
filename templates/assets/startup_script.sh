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
EE_HOSTNAME=
EVENTING_HOSTNAME=
SEARCH_HOSTNAME=

#Capella Environment Variables
CB_HOSTNAME=
CAPELLA_API_KEY_TOKEN=
ORG_ID=
PROJECT_ID=
CLUSTER_ID=

#Chatbot Endpoint
CHATBOT_APP_END_POINT=

#
CB_USERNAME=
CB_PASSWORD=

#LLM Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
HUGGING_FACE_API_KEY=
EOF