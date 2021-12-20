import hashlib
import datetime
import json
from urllib.parse import urlparse
from uuid import uuid4
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
algs = Algs()
ring_ct = Ring_CT()
decoy_transactions = Decoy_addresses()
DB = TinyDB('db_blockchain.json')
NODES = TinyDB('nodes.json')



class Blockchain:
    """ the blockchain class """

    def __init__(self):
        self.nodes = []
        if len(self.read_data(NODES)) > len(self.nodes):
            self.nodes = self.read_data(NODES)
        else:
            self.nodes = []
        self.unconfirmed_transactions = []
        self.new_transactions = []
        self.allnodes = None
        self.chain = [] #stores the blockchain
        self.old_chain = self.read_data(DataBase=DB) #Checks to see if a chain is already present
        if len(self.old_chain) > len(self.chain):
            self.chain = self.old_chain
            self.transactions = []
        else:
            self.transactions = ["Privacy and financial independence are human rights."]
            self.create_block(proof = 1, previous_hash="0") #helps with block creation



    def add_data(self, data, DataBase):
        """ This adds data """
        # data = self.chain
        print(type(data))
        DataBase.truncate()
        for item in data:
            DataBase.insert(item)
        return 'data has been added!!'
    
    def read_data(self, DataBase):
        data = DataBase.all()
        return data
	
    def update_nodes(self, node):
        """ Updates the list of nodes on one node """
        self.nodes.append(node)
        self.add_data(data=self.nodes, DataBase=NODES)
        return self.nodes

    def create_block(self, proof, previous_hash):
        """ Used to make a block """
        if len(self.chain) > 0:
            self.new_transactions = []
            # decoy = self.add_false_transactions()
            if len(self.chain) > 0:
                for transaction in self.transactions:
                    hashed_sender = str(pbkdf2_sha256.hash(transaction['sender']))
                    hashed_sender = hashed_sender.replace('$pbkdf2-sha256$29000$', '')
                    hashed_receiver = str(pbkdf2_sha256.hash(transaction['receiver']))
                    hashed_receiver = hashed_receiver.replace('$pbkdf2-sha256$29000$', '')
                    sender_sign = ring_ct.ring_sign(blockchain=self.chain, primary_address=hashed_sender)
                    receiver_sign = ring_ct.ring_sign(blockchain=self.chain, primary_address=hashed_receiver)
                    amount = transaction['amount']
                    self.new_transactions.append({'sender': sender_sign, 'receiver':receiver_sign, 'amount':amount})
                
                self.transactions = self.new_transactions

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
        self.post_chain()
        return block
    

    def get_prev_block(self):
        """ get the previous block """
        return self.chain[-1]
    


    def post_chain(self):
        """ sends the new chain to all nodes """
        for node in self.nodes:
            chain = self.read_data(DB)
            json = {'blockchain':chain}
            url = r.post(f'http://{node}/insert_chain', json)
            url_status = url.status_code
            print(f"http://{node}/insert_chain   {url_status}")
        return 'chain is updated among all nodes'

    def update_chain(self, new_chain:list):
        """ Updates the chain """
        if len(new_chain) > len(self.chain):
            valid = self.is_chain_valid(chain=new_chain)
            if valid == True:
                self.add_data(data=self.chain)
                self.chain = new_chain
            return self.chain
        else:
            return self.chain

    def proof_of_work(self, previous_proof):
        """ This is used for mining """
        new_proof = 1
        check_proof = False
        algs.difficulty_increase(chain=self.chain, nodes=self.nodes)
        while check_proof is False:
            
            hash_op = hashlib.sha256(str(new_proof**2 -
             previous_proof**2).encode()).hexdigest()
            if hash_op[:algs.count] == algs.difficulty:
                check_proof = True
            else:
                new_proof += 1
        return new_proof 

    def add_false_transactions(self):
        """ Adds fake transactions """
        transactions = []
        decoy_transact = decoy_transactions.decoy_transactions(transactions=transactions)
        for decoy in decoy_transact:
            transactions.append(decoy)   
        return transactions

    def hash(self, block):
        """This is used to hash a block"""
        encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()


    def is_chain_valid(self, chain):
        """Checks if the chain is valid"""
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


    def add_miner_transaction(self, sender:str, receiver, amount:float):
        """ This is used to send or exchange currencies """
        self.transactions.append(
            {
                'sender': sender,
                'receiver': receiver,
                'amount': amount
            }
        )
        previous_block = self.get_prev_block()
        return previous_block['index'] + 1
    
    def add_non_miner_transaction(self, sender:str, receiver:str, amount:float):
        """ This is used to send or exchange currencies """
        if len(self.unconfirmed_transactions) < 5:
            self.unconfirmed_transactions.append(
            {
                'sender': sender,
                'receiver': receiver,
                'amount': amount
            }
        )
        else:
            for transaction in self.unconfirmed_transactions:
                

                # self.new_transactions.append({'sender': sender_sign, })
                self.transactions.append(transaction)
            # self.transactions = self.unconfirmed_transactions
            # if len(self.nodes) > 1:
                # for node in self.nodes:
                #     for transaction in self.transactions:
                #         r.post(f'https://{node}/add_transaction/', json=transaction)
            self.unconfirmed_transactions = []
        previous_block = self.get_prev_block()
        return previous_block['index'] + 1


    """ to prevent loops in the network when adding transactions """
    def add_unconfirmed_transaction(self, sender:str, receiver, amount:float):
        """ This is used to send or exchange currencies """
        if len(self.unconfirmed_transactions) < 5:
            self.unconfirmed_transactions.append(
            {
                'sender': sender,
                'receiver': receiver,
                'amount': amount
            }
        )
        else:
            # for transaction in self.unconfirmed_transactions:
            # self.transactions = self.unconfirmed_transactions
            if len(self.nodes) > 1:
                for node in self.nodes:
                    for transaction in self.unconfirmed_transactions:
                        full_transaction = {'sender': base64.encodebytes(transaction['sender'].encode()), 'receiver': base64.encodebytes(transaction['receiver'].encode()), 'amount': amount}
                        r.post(f'https://{node}/add_transaction/', json=full_transaction)
            self.unconfirmed_transactions = []
        previous_block = self.get_prev_block()
        return previous_block['index'] + 1






    #P2p nodes
    def show_nodes(self):
        """ This tests to see if there are nodes """
        return self.nodes 


    def add_node(self, address):
        """ This method adds a node to the network """
        # test = r.get(f'http://{address}/')
        # parsed_url = address
        # if test.status_code == 200:
        #     self.nodes.append(parsed_url)
        #     self.nodes = set(self.nodes)
        #     self.nodes = list(self.nodes)
        #     print(self.nodes)
        # else:
        #     return('invalid ip address/url')
        test = r.get(f'http://{address}/get_the_chain')
        if test.status_code == 200:
            for node in self.node:
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

        #algorithm for p2p
        """
        Get the chain and validity of the chain among the nodes
        Find the blockchain with the greatest length and replace the other chains
        """


    def replace_chain(self):
        """ This replaces the chain """
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
                    # length = json.loads(response.text)
                    # length = length['length']
                    length = response.json()['length']
                    chain = response.json()['blockchain']
                    if length > max_length and self.is_chain_valid(chain=chain):
                        max_length = length
                        longest_chain=chain
                if longest_chain:
                    if longest_chain != None:
                        if len(longest_chain) > len(self.chain):
                            self.chain = longest_chain
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