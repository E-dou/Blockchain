import requests
import hashlib as hasher
import pickle
import json

my_node = 'http://10.8.163.40'

class Block:
    #初始化区块
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.hash_block()

    #计算区块哈希值
    def hash_block(self):
        sha = hasher.sha256()
        sha.update(str(self.index).encode('utf-8')
                   + str(self.timestamp).encode('utf-8')
                   + str(self.data).encode('utf-8')
                   + str(self.previous_hash).encode('utf-8'))
        return sha.hexdigest()
    
class Blockchain:
    def __init__(self):
        self.blockchain = []

    #挖矿请求
while True:
    # 开始挖矿
    response = requests.get(my_node + '/mine')
    response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

    blockchain_response = requests.get(my_node + '/blocks')
    blockchain_response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

    blockchain_data = blockchain_response.content
    blockchain = pickle.loads(blockchain_data)

    blocks = []
    for block in blockchain:
        blocks.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "previous_hash": block.previous_hash,
            "hash": block.hash
        })
    blocks_json = json.dumps(blocks, indent=2)
    print("The last block of the ledger", blocks[-1])
