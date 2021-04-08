import uuid
import json
import logging
from hashlib import sha256
from datetime import datetime
from pydantic import BaseModel
from ..util import HelperEncoder


class Block:
    def __init__(self, id, data, block_type, timestamp: datetime, previous_hash,
                    data_collection_name, data_key_field_name, data_key_value):
        self.id = id
        self.block_type = block_type
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.data = json.dumps(data, cls=HelperEncoder)

        logging.debug(json.dumps(self.__dict__, sort_keys=True, cls=HelperEncoder))

        self.hash = sha256(json.dumps(self.__dict__, sort_keys=True, cls=HelperEncoder).encode()) \
                        .hexdigest()
        self.data_collection_name = data_collection_name
        self.data_key_field_name = data_key_field_name
        self.data_key_value = data_key_value
        self.superceded = False

    def get_naked_block(self):
        return NakedBlock(self.id, self.timestamp, self.block_type, self.hash, self.previous_hash)

    def get_data_block(self):
        return DataBlock(self.timestamp, self.data_collection_name,
                            self.data, self.hash, self.block_type, self.superceded)


class NakedBlock:
    def __init__(self, id, timestamp, block_type, hash, previous_hash):
        self.id = id
        self.block_type = block_type
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = hash


class DataBlock:
    def __init__(self, timestamp, data_collection_name, data, hash, block_type, superceded):
        self.timestamp = timestamp
        self.collection = data_collection_name
        self.block_type = block_type
        self.data = data
        self.superceded = superceded
        self.hash = hash

    def set_superceded(self):
        self.superceded = True

    def get_document(self):
        document = json.loads(self.data)
        document['hash_id'] = self.hash
        document['block_type'] = self.block_type
        document['superceded'] = self.superceded
        return document


def block_types_lookup(block_type):
    block_types = {"CREATE": 0, "GRANT": 1, "EDIT": 2}
    return block_types[block_type]


def block_types_reverse_lookup(block_type):
    print(block_type)
    block_types = {0: "CREATE", 1: "GRANT", 2: "EDIT"}
    return block_types[block_type]


class ProposedBlock(BaseModel):
    id: str
    block_type: str
    timestamp: str
    data: str
    data_collection_name: str
    data_key_field_name: str
    data_key_value: str


def generate_block(data, block_type, timestamp: datetime, previous_hash,
                    data_collection_name, data_key_field_name, data_key_value):
    return Block(uuid.uuid4().hex, data, block_type, timestamp, previous_hash,
                    data_collection_name, data_key_field_name, data_key_value)

def generate_audit_block(id, data, block_type, timestamp: datetime, previous_hash):
    del data["hash_id"]
    return Block(id, data, block_type, timestamp, previous_hash, '', '', '')


def generate_from_proposed_block(proposed_block: ProposedBlock, previous_hash):
    return Block(proposed_block.id, json.loads(proposed_block.data),
                 proposed_block.block_type, proposed_block.timestamp, previous_hash,
                 proposed_block.data_collection_name, proposed_block.data_key_field_name,
                 proposed_block.data_key_value)
