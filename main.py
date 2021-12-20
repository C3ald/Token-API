from starlette.responses import Response
from passlib.hash import pbkdf2_sha256
from starlette.websockets import WebSocketDisconnect
from blockchain import Blockchain
# from wallet import Wallet
from fastapi import FastAPI, WebSocket
import uvicorn
import socket
import requests as r
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import json
import asyncio
# from Utilities.algorithims import Algs
import time as t
import random
import base64
# from Utilities.cryptography_testing import Make_Keys
# from Utilities.cryptography_testing import primary_addresses
# from Utilities.cryptography_testing import Check_Wallet_Balance
# from Utilities.cryptography_testing import Ring_CT
# from Utilities.cryptography_testing import Decoy_addresses
from Utilities.cryptography_testing import *
ring_ct = Ring_CT()
checkbalance = Check_Wallet_Balance()
create_keys = Make_Keys()
primary_addr = primary_addresses()
decoy_addresses = Decoy_addresses()
 #imported templates
#from fastapi.staticfiles import StaticFiles #imported staticfiles

# {
#  "node": [
#    "http://127.0.0.1:8000", "http://127.0.0.1:8001"
#  ]
#}

tags_metadata = [
    {'name':'information', 
    'description': 'This will allow you to get info about the blockchain',

    'name':'wallet',
    'description': 'this will allow you to access your wallet and make wallets',
    
    'name': 'transaction',
    'description': 'transactions',

    'name': 'mining',
    'description': 'mining', 

    'name': 'nodes',
    'description': 'adding nodes and replacing the chain'
    }]

# CONSTANTS
SERVER_NAME = 'Token Network'
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8000
SERVER_RELOAD = False
DESCRIPTION = "Welcome to The Token Network, a blockchain network with a cryptocurrency called Token, it's like Dogecoin and Bitcoin but faster than Bitcoin and harder to mine than Dogecoin, welcome to the Future of the world."
algs = Algs()
S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostname = socket.gethostname()
IP = socket.gethostbyname(hostname)
# wallet = Wallet()
class Url(BaseModel):
    node: str



# class Phrase(BaseModel):
#     phrase: str


app = FastAPI(title=SERVER_NAME, openapi_tags=tags_metadata, description=DESCRIPTION)

templates = Jinja2Templates(directory="templates/") #Added templates

blockchain = Blockchain()
# wallets = Wallet()

class Transaction(BaseModel):
    sender_publickey: str
    sender_privatekey: str
    sender_publicview_key: str
    receiver: str
    amount: float


# class ConTransaction(BaseModel):
#     sender_publickey: bytes
#     sender_privatekey: bytes
#     receiver: bytes
#     amount: float

class Walletkey(BaseModel):
    publickey: str
    privatekey: str

class Wallet_public(BaseModel):
    viewkey: str

class Passphrase(BaseModel):
    passphrase: str


class Blockchain(BaseModel):
    blockchain: list


class Recover(BaseModel):
    passphrase: str


class Mining(BaseModel):
    address: str


class EncryptedTransaction(BaseModel):
    sender_publickey: bytes
    # sender_publicview_key: bytes
    receiver: bytes
    amount: float    
#def backgroundmining():
 #   """ Mines a block in the background """
  # prev_block = blockchain.get_prev_block()
    # previous proof
    #prev_proof = prev_block['proof']
    # proof
    #proof = blockchain.proof_of_work(previous_proof=prev_proof)
    # previous hash
    #prev_hash = blockchain.hash(block=prev_block)
    # add data
    #transaction = blockchain.add_transaction(sender='Network', reciver='You', amount='0.8')
    # create block
    #block = blockchain.create_block(proof=proof, previous_hash=prev_hash, data=transaction)
    #return blockchain.chain[-1]


# @app.get("/")
# async def index():
#     """ This returns the homepage """
#     return {"Message": "Hello World!", "is_valid": True}
#     #return templates.TemplateResponse('index.html', context={'request': 1234}, status_code=200)

@app.get('/')
async def index():
    """ returns index page """ 
    return "see /docs for the api"


