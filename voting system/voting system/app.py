##cryptography-3.4.8  for dll error
from flask import *
import sqlite3
import secrets
import os
from datetime import datetime
import base64

def calculate_age(dob):
    # Convert the input string to a datetime object
    dob = datetime.strptime(dob, "%Y-%m-%d")
    today = datetime.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

app = Flask(__name__)
app.secret_key = '\xf0?a\x9a\\\xff\xd4;\x0c\xcbHi'

connection = sqlite3.connect('database.db')
cursor = connection.cursor()

cursor.execute("create table if not exists voters(Id INTEGER PRIMARY KEY AUTOINCREMENT, voter_name TEXT, aadhaar_number TEXT, email TEXT, phone TEXT, place TEXT, dob TEXT, image TEXT)")
cursor.execute("create table if not exists candidates(Id INTEGER PRIMARY KEY AUTOINCREMENT, candidate_name TEXT, aadhaar_number TEXT, party_name TEXT, place TEXT, phone TEXT, email TEXT, election_symbol TEXT, image TEXT)")

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/userlogin')
def userlogin():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    from serial_test import ReadFinger
    adhar = ReadFinger()
    if adhar:
        cursor.execute("select * from voters where aadhaar_number = '"+adhar+"'")
        result = cursor.fetchone()
        if result:
            place = result[5]
            session['place'] = place
            session['vid'] = adhar

            connection1 = sqlite3.connect(f"{place}.db")
            cursor1 = connection1.cursor()
            
            cursor1.execute("create table if not exists voting (voter TEXT, candidate_name TEXT, party_name TEXT, election_symbol TEXT, image TEXT)")

            cursor1.execute("select * from voting where voter = '"+session['vid']+"'")
            result = cursor1.fetchall()
            if result:
                return render_template('index.html', msg="Your voting process already completed")
            else:
                cursor.execute("select Id, candidate_name, party_name, election_symbol, image from candidates where place = '"+place+"'")
                result = cursor.fetchall()
                return render_template('userlog.html', result=result, place=place)
        else:
            return render_template('index.html', msg="Wrong adhar number")
    else:
        return render_template('index.html', msg="adhar number not found")

@app.route('/Vote/<Id>')
def Vote(Id):
    print(Id)
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("select candidate_name, party_name, election_symbol, image from candidates where Id = '"+str(Id)+"'")
    result = list(cursor.fetchone())

    connection = sqlite3.connect(f"{session['place']}.db")
    cursor = connection.cursor()
    cursor.execute("create table if not exists voting (voter TEXT, candidate_name TEXT, party_name TEXT, election_symbol TEXT, image TEXT)")
    cursor.execute("insert into voting values('"+session['vid']+"', ?,?,?,?)", result)
    connection.commit()
    return render_template('index.html', msg="Your voting proccess completed. Thank you.")

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if name == 'admin' and password == 'admin':
            return render_template('addvoters.html')
        else:
            return render_template('admin.html', msg = "Entered wrong username or password")
    return render_template('admin.html')

@app.route('/addvoter', methods=['POST', 'GET'])
def addvoter():
    if request.method == 'POST':
        data = request.form
        print(data)
        keys = []
        values = []
        for key in data:
            values.append(data[key])
            keys.append(key)
        print(keys)
        print(values)

        file = request.files['profile']
        filename = file.filename
        file_content = file.read()
        my_string = base64.b64encode(file_content).decode('utf-8')
        values.append(my_string)

        age = calculate_age(values[-2])
        print(f"Age: {age} years")
        if age >= 18:
            connection = sqlite3.connect('database.db')
            cursor = connection.cursor()
            cursor.execute('insert into voters values (NULL, ?,?,?,?,?,?,?)', values)
            connection.commit()
            return render_template('addvoters.html', msg = "voter added successfully")
        else:
            return render_template('addvoters.html', msg="Age should be greater than or equal to 18")
    return render_template('addvoters.html')

@app.route('/voterslist')
def voterslist():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute("select * from voters")
    result = cursor.fetchall()

    return render_template('voters.html', result=result)

