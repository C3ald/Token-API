from tinydb import TinyDB, Query
import random
# Make or use an existing file
db = TinyDB('blockchain.json')



def add_data(data):
	""" This adds data """
	item = data
	db.insert(data)
	return 'chain updated'


def read_data():
	""" reads the data in the database """
	data = db.all()
	return data
	