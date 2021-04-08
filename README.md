
## Table of Contents

- [Table of Contents](#table-of-contents)
- [1. Description](#1-description)
- [2. How it works](#2-how-it-works)
- [3. Required Programs](#3-required-programs)
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

## 2. How it works

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

## 3. Required Programs

- Docker
- Python
- MongoDB Compass (Optional, but makes things easier)
- AWS CLI

For setup instructions see [related links](#7-related-links)

## 4. Running Example Locally

The example project can be run locally either with or without docker as described in
the following sections.

### 4.1. Without Docker

1. Setup a new python virtual environment
   ```
  
   ```
2. 

### 4.2. With Docker

1. 

## 5. Running Example on AWS

Running the example in AWS needs to have a fair number of supporting services to 
work correctly. Ensure that the 

1. 

## 6. Points of Improvement/Potential next steps


## 7. Related links

