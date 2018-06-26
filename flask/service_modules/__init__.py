from random import choice, randint
from time import sleep
from copy import copy
from requests import get, Request, Session

from httplib2 import Http
from oauth2client import file, client, tools

from apiclient.discovery import build, HttpError
from oauth2client.clientsecrets import InvalidClientSecretsError

class FakeGame:
	#for testing
	FBS_TEAMS = {'AF':'Air Force', 'AKRN':'Akron',
	'BAMA':'Alabama', 'UAB':'Alabama-Birmingham', 'ARIZ':'Arizona',
	'ARST':'Arkansas St.', 'ARMY':'Army', 'AUB':'Auburn',
	'BALL':'Ball St.', 'BAY':'Baylor', 'BOISE':'Boise St.',
	'BC':'Boston College', 'BG':'Bowling Green', 'BYU':'Brigham Young',
	'BUF':'Buffalo', 'CAL':'California', 'UCF':'Central Florida',
	'CMU':'Central Michigan', 'CIN':'Cincinnati', 'CLEM':'Clemson',
	'COL':'Colorado', 'CSU':'Colorado St.', 'CONN':'Connecticut',
	'DUKE':'Duke', 'ECU':'East Carolina', 'EMU':'Eastern Michigan',
	'UF':'	Florida', 'FAU':'Florida Atlantic', 'FIU':'Florida International',
	'FSU':'Florida St.', 'FRSNO':'Fresno St.', 'UGA':'Georgia',
	'GTECH':'Georgia Tech', 'HAW':'Hawaii', 'HOU':'Houston',
	'IDAHO':'Idaho', 'ILL':'Illinois', 'IND':'Indiana',
	'IOWA':'Iowa', 'IAST':'Iowa St.', 'KAN':'Kansas',
	'KSST':'Kansas St.', 'KENT':'Kent St.', 'UK':'Kentucky',
	'LSU':'Louisiana St.', 'LTECH':'Louisiana Tech', 'ULL':'Louisiana-Lafayette',
	'ULM':'Louisiana-Monroe', 'LOU':'Louisville', 'MRSHL':'Marshall',
	'MARY':'Maryland', 'MASS':'Massachusetts', 'MEM':'Memphis',
	'MIAF':'Miami (FL)', 'MIAO':'Miami (OH)', 'MICH':'Michigan',
	'MIST':'Michigan St.', 'MTENN':'Middle Tennessee', 'MINN':'Minnesota',
	'MISS':'Mississippi', 'MSST':'Mississippi St.', 'MIZZ':'Missouri',
	'NAVY':'Navy', 'NEB':'Nebraska', 'NEV':'Nevada',
	'UNLV':'Nevada-Las Vegas', 'UNM':'New Mexico', 'NMST':'New Mexico St.',
	'UNC':'North Carolina', 'NCST':'North Carolina St.', 'NTEX':'North Texas',
	'NILL':'Northern Illinois', 'NWEST':'Northwestern', 'NDAME':'Notre Dame',
	'OHIO':'Ohio', 'OHST':'Ohio St.', 'OKST':'Oklahoma St.',
	'OREG':'Oregon', 'ORST':'Oregon St.', 'PSU':'Penn St.',
	'PITT':'Pittsburgh', 'PURD':'Purdue', 'RICE':'Rice',
	'RUTG':'Rutgers', 'SDSU':'San Diego St.', 'SJSU':'San Jose St.',
	'SBAMA':'South Alabama', 'SCAR':'South Carolina', 'USF':'South Florida',
	'SCAL':'Southern California', 'SMU':'Southern Methodist', 'SMISS':'Southern Mississippi',
	'STAN':'Stanford', 'SYR':'Syracuse', 'TMPLE':'Temple',
	'TENN':'Tennessee', 'TEX':'Texas', 'TXAM':'Texas A&M',
	'TCU':'Texas Christian', 'TXST':'Texas St.', 'TTECH':'Texas Tech',
	'UTEP':'Texas-El Paso', 'UTSA':'Texas-San Antonio', 'TOL':'Toledo',
	'TROY':'Troy', 'TLNE':'Tulane', 'TULSA':'Tulsa',
	'UCLA':'UCLA ', 'UTAH':'Utah', 'UTST':'Utah St.',
	'VAND':'Vanderbilt', 'UVA':'Virginia', 'VTECH':'Virginia Tech',
	'WAKE':'Wake Forest', 'WASH':'Washington', 'WSU':'Washington St.',
	'WVU':'West Virginia', 'WKU':'Western Kentucky', 'WMU':'Western Michigan',
	'WIS':'Wisconsin', 'WYO':'Wyoming'
	}

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
		self.homeRank    = str(randint(1, 25)) if randint(0,10) % 10 else 'U'
		self.awayRank    = str(randint(1, 25)) if randint(0,10) % 10 else 'U'
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

	def __del__(self):
		print('%s deconstructed' % (self))
