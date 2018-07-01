from random import choice, randint
from time import sleep
from copy import copy
from json import loads
from os import path

from requests import get, Request, Session

from httplib2 import Http
from oauth2client import file, client, tools

from apiclient.discovery import build, HttpError
from oauth2client.clientsecrets import InvalidClientSecretsError

#@ToDo: Make classes work within a context manager?

SCRIPT_DIR = path.dirname(path.abspath(__file__))

class FakeGameGenerator:

	#@ToDo: Improve chance generation
	#ToDo: Improve score generator
	fbs_json_path = path.join(SCRIPT_DIR, 'fakegames_fbs_dict.json')
	fbs_json = open(fbs_json_path, 'r').read()

	def __init__(self):

		self.FBS_TEAMS = loads(self.fbs_json)
		self.RANKS = [i for i in range(1, 26)]

		fbs_dict_copy         = copy(self.FBS_TEAMS)
		self.home_team_choice = choice(fbs_dict_copy.keys())
		del fbs_dict_copy[self.home_team_choice]
		self.away_team_choice = choice(fbs_dict_copy.keys())

		self.home_team   = self.lookup_full_name(self.home_team_choice)
		self.away_team   = self.lookup_full_name(self.away_team_choice)
		self.gameStatus  = 'scheduled'
		self.gameTime    = 'future'
		self.isImportant = False
		self.isRanked    = True
		self.homeRank    = choice(self.RANKS) if self.chance(10) else 'U'
		self.awayRank    = choice(self.RANKS) if self.chance(10) else 'U'
		self.home_points = self.fake_score(self.homeRank)
		self.away_points = self.fake_score(self.awayRank)

	def generate_new_fake_game(self):

		if self.RANKS != []:

			if self.FBS_TEAMS != {}:
				self.away_team_choice = choice(self.FBS_TEAMS.keys())
				self.away_team = self.lookup_full_name(self.away_team_choice)
				del self.FBS_TEAMS[self.away_team_choice]
				self.home_team_choice = choice(self.FBS_TEAMS.keys())
				self.home_team = self.lookup_full_name(self.home_team_choice)
				del self.FBS_TEAMS[self.home_team_choice]

			self.gameStatus  = 'scheduled'
			self.gameTime    = 'future'
			self.isImportant = False
			self.isRanked    = True

			self.homeRank    = self.generate_rank()
			self.awayRank    = self.generate_rank()
			self.home_points = self.fake_score(self.homeRank)
			self.away_points = self.fake_score(self.awayRank)

	def refill(self):
		self.RANKS = [i for i in range(1, 26)]


	def lookup_full_name(self, acronym):
		if acronym in self.FBS_TEAMS.keys():
			return self.FBS_TEAMS[acronym]
		else:
			return acronym

	def fake_score(self, rank):
		if rank >= 10:
			if not(self.chance(5)):
				points_from_td = randint(0, 8) * 7
			else:
				points_from_td = randint(0, 5) * 7
		else:
			points_from_td = randint(0, 5) * 7

		if not(self.chance(10)):
			points_from_safties = randint(0, 3) * 2
		else:
			points_from_safties = 0

		points_from_fg = randint(0, 4) * 3

		return points_from_td + points_from_fg + points_from_safties

	def choose_and_remove(self, list, fail_val=None):
		if list != []:
			list_choice = choice(list)
			list.remove(list_choice)
			return list_choice
		else:
			return fail_val

	def chance(self, tries):
		if not(randint(0, tries) % tries):
			return True
		else:
			return False

	def generate_rank(self):
		rank = 'U'
		if self.chance(3):
			rank = self.choose_and_remove(self.RANKS, 'U')
		return rank

	def __del__(self):
		print('%s deconstructed' % (self))

class SportsRadarGame:

	#@ToDo: implement format_time()

	fbs_json_path = path.join(SCRIPT_DIR, 'sports_radar_fbs_dict.json')
	fcs_json_path = path.join(SCRIPT_DIR, 'sports_radar_fcs_dict.json')

	fbs_json = open(fbs_json_path, 'r').read()
	fcs_json = open(fcs_json_path, 'r').read()
	FBS_TEAMS = loads(fbs_json)
	FCS_TEAMS = loads(fcs_json)

	#for organizing game data
	def __init__(self, game, rankings):
		self.game = game
		self.rankings = rankings
		self.home_acr    = game['home']
		self.away_acr    = game['away']
		self.home_team   = self.lookup_full_name(game['home'])
		self.away_team   = self.lookup_full_name(game['away'])
		self.gameStatus  = game['status']
		self.gameTime    = self.format_time(game['scheduled'])
		self.awayRank    = 'U'
		self.homeRank    = 'U'
		self.home_points = self.points('home')
		self.away_points = self.points('away')
		self.isImportant = True if 'title' in game.keys() else False
		self.isRanked    = self.ranked(self.home_acr, self.away_acr)

		if self.isRanked and rankings:
			self.awayRank = self.get_team_rank(self.away_acr)
			self.homeRank = self.get_team_rank(self.home_acr)

	def points(self, team):
		if team+'_points' in self.game.keys():
			return game[team+'_points']
		else:
			return ''

	def ranked_game(self, team_1, team_2):
		rank_keys = self.rankings.keys()
		if (self.rankings):
			if (team_1 in rank_keys) or (team_2 in rank_keys):
				return True
			else:
				return False
		else:
			return False

	def get_team_rank(self, team_acr):
		rank_keys = self.rankings.keys()
		if team_acr in rank_keys:
			return self.rankings[team_acr]
		else:
			return 'U'

	def format_time(self, unformatted):
		formatted = unformatted[0:16]
		return formatted

	def lookup_full_name(self, acronym):
		if acronym in self.FBS_TEAMS.keys():
			return self.FBS_TEAMS[acronym]
		elif acronym in self.FCS_TEAMS.keys():
			return self.FCS_TEAMS[acronym]
		else:
			return acronym

	def __del__(self):
		print('%s deconstructed' % (self))

