import action, random, time

random.seed(time.time())

def is_enemy(p1, p2):
	return p1!=p2 and p1!=-1 and p2!=-1

def enemies_count(provinces, players, lands, settings, this, prov):
	return sum(provinces[i].soldiers for i in lands[prov].neighbors if is_enemy(provinces[i].ruler, this))

def check_sea(count, start_sea, dest_sea, can_board):
	return min(count, can_board) if not start_sea and dest_sea else count

def recruitments(provinces, players, lands, settings, this, soldiers, enemies, coming):
	result=[]
	money_remaining=players[this].money
	for land in soldiers:
		if soldiers[land]+coming[land]<enemies[land]<=soldiers[land]+coming[land]+money_remaining and not lands[land].sea:
			result.append(action.Recruit(this, land=land, count=enemies[land]-soldiers[land]-coming[land]))
			money_remaining-=result[-1].count
			coming[land]+=result[-1].count
	for land in soldiers:
		if money_remaining==0:
			break
		if soldiers[land]+coming[land]<80 and not lands[land].sea:
			result.append(action.Recruit(this, land=land, count=min(money_remaining, 80-soldiers[land]-coming[land])))
			coming[land]+=result[-1].count
			money_remaining-=result[-1].count
	if money_remaining>0:
		result.append(action.Recruit(this, land=random.choice([land for land in soldiers if not lands[land].sea]), count=money_remaining))
		coming[result[-1].land]+=money_remaining
	return result, soldiers, enemies, coming

def move(provinces, lands, result, this, start, dest, count):
	result.append(action.Attack(this, start, dest, count=check_sea(count, lands[start].sea, lands[dest].sea, provinces[start].can_board)))

def hopeless_attack(provinces, soldiers, enemies, coming, this, start, dest):
	return enemies[start]<soldiers[start]+coming[start] and is_enemy(provinces[dest].ruler, this)

def hopefull_attack(provinces, soldiers, enemies, coming, this, start, dest):
	return provinces[dest].soldiers+enemies[dest]<soldiers[start] and soldiers[start]+coming[start]>enemies[start]+enemies[dest]+(provinces[dest].soldiers if provinces[dest].ruler==-1 else 0)

def should_attack(provinces, lands, soldiers, enemies, coming, this, start, dest):
	return provinces[dest].ruler!=this and (hopeless_attack(provinces, soldiers, enemies, coming, this, start, dest) or hopefull_attack(provinces, soldiers, enemies, coming, this, start, dest))

def attacks(provinces, players, lands, settings, this, soldiers, enemies, coming):
	result=[]
	for start in soldiers:
		for dest in lands[start].neighbors:
			if should_attack(provinces, lands, soldiers, enemies, coming, this, start, dest):
				move(provinces, lands, result, this, start=start, dest=dest, count=min(soldiers[start], provinces[dest].soldiers+enemies[dest]+1))
				soldiers[start]-=result[-1].count
				if provinces[start].ruler!=-1 and result[-1].count>=provinces[dest].soldiers:
					for n in lands[dest].neighbors:
						if provinces[n].ruler==this:
							enemies[n]-=provinces[dest].soldiers
	return result, soldiers, enemies, coming

def transport(provinces, lands, result, this, soldiers, coming, start, dest, count):
	move(provinces, lands, result, this, start, dest, count)
	soldiers[start]-=result[-1].count
	coming[dest]+=result[-1].count

def spread_soldiers(provinces, players, lands, settings, this, soldiers, enemies, coming):
	result=[]
	for start in soldiers:
		for dest in random.sample(lands[start].neighbors, len(lands[start].neighbors)):
			if provinces[dest].ruler==this:
				if enemies[start]<=0<enemies[dest]:
					transport(provinces, lands, result, this, soldiers, coming, start=start, dest=dest, count=soldiers[start])
				elif enemies[start]<=0 and enemies[dest]<=0:
					transport(provinces, lands, result, this, soldiers, coming, start=start, dest=dest, count=soldiers[start]//max(len(lands[start].neighbors)-1, 1))
				elif soldiers[start]+coming[start]-enemies[start]>0 and soldiers[start]+coming[start]-enemies[start]>=soldiers[dest]+coming[dest]-enemies[dest]:
					transport(provinces, lands, result, this, soldiers, coming, start=start, dest=dest, count=min(soldiers[start]+coming[start]-enemies[start], soldiers[start]))
	return result, soldiers, enemies, coming

def think(provinces, players, lands, settings, this):
	soldiers={i: provinces[i].soldiers for i in provinces.belonging_to(lands, this, sea=True)}
	enemies=[enemies_count(provinces, players, lands, settings, this, land) for land in range(len(lands))]
	coming={land: 0 for land in soldiers}
	result1, soldiers, enemies, coming=recruitments(provinces, players, lands, settings, this, soldiers, enemies, coming)
	result2, soldiers, enemies, coming=attacks(provinces, players, lands, settings, this, soldiers, enemies, coming)
	result3, soldiers, enemies, coming=spread_soldiers(provinces, players, lands, settings, this, soldiers, enemies, coming)
	return result1+result2+result3