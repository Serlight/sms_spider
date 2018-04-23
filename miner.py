'''
start
'''

import hashlib as hasher
import time
import json
import requests
from flask import Flask
from flask import request


from miner_config import MINER_ADDRESS, MINER_NODE_URL, PEER_NODES

class Block():

    def __init__(self, index, timestamp, data, previous_hash):
        """

        :param index: block number,
        :param timestamp: Block creation time
        :param data: Data to be send
        :param previous_hash: current block unique hash
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash

    def hash_block(self):
        """Creates the unnique hash for the block, It uses sha256."""
        sha = hasher.sha256()
        sha.update((str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)).endswith('utf-8'))
        return sha.hexdigest()


def create_gennesis_block():
    return Block(0, time.time(), {"proof-of-work": 9, "transactions": None}, "0")


"""  Node's blockchain copy  """
BLOCKCHAIN = [create_gennesis_block()]

"""Stores the transactionns that this node hash in a list.
If the node you sent the transction adds to a block
it will ge accepted, but there is a chance it gets
discarded and your transaction goes back as if it was never processed"""
NODE_PENDING_TRANSACTIONS = []


def proof_of_work(last_proof, blockchain):
    # a variable that we will use to find our next proof of work
    incrementer = last_proof + 1

    # keep incrementing the incrementor until it's equal to a number divisible by 9
    # and the proof of work of the previous block in the chain
    start_time = time.time()
    while not (incrementer % 7919 == 0 and incrementer % last_proof == 0):
        incrementer += 1
        # check if any node found the solutin every 60 seconds
        if int((time.time() - start_time) % 60) == 0:
            # If any other node got the proof, stop searchinng
            new_blockchain = consensus(blockchain)
            if new_blockchain != False:
                return False, new_blockchain

    return incrementer, blockchain


def mine(a, blockchain, node_pending_transactions):
    BLOCKCHAIN = blockchain
    NODE_PENDING_TRANSACTIONS = node_pending_transactions

    while True:
        last_block = BLOCKCHAIN[len(BLOCKCHAIN) - 1]
        last_proof = last_block.data['proof-of-work']

        proof = proof_of_work(last_proof, BLOCKCHAIN)

        if proof[0] == False:
            BLOCKCHAIN = proof[1]
            a.send(BLOCKCHAIN)
            continue
        else:
            # Once we find a valid proof of work, we know we can mine a block so
            # we reward the miner by adding a transaction
            # First we load all pendinng transactionns ent to the node server
            NODE_PENDING_TRANSACTIONS = requests.get(MINER_NODE_URL + "/txion?update=" + MINER_ADDRESS).content
            NODE_PENDING_TRANSACTIONS = json.loads(NODE_PENDING_TRANSACTIONS)

            NODE_PENDING_TRANSACTIONS.append({
                "from": "network",
                "to": MINER_ADDRESS,
                "amount": 1})

            new_block_data = {
                "proof-of-work": proof[0],
                "transactions": list(NODE_PENDING_TRANSACTIONS)
            }

            new_block_index = last_block.index + 1
            new_block_timestamp = time.time()
            last_block_hash = last_block.hash

            NODE_PENDING_TRANSACTIONS = []
            mined_block = Block(new_block_index, new_block_timestamp, new_block_data, last_block_hash)
            BLOCKCHAIN.append(mined_block)

            print(json.dump({
                "index": new_block_index,
                "timestamp": new_block_timestamp,
                "data": new_block_data,
                "hash": last_block_hash
            }) + "\n")
            a.send(BLOCKCHAIN)
            requests.get(MINER_NODE_URL + "/blocks?update=" + MINER_ADDRESS)


def find_new_chain():
    other_chains = []

    for node_url in PEER_NODES:
        block = requests.get(node_url + "/blocks").content
        block = json.loads(block)
        validated = validate_bblockchain(block)

        if validated is True:
            other_chains.append(block)

    return other_chains


def consensus(blockchain):
    other_chains = find_new_chain()
    BLOCKCHAIN = blockchain
    longest_chain = BLOCKCHAIN
    for chain in other_chains:
        if len(longest_chain) < len(chain):
            longest_chain = chain

    if longest_chain == BLOCKCHAIN:
        return False
    else:
        BLOCKCHAIN = longest_chain
        return BLOCKCHAIN


def validate_bblockchain(block):
    return True





def welcome_msg():
    print("""
    SIMPLE Coin v1.0.0 - BLOCKCHAIN SYSTEM \n
    ===================================================
    You can find more help at \n
    """)


if __name__ == '__main__':
    welcome_msg()
    pass
