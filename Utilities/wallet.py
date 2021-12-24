# from Crypto.PublicKey.RSA import generate
from passlib.hash import pbkdf2_sha256
# from blockchain import Blockchain
# blockchain = Blockchain
import secrets
import random
import string
import requests as r
# from Crypto.PublicKey import RSA, ECC
# from Crypto import Random

class Wallet:
    """ the 'brains' for wallets """
    def __init__(self):
        """ the declaring of variables like the public and privatekey """
        self.publickey = 0
        self.privatekey = 0
        self.balance = 0
        self.keyfile = 0
        self.verify = False
        self.verify1 = False
        self.bits = secrets.randbits(256)
        self.passwd = 0
        self.result = None
        self.phrase = "nothing"
        self.view_key = None
        

    def recover_wallet_with_passphrase(self, passphrase, blockchain):
        """ recover wallet with the passphrase and publickey """
        self.privatekey = pbkdf2_sha256.hash(str(passphrase))
        self.verify = False
        i = 0
        while i != len(blockchain):
            for transaction in blockchain.chain[i]['transactions']:
                publickey = transaction['sender']
                self.verify = pbkdf2_sha256.verify(self.privatekey, publickey)
                if self.verify == True:
                    self.publickey = publickey
                    return True
                else:
                    publickey = transaction['receiver']
                    self.verify = pbkdf2_sha256.verify(self.privatekey, publickey)
                    if self.verify == True:
                        self.publickey = publickey
                        return True
                i = i + 1


    # def view_wallet(self, publickey, privatekey):
    #     """ allows you to see your wallet """
    #     self.checkbalance(publickey=publickey)
    #     response = {"your public key":publickey, "your private key":privatekey, "your balance is": self.balance}
    #     return response
    
     
    # def make_privatekey(self, phrase):
    #     """ makes the private key """
    #     privatekey = pbkdf2_sha256.hash(phrase)
    #     # privatekey = bits_hex[2:]
    #     return privatekey
    
    # def make_publickey(self):
    #     """ makes the public key """
    #     publickey = pbkdf2_sha256.hash(self.privatekey)
    #     return publickey


    def make_wallet(self, password):
        """ makes the wallet """
        # password = self.password()
        # self.phrase = self.passwd
        self.privatekey = pbkdf2_sha256.hash(str(password))
        self.publickey = pbkdf2_sha256.hash(str(self.privatekey))
        self.privatekey = self.privatekey.replace('$pbkdf2-sha256$29000$', '')
        self.publickey = self.publickey.replace('$pbkdf2-sha256$29000$', '')
        if self.view_key == None:
            self.view_key = pbkdf2_sha256.hash(str(password))
            self.view_key = self.view_key.replace('$pbkdf2-sha256$29000$', '')
        return {'publickey': self.publickey, 'privatekey': self.privatekey, 
                'phrase': password, 'viewkey': self.view_key}
    
    def password(self):
        # choose from all letters, numbers, and special characters
        characters = string.ascii_letters + string.punctuation  + string.digits
        self.passwd =  "".join(random.choice(characters) for x in range(70))
        return str(self.passwd)
    
    def verify_wallet(self, privatekey:str, publickey:str):
        """ verifies the wallet """
        self.verify = False
        # self.verify1 = False
        self.verify = pbkdf2_sha256.verify(f'$pbkdf2-sha256$29000${privatekey}', f'$pbkdf2-sha256$29000${publickey}')
        # self.verify1 = pbkdf2_sha256.verify(phrase, privatekey)
        if  self.verify == True:
            return True
        else:
            return False
    
    def check_nodes(self, nodes, publickey, blockchain):
        mainbalace = 0
        i = 0
        o = 1
        for node in nodes:
            node1 = node[i]
            node2 = node[o]
            chain1 = r.get(f'{node1}/get_the_chain').json()
            chain1 = chain1['blockchain']
            chain2 = r.get(f'{node2}/get_the_chain').json()
            chain2 = chain2['blockchain']
            valid1 = blockchain.is_chain_valid(chain=chain1)
            valid2 = blockchain.is_chain_valid(chain=chain2)
            if i < len(nodes):
                i = i + 1
            if o < len(nodes):
                o = o + 1
            if valid1 == True:
                balance1 = self.checkbalance(publickey=publickey, chain=chain1)

            if valid2 == True:
                balance2 = self.checkbalance(publickey=publickey, chain=chain2)
            if valid1 == False:
                balance1 = 0
            if valid2 == False:
                balance2 = 0

            if balance1 > balance2 or mainbalace < balance1:
                mainbalace = balance1
            
            if balance2 > balance1 or mainbalace < balance2:
                mainbalace = balance2
        
        self.balance = mainbalace
        return mainbalace


    def checkbalance(self, viewkey, chain):
        """ checks the balance of a wallet using the view key """
        self.balance = 0
        # i = 1
        # io = 0
        # for x in chain:
        #     print(x)
        #     io = 0
        #     if 2 > len(chain) and self.balance == 0:
        #         print ("chain is empty")
        #         return "chain is empty"
            
        #     elif chain[i] ['data'] [io] ['receiver'] != publickey:
        #         io = io + 1


        #     elif chain[i]["data"] [io] ['receiver'] == publickey:
        #         amount = float(chain[i]["data"] [io] ['amount'])
        #         self.balance = self.balance + amount
        #         io = io + 1

        #     elif chain[i]["data"] [io] ['sender'] == publickey:
        #         amount = float(chain[i]["data"][io]['amount'])
        #         self.balance = self.balance - amount
        #         io = io + 1
                
        #     elif i > len(chain):
        #         return self.balance

        #     else:
        #         i = i + 1
        i = 1
        ii = 0
        stealth_addresses = []
        while i != len(chain):
            for transaction in chain[i]['data']:
                if self.verify_wallet(privatekey=viewkey, publickey=transaction['receiver']) == True:
                    for address in stealth_addresses:
                        if address != transaction['receiver'] or address != transaction['sender']:
                            stealth_addresses.append(transaction['receiver'])
                            self.balance = transaction[ii]['amount'] + self.balance
                        #     unused = True
                        # else:
                        #     unused = False
                        
                
                if  self.verify_wallet(privatekey=viewkey, publickey=transaction['sender']) == True:
                    for address in stealth_addresses:
                        if address != transaction['sender'] or address != transaction['receiver']:
                            stealth_addresses.append(transaction['sender'])
                            self.balance = self.balance - transaction['amount']
                
            #     ii = ii + 1
            i = i + 1
            
    # def generate_rsa_keys(self):
    #     """ Generate RSA Keys """ 
    #     random_gen = Random.new().read
    #     key = RSA.generate(2048, random_gen)
    #     private_key = key.export_key(format='PEM', passphrase=b'self.phrase').decode('utf-8')
    #     public_key = key.public_key().export_key().decode('utf-8')
    #     self.result = OrderedDict(private_key=private_key, public_key=public_key, passphrase=self.phrase)
    #     # private_key = binascii.hexlify(key.exportKey(format='DER')).decode('utf-8')
    #     # public_key = binascii.hexlify(key.public_key().exportKey(format='DER')).decode('utf-8')
    #     # result = OrderedDict(private_key=private_key, public_key=public_key)
    #     return self.result

    # def generate_ecc_keys(self):
    #     """ Generate ECC keys """
    #     key = ECC.generate(curve='secp256r1')
    #     self.privatekey = binascii.hexlify(key.export_key(format='DER')).decode('utf-8')
    #     self.privatekey = str(self.privatekey)
    #     self.publickey = binascii.hexlify(key.public_key().export_key(format="DER")).decode('utf-8')
    #     self.publickey = str(self.publickey)
    #     self.result = OrderedDict(private_key=self.privatekey, public_key=self.publickey)
    #     self.result = dict(self.result)
    #     return self.result
    
    # @staticmethod
    # def verify_ecc_key(privatekey:str, publickey:str):
    #     """ verifies the ECC keys """
    #     priv_key = ECC.import_key(bytes(privatekey))
    #     pub_key = ECC.import_key(bytes(publickey))
    #     key = [priv_key, pub_key]
    #     return key

    def create_stealth_addr(self, chain, password, publickey, privatekey):
        """ Generates one time use keys """
        # self.privatekey = pbkdf2_sha256.hash(str(password))
        # self.publickey = pbkdf2_sha256.hash(str(self.privatekey))
        # self.privatekey = self.privatekey.replace('$pbkdf2-sha256$29000$', '')
        # self.publickey = self.publickey.replace('$pbkdf2-sha256$29000$', '')
        i = 1
        # ii = 0
        transactions = chain[i]['data']
        for transaction in transactions:
            receiver = transaction['receiver']
            sender = transaction['sender']
            if receiver == publickey or pbkdf2_sha256.hash(f'$pbkdf2-sha256$29000${privatekey}',f'$pbkdf2-sha256$29000${receiver}') == True:
                new_wallet = self.make_wallet(password)
                return new_wallet
            
            if sender == publickey or pbkdf2_sha256.hash(f'$pbkdf2-sha256$29000${privatekey}',f'$pbkdf2-sha256$29000${sender}') == True:
                new_wallet = self.make_wallet(password)
                return new_wallet
            
            else:
                return'keys have not been used'
        # return {'publickey': self.publickey, 'privatekey': self.privatekey, 'phrase': self.phrase}



if __name__ == '__main__':
    keychain = Wallet()
    password = keychain.password()
    data = keychain.make_wallet(password)
    print(data)
    valid = keychain.verify_wallet(privatekey=(data['privatekey']), publickey=(data['publickey']))
    print(valid)
