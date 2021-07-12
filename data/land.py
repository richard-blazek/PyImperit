from dataclasses import dataclass

@dataclass
class Land:
	name: str
	border: list
	neighbors: list
	earnings: int
	soldiers: int
	sea: bool
	@property
	def center(self):
		return [sum(p[i] for p in self.border)/len(self.border) for i in [0,1]]
	def border_with(self, another):
		return [pair for pair in zip(self.border, self.border[1:]+self.border[:1]) if pair[0] in another.border and pair[1] in another.border]