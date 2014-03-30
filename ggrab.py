import gspread
import getpass
import unicodecsv

__CLIENTS = {}

def write(filename, values):
	f = open(filename, "w")
	w = unicodecsv.writer(f, encoding='utf-8')
	for row in values:
		w.writerow(row)
	f.close()

def check(d):
	return "".join([d.strip() for d in d])

def getclient(user):
	if user in __CLIENTS:
		return __CLIENTS[user]
	else:
		pwd = getpass.getpass()
		if pwd:
			client = gspread.login(user, pwd)
		else:
			client = None
		__CLIENTS[user] = client
		return client

def grab(user, key, name=None):
	filename = "{0}_{1}.csv".format(key, name or 0)
	client = getclient(user)
	if client:
		# get from gdrive
		if name:
			print "Fetching {0} from Google Docs...".format(name or "first sheet")
		spreadsheet = client.open_by_key(key)
		# fetch sheet
		if name:
			ws = spreadsheet.worksheet(name)
		else:
			ws = spreadsheet.get_worksheet(0)
		# read data
		values = ws.get_all_values()
		keys = values[0]
		cards = []
		for c in values[1:]:
			if check(c):
				cards.append(dict(zip(keys, c)))
		# write to local
		write(filename, values)
		return cards
	else:
		with open(filename, "r") as f:
			r = unicodecsv.DictReader(f)
			return [d for d in r if check(d.values())]
