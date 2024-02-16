import dataclasses, data

@dataclasses.dataclass
class Player:
	money: int=0
	debt: int=0
	dead: bool=False
	def repay(self, repayment):
		return Player(self.money-repayment, self.debt-repayment)
	def add_money(self, amount):
		return Player(self.money+amount, self.debt)
	def die(self):
		return Player(money=0, debt=0, dead=True)
	def can_donate(self):
		return self.money-self.debt
	def can_borrow(self, settings):
		return settings.debt_loan(debt=settings.debt_limit-self.debt)
	def force(self, provinces, lands, index):
		return self.money-self.debt+sum(provinces[i].soldiers+lands[i].earnings*5 for i in range(len(provinces)) if provinces[i].ruler==index)
