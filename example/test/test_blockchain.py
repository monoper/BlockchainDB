import unittest
import time
from blockchain.blockchain import Blockchain
from blockchain.block import Block

class testTest(unittest.TestCase):
    def test_genesis_block_created(self):
        blockchain = Blockchain()
        self.assertEqual(len(blockchain.chain), 1)

    def test_add_single_block(self):
        blockchain = Blockchain()
        blockchain.addBlock(["aaa"])
        self.assertEqual(len(blockchain.chain), 2)

    def test(self):
        self.assertTrue(True)