- [1. Description](#1-description)
- [2. Required Programs](#2-required-programs)
- [3. How it works](#3-how-it-works)
- [4. Running Example Locally](#4-running-example-locally)
  - [4.1. Without Docker](#41-without-docker)
  - [4.2. With Docker](#42-with-docker)
- [5. Running Example on AWS](#5-running-example-on-aws)
- [6. Points of Improvement/Potential next steps](#6-points-of-improvementpotential-next-steps)
- [7. Related links](#7-related-links)

## 1. Description

The idea behind this project was to be a proof of concept for using a blockchain
as a means to create an immutable datastore. The blockchain in this case would act
similar to the transaction log in a traditional sql database except that it would 
act as a record only and not a means to rebuild the current state of the database.

The example is built using FASTApi and the blockchainDB library exposes several FASTApi endpoints that can be integration into any other future examples.

## 2. Required Programs

- Docker
- Python
- MongoDB Compass (Optional, but makes things easier)
- AWS CLI

For setup instructions see [related links](#7-related-links)

## 3. How it works

The blockchain database works by adding an entry to the blockchain and to a specific 
document collection every time a transaction is committed. Each block to be committed
requires a single primary key field as it is used to determine if a block with that
same key has been created previously as it tags all new blocks with no existing key
as a 'CREATE' entry and then any future block as an 'EDIT' block. It will throw an
exception if another 'CREATE' block with the same key is attempted to be committed.
After a candidate block has been created, it will confer with any linked nodes to 
determine if there is any other commits that have completed before the current commit
and will reject the block if the other nodes do not agree on the generated hash. If it
succeeds, the block will be added to the chain and the data to the respective collection and the function will return true. If not, the function will return false.
For each 'EDIT' operation, a flag will be set on each data collection entity with a matching key that will mark all preceding data as superceeded. 

This database recycles the query language used by MongoDB and allows the user of this 
library to query the database based upon that syntax. There is a current limitation in that it will only return data with the superceeded flag being false. If there is
data found for the search, each returned entity will be verified against the blockchain prior to return to the caller. If it fails to verify, the audit function
will return nothing.


## 4. Running Example Locally

The example project can be run locally either with or without docker as described in
the following sections.

### 4.1. Without Docker

1. Navigate to root of example directory
2. Setup a new python virtual environment
   ```
    python3 -m venv venv
   ```
   Activate the environment with the following command
   ```
    source venv/bin/activate
   ```   
3. Install dependancies from requirements file
   ```
    pip3 install -r app/requirements.txt
   ```
4. Start the fastapi development server 

   ```
   export DATABASE='blockmedi',CONNECTION_STRING='mongodb connection string',NODES=['node ip addresses'],USER_POOL_ID='Cognito user pool ID',USER_POOL_WEB_CLIENT_ID='Cognito user pool web client id'

   uvicorn app.main:app --reload
   ```
5. View swagger page to check that server has started at the following url
   ```
   http://127.0.0.1:8000/docs
   ```

### 4.2. With Docker

Using docker compose makes this process easier and the docker compose file provided
with the example as it contains an image for a mongodb instance. The docker-compose configuration is slightly different from that of the environment when hosted on AWS as it uses an HA proxy instance as the load balancer instead of the AWS ALB. 

1. Start the docker instances
   ```
   docker-compose up --build --remove-orphans
   ```
2. View swagger page to check that server has started at the following url
   ```
   https://127.0.0.1:5001/docs
   ```
   or 
   ```
   https://127.0.0.1:5002/docs
   ```
   Target requests to the load balancer at
   ```
   https://127.0.0.1:5000
   ```

## 5. Running Example on AWS

Running the example in AWS needs to have a fair number of supporting services to 
work correctly. The AWS CLI needs to be setup for this to work properly. See the link to the AWS CLI in the [related links](#7-related-links) section for more information.

1. Create base services using CloudFormation in the attached base.yml file. 
   This will create cognito, the ECS cluster, the load balancers, related certificates, and VPC.
   ```
    aws cloudformation deploy \
    --template-file base.yml \
    --stack-name some-stack-name \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides DNSName=testdomain
   ```
2. Commit the code in the example to a repository of your choosing. This is to be able to build and deploy a task definition to the ECS cluster. It is easiest to use Github for this as its free and is easily integrated with codepipeline.
3. Create the pipeline with CloudFormation
   ```
    aws cloudformation deploy \
    --template-file appconfig.yml \
    --capabilities CAPABILITY_IAM 
   ```
   The above command will need to have the parameter overrides added as per what is 
   in the appconfig.yml file. The secrets for github and the mongodb store will
   need to created manually in AWS.
4. Add an A record in Route 53 to link your domain in AWS to the ALB. The hosted zone will need to be created before you can add a record. This would either need to be a new domain created or one transferred from another registrar.

## 6. Points of Improvement/Potential next steps

- Change to be agnostic of backing database. This could be a plugin based system or have a backing database built in.
- The base library needs unit and integration tests added. Could be useful to have it set up in the pipeline or done as part of github/bitbucket/azure devops pipeline.
- The means of voting is dependant on services from AWS, this would be better if it were independant of services provided by AWS.
- There is a threading problem with using FASTApi and python for this type of project. Would be better to either resolve or move away from python. Would also be better to not be quite so dependant on FASTApi, could be good to use protobuf as a potential alternative.


## 7. Related links

- https://aws.amazon.com/cli/
- https://www.docker.com/get-started
- https://fastapi.tiangolo.com/
- https://www.mongodb.com/cloud/atlas
- https://www.python.org/downloads/
- https://pydantic-docs.helpmanual.io/