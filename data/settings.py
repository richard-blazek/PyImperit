from dataclasses import dataclass
import math

@dataclass
class Settings:
	players: list
	colors: list
	is_human: list
	start_positions: list
	password: str
	interest_rate: float
	secession_probability_default: float
	default_money: int
	min_repayment: int
	debt_limit: int
	board_limit: int
	single_client: bool
	def loan_debt(self, amount_borrowed):
		return math.ceil(amount_borrowed*(1+self.interest_rate))
	def debt_loan(self, debt):
		return int(debt/(1+self.interest_rate))
	def loan_repayment(self, debt):
		return min(debt, debt//5+self.min_repayment)
	def secession_probability(self, prov):
	    return max(0, self.secession_probability_default-min(prov.soldiers, 80)/1000)
