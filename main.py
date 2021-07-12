import flask, file_load, route, new_game, os, random, time
import data, action, player_ai
from end_of_turn import end_of_turn, perform_actions

app=flask.Flask(__name__)
app.secret_key=os.urandom(16)
random.seed(time.time())

provinces_file=file_load.FileLoader('./static/provinces.txt', scope={'Province': data.Province, 'Provinces': data.Provinces})
players_file=file_load.FileLoader('./static/players.txt', scope={'Player': data.Player, 'Players': data.Players})
playing_file=file_load.FileLoader('./static/playing.txt')
actions_file=file_load.FileLoader('./static/actions.txt', scope={key: action.__getattribute__(key) for key in dir(action)})
history_file=file_load.FileLoader('./static/history.txt', scope={key: action.__getattribute__(key) for key in dir(action)})
forces_file=file_load.FileLoader('./static/forces.txt')

def load_settings():
	global settings, lands
	settings=file_load.FileLoader('./static/settings.txt', scope={'Settings': data.Settings}).value
	lands=file_load.FileLoader('./static/lands.txt', scope={'Land': data.Land, 'Lands': data.Lands}).value

app.jinja_env.trim_blocks=True
app.jinja_env.lstrip_blocks=True
app.jinja_env.globals.update(type=type)

load_settings()

#Web---------------------------------------------------------------------------
@app.route('/')
def index():
	if 'user' in flask.session:
		return flask.render_template('game.html', players=players_file.value, playing=playing_file.value, provinces=provinces_file.value, user=int(flask.session['user']), lands=lands, settings=settings, next_shown=False)
	return flask.render_template('index.html', players=players_file.value, playing=playing_file.value, settings=settings)

@app.route('/navod')
def navod():
	return flask.render_template('help.html', settings=settings)

@app.route('/history')
def history():
	return flask.render_template('history.html', settings=settings, history=history_file.value, players=players_file.value, provinces=provinces_file.value, lands=lands, **{key: action.__getattribute__(key) for key in dir(action)})

@app.route('/graf')
def diagram():
	return flask.render_template('diagram.html', settings=settings, forces=forces_file.value, players=players_file.value)

@app.errorhandler(404)
def not_found(e):
	return flask.redirect(flask.url_for('index'))

@route.post(app, '/click-on', lambda:'', dest=int, start=int)
def click_on(dest, start):
	provinces, players, user=provinces_file.value, players_file.value, int(flask.session.get('user', '-1'))
	if user==playing_file.value:
		if start==dest and provinces[dest].ruler==user and not lands[dest].sea:
			return flask.render_template('recruitment.html', lands=lands, provinces=provinces, i=dest, players=players, user=user)
		if start!=-1 and provinces[start].ruler==user and dest in lands[start].neighbors:
			return flask.render_template('attack.html', lands=lands, provinces=provinces, start=start, destination=dest)
		if provinces[dest].ruler==-1 and not lands[dest].sea:
			return flask.render_template('buy.html', lands=lands, i=dest, price=provinces[dest].price(lands[dest].earnings), players=players, user=user)

@app.route('/want-to-borrow')
def want_to_borrow():
	return flask.render_template('loan.html', player=players_file.value[int(flask.session.get('user', '-1'))], settings=settings)

@app.route('/want-to-donate/<int:player>')
def want_to_donate(player):
	return flask.render_template('donation.html', settings=settings, beneficiary=player, players=players_file.value, user=int(flask.session.get('user', '-1')))

@route.post(app, '/login', lambda:flask.redirect(flask.url_for('index')), pw=str, player=int)
def login(pw, player):
	if pw==settings.password:
		flask.session['user']=str(player)
		return flask.redirect(flask.url_for('index'))

@route.post(app, '/logout', lambda:flask.redirect(flask.url_for('index')))
def logout():
	flask.session.pop('user', None)

def perform_action(action):
	provinces_file.value, players_file.value, done=action.do(provinces_file.value, players_file.value, lands, settings)
	if done:
		actions_file.value=actions_file.value+[action]
		history_file.value=history_file.value+[action]

@route.post(app, '/borrow', lambda:flask.redirect(flask.url_for('index')), amount=int)
def borrow(amount):
	user=int(flask.session.get('user', '-1'))
	if user>=0:
		perform_action(action.Borrow(user, amount))

@route.post(app, '/donate', lambda:flask.redirect(flask.url_for('index')), amount=int, beneficiary=int)
def donate(amount, beneficiary):
	user=int(flask.session.get('user', '-1'))
	if user>=0:
		perform_action(action.Donate(user, beneficiary, amount))

@route.post(app, '/buy', lambda:flask.redirect(flask.url_for('index')), land=int)
def buy(land):
	user=int(flask.session.get('user', '-1'))
	if user==playing_file.value:
		perform_action(action.Buy(user, land))

@route.post(app, '/recruit', lambda:flask.redirect(flask.url_for('index')), land=int, count=int)
def recruit(land, count):
	user=int(flask.session.get('user', '-1'))
	if user==playing_file.value:
		perform_action(action.Recruit(user, land, count))

@route.post(app, '/attack', lambda:flask.redirect(flask.url_for('index')), start=int, destination=int, count=int)
def attack(start, destination, count):
	user=int(flask.session.get('user', '-1'))
	if user==playing_file.value:
		perform_action(action.Attack(user, start, destination, count))

@route.post(app, '/shownext', lambda:flask.redirect(flask.url_for('index')))
def show_next():
	user=int(flask.session.get('user', '-1'))
	playing=playing_file.value
	if user==playing:
		provinces, players=perform_actions(provinces_file.value, players_file.value, lands, settings, actions_file.value)
		return flask.render_template('game.html', players=players, playing=playing_file.value, provinces=provinces, user=int(flask.session['user']), lands=lands, settings=settings, next_shown=True)

def use_ai():
	new_actions=player_ai.think(provinces_file.value, players_file.value, lands, settings, playing_file.value)
	for a in new_actions:
		perform_action(a)

def living_players(players, first):
	return ((i+first)%len(players) for i in range(len(players)) if not players[(i+first)%len(players)].dead)

@route.post(app, '/next', lambda:flask.redirect(flask.url_for('index')))
def next_turn():
	user=int(flask.session.get('user', '-1'))
	playing=playing_file.value
	if user==playing:
		while True:
			provinces, players, history, forces, actions=provinces_file.value, players_file.value, history_file.value, forces_file.value, actions_file.value
			provinces, players, new_history, new_forces=end_of_turn(provinces, players, lands, settings, actions, playing)
			playing=next(living_players(players, first=playing+1), user)
			provinces_file.value, players_file.value, history_file.value, forces_file.value, playing_file.value, actions_file.value=provinces, players, history+new_history, forces+[new_forces], playing, []
			if settings.is_human[playing]:
				break
			use_ai()
			user=playing
	if settings.single_client:
	    flask.session['user']=str(playing)

@app.route('/admin')
def admin():
	return flask.render_template('admin.html', settings_repr=repr(settings))

@route.post(app, '/newgame', lambda:flask.redirect(flask.url_for('index')), settings=str, pw=str)
def newgame(new_settings, pw):
	if file_load.FileLoader('./static/admin_pw.txt').value==pw:
		new_game.new_game(eval(new_settings, {'Settings': data.Settings}))
		load_settings()
