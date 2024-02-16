class Provinces:
	def __init__(self, *provinces):
		self._prov=list(provinces)

	def __repr__(self):
		return 'Provinces('+','.join(repr(x) for x in self._prov)+')'
	def __getitem__(self, i):
		return self._prov[int(i)]
	def __len__(self):
		return len(self._prov)
	
	def alter(self, pairs):
		result=self._prov.copy()
		for pair in pairs:
			result[pair[0]]=pair[1]
		return Provinces(*result)
	
	def belonging_to(self, lands, ruler, sea=False):
		return [i for i in range(len(self._prov)) if self._prov[i].ruler==ruler and (sea or not lands[i].sea)]
	def restore_ports(self, board_limit):
		return self.alter((i, self._prov[i].restore_port(board_limit)) for i in range(len(self._prov)))