"""Class to handle mongodb database"""

import os
import logging
from pymongo import MongoClient
from .models import Block, generate_audit_block


class CreateBlockAlreadyExistsError(Exception):
    def __init__(self, data_key_field_name, data_key_value):
        self.message = f'Block of type CREATE cannot be created. \
                        Key: {data_key_field_name} and Id: {data_key_value} already exists'


class MongoDb:
    """
    Wrapper for mongodb and performs some basic operations on the database
    """
    def __init__(self):
        if 'CONNECTION_STRING' in os.environ:
            self.connection_string = os.environ['CONNECTION_STRING']
        else:
            raise ValueError('CONNECTION_STRING is required as an environment variable')

        if 'DATABASE' in os.environ:
            self.database_name = os.environ['DATABASE']
        else:
            raise ValueError('DATABASE is required as an environment variable')

    def get_latest_hash(self):
        latest_block = self.__get_database().Blocks.find_one({}, sort=[('_id', -1)])

        if latest_block is None:
            return ''

        return latest_block['hash']

    def commit_block(self, block: Block):
        database = self.__get_database()
        naked_block = block.get_naked_block()

        if database.Blocks.count() == 0:
            logging.info("Genisys block created")
            database.Blocks.insert_one(vars(naked_block))
            return

        data_block = block.get_data_block()
        data_key_value = str(block.data_key_value)

        existing_block_query = {block.data_key_field_name: data_key_value, "block_type": 'CREATE'}
        existing_collection_block_result = list(self.__get_database()[data_block.collection]
                                            .find(filter=existing_block_query))

        if len(existing_collection_block_result) > 0 and block.block_type == 'CREATE':
            raise CreateBlockAlreadyExistsError(block.data_key_field_name, data_key_value)

        existing_block_query_updated = {"$set": {"superceded": True}}
        database[data_block.collection].update({block.data_key_field_name: data_key_value},
                                                existing_block_query_updated, multi=True)

        database.Blocks.insert_one(vars(naked_block))
        database[data_block.collection].insert_one(data_block.get_document())

    def get_block_count(self):
        database = self.__get_database()
        return database.Blocks.count()

    def __get_database(self):
        client = MongoClient(self.connection_string)
        return client[self.database_name]

    def __find_base(self, collection_name, query):
        database = self.__get_database()

        query['superceded'] = False

        return database[collection_name].find(filter=query, projection={'block_type': 0})

    def find_one(self, collection_name, query):
        result = self.__find_base(collection_name, query)
        sorted_result = list(result.sort([("_id", -1)]).limit(1))

        if len(sorted_result) == 0:
            return None

        result = sorted_result[0]
        del result["_id"]
        del result["superceded"]

        return self.audit_result(result)

    def find(self, collection_name, query):
        results = list(self.__find_base(collection_name, query).sort([("_id", -1)]))
        for result in results:
            del result["_id"]
            del result["superceded"]

        return self.audit_results(results)

    def audit_result(self, query_result):
        database = self.__get_database()

        block = database.Blocks.find_one(filter={"hash": query_result['hash_id']})

        proposed_hash = generate_audit_block(block['id'], query_result, block['block_type'],
                             block['timestamp'], block['previous_hash'])

        if proposed_hash.hash == block['hash']:
            return query_result
        return None

    def audit_results(self, query_results):
        database = self.__get_database()
        results = []

        for result in query_results:
            block = database.Blocks.find_one(filter={"hash": result['hash_id']})

            proposed_hash = generate_audit_block(block['id'], result, block['block_type'],
                             block['timestamp'], block['previous_hash']).hash

            if proposed_hash == block['hash']:
                results.append(result)

        return results

    def get_blockchain_hash_links(self):
        block_hash_links = self.__get_database().Blocks.find(sort=[("_id", -1)],
                            projection={'hash': 1, 'previous_hash': 1, '_id': 0})
        return {elem['hash']: elem['previous_hash'] for elem in list(block_hash_links)}
