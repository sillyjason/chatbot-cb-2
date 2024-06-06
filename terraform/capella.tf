/*
This Terraform templates sets up the necessary instances needed to run this Couchbase Chatbot application.
You'll need at least one VM to run the chatbot application and a Couchbase cluster as the backend. 

Before running this file, you'll need to create a terraform.template.tfvars and a variables.tf file. Follow the blog post below:
https://www.couchbase.com/blog/terraform-provider-couchbase-capella/

You'll also need to get your Capella Organization ID, Project ID, and Authentication Token, the details of which is also documented in the blog post.
*/



/*aws vm instance for running the chatbot
replace the 

*/
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

#capella setup 
terraform {
  required_providers {
    couchbase-capella = {
      source  = "registry.terraform.io/couchbasecloud/couchbase-capella"
    }
  }
}
 

provider "couchbase-capella" {
  authentication_token = var.auth_token
}


# Create  cluster resource
resource "couchbase-capella_cluster" "capella-cluster" {
  organization_id = var.organization_id
  project_id      = var.project_id
  name            = "Chatbot with Capella"
  description     = "GenAI Enabled Chatbot with Capella"
  cloud_provider = {
    type   = "aws"
    region = "ap-southeast-1"
    cidr   = "192.168.10.0/23"
  }
  couchbase_server = {
    version = "7.6"
  }
  service_groups = [
    {
      node = {
        compute = {
          cpu = 16
          ram = 32
        }
        disk = {
          storage = 50
          type    = "gp3"
          iops    = 3000
        }
      }
      num_of_nodes = 3
      services     = ["data"]
    },
    {
      node = {
        compute = {
          cpu = 16
          ram = 32
        }
        disk = {
          storage = 50
          type    = "gp3"
          iops    = 3000
        }
      }
      num_of_nodes = 2
      services     = ["index", "query", "search"]
    },
    {
      node = {
        compute = {
          cpu = 16
          ram = 32
        }
        disk = {
          storage = 50
          type    = "gp3"
          iops    = 3000
        }
      }
      num_of_nodes = 2
      services     = ["eventing"]
    }
  ]
  availability = {
    "type" : "multi"
  }
  support = {
    plan     = "developer pro"
    timezone = "PT"
  }
}

# Create bucket main
resource "couchbase-capella_bucket" "main_bucket" {
  name                       = "main"
  organization_id            = var.organization_id
  project_id                 = var.project_id
  cluster_id                 = couchbase-capella_cluster.capella-cluster.id
  type                       = "couchbase"
  storage_backend            = "couchstore"
  memory_allocation_in_mb    = 10000
  bucket_conflict_resolution = "seqno"
  durability_level           = "none"
  replicas                   = 1
  flush                      = true
  time_to_live_in_seconds    = 0
  eviction_policy            = "fullEviction"
}

# Create bucket meta
resource "couchbase-capella_bucket" "meta_bucket" {
  name                       = "meta"
  organization_id            = var.organization_id
  project_id                 = var.project_id
  cluster_id                 = couchbase-capella_cluster.capella-cluster.id
  type                       = "couchbase"
  storage_backend            = "couchstore"
  memory_allocation_in_mb    = 1000
  bucket_conflict_resolution = "seqno"
  durability_level           = "none"
  replicas                   = 1
  flush                      = true
  time_to_live_in_seconds    = 0
  eviction_policy            = "fullEviction"
}


# Create scope raw and collections raw and formatted
resource "couchbase-capella_scope" "scope_raw" {
    scope_name           = "raw" 
    organization_id      = var.organization_id
    project_id           = var.project_id
    cluster_id           = couchbase-capella_cluster.capella-cluster.id
    bucket_id            = couchbase-capella_bucket.main_bucket.id
}

resource "couchbase-capella_collection" "collection_raw" {
    collection_name      = "raw"
    organization_id      = var.organization_id
    project_id           = var.project_id
    cluster_id           = couchbase-capella_cluster.capella-cluster.id
    bucket_id            = couchbase-capella_bucket.main_bucket.id
    scope_name           = couchbase-capella_scope.scope_raw.scope_name
}

resource "couchbase-capella_collection" "collection_formatted" {
    collection_name      = "formatted"
    organization_id      = var.organization_id
    project_id           = var.project_id
    cluster_id           = couchbase-capella_cluster.capella-cluster.id
    bucket_id            = couchbase-capella_bucket.main_bucket.id
    scope_name           = couchbase-capella_scope.scope_raw.scope_name
}


# Create scope data and collections policies & products
resource "couchbase-capella_scope" "scope_data" {
    scope_name           = "data" 
    organization_id      = var.organization_id
    project_id           = var.project_id
    cluster_id           = couchbase-capella_cluster.capella-cluster.id
    bucket_id            = couchbase-capella_bucket.main_bucket.id
}


resource "couchbase-capella_collection" "collection_policies" {
    collection_name      = "policies"
    organization_id      = var.organization_id
    project_id           = var.project_id
    cluster_id           = couchbase-capella_cluster.capella-cluster.id
    bucket_id            = couchbase-capella_bucket.main_bucket.id
    scope_name           = couchbase-capella_scope.scope_data.scope_name
}

resource "couchbase-capella_collection" "collection_products" {
    collection_name      = "products"
    organization_id      = var.organization_id
    project_id           = var.project_id
    cluster_id           = couchbase-capella_cluster.capella-cluster.id
    bucket_id            = couchbase-capella_bucket.main_bucket.id
    scope_name           = couchbase-capella_scope.scope_data.scope_name
}


# Create scope chats and collections human and bot
resource "couchbase-capella_scope" "scope_chats" {
    scope_name           = "chats" 
    organization_id      = var.organization_id
    project_id           = var.project_id
    cluster_id           = couchbase-capella_cluster.capella-cluster.id
    bucket_id            = couchbase-capella_bucket.main_bucket.id
}

resource "couchbase-capella_collection" "collection_human" {
    collection_name      = "human"
    organization_id      = var.organization_id
    project_id           = var.project_id
    cluster_id           = couchbase-capella_cluster.capella-cluster.id
    bucket_id            = couchbase-capella_bucket.main_bucket.id
    scope_name           = couchbase-capella_scope.scope_chats.scope_name
}

resource "couchbase-capella_collection" "collection_bot" {
    collection_name      = "bot"
    organization_id      = var.organization_id
    project_id           = var.project_id
    cluster_id           = couchbase-capella_cluster.capella-cluster.id
    bucket_id            = couchbase-capella_bucket.main_bucket.id
    scope_name           = couchbase-capella_scope.scope_chats.scope_name
}