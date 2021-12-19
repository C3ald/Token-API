import requests as r

API = 'https://token-network.herokuapp.com/'


class Lexar: 
    def __init__(self):
        self.transactionurl = r.post(f'{API}add_transaction', data=self.data)
        self.data = None
        self.key_words = []
    
    def complete_action(self, publickey, privatekey, passphrase):
        data = {'sender_publickey':publickey, 'sender_privatekey':privatekey, 'sender_passphrase':passphrase, 'reciever_publickey': 'network'}
        self.transactionurl
        return self.transactionurl
    
    
    
class KeyWards:
    
    def __init__(self):
        pass
    