@app.route('/addcandidate', methods=['POST', 'GET'])
def addcandidate():
    if request.method == 'POST':
        data = request.form
        print(data)
        keys = []
        values = []
        for key in data:
            values.append(data[key])
            keys.append(key)
        print(keys)
        print(values)

        file = request.files['election_symbol']
        filename = file.filename
        file_content = file.read()
        my_string = base64.b64encode(file_content).decode('utf-8')
        values.append(my_string)

        file = request.files['profile']
        filename = file.filename
        file_content = file.read()
        my_string = base64.b64encode(file_content).decode('utf-8')
        values.append(my_string)

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('insert into candidates values (NULL, ?,?,?,?,?,?,?,?)', values)
        connection.commit()
        return render_template('addcandidates.html', msg = "Candidate added successfully")
    return render_template('addcandidates.html')

@app.route('/candidateslist')
def candidateslist():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute("select * from candidates")
    result = cursor.fetchall()

    return render_template('candidates.html', result=result)

@app.route('/removevoters/<Id>')
def removevoters(Id):
    print(Id)
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute("delete from voters where Id = '"+str(Id)+"'")
    connection.commit()

    cursor.execute("select * from voters")
    result = cursor.fetchall()

    return render_template('voters.html', result=result)

@app.route('/removecandidate/<Id>')
def removecandidate(Id):
    print(Id)
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()

    cursor.execute("delete from candidates where Id = '"+str(Id)+"'")
    connection.commit()
    
    cursor.execute("select * from candidates")
    result = cursor.fetchall()

    return render_template('candidates.html', result=result)

@app.route('/updatevoters/<Id>')
def updatevoters(Id):
    print(Id)
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("select * from voters where Id = '"+str(Id)+"'")
    result = cursor.fetchone()

    session['voterid'] = Id
    return render_template('updatevoters.html', result=result)

@app.route('/votersupdate', methods=['POST', 'GET'])
def votersupdate():
    if request.method == 'POST':
        data = request.form
        print(data)
        keys = []
        values = []
        for key in data:
            values.append(data[key])
            keys.append(key)
        print(keys)
        print(values)

        file = request.files['profile']
        filename = file.filename
        file_content = file.read()
        my_string = base64.b64encode(file_content).decode('utf-8')
        values.append(my_string)

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("update voters set voter_name = ?, aadhaar_number = ?, email = ?, phone = ?, place = ?, dob = ?, image = ? where Id = '"+str(session['voterid'])+"'", values)
        connection.commit()
        cursor.execute("select * from voters")
        result = cursor.fetchall()

        return render_template('voters.html', result=result)
    return render_template('addvoters.html')

@app.route('/updatecondidate/<Id>')
def updatecondidate(Id):
    print(Id)
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute("select * from candidates where Id = '"+str(Id)+"'")
    result = cursor.fetchone()
    print(result)
    session['condidateid'] = Id
    return render_template('updatecandidate.html', result=result)

@app.route('/candidateupdate', methods=['POST', 'GET'])
def candidateupdate():
    if request.method == 'POST':
        data = request.form
        print(data)
        keys = []
        values = []
        for key in data:
            values.append(data[key])
            keys.append(key)
        print(keys)
        print(values)

        file = request.files['election_symbol']
        filename = file.filename
        file_content = file.read()
        my_string = base64.b64encode(file_content).decode('utf-8')
        values.append(my_string)

        file = request.files['profile']
        filename = file.filename
        file_content = file.read()
        my_string = base64.b64encode(file_content).decode('utf-8')
        values.append(my_string)

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("update candidates set candidate_name = ?, aadhaar_number = ?, party_name = ?, place = ?, phone = ?, email = ?, election_symbol = ?, image = ? where Id = '"+str(session['condidateid'])+"'", values)
        connection.commit()
        cursor.execute("select * from candidates")
        result = cursor.fetchall()

        return render_template('candidates.html', result=result)
    return render_template('addcandidates.html')

