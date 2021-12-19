import requests as r
import time as t

wait = t.sleep(0.5)
class miner:
	""" The class for the miner """
	def mining(idel, publickey, privatekey, passphrase):
		""" the mining method it's self """
		start = input("would you like to start mining (y/n)?")
		if start == "y" or "yes" or "YES":
			info = r.get("http://localhost:8000/create_keys")
			block = r.post(f'http://localhost:8000/mining')
			if block.status_code == 200 and info.status_code == 200:
				while idel !=0:
					if block.status_code == 200:
						block = r.post('http://localhost:8000/mining', data={'publickey': publickey, 'privatekey': privatekey, 'passphrase': passphrase}) #you can change the ip of the node
						idel = idel - 0.000001
						print(f"new block is: {block}, type ctrl z, ctrl c to stop the program or wait for idel to equal 0")
					return block
			else:
				print("invalid response, become a node by visiting the github for Token or make sure your chain is running")
		elif start == "n" or "no" or 'NO':
			print("Mining will not start")
		else:
			print('invalid response')
		if idel == 0 or idel < 0:
			print(f'restart the program to mine again, the wallet containing the coins is: {info}')
miners = miner()
publickey = input('input your publickey: ')
privatekey = input('input your privatekey: ')
passphrase = input('input your passphrase: ')
miners.mining(idel=0.1, publickey=publickey, privatekey=privatekey, passphrase=passphrase)