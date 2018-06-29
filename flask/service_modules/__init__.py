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

SCRIPT_DIR = path.dirname(path.abspath(__file__))

class FakeGame:

	#A class for generating fake games that look
	#just like SportsRadar API games for testing

	#@ToDo: Unique rankings (can't have two rank 1's)
	#@ToDo: FCS Teams
	#@ToDo: Title (for isImportant)
	#@ToDO: Generate Fake Game function, instead of 
	#generating on __init__()
	
	fbs_json_path = path.join(SCRIPT_DIR, 'fakegames_fbs_dict.json')
	fbs_json = open(fbs_json_path, 'r').read()
	
	FBS_TEAMS = loads(fbs_json)
	RANKS = [i for i in range(1, 26)]

	def __init__(self):

		self.FBS_TEAMS_COPY   = copy(self.FBS_TEAMS)
		self.home_team_choice = choice(self.FBS_TEAMS_COPY.keys())
		# ensures a unique choice by removing home team from dict
		del self.FBS_TEAMS_COPY[self.home_team_choice]
		self.away_team_choice = choice(self.FBS_TEAMS_COPY.keys())

		self.home_team   = self.lookup_full_name(self.home_team_choice)
		self.away_team   = self.lookup_full_name(self.away_team_choice)
		self.gameStatus  = 'scheduled'
		self.gameTime    = 'future'
		self.isImportant = False
		self.isRanked    = True
		self.homeRank    = choice(self.RANKS) if randint(0,10) % 10 else 'U'
		self.awayRank    = choice(self.RANKS) if randint(0,10) % 10 else 'U'
		self.home_points = self.fake_score(self.homeRank)
		self.away_points = self.fake_score(self.awayRank)

	def choose_and_remove(list, fail_val=None):
		if list != []:
			list_choice = choice(list)
			list.remove(list_choice)
			return list_choice
		else:
			return fail_val

	def lookup_full_name(self, acronym):
		if acronym in self.FBS_TEAMS.keys():
			return self.FBS_TEAMS[acronym]
		else:
			return acronym

	def fake_score(self, rank):
		if rank >= 10:
			points_from_td  = randint(0, 8) * 7 if not(randint(0, 5) % 5) else randint(0, 5) * 7
		else:
			points_from_td  = randint(0, 5) * 7

		points_from_fg      = randint(0, 4) * 3
		points_from_safties = randint(0, 3) * 2 if not(randint(1, 10) % 10) else 0

		return points_from_td + points_from_fg + points_from_safties

	def __del__(self):
		print('%s deconstructed' % (self))

class FakeGameGenerator:
	
	fbs_json_path = path.join(SCRIPT_DIR, 'fakegames_fbs_dict.json')
	fbs_json = open(fbs_json_path, 'r').read()
	
	FBS_TEAMS = loads(fbs_json)
	RANKS = [i for i in range(1, 26)]

	def __init__(self):

		self.FBS_TEAMS_COPY   = copy(self.FBS_TEAMS)
		self.home_team_choice = choice(self.FBS_TEAMS_COPY.keys())
		# ensures a unique choice by removing home team from dict
		del self.FBS_TEAMS_COPY[self.home_team_choice]
		self.away_team_choice = choice(self.FBS_TEAMS_COPY.keys())

		self.home_team   = self.lookup_full_name(self.home_team_choice)
		self.away_team   = self.lookup_full_name(self.away_team_choice)
		self.gameStatus  = 'scheduled'
		self.gameTime    = 'future'
		self.isImportant = False
		self.isRanked    = True
		self.homeRank    = choice(self.RANKS) if randint(0,10) % 10 else 'U'
		self.awayRank    = choice(self.RANKS) if randint(0,10) % 10 else 'U'
		self.home_points = self.fake_score(self.homeRank)
		self.away_points = self.fake_score(self.awayRank)

	def generate_new_fake_game(self):

		if self.RANKS != []:

			if self.FBS_TEAMS != {}:
				self.home_team_choice = choice(self.FBS_TEAMS.keys())
				del self.FBS_TEAMS[self.home_team_choice]
				self.away_team_choice = choice(self.FBS_TEAMS.keys())
				del self.FBS_TEAMS[self.away_team_choice]

			self.home_team   = self.lookup_full_name(self.home_team_choice)
			self.away_team   = self.lookup_full_name(self.away_team_choice)
			self.gameStatus  = 'scheduled'
			self.gameTime    = 'future'
			self.isImportant = False
			self.isRanked    = True

			self.homeRank    = self.generate_rank()
			self.awayRank    = self.generate_rank()
			self.home_points = self.fake_score(self.homeRank)
			self.away_points = self.fake_score(self.awayRank)


	def lookup_full_name(self, acronym):
		if acronym in self.FBS_TEAMS.keys():
			return self.FBS_TEAMS[acronym]
		else:
			return acronym

	def fake_score(self, rank):
		if rank >= 10:
			points_from_td  = randint(0, 8) * 7 if not(randint(0, 5) % 5) else randint(0, 5) * 7
		else:
			points_from_td  = randint(0, 5) * 7

		points_from_fg      = randint(0, 4) * 3
		points_from_safties = randint(0, 3) * 2 if not(randint(1, 10) % 10) else 0

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

