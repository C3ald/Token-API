import socket
import requests as r
import os as os
import time as t
import threading
import passlib
from blockchain import Blockchain
chain = Blockchain()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
class Protocol:
	""" class for the Token protocol """
	def __init__(self):
		self.key = None
		self.blockchain = chain.chain

	def listen(self, host, port):
		s.bind((host, port))
		s.listen()
		conn, addr = s.accept()