class Game:

	FBS_TEAMS = {'WF': 'Wake Forest', 'GST': 'Georgia State', 'LIB': 'Liberty',
	'BC': 'Boston College', 'MFL': 'Miami (FL)', 'BGN': 'Bowling Green', 'MIZ': 'Missouri',
	'NAV': 'Navy', 'MICH': 'Michigan', 'MIS': 'Ole Miss', 'BOISE': 'Boise State', 'GSO': 'Georgia Southern',
	'OHI': 'Ohio', 'IOW': 'Iowa', 'SAB': 'South Alabama', 'AUB': 'Auburn', 'MIN': 'Minnesota', 'UAB': 'UAB',
	'PIT': 'Pittsburgh', 'ILL': 'Illinois', 'CHA': 'Charlotte', 'GT': 'Georgia Tech', 'VAN': 'Vanderbilt',
	'FIU': 'Florida International', 'BYU': 'Brigham Young', 'TXAM': 'Texas A&M', 'WMC': 'Western Michigan',
	'KNT': 'Kent State', 'HAW': 'Hawaii', 'MAR': 'Maryland', 'NIL': 'Northern Illinois', 'APP': 'Appalachian State',
	'KAN': 'Kansas', 'SYR': 'Syracuse', 'RICE': 'Rice', 'KST': 'Kansas State', 'EMC': 'Eastern Michigan',
	'CMC': 'Central Michigan', 'BAMA': 'Alabama', 'TSA': 'Tulsa', 'NEV': 'Nevada', 'FLA': 'Florida', 'UGA': 'Georgia',
	'TCU': 'TCU', 'OSU': 'Ohio State', 'TXST': 'Texas State', 'WVU': 'West Virginia', 'LSU': 'Louisianna State', 'UCONN': 'Connecticut',
	'UVA': 'Virginia', 'BUF': 'Buffalo', 'TRY': 'Troy', 'CSU': 'Colorado State', 'NM': 'New Mexico', 'OKS': 'Oklahoma State',
	'TEN': 'Tennessee', 'TUL': 'Tulane', 'MOH': 'Miami (OH)', 'RUT': 'Rutgers', 'UMASS': 'Massachusetts', 'OKL': 'Oklahoma',
	'PSU': 'Penn State', 'AKR': 'Akron', 'SMU': 'Southern Methodist', 'ULM': 'Louisiana-Monroe', 'NEB': 'Nebraska', 'ISU': 'Iowa State',
	'FSU': 'Florida State', 'WYO': 'Wyoming', 'COL': 'Colorado', 'TEM': 'Temple', 'ASU': 'Arizona State', 'NC': 'North Carolina',
	'ND': 'Notre Dame', 'ODU': 'Old Dominion', 'TEX': 'Texas', 'ECU': 'East Carolina', 'TEP': 'UTEP', 'MSU': 'Michigan State',
	'NW': 'Northwestern', 'BALL': 'Ball State', 'CAL': 'California', 'FRE': 'Fresno State', 'CC': 'Coastal Carolina', 'CLE': 'Clemson',
	'UNLV': 'UNLV', 'WAS': 'Washington', 'NTX': 'North Texas', 'NMS': 'New Mexico State', 'MEM': 'Memphis', 'UCLA': 'UCLA',
	'MSST': 'Mississippi State', 'WIS': 'Wisconsin', 'SC': 'South Carolina', 'ORE': 'Oregon', 'PUR': 'Purdue', 'USF': 'South Florida',
	'USC': 'South California', 'USM': 'Southern Miss', 'MSH': 'Marshall', 'CIN': 'Cincinnati', 'BAY': 'Baylor', 'DUK': 'Duke', 'WST': 'Washington State',
	'TOL': 'Toledo', 'LOU': 'Louisville', 'TT': 'Texas Tech', 'FAU': 'Florida Atlantic', 'UCF': 'UCF', 'LT': 'Louisiana Tech',
	'UTSA': 'UTSA', 'SJS': 'San Jose State', 'ARKS': 'Arkansas State', 'STA': 'Stanford', 'AF': 'Air Force', 'MTS': 'Middle Tennessee',
	'UTH': 'Utah', 'IU': 'Indiana', 'UTS': 'Utah State', 'HOU': 'Houston', 'VT': 'Virginia Tech', 'ULL': 'Louisiana-Lafayette',
	'ORS': 'Oregon State', 'NCST': 'North Carolina State', 'SDSU': 'San Diego State', 'WKY': 'Western Kentucky', 'ARI': 'Arizona',
	'ARK': 'Arkansas', 'ARM': 'Army', 'KEN': 'Kentucky'
	}

	FCS_TEAMS = {'WC': 'Western Carolina', 'HAMP': 'Hampton', 'WM': 'William & Mary', 'DRT': 'Dartmouth', 'JM': 'James Madison',
	'CCH': 'Charleston Southern', 'NAT': 'North Carolina A&T', 'UNI': 'Northern Iowa', 'NAZ': 'Northern Arizona', 'CPS': 'Cal Poly',
	'ALCST': 'Alcorn State', 'SIL': 'Southern Illinois', 'SAM': 'Samford', 'MUR': 'Murray State', 'PRI': 'Princeton',
	'JAC': 'Jacksonville', 'RIL': 'Rhode Island', 'PRV': 'Prairie View A&M', 'RM': 'Robert Morris', 'UMAINE': 'Maine',
	'SAU': 'Stephen F. Austin', 'VAL': 'Valparaiso', 'JVS': 'Jacksonville State', 'FAMU': 'Florida A&M', 'CHT': 'Chattanooga',
	'HAR': 'Harvard', 'SVS': 'Savannah State', 'LAM': 'Lamar', 'APY': 'Austin Peay', 'NIC': 'Nicholls State', 'LAF': 'Lafayette',
	'VIL': 'Villanova', 'APB': 'Arkansas-Pine Bluff', 'TSO': 'Texas Southern', 'FUR': 'Furman', 'ACU': 'Abilene Christian',
	'SDS': 'South Dakota State', 'CMB': 'Columbia', 'DRA': 'Drake', 'GTOWN': 'Georgetown', 'DEL': 'Delaware', 'HB': 'Houston Baptist',
	'HC': 'Holy Cross', 'YSU': 'Youngstown State', 'SCH': 'Sacred Heart', 'NWS': 'Northwestern State', 'BUT': 'Butler', 'MNM': 'Monmouth',
	'BUC': 'Bucknell', 'SCS': 'South Carolina State', 'SHS': 'Sam Houston State', 'FOR': 'Fordham', 'DLS': 'Delaware State',
	'NFS': 'Norfolk State', 'GRA': 'Grambling State', 'EW': 'Eastern Washington', 'WOF': 'Wofford', 'TNST': 'Tennessee State',
	'STU': 'Stetson', 'MOS': 'Montana State', 'MOR': 'Morehead State', 'KENN': 'Kennesaw State', 'MGN': 'Morgan State', 'COR': 'Cornell',
	'CSUS': 'Sacramento State', 'GWB': 'Gardner-Webb', 'IDS': 'Idaho State', 'PEN': 'Pennsylvania', 'SUT': 'Southern Utah',
	'ILS': 'Illinois State', 'EKY': 'Eastern Kentucky', 'BCU': 'Bethune-Cookman', 'IDA': 'Idaho', 'NH': 'New Hampshire', 'MONT': 'Montana',
	'JST': 'Jackson State', 'CCSU': 'Central Connecticut State', 'SEM': 'Southeast Missouri State', 'SEL': 'Southeastern Louisiana',
	'CGT': 'Colgate', 'MVS': 'Mississippi Valley State', 'ELO': 'Elon', 'WAG': 'Wagner', 'UNA': 'North Alabama', 'UND': 'North Dakota',
	'DUQ': 'Duquesne', 'NDS': 'North Dakota State', 'NOCO': 'Northern Colorado', 'BRY': 'Bryant University', 'VMI': 'Virginia Military Institute',
	'LEI': 'Lehigh', 'WIL': 'Western Illinois', 'ALB': 'Albany', 'SU': 'Southern University', 'BRN': 'Brown', 'MER': 'Mercer',
	'SBK': 'Stony Brook', 'PRES': 'Presbyterian', 'SD': 'South Dakota', 'WBS': 'Weber State', 'AAM': 'Alabama A&M', 'MST': 'Marist',
	'TWN': 'Towson', 'PRST': 'Portland State', 'RCH': 'Richmond', 'CAM': 'Campbell', 'CIT': 'Citadel', 'EIL': 'Eastern Illinois',
	'DAV': 'Davidson', 'UCD': 'UC Davis', 'UCA': 'Central Arkansas', 'MIZST': 'Missouri State', 'DAY': 'Dayton', 'TNT': 'Tennessee Tech',
	'STF': 'St. Francis (PA)', 'IW': 'Incarnate Word', 'HOW': 'Howard', 'ETSU': 'East Tennessee State', 'TNM': 'Tennessee-Martin',
	'MCN': 'McNeese State', 'INDS': 'Indiana State', 'YAL': 'Yale', 'SDG': 'San Diego', 'ALAST': 'Alabama State', 'NCC': 'North Carolina Central'
	}

	#for organizing game data
	def __init__(self, game, rankings, test):
		if test:
			return
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
	#for handling sportsradar API calls
	def __init__(self, sports_radar_api_key):
		self.raw_request_data  = {} #class table for referencing all request json data
		self.ranks       = {}
		self.apiCalls    = 0
		self.session     = Session()
		self.agent       = {"user-agent": "cfb-sheets-writer-script"}
		self.init_params = {'limit':'9999999', 'api_key': sports_radar_api_key}
		self.session.headers.update(self.agent)
		self.session.params.update(self.init_params)

	def get_games(self, season, week):

		try:
			response = self.session.get("http://api.sportradar.us/ncaafb-t1/" + str(season) + "/REG/" + str(week) + "/schedule.json?").json()
		except ValueError:
			print("Invalid API Key for SportsRadar Calls, or no json was returned")
			self.apiCalls += 1
			return False

		self.raw_request_data['game_data_json'] = response
		sleep(1)
		self.apiCalls += 1
		return response['games'] if 'games' in response.keys() else response

	def get_ranks(self, season, week):
		poll = "AP25" if int(week) < 10 else "CFP25"

		try:
			response = self.session.get("http://api.sportradar.us/ncaafb-t1/polls/" + str(poll) + "/" + str(season) + "/" + str(week) + "/rankings.json?").json()
		except ValueError:
			print("Invalid API Key for SportsRadar Calls, or no json was returned")
			self.apiCalls += 1
			return False

		self.raw_request_data['poll_data_json'] = response

		sleep(1)
		self.apiCalls += 1

		if not('rankings' in response.keys()):
			return False
		else:
			for team in response['rankings']:
				self.ranks[team['id']] = team['rank']
			return self.ranks

	def get_team_hierarchy(self, division):

		try:
			response = self.session.get("http://api.sportradar.us/ncaafb-t1/teams/" + str(division) + "/hierarchy.json?").json()
		except ValueError:
			print("Invalid API Key for SportsRadar Calls, or no json was returned")
			self.apiCalls += 1
			return False

		self.raw_request_data['team_hierarchy_json'] = response
		sleep(1)
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