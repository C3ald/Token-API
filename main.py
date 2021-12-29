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
from sys import getsizeof
# from Utilities.cryptography_testing import Make_Keys
# from Utilities.cryptography_testing import primary_addresses
# from Utilities.cryptography_testing import Check_Wallet_Balance
# from Utilities.cryptography_testing import Ring_CT
# from Utilities.cryptography_testing import Decoy_addresses
from Utilities.cryptography_testing import *
from fastapi_signals import *
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

templates = Jinja2Templates(directory="templates/")

blockchain = Blockchain()


class Transaction(BaseModel):
    sender_public_send_key: str
    sender_private_send_key: str
    sender_view_key: str
    receiver: str
    amount: float


class Walletkey(BaseModel):
    publickey: str
    privatekey: str

class Wallet_public(BaseModel):
    viewkey: str

class Passphrase(BaseModel):
    passphrase: str


class Blockchain(BaseModel):
    block: dict


class Recover(BaseModel):
    passphrase: str


class Mining(BaseModel):
    address: str


class EncryptedTransaction(BaseModel):
    sender_publickey: bytes
    receiver: bytes
    amount: float    

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
        # get previous block
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
    # decoy = decoy_addresses.decoy_transactions(amount)
        # create block
    message = blockchain.create_block(proof=proof, previous_hash=prev_hash, forger=keys.address)
        #returns the last block in the chain
    return {'message': message}
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
async def add_transaction(transaction: Transaction):
    """ Allows transactions to be added to the chain from nodes"""
    senderpublicsendkey = transaction.sender_public_send_key
    senderprivatesendkey = transaction.sender_private_send_key
    senderviewkey = transaction.sender_view_key
    receiver = transaction.receiver
    amount = transaction.amount
    new_transaction = blockchain.add_unconfirmed_transaction(senderprivatekey=senderprivatesendkey, 
    sendersendpublickey=senderpublicsendkey, 
    receiver=receiver, 
    senderviewkey=senderviewkey, 
    amount=amount)
    blockchain.broadcast_transaction(transaction=new_transaction)
    result = 'transaction has been added and is awaiting verification'
    return result







@app.post('/add_unconfirmed_transaction', tags=['transaction'])
async def add_unconfirmed_transaction(transaction: Transaction):
    """ broadcasts transactions to all nodes to be verified by miners"""
    senderpublicsendkey = transaction.sender_public_send_key
    senderprivatesendkey = transaction.sender_private_send_key
    senderviewkey = transaction.sender_view_key
    receiver = transaction.receiver
    amount = transaction.amount
    new_transaction = blockchain.add_unconfirmed_transaction(senderprivatekey=senderprivatesendkey, 
    sendersendpublickey=senderpublicsendkey, 
    receiver=receiver, 
    senderviewkey=senderviewkey, 
    amount=amount)
    blockchain.broadcast_transaction(transaction=new_transaction)
    result = 'transaction has been added and is awaiting verification'
    return result

""" Wallets should be made offline. """





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




@app.get("/replace_chain", tags=['nodes'])
async def replace_chain():
    """ replaces the current chain with the most recent and longest chain """
    blockchain.replace_chain()
    blockchain.is_chain_valid(chain=blockchain.chain)
    return{'message': 'chain has been updated and is valid', 
           'longest chain': blockchain.chain}



@app.websocket('/dashboard')
async def dashboard(websocket: WebSocket):
    """ P2p Dashboard """
    await websocket.accept()
    # block = blockchain.chain
    # websocket.send_json(block)
    while True:
        block = blockchain.chain
        await websocket.send_text(f'Message: {block}')
        await asyncio.sleep(10)



@app.websocket("/ws")
async def dashboard_endpoint(websocket: WebSocket):
    """ This shows real time data for nodes"""
    await websocket.accept()
    message = None
    while True:
        try:
        
            if message != blockchain.chain:
                message = blockchain.chain
                await websocket.send_json(message)
                print(message)
                t.sleep(0.2)
            else:
                pass
        except Exception as e:
            pass
        break
    print('client disconnected')


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
            pass
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


@app.post('/insert_block', tags=['nodes'])
async def insert_chain(chain:Blockchain):
    """ replace the chain if all nodes are down or if node has a 
    firewall preventing get requests from web servers """
    updated_chain = blockchain.update_chain(new_chain=chain.block)
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
    # blockchain.replace_chain()
    uvicorn.run('main:app', host=SERVER_HOST, port=SERVER_PORT, reload=SERVER_RELOAD)
    # ran = run
    # while run == ran:
    #     update = blockchain.replace_chain()
    #     t.sleep(60.0)