from dataclasses import dataclass

@dataclass
class Province:
	ruler: int=-1
	soldiers: int=0
	can_board: int=0
	def price(self, earnings):
		return self.soldiers+earnings
	def set_soldiers(self, count):
		return Province(self.ruler, count, self.can_board)
	def set_ruler(self, ruler):
		return Province(ruler, self.soldiers, self.can_board)
	def add_soldiers(self, count):
		return self.set_soldiers(self.soldiers+count)
	def restore_port(self, board_limit):
		return Province(self.ruler, self.soldiers, board_limit)
	def after_boarding(self, count):
		return Province(self.ruler, self.soldiers, self.can_board-count)
	def after_attack(self, attacker, soldiers):
		return self.set_ruler(attacker if soldiers>self.soldiers else self.ruler).set_soldiers(abs(self.soldiers+soldiers*(1 if self.ruler==attacker else -1)))