class Game:

	fbs_json_path = path.join(SCRIPT_DIR, 'sports_radar_fbs_dict.json')
	fcs_json_path = path.join(SCRIPT_DIR, 'sports_radar_fcs_dict.json')

	fbs_json = open(fbs_json_path, 'r').read()
	fcs_json = open(fcs_json_path, 'r').read()
	FBS_TEAMS = loads(fbs_json)
	FCS_TEAMS = loads(fcs_json)

	#for organizing game data
	def __init__(self, game, rankings):
		self.home_acr    = game['home']
		self.away_acr    = game['away']
		self.home_team   = self.lookup_full_name(game['home'])
		self.away_team   = self.lookup_full_name(game['away'])
		self.gameStatus  = game['status']
		self.gameTime    = self.format_time(game['scheduled'])
		self.awayRank    = 'U'
		self.homeRank    = 'U'
		self.home_points = game['home_points'] if 'home_points' in game.keys() else ''
		self.away_points = game['away_points'] if 'away_points' in game.keys() else ''
		self.isImportant = True if 'title' in game.keys() else False
		self.isRanked    = True if (rankings) and (self.home_acr in rankings.keys()) or (self.away_acr in rankings.keys()) else False

		if self.isRanked and rankings:
			self.awayRank = str(rankings[self.away_acr]) if (self.away_acr in rankings.keys()) else 'U'
			self.homeRank = str(rankings[self.home_acr]) if (self.home_acr in rankings.keys()) else 'U'

	#@ToDo: Implement this fully
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
	#@ToDo: proper error message reporting

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
	def __init__(self, sheet_id, scope, apiKey):
		self.spreadsheetId = sheet_id
		self.storage       = file.Storage('credentials.json')
		self.creds         = self.storage.get()
		self.scope         = scope
		self.apiCalls      = 0
		self.auth        = False

		if not self.creds or self.creds.invalid:
			try:
				client.flow_from_clientsecrets(
					)
				self.flow  = client.flow_from_clientsecrets('client_secret.json', self.scope)
				self.creds = tools.run_flow(self.flow, self.storage)
				self.auth  = True
			except InvalidClientSecretsError:
				print("Invalid OAuth2 and Client Secret credentials")
				self.auth = False
				return


		self.GoogleSheetsService = build('sheets', 'v4', http=self.creds.authorize(Http()))
		self.sheetPtr            = self.GoogleSheetsService.spreadsheets().values()
		self.auth              = True

	def get_sheet_values(self, sheet):
		response        = self.sheetPtr.get(spreadsheetId=self.spreadsheetId,range=str(sheet)).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response

	def get_range_values(self, sheet, range):
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.get(spreadsheetId=self.spreadsheetId,range=requested_range).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response.get('values') if response.get('values') is not None else 0

	def get_column_range_values(self, sheet, range):
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.get(spreadsheetId=self.spreadsheetId,range=requested_range, body={'majorDimension':'columns'}).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response

	def write_column_range_values(self, sheet, range, values):
		print("Writing:", values, 'in range:', range, 'majorDimension=columns')
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.update(spreadsheetId=self.spreadsheetId,range=requested_range,valueInputOption='USER_ENTERED',body={'values':values, 'majorDimension':'columns'}).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response

	def write_row_range_values(self, sheet, range, values):
		print("Writing:", values, 'in range:', range, ', majorDimension=rows')
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.update(spreadsheetId=self.spreadsheetId,range=requested_range,valueInputOption='USER_ENTERED',body={'values':values}).execute()
		sleep(0.26)
		self.apiCalls += 1
		return response

	def clear_column_values(self, sheet, range):
		payload = {}
		requested_range = str(sheet) + '!' + str(range)
		response        = self.sheetPtr.clear(spreadsheetId=self.spreadsheetId, range=requested_range, body=payload).execute()

	def __del__(self):
		print('%s deconstructed. Calls to API: %s.' % (self, self.apiCalls))
		