class SportsRadarService:

	#A Class for handling Sports Radar API calls

	#@ToDo: Rename me to SportsRadar NCAA Service?

	def __init__(self, sports_radar_api_key):
		self.raw_request_data = {}
		self.ranks            = {}
		self.apiCalls         = 0
		self.sleep_time       = 1
		self.session          = Session()
		self.root             = "http://api.sportradar.us/ncaafb-t1"
		self.agent            = {"user-agent": "YASSP-PY-script"}
		self.init_params      = {'limit':'9999999',
								'api_key': sports_radar_api_key}

		self.session.headers.update(self.agent)
		self.session.params.update(self.init_params)

	def err(self, error):
		print("Error in SportsRadarService: %s." % error)

	def get_games(self, season, week):
		try:
			response = self.session.get("%s/%s/REG/%s/schedule.json?"
				% (self.root, season, week)
				).json()
		except ValueError as e:
			self.err(e)
			self.apiCalls += 1
			return False

		self.raw_request_data['game_data_json'] = response
		sleep(self.sleep_time)
		self.apiCalls += 1
		return response['games'] if 'games' in response.keys() else response

	def get_ranks(self, season, week):
		poll = "AP25" if int(week) < 10 else "CFP25"
		try:
			response = self.session.get("%s/polls/%s/%s/%s/rankings.json?"
				% (self.root, poll, season, week)
				).json()
		except ValueError as e:
			self.err(e)
			self.apiCalls += 1
			return False

		self.raw_request_data['poll_data_json'] = response

		sleep(self.sleep_time)
		self.apiCalls += 1

		if not('rankings' in response.keys()):
			return False
		else:
			for team in response['rankings']:
				self.ranks[team['id']] = team['rank']
			return self.ranks

	def get_team_hierarchy(self, division):

		try:
			response = self.session.get("%s/%s/hierarchy.json?"
				% (self.root, division)
				)
		except ValueError as e:
			self.err(e)
			self.apiCalls += 1
			return False

		self.raw_request_data['team_hierarchy_json'] = response
		sleep(self.sleep_time)
		self.apiCalls += 1
		return response

	def __del__(self):
		print('%s deconstructed. Calls to API: %s.' % (self, self.apiCalls))

class SheetScribeService:

	#Google sheets wriiiiiiiterrrrrr, Google Sheets wriiiiiiiterrrr
	#@ToDo: condense *_column_*() into one function with column argument

	def __init__(self, sheet_id, scope, apiKey):
		self.secrets       = 'client_secret.json'
		self.spreadsheetId = sheet_id
		self.storage       = file.Storage(self.secrets_file)
		self.creds         = self.storage.get()
		self.scope         = scope
		self.apiCalls      = 0
		self.auth          = False

		if not self.creds or self.creds.invalid:
			try:
				client.flow_from_clientsecrets()
				flow  = client.flow_from_clientsecrets(self.secrets, self.scope)
				self.creds = tools.run_flow(flow, self.storage)
				self.auth  = True
			except InvalidClientSecretsError:
				print("Invalid OAuth2 and Client Secret credentials")
				self.auth = False
				return

		self.build = build('sheets', 'v4', http=self.creds.authorize(Http()))
		self.sheetPtr = self.build.spreadsheets().values()
		self.auth = True

	def get_sheet_values(self, sheet):
		response        = self.sheetPtr.get(spreadsheetId=self.spreadsheetId,
											range=str(sheet)
											).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response

	def get_range_values(self, sheet, range):
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.get(spreadsheetId=self.spreadsheetId,
											range=requested_range
											).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response.get('values') if response.get('values') is not None else 0

	def get_column_range_values(self, sheet, range):
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.get(spreadsheetId=self.spreadsheetId,
											range=requested_range,
											body={'majorDimension':'columns'}
											).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response

	def write_column_range_values(self, sheet, range, values):
		print("Writing:", values, 'in range:', range, 'majorDimension=columns')
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.update(spreadsheetId=self.spreadsheetId,
											   range=requested_range,
											   valueInputOption='USER_ENTERED',
											   body={'values':values,
											   		 'majorDimension':'columns'}
											   ).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response

	def write_row_range_values(self, sheet, range, values):
		print("Writing:", values, 'in range:', range, ', majorDimension=rows')
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.update(spreadsheetId=self.spreadsheetId,
											   range=requested_range,
											   valueInputOption='USER_ENTERED',
											   body={'values':values}
											   ).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response

	def clear_column_values(self, sheet, range):
		payload = {}
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.clear(spreadsheetId=self.spreadsheetId,
											  range=requested_range,
											  body=payload
											  ).execute()
	def __del__(self):
		print('%s deconstructed. Calls to API: %s.' % (self, self.apiCalls))
