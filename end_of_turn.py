import random, time
import data

random.seed(time.time())

def earn_money(provinces, player, lands, settings, i):
	return player.add_money(lands.total_earnings(provinces.belonging_to(lands, i)))

def repay_debt(provinces, player, lands, settings, i):
	return player.repay(settings.loan_repayment(player.debt))

def seize_provinces(provinces, player, lands, settings, i):
	seizurable=provinces.belonging_to(lands, i, sea=True)
	remaining=random.choice(seizurable)
	return provinces.alter((prov_i, provinces[prov_i].set_ruler(-1).set_soldiers(lands[prov_i].default_soldiers)) for prov_i in seizurable if prov_i!=remaining), data.Player(), [dict(type='seizure', player=i, land_count=len(seizurable)-1)]

def repay_or_seize(provinces, player, lands, settings, i):
	return seize_provinces(provinces, player, lands, settings, i) if settings.loan_repayment(player.debt)>player.money else (provinces, repay_debt(provinces, player, lands, settings, i), [])

def financial_operations(provinces, player, lands, settings, i):
	return repay_or_seize(provinces, earn_money(provinces, player, lands, settings, i), lands, settings, i)

def detached_provinces(provinces, player, lands, settings, remaining, playing):
	return (i for i,prov in enumerate(provinces) if i!=remaining and prov.ruler==playing and not lands[i].sea and random.random()<settings.secession_probability(prov))

def do_secessions(provinces, player, lands, settings, playing, detached):
	return provinces.alter((prov_i, data.Province(-1, lands[prov_i].soldiers, settings.board_limit)) for prov_i in detached), [dict(type='secession', player=playing, land=prov_i) for prov_i in detached]

def secession(provinces, player, lands, settings, playing):
	return do_secessions(provinces, player, lands, settings, playing, detached_provinces(provinces, player, lands, settings, random.choice(provinces.belonging_to(lands, playing) or [-1]), playing))

def perform_actions(provinces, players, lands, settings, actions):
	for action in actions:
		provinces, players=action.after_turn(provinces, players, lands, settings)
	return provinces, players

def is_dead(provinces, lands, index):
	return sum(provinces[i].soldiers+lands[i].earnings for i in provinces.belonging_to(lands, index, sea=True))<=0

def dying_players(provinces, lands, players):
	return [i for i in range(len(players)) if is_dead(provinces, lands, i) and not players[i].dead]

def perform_deaths(players, dying):
	return players.alter((i, players[i].die()) for i in dying), [dict(type='death', player=i) for i in dying if not players[i].dead]

def check_deaths(provinces, players, lands, settings):
	return perform_deaths(players, dying_players(provinces, lands, players))

def compute_forces(provinces, players, lands, settings):
	return [player.force(provinces, lands, i) for i,player in enumerate(players)]

def end_of_turn(provinces, players, lands, settings, actions, i):
	provinces, players=perform_actions(provinces, players, lands, settings, actions)
	provinces, player, history1=financial_operations(provinces, players[i], lands, settings, i)
	provinces, history2=secession(provinces, player, lands, settings, i)
	players, history3=check_deaths(provinces, players.alter([(i,player)]), lands, settings)
	return provinces.restore_ports(settings.board_limit), players, history1+history2+history3, compute_forces(provinces, players, lands, settings)