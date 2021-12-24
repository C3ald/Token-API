class Algs:
	""" algorithms for the blockchain """
	def __init__(self):
		self.difficulty = 0
		self.fee = 0.00001
		self.list_count = ['0','0','0','0','0','0']
		self.count = str(len(self.list_count))
		self.new_amount = 0
		self.amount = 1.63

	
	def difficulty_increase(self, chain:list, nodes):
		""" difficulty of a block """
		# i = 0
		# self.count = 0
		# self.list_count = []
		# self.difficulty = 0
		# chain_index = 0
		self.amount = self.amount_change(chain=chain)
		# if len(chain) > 1999:
		# 	while chain_index != len(chain):
		# 		if chain[i]['index'] % 2000 == 0:
		# 			self.amount_change(amount = self.amount)
		# 			if len(self.list_count) < 62:
		# 				self.list_count = self.list_count.append('0')
		# 				print('a')
		# 				return self.amount
		# 		if len(self.list_count) < 62:
		# 			i = i + 1
		# 			chain_index = chain_index + 1
		# 		else:
		# 			chain_index = len(chain) + 1

		# else:
		self.count = len(self.list_count)
		self.difficulty = "".join(self.list_count)
		return self.difficulty
		

	def network_fee(self, amount):
		""" the fee for transactions """
		self.fee = 0.00001
		self.new_amount = 0
		# self.fee = amount * self.fee
		self.new_amount = amount - self.fee
		return self.new_amount
	
	
	# def amount_change(self, amount, nodes, chain):
	def amount_change(self, chain):
		""" the change in block reward """
		if len(chain) > 2:
			i = 1
			transaction = chain [i]['transaction']
		# self.new_amount = 0
		# if len(chain) > 19999:
		# 	if len(chain) % 20000 == 0:
		# 		self.new_amount = amount / 2
		# 		if 0 < self.new_amount - (len(nodes) / 1000):
		# 			self.new_amount = self.new_amount - (len(nodes) / 1000)
		# self.amount = self.new_amount
			new_amount = 1.63
		# for block in chain:
		# 	for transaction in block:
			while i != len(chain):
				for data in transaction:
					new_amount = new_amount + self.fee
				i = i + 1
		else:
			new_amount = 1.63
		self.amount = new_amount
		return self.amount
	
