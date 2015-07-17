import gspread
import getpass
import unicodecsv
import json
import os
from oauth2client.client import SignedJwtAssertionCredentials

__CLIENTS = {}

def write(filename, values):
    f = open(filename, "w")
    w = unicodecsv.writer(f, encoding='utf-8')
    for row in values:
        w.writerow(row)
    f.close()

def check(d):
    return "".join([d.strip() for d in d])

def getclient(jsonfile='creds.json'):
    if os.path.exists(jsonfile):
        source = jsonfile
        json_data = json.load(open(jsonfile))
        email = json_data['client_email']
        pkey = json_data['private_key']
    else:
        source = "env"
        email = os.environ.get("GGRAB_EMAIL")
        pkey = os.environ.get("GGRAB_KEY")
    scope = ['https://spreadsheets.google.com/feeds']
    if not email or not pkey:
        return None
    credshash = hash(email + pkey)
    if credshash in __CLIENTS:
        return __CLIENTS[credshash]
    else:
        print "Logging in with credentials from {}...".format(source)
        creds = SignedJwtAssertionCredentials(email, pkey, scope)
        client = gspread.authorize(creds)
        __CLIENTS[credshash] = client
        return client

def sanitise(s):
    return "".join([c for c in s if c.isalnum()])

def grab(name=None, key=None, sheetname=None, cached=False):
    filename = "{0}_{1}.csv".format(sanitise(key or name), sanitise(sheetname or "0"))
    client = (not cached) and getclient()
    if client:
        # get from gdrive
        if sheetname:
            print "Loading {}...".format(key or name),
        if key:
            spreadsheet = client.open_by_key(key)
        else:
            spreadsheet = client.open(name)
        # fetch sheet
        print "\b\b\b\b: {}...".format(sheetname or "0")
        if sheetname:
            ws = spreadsheet.worksheet(sheetname)
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
    elif os.path.exists(filename):
        print "Loading cached sheet ({} - {}) from local filesystem...".format((key or name), sheetname or "0")
        with open(filename, "r") as f:
            r = unicodecsv.DictReader(f)
            return [d for d in r if check(d.values())]
    else:
        print "Could not load {} - {}.".format((key or name), sheetname or "0")
        return []
