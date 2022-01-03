import hashlib
import datetime
import time
import json
from urllib.parse import urlparse
from uuid import uuid1, uuid4
import requests as r
# from Utilities.algorithms import Algs
import random 
from passlib.hash import pbkdf2_sha256
import base64
from Utilities.cryptography_testing import *
from tinydb import TinyDB, Query
#git add .
#git commit -m "Message"
#git push
import sys
algs = Algs()
ring_ct = Ring_CT()
decoy_transactions = Decoy_addresses()
DB = TinyDB('db_blockchain.json')
NODES = TinyDB('nodes.json')
UNconfirmed_transactions = TinyDB('unconfirmed_transactions.json')
signatures = Signatures()


class Blockchain:
    """ the blockchain class """

    def __init__(self):
        self.nodes = []
        if len(self.read_data(NODES)) > len(self.nodes):
            self.nodes = self.read_data(NODES)
        else:
            self.read_data(NODES)
            self.nodes = []
        # self.unconfirmed_transactions = self.read_data(UNconfirmed_transactions)
        # self.unconfirmed_transactions = self.add_data(data=[], DataBase=UNconfirmed_transactions)
        self.unconfirmed_transactions = []
        self.new_transactions = []
        self.allnodes = None
        self.chain = [] #stores the blockchain
        self.old_chain = self.read_data(DataBase=DB) #Checks to see if a chain is already present
        if len(self.old_chain) > len(self.chain):
            self.chain = self.old_chain
            self.transactions = []
        else:
            self.transactions = ["How's our data?"]
            self.create_block(proof = 1, previous_hash="0", forger='Network') #helps with block creation
        self.replace_chain()



    def add_data(self, data, DataBase):
        """ This adds data to the database that is selected """
        # data = self.chain
        # print(type(data))
        DataBase.truncate()
        for item in data:
            DataBase.insert(item)
        return 'data has been added!!'
    
    def read_data(self, DataBase):
        """ Reads all the data in the selected database """
        data = DataBase.all()
        return data
	
    def update_nodes(self, node):
        """ Updates the list of nodes on one node to prevent loops when announcing new nodes on the network"""
        self.nodes.append(node)
        self.add_data(data=self.nodes, DataBase=NODES)
        return self.nodes

    def create_block(self, proof, previous_hash, forger):
        """ Used to make a block and when a block is being made the transactions are verified, invalid transactions are removed from the list of 
        transactions, the list of transactions resets. When the block is added it is announced to all the nodes as a new block """
        if len(self.chain) > 0:
            valid = self.suspendAlgorithm(forger)
            if valid == False:
                self.new_transactions = []
                miner_reward = algs.amount_change(self.chain)
            # decoy = self.add_false_transactions()
                transactionlist = []
                if len(self.chain) > 0:
                    for transaction in self.unconfirmed_transactions:
                        validtransaction = self.verify_transactions(transaction)
                        if validtransaction != None:
                            self.transactions.append()
                    if len(self.transactions) > 0:
                        blocksizelimit = False
                        for transaction in self.transactions:
                            if blocksizelimit(transactionlist) == False:
                                hashed_sender = transaction['sender']
                        # hashed_sender = hashed_sender.replace('$pbkdf2-sha256$29000$', '')
                                hashed_receiver = transaction['receiver']
                                signature = str(transaction['sender signature'])
                                transactionid = str(transaction['id'])
                                timestamp = str(transaction['timestamp'])
                        # hashed_receiver = hashed_receiver.replace('$pbkdf2-sha256$29000$', '')
                                sender_sign = ring_ct.ring_sign(blockchain=self.chain, primary_address=hashed_sender)
                                receiver_sign = ring_ct.ring_sign(blockchain=self.chain, primary_address=hashed_receiver)
                                amount = transaction['amount']
                                new_transaction = {'sender': sender_sign,'amount': amount, 'receiver':receiver_sign, 'sender signature': signature, 'id': transactionid, 'timestamp': timestamp}
                                transactionlist.append(new_transaction)
                                self.new_transactions.append(new_transaction)
                                self.transactions = self.new_transactions
                            else:
                                break
                    sender = Decoy_addresses().decoy_keys()['publickey']
                    self.add_miner_transaction(sender=sender, receiver=forger, amount=miner_reward)
            else:
                return 'Address cannot forge block due to it being in the receiving end of a transaction in the most recent 20 blocks'

        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.utcnow()),
            'proof': proof,
            'previous_hash': previous_hash,
            'data': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        self.add_data(data=self.chain, DataBase=DB)
        self.post_chain(block)
        return block
    

    def get_prev_block(self):
        """ get the previous block on the current blockchain """
        return self.chain[-1]
    


    def post_chain(self, block):
        """ sends the new block to all nodes """
        for node in self.nodes:
            chain = block
            json = {'blockchain':chain}
            url = r.post(f'http://{node}/insert_block', json)
            url_status = url.status_code
            print(f"http://{node}/insert_block \n{url_status}")
        return 'chain is updated among all nodes'

    def update_chain(self, block:dict):
        """ Updates the chain and checks if the new block is valid """
        lengthofunconfirmedtransactions = len(self.unconfirmed_transactions)
        lengthofblocktransactions = len(block['data'])
        if lengthofunconfirmedtransactions < lengthofblocktransactions:
            new_chain = self.chain
            sizeCheck = self.recevBlockCheckSize(block=block)
            new_chain.append(block)
            if len(new_chain) > len(self.chain):
                valid = self.is_chain_valid(chain=new_chain)
                self.checkTransactions(block)
                if valid == True and sizeCheck == True:
                    self.add_data(data=self.chain)
                    self.chain = new_chain
                return self.chain
            else:
                return self.chain
        else:
            self.replace_chain()
        self.unconfirmed_transactions = []
        self.add_data(data=self.unconfirmed_transactions, DataBase=UNconfirmed_transactions)
        return self.chain

    
    def proof_of_work(self, previous_proof):
        """ This is used for mining, the proof of work algorithm """
        new_proof = 1
        check_proof = False
        algs.difficulty_increase(chain=self.chain, nodes=self.nodes)
        chain = self.chain
        while check_proof is False:
            if chain == self.chain:
                hash_op = hashlib.sha256(str(new_proof**2 -
                previous_proof**2).encode()).hexdigest()
                if hash_op[:algs.count] == algs.difficulty:
                    check_proof = True
                else:
                    new_proof += 1
            else:
                check_proof = False
                break
        return new_proof 

    def add_false_transactions(self, transaction):
        """ Adds fake transactions """
        transactions = []
        transactions.append(transaction)
        decoy_transact = decoy_transactions.decoy_transactions(transactions=transactions)
        for decoy in decoy_transact:
            transactions.append(decoy)   
        return transactions

    def hash(self, block):
        """This is used to hash a block using sha256"""
        encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()

    def blockSizeCheck(self, transactions:list):
        """ Checks the block size of blocks that haven't been created yet """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.utcnow()),
            'proof': random.randint(200,1000000000000),
            'previous_hash': hashlib.sha256(self.chain[-1].encode()).hexdigest(),
            'data': transactions + transactions[-1]
        }
        # sizeofNewblock = sys.getsizeof(block)
        size_check = self.dynamicSizeLimit(block)
        return size_check


    def recevBlockCheckSize(self, block):
        """ Checks block size of a newly made block """
        sizeofblock = self.dynamicSizeLimit(block)
        return sizeofblock
    
    def dynamicSizeLimit(self, Newblock):
        """ Checks using the newest 100 blocks' size """
        sizeofblock = 0
        if len(self.chain) >= 20:
            newest100blocks = self.chain[-20:]
        else:
            newest100blocks = self.chain
        for block in newest100blocks:
            sizeofblock = sys.getsizeof(block) + sizeofblock
        mean = sizeofblock / 20
        times2 = mean * 2
        if sys.getsizeof(Newblock) <= times2:
            return True
        else:
            return False


    def is_chain_valid(self, chain):
        """Checks if the chain is valid with checking the previous hash and the proof"""
        previous_block = chain[0]
        block_index = 1
        algs.difficulty_increase(chain=chain, nodes=self.nodes)
        while block_index < len(chain):
            block = chain[block_index]

            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof - previous_proof).encode()).hexdigest()
            

            if hash_operation[:algs.count] == algs.difficulty:
                return False
            previous_block = block
            block_index += 1
        return True


    def add_miner_transaction(self, sender:str, receiver:str, amount:float):
        """ This is used to add miner transactions """
        hashed_sender = str(pbkdf2_sha256.hash(sender))
        hashed_sender = hashed_sender.replace('$pbkdf2-sha256$29000$', '')
        hashed_receiver = str(pbkdf2_sha256.hash(receiver))
        hashed_receiver = hashed_receiver.replace('$pbkdf2-sha256$29000$', '')
        senders = ring_ct.make_ring_sign(blockchain=self.chain, primary_address=hashed_sender)
        receivers = ring_ct.make_ring_sign(blockchain=self.chain, primary_address=hashed_receiver)
        transactionID = uuid1().hex
        timestamp = time.time()
        transactionforsigning = {'sender': senders, 'amount': amount, 'receiver': receivers, 'id': transactionID, 'timestamp': timestamp}
        transaction = self.signTransaction(transactionforsigning)
        signsender = transaction
        # signreceiver = transaction['signature of receiver']
        minertransaction = {'sender': senders,'amount': amount, 'receiver':receivers, 'sender signature': signsender, 'id': transactionID, 'timestamp': timestamp}
        self.transactions.append(minertransaction)
        previous_block = self.get_prev_block()
        return previous_block['index'] + 1
    
    # def add_non_miner_transaction(self, sender:str, receiver:str, amount:float):
    #     """ This is used to send or exchange currencies """
    #     if len(self.unconfirmed_transactions) < 5:
    #         self.unconfirmed_transactions.append(
    #         {
    #             'sender': sender,
    #             'receiver': receiver,
    #             'amount': amount
    #         }
    #     )
            
    #     else:
    #         for transaction in self.unconfirmed_transactions:

    def checkTransactions(self, block):
        """ checks if a transaction is in new block """
        numOfTransactionsInBlock = 0
        for transaction in block['data']:
            verify1 = self.equals(transaction)
            verify2 = self.signaturecheck(transaction)
            if verify1 == True and verify2 == True:
                self.unconfirmed_transactions.remove(transaction)
                numOfTransactionsInBlock = numOfTransactionsInBlock + 1
        return numOfTransactionsInBlock
                
        #         return True
        # return False

    def doubleSpendCheck(self, transaction):
        """ checks for double spending in the block"""
        verify = self.equals(transaction)
        verify2 = self.timeStampCheck(transaction)
        if verify == True or verify2 == True:
            return True
        return False



    def equals(self, transaction):
        """ checks for repeat transcation ids in the transaction """
        for uncontransaction in self.unconfirmed_transactions:
            transactionID = transaction['id']
            unconfirmedtransactionID = uncontransaction['id']
            if transactionID == unconfirmedtransactionID:
                return True
        return False

    def timeStampCheck(self, transaction):
        """ Checks for a reapeat timestamp in the transaction """
        for uncontransaction in self.unconfirmed_transactions:
            unconfirmedtimestamp = uncontransaction['timestamp']
            transactiontimestamp = transaction['timestamp']
            if unconfirmedtimestamp == transactiontimestamp:
                return True
        return False
            


    def suspendAlgorithm(self, address):
        """ Checks to see if the address is reapeating in the blockchain, this is to prevent someone from owning too 
        much of the blockchain and fight against large scale mining and 51% attacks """
        blockIndex = self.chain[-1]['index']
        blockIndex = blockIndex - 20
        if blockIndex >=0:
            for block in self.chain[20:]:
                for data in block['data']:
                    for receiver in data['receiver']:
                        stealthAddress = receiver
                        verify = Check_Wallet_Balance().verify_keys(publickey=stealthAddress, privatekey=address)
                        if verify == True:
                            return True
            return False
        if blockIndex < 0:
            for block in self.chain[1:]:
                for data in block['data']:
                    for receiver in data['receiver']:
                        stealthAddress = receiver
                        verify = Check_Wallet_Balance().verify_keys(publickey=stealthAddress, privatekey=address)
                        if verify == True:
                            return True
            return False
            




    # def checkIfTransactionIsInBlockSenderSignature(self, block):
    #     """ checks if transaction is already in block to prevent double spending """
    #     for transaction in self.unconfirmed_transactions:
    #         blockTransactions = block['data']
    #         for blockTransaction in blockTransactions:
    #             address = transaction['sender view key']
    #             primaddress = primary_addresses().make_primary_address(address)
    #             verifykey = Check_Wallet_Balance().verify_stealth_keys(stealth_key=blockTransaction, primary_address=primaddress)
    #             if verifykey != True:
    #                 return False


    #             self.transactions.append(transaction)
    #         self.unconfirmed_transactions = []
    #     self.add_data(data=self.unconfirmed_transactions, DataBase=UNconfirmed_transactions)
    #     previous_block = self.get_prev_block()
    #     return previous_block['index'] + 1
    def broadcast_transaction(self, transaction):
        """ sends list of unconfirmed transactions to all nodes """
        for node in self.nodes:
            url = f'http://{node}/add_transaction/'
            json = {'transaction': transaction}
            r.post(url, json)



    """ to prevent loops in the network when adding transactions """
    def add_unconfirmed_transaction(self, senderprivatekey:str, senderviewkey:str, sendersendpublickey, receiver, amount:float):
        """ This is used to add transactions so they can be verified """
        # addressofsender = primary_addresses().make_primary_address(senderviewkey)
        # signature = self.signTransaction(addressofsender, receiver)
        # signatureofsender = signature['signature of sender']
        # signatureofreceiver = signature['signature of receiver']
        unconfirmedTransaction = {'sender send publickey':sendersendpublickey, 'sender send privatekey': senderprivatekey, 'sender address': senderviewkey, 'receiver': receiver,'amount': amount,'id': uuid1(),'timestamp': time.time()}
        verify = self.doubleSpendCheck(unconfirmedTransaction)
        if verify == False:
            self.unconfirmed_transactions.append(unconfirmedTransaction)
        # self.unconfirmed_transactions = set(self.unconfirmed_transactions)
        # self.add_unconfirmed_transaction = list(self.unconfirmed_transactions)
        return unconfirmedTransaction

        # if len(self.unconfirmed_transactions) < 5:
        #     self.unconfirmed_transactions.append(
        #     {
        #         'sender': sender,
        #         'receiver': receiver,
        #         'amount': amount
        #     }
        # )
        # else:
        #     if len(self.nodes) > 1:
        #         for node in self.nodes:
        #             for transaction in self.unconfirmed_transactions:
        #                 full_transaction = {'sender': base64.encodebytes(transaction['sender'].encode()), 'receiver': base64.encodebytes(transaction['receiver'].encode()), 'amount': amount}
        #                 r.post(f'https://{node}/add_transaction/', json=full_transaction)
        #     self.unconfirmed_transactions = []
        # self.add_data(data=self.unconfirmed_transactions, DataBase=UNconfirmed_transactions)
        # previous_block = self.get_prev_block()
        # return previous_block['index'] + 1



    def verify_transactions(self, transaction):
        """ verifies transactions on the blockchain """
        senderSendPublickey = transaction['sender send publickey']
        senderSendPrivatekey = transaction['sender send privatekey']
        senderviewkey = transaction['sender address']
        receiver = transaction['receiver']
        amount = transaction['amount']
        transactionID = transaction['id']
        timestamp = transaction['timestamp']
        if amount > 0:
            verify4 = True
        else:
            verify4 = False
        verify1 = Check_Wallet_Balance().verify_keys(publickey=senderSendPublickey, privatekey=senderSendPrivatekey)
        verify2 = Check_Wallet_Balance().verify_keys(publickey=senderviewkey, privatekey=senderSendPrivatekey)
        address = primary_addresses().make_primary_address(senderviewkey)
        balance = Check_Wallet_Balance().balance_check(public_view_key=senderviewkey, blockchain=self.chain)
        balance = balance['balance']
        newBalance = balance - amount
        if verify1 == True and verify2 == True and newBalance >= 0 and verify4 == True:
            hashed_sender = str(pbkdf2_sha256.hash(address))
            hashed_receiver = str(pbkdf2_sha256.hash(receiver))
            senderSign = self.signTransaction(transaction)
            # receiverSign = transaction['signature of receiver']
            verifiedTransaction = {'sender': hashed_sender, 'amount': amount, 'receiver': hashed_receiver, 'sender signature': senderSign, 'id': transactionID, 'timestamp':timestamp}
            verify3 = self.doubleSpendCheck(verifiedTransaction)
            if verify3 == False:
                return verifiedTransaction
            else:
                # verifiedTransaction = {'sender': hashed_sender, 'amount': 0.0, 'receiver': hashed_receiver, 'sender signature': senderSign, 'id': transactionID, 'timestamp':timestamp}
                self.removeTransaction(transaction)
        else:
            self.removeTransaction(transaction)


    def signTransaction(self, transaction):
        """ signs transactions """
        signature = signatures.signTransaction(transaction)
        return signature

    #P2p nodes
    def removeTransaction(self, transaction):
        """ Removes invalid transactions """
        self.unconfirmed_transactions.remove(transaction)



    def add_node(self, address):
        """ This method adds a node to the network """
        test = r.get(f'http://{address}/get_the_chain')
        if test.status_code == 200:
            for node in self.nodes:
                json = {'node':address}
                r.post(f'http://{node}/add_one_node/', json=json)
                json = {'node':node}
                r.post(f'http://{address}/add_one_node/', json=json)
            new_node = address
            self.nodes.append(new_node)
            self.nodes = set(self.nodes)
            self.nodes = list(self.nodes)
            self.add_data(data=self.nodes, DataBase=NODES)
            return self.nodes[-1]
        else:
            return {'message': 'invalid node address!'}

        """
        Get the chain and validity of the chain among the nodes
        Find the blockchain with the greatest length and replace the other chains
        """


    def replace_chain(self):
        """ This replaces the chain and checks if it is valid """
        network = self.nodes
        if len(self.nodes) == 0:
            return {'message': 'add some nodes to get the latest chain','blockchain': self.chain}
        else:
            longest_chain = None
            max_length = len(self.chain)
            for node in network:
                print(f'https://{node}/get_the_chain')
                response = r.get(f'https://{node}/get_the_chain')
                if response.status_code==200:
                    length = response.json()['length']
                    chain = response.json()['blockchain']
                    if length > max_length and self.is_chain_valid(chain=chain):
                        max_length = length
                        longest_chain=chain
                if longest_chain != None:
                    if len(longest_chain) > len(self.chain):
                        self.chain = longest_chain
                        self.unconfirmed_transactions = []
                        self.add_data(data=self.unconfirmed_transactions, DataBase=UNconfirmed_transactions)
                        return True
                    else:
                        longest_chain = self.chain
                else:
                    longest_chain = self.chain
                if response.status_code != 200:
                    longest_chain = self.chain
                    max_length = len(self.chain)
                
                return False

    def protocol_connections(self):
        """ The Token Protocol p2p network connection algorithm"""
        all_nodes = self.get_most_nodes()
        interval1 = random.randint(2, len(all_nodes))
        x = 0
        while x != interval1:
            self.nodes.append(random.choice(all_nodes))
            x = x + 1
        return self.nodes
        # nodes_to_connect = self.nodes
        # num_of_connections = 0
        # num_of_connections_in_proxy = 0
        # if len(nodes_to_connect) == 0 or len(nodes_to_connect) < 1:
        #     connections = r.get(f'https://token-network.herokuapp.com').json()
        #     if len(connections['nodes']) != 0 or len(connections['nodes']) - 1 > 3:
        #         chance_of_proxy = random.randint(1,2)
        #         if chance_of_proxy == 2:
        #             proxy = random.randint(0, len(connections['nodes']))
        #             node2 = connections['nodes'][proxy]
        #             connections = r.get(f'https://{node2}/show_nodes').json()
        #             if len(connections['nodes']) != 0 or len(connections['nodes']) - 1 > 3:
        #                 num_of_connections_in_proxy = random.randint(1, (len(connections['nodes']) - 1))
        #             if num_of_connections_in_proxy != 0:
        #                 x = 0
                        
        #                 num_of_more_connections = random.randint(0, (num_of_connections_in_proxy - 1))
        #                 while x !=num_of_connections_in_proxy or x < num_of_connections_in_proxy:
        #                     num_of_added_connections = random.randint(0,num_of_connections_in_proxy)

                        
        #         num_of_connections = random.randint(1, (len(connections['nodes']) - 1))
        #     else:
        #         connections = connections['nodes']
        #         self.nodes.append(connections)

    def get_most_nodes(self):
        """ gets some of the nodes on the network """
        all_nodes = self.nodes
        if len(all_nodes) < 2:
            for node in all_nodes:
                node_sets = r.get(f'https://{node}/show_nodes')
                status = node_sets.status_code
                if status == 200:
                    all_nodes.append(node_sets.json()['nodes'])
                    all_nodes = set(all_nodes)
                    all_nodes = list(all_nodes)
                for nodes in node_sets:
                    more_nodes = r.get(f'https://{nodes}/show_nodes')
                    if more_nodes.status_code == 200:
                        all_nodes.append(more_nodes.json()['nodes'])
                        all_nodes = set(all_nodes)
                        all_nodes = list(all_nodes)
        else:
            return {'message': 'you must add more manually'}
        self.allnodes = all_nodes
        return self.allnodes

                    




    
    def update_transactions(self):
        """ updates the list of transactions """
        network = len(self.nodes)
        if network != 0:
            current_transactions = self.transactions
            updated_transactions = []
            length_current = len(self.chain)
            for node in network:
                node_transactions = r.get(f'http://{node}/get_the_chain').json()
                is_valid = self.is_chain_valid(node_transactions)
                if is_valid != True:
                    continue
                else:
                    i = 1
                    ii = 1
                    iii = 0
                    length = node_transactions['length']
                    while length > i:
                        while ii < len(node_transactions['blockchain'][i]['transactions']):
                            transactions = node_transactions['blockchain'][i]['transactions']
                            if transactions == self.chain[i][transactions]:
                                i = i + 1
                                # return True
                            else:
                                if i - 1 == length_current:
                                    iii = 0
                                    while len(transactions) > iii:
                                        if self.transactions != transactions[iii]:
                                            self.transactions.append(transactions[iii])
                                        iii = iii + 1
                                    ii = ii + 1
                                    return False
                                else:
                                    self.replace_chain()
                                    return True                     
        else:
            return {'message': 'No nodes found in node.'}
        # self.transactions = self.transactions.append(updated_transactions)