@app.get("/get_the_chain", tags=['information'])
async def get_the_chain():
    """ Use this to get the whole blockchain """
    # update = blockchain.replace_chain()
    response = {"blockchain": blockchain.chain, "length": len(blockchain.chain)}
    return response


@app.post("/mining", tags=['mining'])
async def mine(keys:Mining):
    """ This allows you to mine blocks """
    # update_chain = blockchain.replace_chain()
    # valid = wallets.verify_wallet(publickey=keys.publickey, privatekey=keys.privatekey)
    # if valid == True:
        # Previous Block
    prev_block = blockchain.get_prev_block()
        # previous proof
    prev_proof = prev_block['proof']
        # proof
    proof = blockchain.proof_of_work(previous_proof=prev_proof)
        # previous hash
    prev_hash = blockchain.hash(block=prev_block)
        # add data
    amount = algs.amount_change(chain=blockchain.chain)
        # stealth_key = pbkdf2_sha256.hash(str(keys.publickey))
    sender = decoy_addresses.decoy_keys()['publickey']
    transaction = blockchain.add_miner_transaction(sender=sender, receiver=keys.address, amount=amount)
        #decoy transactions
    # decoy = decoy_addresses.decoy_transactions(amount)
        # create block
    create_block = blockchain.create_block(proof=proof, previous_hash=prev_hash)
        #returns the last block in the chain
    return {'message': blockchain.chain[-1]}
    # else:
    #     return "no wallet detected"


@app.get("/status", tags=['information'])
async def is_valid():
    """ Checks to see if chain is valid """
    is_valid = blockchain.is_chain_valid(chain=blockchain.chain)
    if is_valid:
        response = {"message": "Not compromised"}
    else:
        response = {"message": "Blockchain has been compromised"}
    return response


@app.post("/add_transaction/", tags=['transaction'])
async def add_transaction(transaction: EncryptedTransaction):
    """ Allows transactions to be added to the chain"""
    sender = transaction.sender_publickey
    receiver = transaction.receiver
    sender = str(base64.decodebytes(sender).decode())
    receiver = str(base64.decodebytes(receiver).decode())
    blockchain.add_non_miner_transaction(sender=sender, receiver=receiver, amount=transaction.amount)
    # blockchain.replace_chain()
    # sender_publickey = str(base64.decodebytes(transaction.sender_publickey).decode())
    # # sender_privatekey = str(base64.decodebytes(transaction.sender_privatekey).decode())
    # sender_viewkey = str(base64.decodebytes(transaction.sender_publicview_key).decode())
    # receiver = str(base64.decodebytes(transaction.receiver).decode())
    # # sender_receivekey = str(base64.decodebytes(transaction.sender_address))
    # sender_receivekey = primary_addr.make_primary_address(sender_viewkey)
    # # verify = checkbalance.verify_keys(publickey=sender_publickey, privatekey=sender_privatekey)
    # # verify2 = checkbalance.verify_keys(publickey=sender_viewkey, privatekey=sender_privatekey)
    # # if verify == True and verify2 == True:
    # balance = checkbalance.balance_check(primary_address=sender_viewkey, blockchain=blockchain.chain)
    # amount = algs.network_fee(amount=transaction.amount)
    # new_balance = balance['balance'] - amount
    # if new_balance > 0:
    #     sender = sender_receivekey
    #     receiver = receiver
    #     sender_key = create_keys.make_stealth_keys(primary_address=sender)
    #     receiver_key = create_keys.make_stealth_keys(primary_address=receiver)
    #     amount = transaction.amount
    #     blockchain.add_non_miner_transaction(sender=sender_key, receiver=receiver_key, amount=amount)
    #     result = 'transaction was successful'
    # else:
    #     result = 'invalid balance'
    # # else:
    # #     result = 'invalid keys'
    # return result
    # update_chain = blockchain.replace_chain()
    # update_transactions = blockchain.update_transactions()
    # sender_publickey = base64.decodebytes(transaction.sender_publickey)
    # sender_privatekey = base64.decodebytes(transaction.sender_privatekey)
    # receiver = base64.decodebytes(transaction.receiver)
    # sender_publickey = sender_publickey.decode()
    # sender_privatekey = sender_privatekey.decode()
    # receiver = receiver.decode()
    # verify = wallets.verify_wallet(publickey=sender_publickey, privatekey=sender_privatekey)
    # if verify == True:
    #     wallets.checkbalance(chain=blockchain.chain, viewkey=sender_privatekey)
    #     balance_check = wallets.balance
    #     algs.network_fee(amount=transaction.amount)
    #     amount = algs.amount
    #     balance = balance_check - amount
    #     if balance > 0:
    #         sender = pbkdf2_sha256.hash(transaction.sender_publickey)
    #         receiver = pbkdf2_sha256.hash(transaction.receiver)
    #         result = blockchain.add_non_miner_transaction(sender=sender, receiver=receiver, amount=amount)
    #         # decoy = decoy_transactions(amount_sent=amount)
    #     else:
    #         result = "Not enough Tokens"
    #     return result
    # else:
    #     return "invalid wallet or response"






