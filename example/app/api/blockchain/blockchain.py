"""Implementation of the actual blockchain"""

import asyncio
import json
import os
from datetime import datetime, timezone
import time
import logging
import requests
import boto3
from injector import inject
from .mongo import MongoDb
from .models import Block, ProposedBlock, generate_block, generate_from_proposed_block


class Blockchain:
    """Primary class to control the blockchain"""
    @inject
    def __init__(self):
        self.database = MongoDb()
        self.nodes = []

        if 'ENVIRONMENT' not in os.environ or os.environ['ENVIRONMENT'] == 'local' \
            or os.environ['ENVIRONMENT'] == 'development':
            if 'NODES' in os.environ and len(os.environ['NODES']) > 0:
                self.nodes = json.loads(os.environ['NODES'])
        else:
            self.nodes = get_aws_nodes()

        logging.info(f'Using nodes: {self.nodes}')

        count = self.database.get_block_count()
        if count == 0:
            self.__create_genesis_block()

    def __create_genesis_block(self):
        """Creates the genesys block for the chain. This should only be called once"""
        self.__commit(Block([], 'GENISYS', '', '', '', '', '', ''))

    def commit_transaction(self, transaction, block_type, data_collection_name,
                            data_key_field_name, data_key_value):
        """Handles the commit for any transaction either create or edit"""
        retry_count = 3
        count = 0

        while count < retry_count:
            new_block = generate_block(transaction, block_type,
                                       datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %z"),
                                       self.last_block, data_collection_name, data_key_field_name,
                                       data_key_value)

            logging.info(f'New block created with hash: {new_block.hash}')
            is_valid = self.validate_block(new_block)

            if is_valid:
                self.__commit(new_block)
                return True

            logging.info('Not enough successful results for block. Block rejected.')
            count += 1
            time.sleep(0.1 * count)
        return False

    def __commit(self, block: Block):
        """
        Starts the process to add a block to the blockchain
        """
        self.database.commit_block(block)
        return block

    def get_proposed_block_hash(self, proposed_block: ProposedBlock):
        """
        Generates a block that is potentially to be added to the blockchain
        """
        logging.debug(f'proposed: {proposed_block}')
        block = generate_from_proposed_block(proposed_block, self.last_block)
        logging.debug(block)
        return block.hash

    def get_new_block_hash(self, transaction, block_type, timestamp, data_collection_name,
                           data_key_field_name, data_key_value):
        """
        Generates a candidate block and calculates its hash
        """
        logging.info(f'Previous hash: {self.last_block}')

        new_block = generate_block(transaction, block_type, timestamp,
                          self.last_block, data_collection_name,
                          data_key_field_name, data_key_value)

        logging.info(f'New block: {transaction}, {block_type}, {timestamp},\
                        {data_collection_name}, {data_key_field_name}, {data_key_value}')

        return new_block.hash

    def validate_block(self, block: Block):
        """
        Dispatchs blocks for comparison against other nodes and determines
        the results
        """
        if len(self.nodes) == 0:
            return True

        proposed_block = ProposedBlock(**vars(block))

        logging.info('Starting node conferral process')
        results = asyncio.run(self.validate_with_other_nodes(proposed_block))

        logging.info(f'Node conferral results: {results}')

        successful_nodes = []

        for result in results:
            logging.info(f'status code: {result.status_code} hash: {result.text}')
            logging.debug(f'Current hash: {block.hash} Conferral Node hash: {result.text}')

            if result.status_code == 200 and result.text == f'"{block.hash}"':
                logging.debug('Adding successful validated node')
                successful_nodes.append(result)

        logging.debug(f'Successful Nodes: {len(successful_nodes)}')
        logging.debug(f'All results: {len(results)}')
        logging.debug(f'Rate of success: {(len(successful_nodes) / len(results)) + 0.0}')

        return ((len(successful_nodes) / len(results)) + 0.0) > 0.75

    async def validate_with_other_nodes(self, proposed_block):
        """
        Handles the coallation of the block validation requests
        """
        logging.debug(f'Using nodes: {self.nodes}')

        outstanding_requests_tasks = [self.validate_with_other_node_request(node, proposed_block)
                                        for node in self.nodes]

        if len(outstanding_requests_tasks) == 0:
            return []

        return await asyncio.gather(*outstanding_requests_tasks)

    async def validate_with_other_node_request(self, node, proposed_block):
        """
        Dispatchs the proposed block for other nodes to confirm the hash is valid
        """
        logging.info(f'Attempting to confirm with node at address: \
                        {node}/api/blockchain/validate-block and payload: {proposed_block.json()}')

        return requests.post(f'{node}/api/blockchain/validate-block', data=proposed_block.json())

    def validate(self):
        """
        Validates the blockchain itself to ensure that all nodes are accounted for and in order
        based upon the links from one block to the next. Similar to traversal of a linked list.
        """
        hash_links = self.database.get_blockchain_hash_links()
        visited = {}

        if len(hash_links) == 0:
            return True

        list_keys = list(hash_links.keys())
        next_key = hash_links[list_keys[0]]
        visited[list_keys[0]] = True
        hash_links.pop(list_keys[0])

        while next_key != '':
            tmp_key = hash_links[next_key]
            hash_links.pop(next_key)
            next_key = tmp_key

        if len(hash_links) > 0:
            logging.error('Blockchain failed to validate at: ')
            return False

        logging.info(f'Blockchain failed to validate at: {datetime.timestamp()}')
        return True

    def find_one(self, collection_name, query):
        """
        Wrapper to call to find a single node and its real value in the database
        """
        return self.database.find_one(collection_name, query)

    def find(self, collection_name, query):
        """
        Wrapper to call to find a multiple nodes and their real values in the database
        """
        return self.database.find(collection_name, query)

    @property
    def last_block(self):
        return self.database.get_latest_hash()


def get_aws_nodes():
    client = boto3.client('servicediscovery')
    metadata_uri = os.environ['ECS_CONTAINER_METADATA_URI']
    container_metadata = requests.get(metadata_uri).json()
    container_ip = container_metadata['Networks'][0]['IPv4Addresses'][0]
    node_ips = []
    for service in client.list_services()['Services']:
        for instance in client.list_instances(
            ServiceId=service['Id'],
            MaxResults=100
        )['Instances']:
            if container_ip != instance['Attributes']['AWS_INSTANCE_IPV4']:
                node_ips.append(instance['Attributes']['AWS_INSTANCE_IPV4'])
    return node_ips
