import os
from random import choice
from service_modules import FakeGame, Game, SportsRadarService, SheetScribeService, FakeGameGenerator
from flask import Flask, render_template, request, session

#@ToDo: Cleanup this top portion and constants before function defs
#@ToDo: Move Funny phrases into a json file or other such file
#ToDo: Force max col width of 80
#@ToDo: Proper error_sheet.html

directory            = os.path.dirname(os.path.abspath(__file__))
sportsradar_key_file = os.path.join(directory, 'sports-radar-api-key')
remote               = False

if "LOCATION" in os.environ:
	if os.environ['LOCATION'] == "remote":
		remote = True

FLASK_APP            = Flask(__name__)
FLASK_APP.secret_key = 'hunter2'

if __name__ == "__main__":
	FLASK_APP.run(debug=True)

SPORTSRADAR_API_KEY = open(sportsradar_key_file, "r").read().rstrip("\n\r")

FUNNY_PHRASES = ["Go Dawgs!", "Don't worry, we're all champions of life.", "All aboard the Gus Bus!", "D I L L Y D I L L Y.",
"Shark Lovers Only.", "This program is approved by Joey Freshwater.", "Five Star Hearts ONLY.", "*Dooley takes note*", "7-3 Rutgers.",
"M 0 - 0 N", "M 0w0 N... whats this.", "Verne Lundquist: Oh no!", "Gary: Notice Me Saban.", "All Alabama has on the field is fat guys.",
"Sam Darnold wouldn't want it any other way.", "You know who would've made a great CFB Quaterback? Brett Farve.", "OwO what's this.",
"Beat the War-tigle crap out of em'.", "UCF: 2017-8 National Champions.", "Les Miles is eating grass again.", "The kicker got ejected for targeting.",
"We want BAMA.", "Vandy wanted Bama, Vandy got Bama.", "Missouri belongs in the SEC.", "Troy > LSU > Auburn > Bama.", "Like they say, it's an ongoing investigation."
]

def render_from_fake_games(sheet_id, sheet_name, season, week):

	#@ToDo: Move writing names and ranks into /football_post function
	#@ToDo: col width 80
	#@ToDo: create a fake_flask.html for supporting new FakeGameGenerator class
	#@ToDo: 


	scribe    = SheetScribeService(sheet_id, 'https://www.googleapis.com/auth/spreadsheets', None)
	sub_sheet = sheet_name

	#We need to wreck our sheet's A-H
	#columns to make way for new info
	for column in ['A', 'B', 'C', 'E', 'F', 'G']:
		#Check for fidelity
		try:
			scribe.clear_column_values(sheet_name, '%s3:%s1000' % (column, column))
		except HttpError:
			#@ToDo: Proper error_sheet.html
			return "<h1>Request spreadsheet entity %s or sub_sheet %s not found.</h1>" % (sheet_id, sub_sheet)

	already_there = None
	try:
		already_there = scribe.get_range_values(sub_sheet, "D3:D28")
	except HttpError:
		return "<h1>Request spreadsheet entity %s or sub_sheet vals %s not found.</h1>" % (sheet_id, already_there)
	print("VALS", already_there)

	if already_there != 0:
		for x in range(len(already_there)):
			print("Val %s" % (already_there[x]))

	#Assuming scribe service didn't bail, let's grab the games
	#radar_service = SportsRadarService(SPORTSRADAR_API_KEY)
	#games         = radar_service.get_games(season, week)
	#ranks         = radar_service.get_ranks(season, week)

	fake_games = []
	away_ranks = []
	away_teams = []
	home_ranks = []
	home_teams = []

	if not(scribe.auth):
		return "Sheets Writer Service Module returned with: %s. Go back to setup." % (scribe.auth)

	game_instance = FakeGameGenerator()
	while game_instance.RANKS != []:

		info = {}

		game_instance.generate_new_fake_game()

		#there were vals in the sheet already, sub them in
		#if already_there != 0 and already_there[i] != "":
		#	game_instance.away_points = int(already_there[i][0])

		#ToDo: If game_instance.isImportant it must be a bowl game
		#we need to pass the title into our flask.html to signify this
		if (game_instance.isRanked) or (game_instance.isImportant):
			#passing the whole real_games list into
			#flask.html means that we need to parse it there
			#and not here, saving us a bunch of time
			fake_games.append(game_instance)

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
	scribe.write_column_range_values(sub_sheet, 'B3', away_ranks_payload)
	scribe.write_column_range_values(sub_sheet, 'C3', away_teams_payload)
	scribe.write_column_range_values(sub_sheet, 'F3', home_ranks_payload)
	scribe.write_column_range_values(sub_sheet, 'G3', home_teams_payload)

	#increment our counters for fun stats in post.html
	session['google_sheets_api_calls'] += scribe.apiCalls
	#session['sportsradar_api_calls']   += radar_service.apiCalls

	print(fake_games)

	return render_template('flask.html',
		seq=fake_games,
		remote=remote,
		phrase=choice(FUNNY_PHRASES),
		sheet_id_truncated=sheet_id[0:7] + "...",
		sub_sheet=sheet_name,
		season=season,
		week=week
		)

def render_from_real_games(sheet_id, sheet_name, season, week):

	#@ToDo Move writing names and ranks into /football_post function
	scribe    = SheetScribeService(sheet_id, 'https://www.googleapis.com/auth/spreadsheets', None)
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

		game_instance = Game(game, radar_service.ranks)

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
		phrase=choice(FUNNY_PHRASES),
		sheet_id_truncated=sheet_id[0:7] + "...",
		sub_sheet=sheet_name,
		season=season,
		week=week
		)


@FLASK_APP.route("/")
def init():
	#@ToDo: Put something better here
	return "<h1>running</h1>"

@FLASK_APP.route("/")
@FLASK_APP.route("/setup/")
def setup_flask():
	return render_template('setup.html', remote=remote)

@FLASK_APP.route("/")
@FLASK_APP.route("/ncaa-football/", methods=['GET', 'POST'])
def flask_post():

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
