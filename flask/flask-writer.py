from random import choice
from os import path, environ
from service_modules import SportsRadarGame, SportsRadarService, SheetScribeService, FakeGameGenerator
from flask import Flask, render_template, request, session

#@ToDo: Force max col width of 80
#@ToDo: rename templates to something more fitting
#@ToDo: Rename flask-writer to YASSP (yet another score storing program)
#@ToDo: Comment on ALL THE THINGS
#@ToDo: Imlement reading back of scores

SCRIPT_DIR = path.dirname(path.abspath(__file__))

SPORTSRADAR_KEY_PATH = path.join(SCRIPT_DIR, 'sports-radar-api-key')
SPORTSRADAR_API_KEY = open(SPORTSRADAR_KEY_PATH, "r").read().rstrip("\n\r")

PHRASES_PATH = path.join(SCRIPT_DIR, 'phrases')
PHRASES_FILE = open(PHRASES_PATH, "r")
PHRASES = [line for line in PHRASES_FILE.read().split("\n")]

FLASK_APP = Flask(__name__)
SCOPE = "https://www.googleapis.com/auth/spreadsheets"

remote = False
if "LOCATION" in environ:
	if environ['LOCATION'] == "remote":
		remote = True

if __name__ == "__main__":
	FLASK_APP.run(debug=True)

FLASK_APP.secret_key = 'hunter2'

def render_from_fake_games(sheet_id, sheet_name, season, week):

	#@ToDo: Move writing names and ranks into /football_post function

	scribe    = SheetScribeService(sheet_id, SCOPE, None)
	sub_sheet = sheet_name

	#We need to wreck our sheet's A-C and E-G
	#columns to make way for new info, but not
	#D or H because we want to check for values there
	for column in ['A', 'B', 'C', 'E', 'F', 'G']:
		#Check for fidelity
		try:
			scribe.clear_column_values(sheet_name,
									   '%s3:%s1000' %
									   (column, column)
									   )
		except HttpError as e:
			return render_template('error.html',
									remote=remote,
									scribe=true,
									instance=scribe,
									error=e
									)

	away_already_there = None
	home_already_there = None
	try:
		away_already_there = scribe.get_range_values(sub_sheet, "D3:D250")
		home_already_there = scribe.get_range_values(sub_sheet, "H3:H250")
		scribe.clear_column_values(sheet_name,'H3:H1000')
	except HttpError as e:
		return render_template('error.html',
								remote=remote,
								scribe=true,
								instance=scribe,
								error=e
								)

	fake_games = []
	away_ranks = []
	away_teams = []
	home_ranks = []
	home_teams = []

	if not(scribe.auth):
		return render_template('error.html',
								remote=remote,
								scribe=true,
								instance=scribe,
								error="returned: %s" % (scribe.auth)
								)
	i = 0
	game_instance = FakeGameGenerator()
	while game_instance.RANKS != []:

		info = {}

		game_instance.generate_new_fake_game()

		# if there were vals in the sheet already, sub them in
		if away_already_there != 0 and away_already_there[i] != "":
			game_instance.away_points = int(away_already_there[i][0])

		if home_already_there != 0 and home_already_there[i] != "":
			game_instance.home_points = int(home_already_there[i][0])

		#ToDo: If game_instance.isImportant it must be a bowl game
		#we need to pass the title into our flask.html to signify this
		if (game_instance.isRanked) or (game_instance.isImportant):
			info['away_team'] = game_instance.away_team
			info['home_team'] = game_instance.home_team
			info['awayRank'] = game_instance.awayRank
			info['homeRank'] = game_instance.homeRank
			info['away_points'] = game_instance.away_points
			info['home_points'] = game_instance.home_points
			info['gameTime'] = game_instance.gameTime
			info['gameStatus'] = game_instance.gameStatus
			fake_games.append(info)

			away_ranks.append(game_instance.awayRank)
			away_teams.append(game_instance.away_team)
			home_ranks.append(game_instance.homeRank)
			home_teams.append(game_instance.home_team)
			i += 1

	#wrap our payloads for google sheets
	away_ranks_payload = [away_ranks]
	away_teams_payload = [away_teams]
	home_ranks_payload = [home_ranks]
	home_teams_payload = [home_teams]

	#since we made it this far, we probably
	#don't need a fidelity check
	scribe.write_column_range_values(sub_sheet, 'B3', away_ranks_payload)
	scribe.write_column_range_values(sub_sheet, 'C3', away_teams_payload)
	scribe.write_column_range_values(sub_sheet, 'F3', home_ranks_payload)
	scribe.write_column_range_values(sub_sheet, 'G3', home_teams_payload)

	#increment our counters for fun stats in post.html
	session['google_sheets_api_calls'] += scribe.apiCalls

	return render_template('flask.html',
		seq=fake_games,
		remote=remote,
		phrase=choice(PHRASES),
		sheet_id_truncated=sheet_id[0:7] + "...",
		sub_sheet=sheet_name,
		season=season,
		week=week
		)

