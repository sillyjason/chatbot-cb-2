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
EOF