@app.post('/add_unconfirmed_transaction', tags=['transaction'])
async def add_unconfirmed_transaction(transaction: Transaction):
    """ broadcasts transactions to all nodes to be verified by miners"""
    verify = checkbalance.verify_keys(publickey=transaction.sender_publickey, privatekey=transaction.sender_privatekey)
    verify2 = checkbalance.verify_keys(publickey=transaction.sender_publicview_key, privatekey=transaction.sender_privatekey)
    if verify == True and verify2 == True:
        balance = checkbalance.balance_check(primary_address=transaction.sender_publicview_key, blockchain=blockchain.chain)
        amount = algs.network_fee(amount=transaction.amount)
        new_balance = balance ['balance']- amount
        if new_balance > 0:
            receiver = transaction.receiver
            sender = primary_addr.make_primary_address(public_view=transaction.sender_publicview_key)
            sender_key = create_keys.make_stealth_keys(primary_address=sender)
            receiver_key = create_keys.make_stealth_keys(primary_address=receiver)
            blockchain.add_unconfirmed_transaction(sender=sender_key, receiver=receiver_key, amount=amount)
            result = 'transaction was successful'
        else:
            result = 'invalid balance'
    else:
        result = 'invalid keys'
    return result
    # if verify == True:
    #     wallets.checkbalance(chain=blockchain.chain, viewkey=transaction.sender_privatekey)
    #     balance_check = wallets.balance
    #     algs.network_fee(amount=transaction.amount)
    #     amount = algs.amount
    #     balance = balance_check - amount
    #     if balance > 0:
    #         # sender = pbkdf2_sha256.hash(transaction.sender_publickey)
    #         # receiver = pbkdf2_sha256.hash(transaction.receiver)
    #         result = blockchain.add_unconfirmed_transaction(sender=transaction.sender_publickey, receiver=transaction.receiver, amount=amount, sender_privatekey=transaction.sender_privatekey)
    #         # decoy = decoy_transactions(amount_sent=amount)
    #     else:
    #         result = "Not enough Tokens"
    #     return result
    # else:
    #     return "invalid wallet or response"

""" Wallets should be made offline. """
# @app.get('/create_keys', tags=['wallet'])
# async def create_keys():
#     """ Makes a public and private key """
#     wallets.make_wallet()
#     # wallets.generate_ecc_keys
#     result = {"publickey": wallets.publickey,"privatekey": wallets.privatekey,'phrase': wallets.phrase,"message": "do not share your private key or your passphrase!!!"}
#     # print(wallets.result)
#     return result

    

# #Peer 2 peer network/decentralized
@app.get("/show_nodes/", tags=['nodes'])
async def show_nodes(): 
    result = blockchain.show_nodes()
    return {'nodes':result}



@app.post("/add_node/", tags=['nodes'])
async def add_node(url:Url):
    """ This is used to add nodes """
    item = url.node
    blockchain.add_node(item) 
            # transaction = blockchain.add_transaction(sender='Network', receiver=wallets.publickey, amount=30)
    result = item
    return result


