/*
This Terraform templates sets up the necessary instances needed to run this Couchbase Chatbot application.
You'll need at least one VM to run the chatbot application. 
*/


#aws vm instance for running the chatbot
provider "aws" {
    region = "ap-southeast-1"
    access_key = var.access_key
    secret_key = var.secret_key
}

resource "aws_instance" "web" {
  ami           = "ami-0b287aaaab87c114d"
  instance_type = "t3.2xlarge"
  vpc_security_group_ids = ["sg-0bf97419aaad88160"] // if no security group needs be specified, delete this line

  user_data = <<-EOF
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
                cat > .env <<- EOF
                #EE Environment Variables
                

                #Capella Environment Variables
                

                #Chatbot Endpoint
                
                #CB User Credential

                #LLM Keys
                EOF

  tags = {
    Name = "rag-with-couchbase"
  }
}
