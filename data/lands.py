class Lands:
	def __init__(self, *lands):
		self._lands=list(lands)
	def __getitem__(self, i):
		return self._lands[int(i)]
	def __len__(self):
		return len(self._lands)
	
	def total_earnings(self, indices):
		return sum(self[i].earnings for i in indices)
	def move_is_boarding(self, start, dest):
		return not self[start].sea and self[dest].sea