@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        place = request.form['place']
        connection = sqlite3.connect(f"{place}.db")
        cursor = connection.cursor()
        
        cursor.execute("create table if not exists voting (voter TEXT, candidate_name TEXT, party_name TEXT, election_symbol TEXT, image TEXT)")

        cursor.execute("select * from voting")
        result = cursor.fetchall()
        if result:
            conn = sqlite3.connect("database.db")
            cr = conn.cursor()
            cr.execute("select * from candidates where place = '"+place+"'")
            List = cr.fetchall()
            candidates = []
            parties = []
            for row in List:
                candidates.append(row[1])
                parties.append(row[3])

            votes = []
            
            for name in candidates:
                cursor.execute("select * from voting where candidate_name = '"+name+"'")
                res = cursor.fetchall()
                if res:
                    votes.append(int(len(res)/2))
                else:
                    votes.append(0)
            
            Results = None
            if os.path.exists(f"{place}_result.db"):
                pl_connection = sqlite3.connect(f"{place}_result.db")
                pl_cr = pl_connection.cursor()
                command = """SELECT party, candidate, votes
                FROM Result
                WHERE votes = (SELECT MAX(Votes) FROM Result);"""
                pl_cr.execute(command)
                Results = pl_cr.fetchall()
                Results = list(set(Results))
                print(Results)
            return render_template('resultannounce.html', Results=Results, candidates=candidates, parties=parties, votes=votes, place=place, n = len(parties))
        else:
            return render_template('resultannounce.html', msg=f"Data not found of {place}")
    return render_template('resultannounce.html')

@app.route('/results', methods=['POST', 'GET'])
def results():
    if request.method == 'POST':
        place = request.form['place']
        connection = sqlite3.connect(f"{place}.db")
        cursor = connection.cursor()
        
        cursor.execute("create table if not exists voting (voter TEXT, candidate_name TEXT, party_name TEXT, election_symbol TEXT, image TEXT)")

        cursor.execute("select * from voting")
        result = cursor.fetchall()
        if result:
            conn = sqlite3.connect("database.db")
            cr = conn.cursor()
            cr.execute("select * from candidates where place = '"+place+"'")
            List = cr.fetchall()
            candidates = []
            parties = []
            for row in List:
                candidates.append(row[1])
                parties.append(row[3])

            votes = []
            
            for name in candidates:
                cursor.execute("select * from voting where candidate_name = '"+name+"'")
                res = cursor.fetchall()
                if res:
                    votes.append(int(len(res)/2))
                else:
                    votes.append(0)
            
            Results = None
            if os.path.exists(f"{place}_result.db"):
                pl_connection = sqlite3.connect(f"{place}_result.db")
                pl_cr = pl_connection.cursor()
                command = """SELECT party, candidate, votes
                FROM Result
                WHERE votes = (SELECT MAX(Votes) FROM Result);"""
                pl_cr.execute(command)
                Results = pl_cr.fetchall()
                Results = list(set(Results))
                print(Results)
            return render_template('results.html', Results=Results, candidates=candidates, parties=parties, votes=votes, place=place, n = len(parties))
        else:
            return render_template('results.html', msg=f"Result not yet announced of {place}")
    return render_template('results.html')


@app.route('/announce/<pls>')
def announce(pls):
    print(pls)
    conn = sqlite3.connect("database.db")
    cr = conn.cursor()
    cr.execute("select * from candidates where place = '"+pls+"'")
    List = cr.fetchall()
    candidates = []
    parties = []
    for row in List:
        candidates.append(row[1])
        parties.append(row[3])

    votes = []
    
    connection = sqlite3.connect(f"{pls}.db")
    cursor = connection.cursor()
    for name in candidates:
        cursor.execute("select * from voting where candidate_name = '"+name+"'")
        res = cursor.fetchall()
        if res:
            votes.append(int(len(res)/2))
        else:
            votes.append(0)
    pl_connection = sqlite3.connect(f"{pls}_result.db")
    pl_cr = pl_connection.cursor()
    pl_cr.execute("create table if not exists Result(party TEXT, candidate TEXT, votes TEXT)")

    for i in range(len(parties)):
        pl_cr.execute("insert into Result values(?,?,?)", [parties[i], candidates[i], votes[i]])
        pl_connection.commit()
    
    command = """SELECT party, candidate, votes
    FROM Result
    WHERE votes = (SELECT MAX(Votes) FROM Result);"""
    pl_cr.execute(command)
    Results = pl_cr.fetchall()
    Results = list(set(Results))
    print(Results)
    return render_template('resultannounce.html', Results=Results, candidates=candidates, parties=parties, votes=votes, place=pls, n = len(parties))
    
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
