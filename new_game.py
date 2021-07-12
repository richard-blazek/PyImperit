import random, time
import data, file_load

random.seed(time.time())

def new_game(settings):
	lands=file_load.FileLoader('./static/lands.txt', scope={'Land': data.Land, 'Lands': data.Lands}).value
	bases={province: player for player, province in enumerate(random.sample(settings.start_positions, len(settings.players)))}
	players=[data.Player(money=settings.default_money, debt=0) for i in range(len(settings.players))]
	provinces=[data.Province(ruler=bases.get(i,-1), soldiers=(0 if land.sea else land.soldiers), can_board=settings.board_limit) for i, land in enumerate(lands)]
	file_load.FileLoader('./static/actions.txt').value=[]
	file_load.FileLoader('./static/history.txt').value=[]
	file_load.FileLoader('./static/playing.txt').value=0
	file_load.FileLoader('./static/settings.txt').value=settings
	file_load.FileLoader('./static/players.txt').value=data.Players(*players)
	file_load.FileLoader('./static/provinces.txt').value=data.Provinces(*provinces)
	file_load.FileLoader('./static/forces.txt').value=[[players[player].force(provinces, lands, player) for player in range(len(players))]]

if __name__=='__main__':
	new_game(data.Settings(**{key: eval(input(key+': ')) for key in data.Settings.__annotations__}))