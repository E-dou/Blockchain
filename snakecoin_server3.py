#区块链：区块+链

#定义 -> py class
#不可更改 -> Hash
#去中心化 -> Consensus
#共识机制 -> Proof-of-Work

#去中心化表现为：不同矿工维护的是一个账本
#针对每个矿工而言：
#职能1 处理请求，帮助记录信息
#职能2 得到好处——挖矿
#如果矿工挖到一个币，就新建一个区块，把交易记录打包放在区块中
#这样，由区块构成的“账本”就越来越长
#而这个账本不是仅仅由一个矿工维护，而是所有矿工共同维护
#所有矿工共同维护的这个“账本”就是区块链

#什么是“挖矿”？-> 工作量证明
#（可以理解为，一群电脑在做数学题，谁算得快谁就会得到系统的奖励（挖到矿））


#snakecoin矿工服务端代码
#1.交易记录功能
#2.挖矿功能
#3.账本查询功能

from flask import Flask
from flask import request
import json
import requests
import hashlib as hasher
import datetime as date
from colorama import Fore
import pickle

#定义节点
node = Flask(__name__)



#定义区块结构体
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
    def __init__ (self):
        self.blockchain = []

#创世块
def create_genesis_block():
    return Block(0, date.datetime.now(), {
        'proof-of-work': 9,#工作量证明
        'transactions': None
    }, '0')


#配置信息与变量定义（矿工）
#本矿工ip
my_node = 'http://10.8.163.40'
#本矿工地址
miner_address = 'kuanggong1_address'
#所有矿工的ip
node1 = 'http://10.8.163.40'
#node2 = ''
all_nodes = {node1}#, node2}
#所有矿工的ip
peer_nodes = all_nodes.difference({my_node})
timeout = 5


#矿工职能2：挖矿
#区块链
bc = Blockchain()
bc.blockchain.append(create_genesis_block())
#该节点待处理交易
this_nodes_transactions = []


#矿工职能1：处理请求，帮助记录信息
#处理 POST 请求，处理区块交易
@node.route('/txion', methods=['POST'])
def transaction():
    #获取 POST 请求的数据
    new_txion = request.get_json()
    #添加交易到待处理列表
    this_nodes_transactions.append(new_txion)
    #显示提交的交易
    print('New transaction')
    print('From: {}'.format(new_txion['from'].encode('ascii', 'replace')))
    print('To: {}'.format(new_txion['to'].encode('ascii','replace')))
    print('Amount: {}\n'.format(new_txion['amount']))
    #回应客户端交易已提交
    return 'Transaction submission successful\n'

#处理 GET 请求/blocks，用于获取区块链
@node.route('/blocks', methods=['GET'])
def get_blocks():
    #将区块链转换为JSON格式
    blocks = []
    for block in bc.blockchain:
        blocks.append({
            "index": block.index,
            "timestamp": str(block.timestamp),
            "data": block.data,
            "previous_hash": block.previous_hash,
            "hash": block.hash
        })
    #将Python字典转换为JSON格式
    chain_to_send = json.dumps(blocks, indent = 2)
    chain_to_send_object = pickle.dumps(blockchain)
    #返回JSON格式的区块链
    return chain_to_send_object

#得到全网所有账本
def find_new_chains():
    #用GET请求获取其他节点的区块链
    other_chains = []
    for node_url in peer_nodes:
        #使用try避免一个矿工（节点）网络连接失败
        try:
            block = requests.get(node_url + '/blocks', timeout = timeout)
            #将JSON格式转换为Python字典
            block = pickle.loads(block.content)
            other_chains.append(block)
            print('------------已拿到其他矿工账本------------')
        except:
            print('------------获取其他矿工账本失败------------')
            pass
    return other_chains


#实现工作量证明算法（挖矿的算法）
#返回值能够被9（工作量证明初始值）和上一次last_proof整除
def proof_of_work(last_proof):
    #工作量证明初始值
    incrementor = last_proof + 1
    #循环，直到找到一个值，能够被9整除，且能够被上一次last_proof整除
    while not (incrementor % 9 == 0 and incrementor % last_proof == 0):
        incrementor += 1
    #返回找到的值
    return incrementor


#处理 GET 请求/mine，用于挖矿
@node.route('/mine', methods=['GET'])
def mine():
    #获取上一个区块的工作量证明
    last_block = blockchain[len(blockchain) - 1]
    last_proof = last_block.data['proof-of-work']
    #程序在此处暂停，直到找到一个新的工作量证明
    proof = proof_of_work(last_proof)
    #给工作量证明的奖励，即通过交易奖励挖矿者
    this_nodes_transactions.append({
        'from': 'network',
        'to': miner_address,
        'amount': 1
    })

    #创建新区块，把工作量证明和所有交易一起打包
    new_block_data = {
        'proof-of-work': proof,
        'transactions': list(this_nodes_transactions)
    }
    new_block_index = last_block.index + 1
    new_block_timestamp = this_timestamp = date.datetime.now()
    last_block_hash = last_block.hash
    #清空待处理交易列表
    this_nodes_transactions[:] = []
    #创建新块
    mined_block = Block(
        new_block_index,
        new_block_timestamp,
        new_block_data,
        last_block_hash
    )
    print("------------挖到币了^_^------------")

    #若目前维护的账本是最长的账本（别人是否抢先挖到币），则更新；否则不更新
    #共识算法 -> 选择最长的账本
    #获取其他节点的区块链
    other_chains = find_new_chains()
    #若其他节点的区块链比本节点的区块链长，则更新本节点的区块链
    longest_chain = bc.blockchain
    print("自己账本长度：", len(bc.blockchain))
    for chain in other_chains:
            print("别人账本长度：", len(chain))
            if len(longest_chain) < len(chain):
                print('------------自己账本没别人长TT------------')
                longest_chain = chain
    #如果自己账本最长或和别人等长，则把新挖到的币加进去
    if len(bc.blockchain) == len(longest_chain):
        bc.blockchain.append(mined_block)
    else:
        bc.blockchain = longest_chain
    print("共识算法后自己账本的长度：", len(bc.blockchain))
    return "finished mining\n"

    #运行应用
    if __name__ == '__main__':
        node.run('0.0.0.0', 5000)#可以局域网通过ip访问