@app.post('/add_one_node/', tags=['nodes'])
async def add_one_node(url:Url):
	""" adds one node """
	item = url.node
	blockchain.update_nodes(node=item)
	return item
    # if wallets.privatekey != 0:
    #     for item in node:
    #         for item in item[1]:
    #             blockchain.add_node(item) 
    #             transaction = blockchain.add_transaction(sender='Network', receiver=wallets.publickey, amount=30)
    #             result = blockchain.show_nodes(), transaction
    #             return result
    # else:
    #     return "no wallet is detected"
    #nodes = blockchain.show_nodes()
    #return {"message": f"the node {node.node} has been added", "data": {"count": len(nodes), 'nodes': nodes}}



@app.get("/replace_chain", tags=['nodes'])
async def replace_chain():
    """ replaces the current chain with the most recent and longest chain """
    # use the replace chain method to see if the block is valid
    blockchain.replace_chain()
    blockchain.is_chain_valid(chain=blockchain.chain)
    return{'message': 'chain has been updated and is valid', 
           'longest chain': blockchain.chain}
    #check to see if the chain needs to be replaced
    #check if the chain is correct

# @app.post("/rsa_wallet")
# async def rsa_wallet(passhrase: Passphrase):
#     """ This makes the rsa wallet """
#     wallet = rsa_Wallet(passphrase=passhrase)
#     result = wallet.generate_rsa_keys()
#     print(type(result))
#     return result


@app.websocket("/ws")
async def dashboard_endpoint(websocket: WebSocket):
    """ This shows real time data for nodes"""
    # update_chain = blockchain.replace_chain()
    await websocket.accept()
    message = None
    while True:
        try:
        # await asyncio.sleep(0.1)
            if message != blockchain.chain:
                message = blockchain.chain
                await websocket.send_json(message)
                print(message)
                t.sleep(0.2)
            else:
                pass
        except Exception as e:
            break
        print('client disconnected')
    # if False:
    #     websocket.close()
    # # WebSocketDisconnect()
    # print("client disconnected")
@app.websocket("/nodes")
async def dashboard_endpoint(websocket: WebSocket):
    """ This shows real time data of each node, this should be used for detecting new nodes in the network or helping with automating adding nodes"""
    await websocket.accept()
    message = None
    while True:
        try:
            if message != blockchain.nodes:
                message = blockchain.nodes
                await websocket.send_json(message)
                print(message)
                t.sleep(0.2)
            else:
                pass
        except Exception as e:
            break
        print('client disconnected')

    




@app.post('/check_balance', tags=['wallet'])
async def check_balance(wallet:Wallet_public):
    """ Checks the balance of a wallet with the view key """
    #this route checks the balance of a publickey
    # wallets.checkbalance(viewkey=wallet.viewkey, chain=blockchain.chain)
    # return {"publickey":wallet.viewkey,
    #         "balance": wallets.balance}
    balance = checkbalance.balance_check(wallet.viewkey, blockchain=blockchain.chain)
    return {'Address': balance['receive address'], 'balance': f'{balance["balance"]}Tokens'}


@app.post('/insert_chain', tags=['nodes'])
async def insert_chain(chain:Blockchain):
    """ replace the chain if all nodes are down or if node has a 
    firewall preventing get requests from web servers """
    updated_chain = blockchain.update_chain(new_chain=chain.blockchain)
    return updated_chain
    # if is_valid == True:
    #     blockchain.chain
    #     return chain
    # else:
    #     return "Invalid chain"





# @app.post('/recover_wallet', tags=['wallet'])
# async def recover_wallet(recover:Recover):
#     """ recover wallet with passphrase and publickey """
#     is_valid = wallets.recover_wallet_with_passphrase(recover.passphrase)
#     if is_valid == True:
#         return {'message': 'Wallet recovery is successful!', 'private key': wallets.privatekey, 'public key': wallets.publickey, 'passphrase': recover.passphrase}
#     else:
#         return 'invalid publickey or passphrase!'

if __name__ == '__main__':
    # hostname = socket.gethostname()
    # IP = socket.gethostbyname(hostname)
    uvicorn.run('main:app', host=SERVER_HOST, port=SERVER_PORT, reload=SERVER_RELOAD)
    # ran = run
    # while run == ran:
    #     update = blockchain.replace_chain()
    #     t.sleep(60.0)