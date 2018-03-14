import os
import sqlite3
import requests
import json
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'gw2chars.db'),
    SECRET_KEY='bleh',
    USERNAME='mp',
    PASSWORD='mp'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('db-scripts.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    init_db()
    print('Initialized Database')

@app.route('/', methods=['GET', 'POST'])
def show_accounts():
    if request.method == 'POST':
        session['account'] = request.form.get('accounts')
        return redirect(url_for('show_characters'))
    db = get_db()
    cur = db.execute('SELECT ID, Account_ID, API_Key FROM Accounts')
    accs = cur.fetchall()
    return render_template('show_accounts.html', accounts=accs)

@app.route('/account', methods=['GET'])
def show_characters():
    if 'account' in session:
        acc = session['account']
        db = get_db()
        cur = db.execute('SELECT ID, Name, Level, Race, Profession FROM Characters WHERE Account_ID = ? ORDER BY Name', [acc])
        chars = cur.fetchall()
        cur = db.execute('SELECT Character_ID, Equipment_ID, Slot, Name, Level, Rarity, Icon, Stats FROM Equipment WHERE Account_ID = ?', [acc])
        equips = cur.fetchall()
        return render_template('show_characters.html', characters=chars, equipment=equips)
    else:
        return redirect(url_for('show_accounts'))
    

@app.route('/refresh', methods=['POST'])
def refresh_from_api():
    if 'account' in session:
        acc = session['account']
        ak = RefreshCharacterInfo(acc)
        return redirect(url_for('show_characters'))
    else:
        return redirect(url_for('show_accounts'))

def CleanDatabase(accountid):
    db = get_db()
    db.execute("DELETE FROM Characters WHERE Account_ID = ?", [accountid])
    db.execute("DELETE FROM Equipment WHERE Account_ID = ?", [accountid])
    db.commit()

def GetCharacters(apikey):
    chars = requests.get(url='https://api.guildwars2.com/v2/characters?access_token=' + apikey).json()
    return chars

def GetCharacterInfo(apikey, characterName):
    r = requests.get(url='https://api.guildwars2.com/v2/characters/' + characterName + '?access_token=' + apikey)
    j = json.loads(r.text)
    characterinfo = dict(race=j['race'],profession=j['profession'],level=j['level'],equipment=j['equipment'],created=j['created'])
    return characterinfo

def GetEquipmentInfo( equipmentIDs):
    r = requests.get(url='https://api.guildwars2.com/v2/items?ids=' + equipmentIDs)
    j = json.loads(r.text)
    return j

def RefreshCharacterInfo(accountid):
    CleanDatabase(accountid)
    db = get_db()
    cur = db.execute('SELECT API_Key FROM Accounts WHERE ID = ?', [accountid])
    apikey = cur.fetchone()[0]
    
    gw2characters = GetCharacters(apikey)

    for gw2character in gw2characters:
        gw2characterinfo = GetCharacterInfo(apikey, gw2character)
        
        character_id = 0
        
        cur = db.cursor()
        cur.execute("INSERT INTO Characters (Account_ID, Name, Level, Race, Profession) VALUES (?, ?, ?, ?, ?)", [accountid, gw2character, gw2characterinfo['level'], gw2characterinfo['race'], gw2characterinfo['profession']])
        character_id = cur.lastrowid
        db.commit()
        equipment_ids = ''

        for equipment in gw2characterinfo['equipment']:
            equipment_ids = equipment_ids + str(equipment['id']) + ','
            if "stats" in equipment:
                statraw = equipment['stats']['attributes']
                statformatted = ', '.join("{!s} {!r}".format(key, val) for (key,val) in statraw.items())
                db.execute("INSERT INTO Equipment (Account_ID, Character_ID, Equipment_ID, Slot, Stats) VALUES (?, ?, ?, ?, ?)", [accountid, character_id, str(equipment['id']), str(equipment['slot']), statformatted])
            else:
                db.execute("INSERT INTO Equipment (Account_ID, Character_ID, Equipment_ID, Slot) VALUES (?, ?, ?, ?)", [accountid, character_id, str(equipment['id']), str(equipment['slot'])])

        db.commit()

        equipmentdetails = GetEquipmentInfo(equipment_ids[:-1])

        for equipitem in equipmentdetails:
            if (equipitem['type'] != 'Gathering'):
                if("details" in equipitem and "infix_upgrade" in equipitem['details']):
                    statraw = equipitem['details']['infix_upgrade']['attributes']
                    statformatted = ''
                    for stat in statraw:
                        stattemp = ' '.join("{}".format(val) for (key,val) in stat.items())
                        statformatted = statformatted + stattemp + ', '
                        
                    db.execute("UPDATE Equipment SET NAME = ?, LEVEL = ?, Rarity = ?, ICON = ?, STATS = ? WHERE CHARACTER_ID = ? AND EQUIPMENT_ID = ?", [equipitem['name'],equipitem['level'], equipitem['rarity'], equipitem['icon'], statformatted[:-2], character_id, equipitem['id']])
                else:
                    db.execute("UPDATE Equipment SET NAME = ?, LEVEL = ?, Rarity = ?, ICON = ? WHERE CHARACTER_ID = ? AND EQUIPMENT_ID = ?", [equipitem['name'],equipitem['level'], equipitem['rarity'], equipitem['icon'], character_id, equipitem['id']])


if __name__ == '__main__':
    app.run()