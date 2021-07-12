class Players:
	def __init__(self, *players):
		self._pl=list(players)
	
	def __repr__(self):
		return 'Players('+','.join(repr(x) for x in self._pl)+')'
	def __getitem__(self, i):
		return self._pl[int(i)]
	def __len__(self):
		return len(self._pl)
	
	def alter(self, pairs):
		result=self._pl.copy()
		for pair in pairs:
			result[pair[0]]=pair[1]
		return Players(*result)
	
	def transfer_money(self, donor, beneficiary, amount):
		return self.alter([(donor, self[donor].add_money(-amount)), (beneficiary, self[beneficiary].add_money(amount))])