def render_from_real_games(sheet_id, sheet_name, season, week):

	#@ToDo Move writing names and ranks into /football_post function

	scribe    = SheetScribeService(sheet_id, SCOPE, None)
	sub_sheet = sheet_name

	#We need to wreck our sheet's A-H
	#columns to make way for new info
	for column in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
		#Check for fidelity
		try:
			scribe.clear_column_values(sheet_name, '%s3:%s1000' % (column, column))
		except HttpError:
			#@ToDo: Proper error_sheet.html
			return "<h1>Request spreadsheet entity %s or sub_sheet %s not found.</h1>" % (sheet_id, sheet_name)

	#Assuming scribe service didn't bail, let's grab the games
	radar_service = SportsRadarService(SPORTSRADAR_API_KEY)
	games         = radar_service.get_games(season, week)
	ranks         = radar_service.get_ranks(season, week)

	real_games = []
	away_ranks = []
	away_teams = []
	home_ranks = []
	home_teams = []

	if not(games):
		#@ToDo: Proper error_sheet.html
		return "Radar Service Module returned with: %s. Go back to setup." % (str(games))

	for game in games:

		game_instance = SportsRadarGame(game, radar_service.ranks)

		#ToDo: If game_instance.isImportant it must be a bowl game
		#we need to pass the title into our flask.html to signify this
		if (game_instance.isRanked) or (game_instance.isImportant):
			#passing the whole real_games list into
			#flask.html means that we need to parse it there
			#and not here, saving us a bunch of time
			real_games.append(game_instance)

			away_ranks.append(game_instance.awayRank)
			away_teams.append(game_instance.away_team)
			home_ranks.append(game_instance.homeRank)
			home_teams.append(game_instance.home_team)

	#wrap our payloads for google sheets
	away_ranks_payload = [away_ranks]
	away_teams_payload = [away_teams]
	home_ranks_payload = [home_ranks]
	home_teams_payload = [home_teams]

	#since we made it this far, we probably
	#don't need a fidelity check
	scribe.write_column_range_values(sheet_name, 'B3', away_ranks_payload)
	scribe.write_column_range_values(sheet_name, 'C3', away_teams_payload)
	scribe.write_column_range_values(sheet_name, 'F3', home_ranks_payload)
	scribe.write_column_range_values(sheet_name, 'G3', home_teams_payload)

	#increment our counters for fun stats in post.html
	session['google_sheets_api_calls'] += scribe.apiCalls
	session['sportsradar_api_calls']   += radar_service.apiCalls

	return render_template('flask.html',
		seq=real_games,
		remote=remote,
		phrase=choice(PHRASES),
		sheet_id_truncated=sheet_id[0:7] + "...",
		sub_sheet=sheet_name,
		season=season,
		week=week
		)


@FLASK_APP.route("/")
def init():
	#@ToDo: Proper Startup template
	return "<h1>running</h1>"

@FLASK_APP.route("/")
@FLASK_APP.route("/setup/")
def setup_flask():
	return render_template('setup.html', remote=remote)

@FLASK_APP.route("/")
@FLASK_APP.route("/ncaa-football/", methods=['GET', 'POST'])
def flask_post():

	#@ToDo: Super secret password check for now

	if request.method == "POST":

		#collect and use the session table to cache our info
		#we will need this later for the flask response
		sheet_id   = request.form['SPREADSHEETID']
		sheet_name = request.form['SHEETNAME']
		season     = request.form['SEASON']
		week       = request.form['WEEK']

		session["sheet_id"]   = sheet_id
		session["sheet_name"] = sheet_name
		session['google_sheets_api_calls'] = 0
		session['sportsradar_api_calls']   = 0

		#print('Posted - ID: %s, Name: %s, Season: %s, Week: %s.' % (sheet_id, sheet_name, season, week))

		if 'FAKEGAMES' in request.form:
			if request.form['FAKEGAMES']:
				return render_from_fake_games(sheet_id, sheet_name, season, week)

		#render_from_real_games() will return a render_template(flask.html)
		return render_from_real_games(sheet_id, sheet_name, season, week)

@FLASK_APP.route("/")
@FLASK_APP.route("/football_post", methods=['GET', 'POST'])
def football_post():

		away_scores = []
		home_scores = []

		if request.method == "POST":

			for i in range(0, (len(request.form)/2)):

				#because we set our flask.html to use forms
				#with away/home_index0 we can now pull them
				#using the form immutable dict
				home = request.form['home_' + str(i)]
				away = request.form['away_' + str(i)]

				away_scores.append(away)
				home_scores.append(home)

				#print( "AWAY", away, "HOME: ", home)

			#wrapped payloads for google Sheets
			away_score_payload = [away_scores]
			home_score_payload = [home_scores]

			#create a new scribe
			scribe = SheetScribeService(session['sheet_id'], 'https://www.googleapis.com/auth/spreadsheets', None)

			#write our wrapped payloads
			try:
				#same fidelity check from earlier
				scribe.write_column_range_values(session['sheet_name'], 'D3', away_score_payload)
				scribe.write_column_range_values(session['sheet_name'], 'H3', home_score_payload)
			except HttpError:
				#@ToDo: Proper error_sheet.html
				return "<h1>Request spreadsheet entity %s or sub_sheet %s not found.</h1>" % (session['sheet_id'], session['sheet_name'])

			#Increment our counter for fun stats
			session['google_sheets_api_calls'] += scribe.apiCalls

			return render_template('post.html',
				sportsradar_api_calls=session['sportsradar_api_calls'],
				google_sheets_api_calls=session['google_sheets_api_calls']
				)
		else:
			return "response ERR"
