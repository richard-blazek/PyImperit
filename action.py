import data, dataclasses

@dataclasses.dataclass
class Action:
	player: int
	def do(self, provinces, players, lands, settings):
		return (*self._do(provinces, players, lands, settings), True) if self._possible(provinces, players, lands, settings) else (provinces, players, False)
	def after_turn(self, provinces, players, lands, settings):
		return provinces, players

@dataclasses.dataclass
class Borrow(Action):
	amount: int
	def _possible(self, provinces, players, lands, settings):
		return players[self.player].debt<=players[self.player].can_borrow(settings)
	def _do(self, provinces, players, lands, settings):
		return provinces, players.alter([(self.player, data.Player(money=players[self.player].money+self.amount, debt=players[self.player].debt+settings.loan_debt(self.amount)))])

@dataclasses.dataclass
class Donate(Action):
	beneficiary: int
	amount: int
	def _possible(self, provinces, players, lands, settings):
		return self.amount<=players[self.player].can_donate()
	def _do(self, provinces, players, lands, settings):
		return provinces, players.transfer_money(self.player, self.beneficiary, self.amount)

@dataclasses.dataclass
class Buy(Action):
	land: int
	def _possible(self, provinces, players, lands, settings):
		return players[self.player].money>=provinces[self.land].price(lands[self.land].earnings) and [1 for i in lands[self.land].neighbors if provinces[i].ruler==self.player and not lands[i].sea] and not lands[self.land].sea
	def _do(self, provinces, players, lands, settings):
		return provinces.alter([(self.land, provinces[self.land].set_ruler(self.player).set_soldiers(0))]), players.alter([(self.player, players[self.player].add_money(-provinces[self.land].price(lands[self.land].earnings)))])

@dataclasses.dataclass
class Recruit(Action):
	land: int
	count: int
	def _possible(self, provinces, players, lands, settings):
		return provinces[self.land].ruler==self.player and players[self.player].money>=self.count and not lands[self.land].sea
	def _do(self, provinces, players, lands, settings):
		return provinces, players.alter([(self.player, players[self.player].add_money(-self.count))])
	def after_turn(self, provinces, players, lands, settings):
		return provinces.alter([(self.land, provinces[self.land].add_soldiers(self.count))]), players


@dataclasses.dataclass
class Attack(Action):
	start: int
	destination: int
	count: int
	def _possible(self, provinces, players, lands, settings):
		return provinces[self.start].ruler==self.player and provinces[self.start].soldiers>=self.count and self.destination in lands[self.start].neighbors and (not lands[self.destination].sea or lands[self.start].sea or self.count<=provinces[self.start].can_board)
	def _do(self, provinces, players, lands, settings):
		return provinces.alter([(self.start, provinces[self.start].add_soldiers(-self.count).after_boarding(self.count if lands.move_is_boarding(self.start, self.destination) else 0))]), players
	def after_turn(self, provinces, players, lands, settings):
		transfer_money=self.count>provinces[self.destination].soldiers and self.player!=provinces[self.destination].ruler and not lands[self.destination].sea and provinces[self.destination].ruler!=-1
		return provinces.alter([(self.destination, provinces[self.destination].after_attack(self.player, self.count))]), players.transfer_money(provinces[self.destination].ruler, self.player, (players[provinces[self.destination].ruler].money//max(len(provinces.belonging_to(lands, provinces[self.destination].ruler)), 1) if transfer_money else 0))